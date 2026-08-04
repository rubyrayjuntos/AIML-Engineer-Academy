"""
Module 2 – LLM Architecture Mechanics
======================================
Pure-NumPy implementations of the core numerical mechanics tested in this lab:

  - Causal attention mask construction
  - Multi-head attention (MHA) KV-cache parameter counting
  - Grouped-query attention (GQA) KV-cache accounting
  - Simplified multi-latent attention (MLA) KV-cache accounting
  - Low-rank adapter (LoRA) parameter counting and forward pass
  - Symmetric 4-bit quantization / dequantization
  - GRPO group-advantage normalisation
  - Top-k mixture-of-experts (MoE) routing with capacity and balance metrics

All functions are deterministic and stateless; they accept plain Python scalars
or NumPy arrays and return plain Python scalars or NumPy arrays.
"""
from __future__ import annotations

import math

import numpy as np

# ---------------------------------------------------------------------------
# 1. Causal attention mask
# ---------------------------------------------------------------------------


def causal_mask(seq_len: int) -> np.ndarray:
    """Return a boolean lower-triangular causal mask of shape (seq_len, seq_len).

    mask[i, j] is True when position j may attend to position i
    (i.e. j <= i).
    """
    return np.tril(np.ones((seq_len, seq_len), dtype=bool))


# ---------------------------------------------------------------------------
# 2. KV-cache accounting
# ---------------------------------------------------------------------------


def mha_kv_cache_bytes(
    num_layers: int,
    num_heads: int,
    head_dim: int,
    seq_len: int,
    bytes_per_element: int = 2,
) -> int:
    """Return bytes required for a full MHA KV-cache.

    KV cache stores one K tensor and one V tensor per layer, each of shape
    (num_heads, seq_len, head_dim).
    """
    elements_per_layer = 2 * num_heads * seq_len * head_dim
    return num_layers * elements_per_layer * bytes_per_element


def gqa_kv_cache_bytes(
    num_layers: int,
    num_kv_heads: int,
    head_dim: int,
    seq_len: int,
    bytes_per_element: int = 2,
) -> int:
    """Return bytes required for a GQA KV-cache.

    GQA shares key/value projections across *num_kv_heads* groups instead of
    replicating them for every query head.
    """
    elements_per_layer = 2 * num_kv_heads * seq_len * head_dim
    return num_layers * elements_per_layer * bytes_per_element


def mla_kv_cache_bytes(
    num_layers: int,
    latent_dim: int,
    seq_len: int,
    bytes_per_element: int = 2,
) -> int:
    """Return bytes required for a simplified MLA KV-cache.

    MLA compresses keys and values into a single latent vector of size
    *latent_dim* per position and layer, rather than storing full K and V.
    """
    elements_per_layer = latent_dim * seq_len
    return num_layers * elements_per_layer * bytes_per_element


# ---------------------------------------------------------------------------
# 3. LoRA mechanics
# ---------------------------------------------------------------------------


def lora_trainable_params(
    in_features: int,
    out_features: int,
    rank: int,
) -> int:
    """Return the number of trainable parameters added by one LoRA adapter.

    A LoRA adapter decomposes the weight update as delta_W = B @ A where
    A has shape (rank, in_features) and B has shape (out_features, rank).
    """
    return rank * in_features + out_features * rank


def lora_forward(
    x: np.ndarray,
    W: np.ndarray,
    A: np.ndarray,
    B: np.ndarray,
    alpha: float,
    rank: int,
) -> np.ndarray:
    """Compute the LoRA-adapted linear forward pass.

    output = x @ W.T + (x @ A.T @ B.T) * (alpha / rank)

    Parameters
    ----------
    x : shape (..., in_features)
    W : shape (out_features, in_features) – frozen base weights
    A : shape (rank, in_features)
    B : shape (out_features, rank)
    alpha : LoRA scaling hyper-parameter
    rank : adapter rank (same as A.shape[0])
    """
    base = x @ W.T
    adapter = (x @ A.T @ B.T) * (alpha / rank)
    return base + adapter


# ---------------------------------------------------------------------------
# 4. Symmetric 4-bit quantization
# ---------------------------------------------------------------------------

_INT4_MAX = 7  # signed 4-bit: range [-8, 7]; we use symmetric [-7, 7]


def quantize_symmetric_int4(
    weights: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Quantize a float array to symmetric signed 4-bit integers.

    Returns
    -------
    q_weights : int8 array with values in [-7, 7]
    scale     : float scalar – the per-tensor scale factor
    """
    abs_max = np.max(np.abs(weights))
    if abs_max == 0.0:
        return np.zeros_like(weights, dtype=np.int8), 1.0
    scale = abs_max / _INT4_MAX
    q_weights = np.round(weights / scale).clip(-_INT4_MAX, _INT4_MAX).astype(np.int8)
    return q_weights, float(scale)


def dequantize_symmetric_int4(
    q_weights: np.ndarray,
    scale: float,
) -> np.ndarray:
    """Dequantize symmetric 4-bit integers back to float32."""
    return q_weights.astype(np.float32) * scale


# ---------------------------------------------------------------------------
# 5. GRPO group-advantage normalisation
# ---------------------------------------------------------------------------


def grpo_advantages(rewards: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Normalise a group of scalar rewards to zero mean, unit variance.

    This is the group-relative policy optimisation (GRPO) advantage
    estimator: A_i = (r_i - mean(r)) / (std(r) + eps).

    Parameters
    ----------
    rewards : 1-D float array of per-sample rewards within one group
    eps     : small constant for numerical stability
    """
    rewards = np.asarray(rewards, dtype=np.float64)
    mean = rewards.mean()
    std = rewards.std()
    return (rewards - mean) / (std + eps)


# ---------------------------------------------------------------------------
# 6. Top-k MoE routing
# ---------------------------------------------------------------------------


def moe_routing(
    logits: np.ndarray,
    top_k: int,
    num_experts: int,
    expert_capacity: int,
) -> dict:
    """Compute top-k MoE routing statistics.

    Parameters
    ----------
    logits          : shape (num_tokens, num_experts) – raw router logits
    top_k           : number of experts selected per token
    num_experts     : total number of experts
    expert_capacity : maximum tokens each expert may process

    Returns
    -------
    dict with keys:
      - "dispatch_mask"    : bool array (num_tokens, num_experts)
      - "load_per_expert"  : int array (num_experts,) – tokens dispatched
      - "dropped_tokens"   : int – tokens that exceeded expert capacity
      - "imbalance_ratio"  : float – max_load / mean_load (1.0 = perfect)
    """
    num_tokens, _ = logits.shape

    # Soft-max probabilities (for load computation)
    probs = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs /= probs.sum(axis=1, keepdims=True)

    # Select top-k experts per token (deterministic: ties broken by index)
    top_k_indices = np.argsort(logits, axis=1)[:, -top_k:]  # (T, k)

    dispatch_mask = np.zeros((num_tokens, num_experts), dtype=bool)
    load_per_expert = np.zeros(num_experts, dtype=int)
    dropped_tokens = 0

    for token_idx in range(num_tokens):
        for expert_idx in top_k_indices[token_idx]:
            if load_per_expert[expert_idx] < expert_capacity:
                dispatch_mask[token_idx, expert_idx] = True
                load_per_expert[expert_idx] += 1
            else:
                dropped_tokens += 1

    mean_load = load_per_expert.mean()
    imbalance_ratio = float(load_per_expert.max() / mean_load) if mean_load > 0 else 1.0

    return {
        "dispatch_mask": dispatch_mask,
        "load_per_expert": load_per_expert,
        "dropped_tokens": dropped_tokens,
        "imbalance_ratio": imbalance_ratio,
    }

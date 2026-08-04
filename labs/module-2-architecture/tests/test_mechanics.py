"""
Tests for Module 2 – LLM Architecture Mechanics

13 tests covering:
  - causal_mask (2)
  - KV-cache accounting: mha, gqa, mla (3)
  - LoRA: param count, forward (2)
  - quantization: roundtrip, range (2)
  - GRPO advantages: mean, std (2)
  - MoE routing: dispatch shape, capacity enforcement (2)
"""
import numpy as np
import pytest

from app.mechanics import (
    causal_mask,
    dequantize_symmetric_int4,
    gqa_kv_cache_bytes,
    grpo_advantages,
    lora_forward,
    lora_trainable_params,
    mha_kv_cache_bytes,
    mla_kv_cache_bytes,
    moe_routing,
    quantize_symmetric_int4,
)


# ---------------------------------------------------------------------------
# Causal mask
# ---------------------------------------------------------------------------


def test_causal_mask_shape():
    mask = causal_mask(5)
    assert mask.shape == (5, 5)


def test_causal_mask_lower_triangular():
    mask = causal_mask(8)
    assert np.all(mask == np.tril(np.ones((8, 8), dtype=bool)))


# ---------------------------------------------------------------------------
# KV-cache accounting
# ---------------------------------------------------------------------------


def test_mha_kv_cache_bytes():
    # 2 layers, 4 heads, head_dim=8, seq=10, fp16 (2 bytes)
    result = mha_kv_cache_bytes(
        num_layers=2, num_heads=4, head_dim=8, seq_len=10, bytes_per_element=2
    )
    expected = 2 * (2 * 4 * 10 * 8) * 2
    assert result == expected


def test_gqa_kv_cache_less_than_mha():
    mha = mha_kv_cache_bytes(32, num_heads=32, head_dim=128, seq_len=4096)
    gqa = gqa_kv_cache_bytes(32, num_kv_heads=8, head_dim=128, seq_len=4096)
    assert gqa < mha


def test_mla_kv_cache_less_than_gqa():
    gqa = gqa_kv_cache_bytes(32, num_kv_heads=8, head_dim=128, seq_len=4096)
    mla = mla_kv_cache_bytes(32, latent_dim=512, seq_len=4096)
    assert mla < gqa


# ---------------------------------------------------------------------------
# LoRA
# ---------------------------------------------------------------------------


def test_lora_trainable_params():
    params = lora_trainable_params(in_features=512, out_features=512, rank=8)
    # A: 8*512 + B: 512*8 = 4096 + 4096 = 8192
    assert params == 8192


def test_lora_forward_with_zero_adapter():
    rng = np.random.default_rng(0)
    W = rng.standard_normal((4, 8)).astype(np.float32)
    A = rng.standard_normal((2, 8)).astype(np.float32)
    B = np.zeros((4, 2), dtype=np.float32)  # zero adapter
    x = rng.standard_normal((3, 8)).astype(np.float32)
    out = lora_forward(x, W, A, B, alpha=1.0, rank=2)
    expected = x @ W.T
    np.testing.assert_allclose(out, expected, atol=1e-5)


# ---------------------------------------------------------------------------
# Quantization
# ---------------------------------------------------------------------------


def test_quantization_roundtrip_small_error():
    rng = np.random.default_rng(7)
    weights = rng.standard_normal(256).astype(np.float32)
    q, scale = quantize_symmetric_int4(weights)
    deq = dequantize_symmetric_int4(q, scale)
    max_err = np.max(np.abs(weights - deq))
    # Max error ≤ 0.5 * scale (one quantization step)
    assert max_err <= 0.5 * scale + 1e-6


def test_quantization_range():
    rng = np.random.default_rng(3)
    weights = rng.standard_normal(512).astype(np.float32) * 5
    q, _ = quantize_symmetric_int4(weights)
    assert int(q.min()) >= -7
    assert int(q.max()) <= 7


# ---------------------------------------------------------------------------
# GRPO advantages
# ---------------------------------------------------------------------------


def test_grpo_advantages_mean_near_zero():
    rewards = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    adv = grpo_advantages(rewards)
    assert abs(adv.mean()) < 1e-6


def test_grpo_advantages_std_near_one():
    rewards = np.array([0.5, -1.5, 2.0, 0.0, 3.5, -0.5])
    adv = grpo_advantages(rewards)
    assert abs(adv.std() - 1.0) < 0.01


# ---------------------------------------------------------------------------
# MoE routing
# ---------------------------------------------------------------------------


def test_moe_routing_dispatch_shape():
    rng = np.random.default_rng(99)
    logits = rng.standard_normal((16, 4)).astype(np.float32)
    result = moe_routing(logits, top_k=2, num_experts=4, expert_capacity=10)
    assert result["dispatch_mask"].shape == (16, 4)


def test_moe_routing_capacity_enforced():
    rng = np.random.default_rng(42)
    num_tokens, num_experts, capacity = 32, 4, 5
    logits = rng.standard_normal((num_tokens, num_experts)).astype(np.float32)
    result = moe_routing(logits, top_k=2, num_experts=num_experts, expert_capacity=capacity)
    assert np.all(result["load_per_expert"] <= capacity)

"""
Tests for Module 2 – LLM Architecture Mechanics

Covering:
  - causal_mask, KV-cache, LoRA, quantization, GRPO, MoE
  - diffusion: schedule, q_sample, predict_x0, ddim_step
  - DPO loss toy
"""
import math

import numpy as np
import pytest

from app.mechanics import (
    causal_mask,
    cosine_alpha_bar,
    ddim_step,
    dequantize_symmetric_int4,
    dpo_loss,
    gqa_kv_cache_bytes,
    grpo_advantages,
    lora_forward,
    lora_trainable_params,
    mha_kv_cache_bytes,
    mla_kv_cache_bytes,
    moe_routing,
    predict_x0_from_eps,
    q_sample,
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


def test_lora_forward_applies_nonzero_adapter():
    rng = np.random.default_rng(1)
    W = rng.standard_normal((4, 8)).astype(np.float32)
    A = rng.standard_normal((2, 8)).astype(np.float32)
    B = rng.standard_normal((4, 2)).astype(np.float32)
    x = rng.standard_normal((3, 8)).astype(np.float32)
    alpha, rank = 16.0, 2
    out = lora_forward(x, W, A, B, alpha=alpha, rank=rank)
    expected = x @ W.T + (x @ A.T @ B.T) * (alpha / rank)
    np.testing.assert_allclose(out, expected, atol=1e-5)
    assert not np.allclose(out, x @ W.T, atol=1e-4)


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
    assert result["dispatch_mask"].sum() > 0
    assert result["load_per_expert"].sum() == result["dispatch_mask"].sum()
    assert result["imbalance_ratio"] >= 1.0


def test_moe_routing_capacity_enforced():
    rng = np.random.default_rng(42)
    num_tokens, num_experts, capacity = 32, 4, 5
    logits = rng.standard_normal((num_tokens, num_experts)).astype(np.float32)
    result = moe_routing(logits, top_k=2, num_experts=num_experts, expert_capacity=capacity)
    assert np.all(result["load_per_expert"] <= capacity)


def test_moe_routing_drops_when_capacity_is_tight():
    logits = np.zeros((32, 4), dtype=np.float32)
    logits[:, 0] = 10.0
    result = moe_routing(logits, top_k=1, num_experts=4, expert_capacity=5)
    assert result["load_per_expert"][0] == 5
    assert result["dropped_tokens"] == 27
    assert int(result["dispatch_mask"].sum()) == 5


# ---------------------------------------------------------------------------
# Diffusion schedule
# ---------------------------------------------------------------------------


def test_cosine_alpha_bar_endpoints():
    alpha_bar = cosine_alpha_bar(1000)
    assert alpha_bar.shape == (1000,)
    assert alpha_bar[0] > 0.99
    assert alpha_bar[-1] < 0.05
    assert np.all(np.diff(alpha_bar) <= 1e-12)  # non-increasing


def test_q_sample_t0_near_x0_with_zero_noise():
    alpha_bar = cosine_alpha_bar(1000)
    x0 = np.ones(4, dtype=np.float64)
    eps = np.zeros(4, dtype=np.float64)
    xt = q_sample(x0, t=0, alpha_bar=alpha_bar, eps=eps)
    np.testing.assert_allclose(xt, x0, atol=1e-3)


def test_q_sample_energy_increases_with_t():
    rng = np.random.default_rng(0)
    alpha_bar = cosine_alpha_bar(1000)
    x0 = np.ones(32, dtype=np.float64)
    eps = rng.standard_normal(32)
    e_early = float(np.mean(q_sample(x0, t=10, alpha_bar=alpha_bar, eps=eps) ** 2))
    e_late = float(np.mean(q_sample(x0, t=900, alpha_bar=alpha_bar, eps=eps) ** 2))
    # Clean signal energy is 1; late timesteps should be closer to noise energy (~1)
    # while early timesteps stay closer to x0. Compare SNR-weighted residual instead:
    residual_early = float(np.mean((q_sample(x0, t=10, alpha_bar=alpha_bar, eps=eps) - x0) ** 2))
    residual_late = float(np.mean((q_sample(x0, t=900, alpha_bar=alpha_bar, eps=eps) - x0) ** 2))
    assert residual_late > residual_early
    assert e_late > 0 and e_early > 0


def test_predict_x0_recovers_from_q_sample():
    rng = np.random.default_rng(1)
    alpha_bar = cosine_alpha_bar(200)
    x0 = rng.standard_normal(16)
    eps = rng.standard_normal(16)
    t = 80
    xt = q_sample(x0, t, alpha_bar, eps)
    x0_hat = predict_x0_from_eps(xt, t, alpha_bar, eps)
    np.testing.assert_allclose(x0_hat, x0, atol=1e-9)


def test_ddim_step_identity_at_same_t():
    rng = np.random.default_rng(2)
    alpha_bar = cosine_alpha_bar(100)
    x0 = rng.standard_normal(8)
    eps = rng.standard_normal(8)
    t = 40
    xt = q_sample(x0, t, alpha_bar, eps)
    same = ddim_step(xt, t, alpha_bar, eps, t_prev=t)
    np.testing.assert_allclose(same, xt, atol=1e-9)


def test_ddim_step_reduces_error_toward_x0():
    rng = np.random.default_rng(3)
    alpha_bar = cosine_alpha_bar(100)
    x0 = rng.standard_normal(8)
    eps = rng.standard_normal(8)
    t = 50
    xt = q_sample(x0, t, alpha_bar, eps)
    x_prev = ddim_step(xt, t, alpha_bar, eps, t_prev=t - 1)
    err_t = float(np.mean((xt - x0) ** 2))
    err_prev = float(np.mean((x_prev - x0) ** 2))
    assert err_prev < err_t
    # Full algebraic clean estimate still comes from predict_x0 (ᾱ may not be 1 at index 0).
    x0_hat = predict_x0_from_eps(xt, t, alpha_bar, eps)
    np.testing.assert_allclose(x0_hat, x0, atol=1e-9)


def test_ddim_step_deterministic():
    rng = np.random.default_rng(4)
    alpha_bar = cosine_alpha_bar(64)
    xt = rng.standard_normal(5)
    eps = rng.standard_normal(5)
    a = ddim_step(xt, 20, alpha_bar, eps, t_prev=10)
    b = ddim_step(xt, 20, alpha_bar, eps, t_prev=10)
    np.testing.assert_array_equal(a, b)


# ---------------------------------------------------------------------------
# DPO loss toy
# ---------------------------------------------------------------------------


def test_dpo_loss_beta_zero_is_log2():
    loss = dpo_loss(0.0, 0.0, 0.0, 0.0, beta=0.0)
    assert loss == pytest.approx(math.log(2.0), rel=0, abs=1e-12)


def test_dpo_loss_prefers_higher_margin():
    # Larger preferred-vs-rejected margin under the policy → lower DPO loss.
    low_margin = dpo_loss(logp_w=-1.0, logp_l=-1.1, logp_ref_w=-1.0, logp_ref_l=-1.0, beta=0.5)
    high_margin = dpo_loss(logp_w=-0.2, logp_l=-2.0, logp_ref_w=-1.0, logp_ref_l=-1.0, beta=0.5)
    assert high_margin < low_margin


def test_dpo_loss_known_fixture():
    # β·Δ = 0.1 * ((-0.5 - -1.5) - ( -1.0 - -1.0 )) = 0.1 * 1.0 = 0.1
    # loss = softplus(-0.1) = log(1 + exp(-0.1))
    loss = dpo_loss(-0.5, -1.5, -1.0, -1.0, beta=0.1)
    expected = math.log1p(math.exp(-0.1))
    assert loss == pytest.approx(expected, rel=0, abs=1e-12)


def test_dpo_loss_batch_mean():
    loss = dpo_loss(
        np.array([-0.5, -0.4]),
        np.array([-1.5, -1.4]),
        np.array([-1.0, -1.0]),
        np.array([-1.0, -1.0]),
        beta=0.1,
    )
    a = math.log1p(math.exp(-0.1))
    b = math.log1p(math.exp(-0.1))  # same Δ=1.0 for both rows
    assert loss == pytest.approx(0.5 * (a + b), abs=1e-12)

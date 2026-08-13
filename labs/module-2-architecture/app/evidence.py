"""
Module 2 evidence generator
============================
Produces a machine-readable JSON artifact that demonstrates each competency
implemented in app/mechanics.py.

Usage:
    python -m app.evidence --output artifacts/evidence.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time

import numpy as np

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
from app.qlora_optional import build_qlora_plan, maybe_run_gpu_dry_run

_LAB_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def generate_evidence() -> dict:
    rng = np.random.default_rng(42)
    evidence: dict = {
        "module": "module-2-architecture",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "competencies": {},
        "claims": {
            "gpu_used": False,
            "qlora_executed": False,
            "cuda_available": False,
            "numpy_mechanics_measured": True,
        },
    }

    # 1. Causal mask
    mask = causal_mask(6)
    evidence["competencies"]["causal_attention_mask"] = {
        "seq_len": 6,
        "mask": mask.tolist(),
        "lower_triangular": bool(np.all(np.tril(mask) == mask)),
    }

    # 2. KV-cache accounting
    kv_mha = mha_kv_cache_bytes(32, 32, 128, 4096)
    kv_gqa = gqa_kv_cache_bytes(32, 8, 128, 4096)
    kv_mla = mla_kv_cache_bytes(32, 512, 4096)
    evidence["competencies"]["kv_cache_accounting"] = {
        "mha_bytes": kv_mha,
        "gqa_bytes": kv_gqa,
        "mla_bytes": kv_mla,
        "gqa_reduction_vs_mha": round(kv_mha / kv_gqa, 2),
        "mla_reduction_vs_mha": round(kv_mha / kv_mla, 2),
    }

    # 3. LoRA
    params = lora_trainable_params(4096, 4096, rank=16)
    W = rng.standard_normal((4096, 4096)).astype(np.float32) * 0.02
    A = rng.standard_normal((16, 4096)).astype(np.float32) * 0.01
    B = np.zeros((4096, 16), dtype=np.float32)
    x = rng.standard_normal((1, 4096)).astype(np.float32)
    out = lora_forward(x, W, A, B, alpha=16.0, rank=16)
    evidence["competencies"]["lora"] = {
        "in_features": 4096,
        "out_features": 4096,
        "rank": 16,
        "trainable_params": params,
        "output_shape": list(out.shape),
    }

    # 4. Quantization
    weights = rng.standard_normal(1024).astype(np.float32)
    q, scale = quantize_symmetric_int4(weights)
    deq = dequantize_symmetric_int4(q, scale)
    max_error = float(np.max(np.abs(weights - deq)))
    evidence["competencies"]["quantization_int4"] = {
        "weight_count": len(weights),
        "scale": round(float(scale), 6),
        "max_reconstruction_error": round(max_error, 6),
        "q_range": [int(q.min()), int(q.max())],
    }

    # 5. GRPO
    rewards = np.array([1.0, 0.5, -0.5, 0.0, 2.0, -1.0])
    adv = grpo_advantages(rewards)
    evidence["competencies"]["grpo_advantages"] = {
        "rewards": rewards.tolist(),
        "advantages": [round(float(a), 6) for a in adv],
        "mean_near_zero": bool(abs(adv.mean()) < 1e-6),
        "std_near_one": bool(abs(adv.std() - 1.0) < 0.01),
    }

    # 6. MoE routing
    logits = rng.standard_normal((64, 8)).astype(np.float32)
    result = moe_routing(logits, top_k=2, num_experts=8, expert_capacity=20)
    evidence["competencies"]["moe_routing"] = {
        "num_tokens": 64,
        "num_experts": 8,
        "top_k": 2,
        "expert_capacity": 20,
        "load_per_expert": result["load_per_expert"].tolist(),
        "dropped_tokens": result["dropped_tokens"],
        "imbalance_ratio": round(result["imbalance_ratio"], 4),
    }

    # 7. Diffusion schedule + reverse (DDIM toy)
    alpha_bar = cosine_alpha_bar(1000)
    x0 = np.ones(8, dtype=np.float64)
    eps = rng.standard_normal(8)
    x_mid = q_sample(x0, t=500, alpha_bar=alpha_bar, eps=eps)
    x0_hat = predict_x0_from_eps(x_mid, 500, alpha_bar, eps)
    x_prev = ddim_step(x_mid, 500, alpha_bar, eps, t_prev=499)
    evidence["competencies"]["diffusion_schedule"] = {
        "timesteps": 1000,
        "alpha_bar_first": round(float(alpha_bar[0]), 6),
        "alpha_bar_last": round(float(alpha_bar[-1]), 6),
        "mid_mean_square": round(float(np.mean(x_mid**2)), 6),
        "non_increasing": bool(np.all(np.diff(alpha_bar) <= 1e-12)),
    }
    evidence["competencies"]["diffusion_reverse"] = {
        "method": "ddim_eta0",
        "predict_x0_max_err": round(float(np.max(np.abs(x0_hat - x0))), 12),
        "ddim_error_reduced": bool(
            float(np.mean((x_prev - x0) ** 2)) < float(np.mean((x_mid - x0) ** 2))
        ),
        "note": "Single algebraic reverse step with known eps — not image generation",
    }

    # 8. DPO loss toy
    loss = dpo_loss(-0.5, -1.5, -1.0, -1.0, beta=0.1)
    evidence["competencies"]["dpo_loss"] = {
        "beta": 0.1,
        "loss": round(loss, 8),
        "note": "Closed-form DPO BCE on provided log-probs — not an RLHF train",
    }

    # 9. Optional QLoRA track plan (CPU-safe; never claims GPU by default)
    qlora_plan = maybe_run_gpu_dry_run(build_qlora_plan())
    evidence["optional_gpu_track"] = {
        "qlora_plan_claims": qlora_plan["claims"],
        "lora_rank": qlora_plan["lora"]["r"],
        "note": "Required path is NumPy mechanics; GPU QLoRA is opt-in via ACADEMY_GPU=1",
    }
    evidence["claims"].update(
        {
            "gpu_used": bool(qlora_plan["claims"]["gpu_used"]),
            "qlora_executed": bool(qlora_plan["claims"]["qlora_executed"]),
            "cuda_available": bool(qlora_plan["claims"]["cuda_available"]),
            "diffusion_image_generated": False,
            "dpo_policy_trained": False,
        }
    )

    # Assessment rubric (100 points)
    evidence["assessment_rubric"] = [
        {"competency": "Causal attention mask", "points": 7},
        {"competency": "MHA KV-cache accounting", "points": 7},
        {"competency": "GQA KV-cache accounting", "points": 7},
        {"competency": "MLA KV-cache accounting", "points": 7},
        {"competency": "LoRA parameter counting", "points": 7},
        {"competency": "LoRA forward pass", "points": 7},
        {"competency": "Symmetric 4-bit quantization", "points": 7},
        {"competency": "GRPO advantage normalisation", "points": 7},
        {"competency": "MoE top-k routing", "points": 7},
        {"competency": "Diffusion schedule + DDIM reverse toy", "points": 12},
        {"competency": "DPO loss toy", "points": 8},
        {"competency": "Optional QLoRA plan + honest GPU claims", "points": 9},
        {"competency": "Deterministic evidence artifact", "points": 8},
    ]
    evidence["total_points"] = 100

    evidence_str = json.dumps(evidence, indent=2, sort_keys=True)
    evidence["checksum"] = _sha256(evidence_str)

    return evidence


def main(output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    ev = generate_evidence()
    output.write_text(json.dumps(ev, indent=2))
    print(f"Evidence written to {output}")
    print(f"Checksum: {ev['checksum']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Module 2 evidence artifact")
    parser.add_argument("--output", type=pathlib.Path, default=_LAB_ROOT / "artifacts" / "evidence.json")
    args = parser.parse_args()
    main(args.output)

"""
Optional QLoRA track for Module 2.

Default (CI / Cloud Agent): write a CPU-safe QLoRA *plan* JSON. Never claims
GPU training ran. Does not import torch/transformers unless ACADEMY_GPU=1.

Optional GPU path (local CUDA machine):
  export ACADEMY_GPU=1
  pip install -r requirements-gpu.txt
  # Optionally set ACADEMY_QLORA_MODEL to a tiny local/HF id; otherwise dry-run.
  python -m app.qlora_optional --output artifacts/qlora_plan.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

from app.gpu_gate import cuda_available, gpu_track_requested, track_status

_LAB_ROOT = pathlib.Path(__file__).resolve().parent.parent

DEFAULT_PLAN = {
    "track": "optional-qlora",
    "method": "QLoRA",
    "quantization": {
        "load_in_4bit": True,
        "bnb_4bit_quant_type": "nf4",
        "bnb_4bit_compute_dtype": "bfloat16",
        "bnb_4bit_use_double_quant": True,
    },
    "lora": {
        "r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
        "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
        "bias": "none",
        "task_type": "CAUSAL_LM",
    },
    "maps_from_lab_numerics": {
        "lora_trainable_params": "app.mechanics.lora_trainable_params",
        "symmetric_int4": "app.mechanics.quantize_symmetric_int4",
        "note": "NumPy helpers teach the arithmetic; production QLoRA uses NF4 + PEFT adapters",
    },
    "awq_vs_gguf": {
        "AWQ": "Activation-aware weight-only quantization for GPU inference serving",
        "GGUF": "llama.cpp / edge format after (optional) conversion — not produced by CI",
    },
}


def build_qlora_plan(model_id: str | None = None) -> dict:
    status = track_status()
    plan = {
        **DEFAULT_PLAN,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_id": model_id or "unset-cpu-plan",
        "gate": status,
        "claims": {
            "gpu_used": False,
            "qlora_executed": False,
            "cuda_available": status["cuda_available"],
            "weights_downloaded": False,
        },
    }
    return plan


def maybe_run_gpu_dry_run(plan: dict) -> dict:
    """
    When ACADEMY_GPU=1 and CUDA is available, attempt a *dry-run* validation of
    optional imports. Still does not download large base models unless
    ACADEMY_QLORA_EXECUTE=1 and ACADEMY_QLORA_MODEL are both set.
    """
    import os

    if not gpu_track_requested():
        plan["execution"] = {"status": "skipped", "reason": "ACADEMY_GPU!=1"}
        return plan

    if not cuda_available():
        plan["execution"] = {"status": "skipped", "reason": "CUDA not available"}
        plan["claims"]["cuda_available"] = False
        return plan

    plan["claims"]["cuda_available"] = True
    try:
        import bitsandbytes  # noqa: F401
        import peft  # noqa: F401
        import torch
        import transformers  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        plan["execution"] = {
            "status": "skipped",
            "reason": f"GPU deps missing: {exc}",
            "hint": "pip install -r requirements-gpu.txt",
        }
        return plan

    plan["execution"] = {
        "status": "dry_run_imports_ok",
        "torch_version": getattr(torch, "__version__", "unknown"),
        "cuda_device_count": int(torch.cuda.device_count()),
        "device0": torch.cuda.get_device_name(0) if torch.cuda.device_count() else None,
    }

    execute = os.getenv("ACADEMY_QLORA_EXECUTE", "").strip() == "1"
    model_id = os.getenv("ACADEMY_QLORA_MODEL", "").strip()
    if not execute or not model_id:
        plan["execution"]["train"] = (
            "not_run — set ACADEMY_QLORA_EXECUTE=1 and ACADEMY_QLORA_MODEL=<hf-or-local-id> "
            "to attempt a real train (out of CI scope)"
        )
        return plan

    # Explicit opt-in only: we still refuse silent mega-downloads in academy CI.
    plan["claims"]["gpu_used"] = True
    plan["execution"]["train"] = (
        f"operator_requested model={model_id} — wire your trainer here "
        "(PEFT get_peft_model + Trainer). Academy CI never sets this flag."
    )
    plan["claims"]["qlora_executed"] = False  # honest: no trainer shipped by default
    plan["model_id"] = model_id
    return plan


def main(output: pathlib.Path, model_id: str | None = None) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    plan = maybe_run_gpu_dry_run(build_qlora_plan(model_id))
    output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    print(f"QLoRA plan written to {output}")
    print(f"claims={plan['claims']}")
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optional QLoRA track planner / dry-run")
    parser.add_argument("--output", type=pathlib.Path, default=_LAB_ROOT / "artifacts" / "qlora_plan.json")
    parser.add_argument("--model-id", type=str, default=None)
    args = parser.parse_args()
    main(args.output, args.model_id)

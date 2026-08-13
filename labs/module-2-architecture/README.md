# Module 2 – LLM Architecture Mechanics Lab

## Overview

Pure-NumPy implementations and tests covering the core numerical mechanics
of modern LLM architectures:

| Topic | Implementation |
|---|---|
| Causal attention mask | `app/mechanics.py` |
| MHA / GQA / MLA KV-cache accounting | `app/mechanics.py` |
| LoRA adapter parameter counting & forward pass | `app/mechanics.py` |
| Symmetric 4-bit quantization / dequantization | `app/mechanics.py` |
| GRPO group-advantage normalisation | `app/mechanics.py` |
| Top-k MoE routing with capacity & imbalance | `app/mechanics.py` |
| Cosine diffusion schedule + `q_sample` | `app/mechanics.py` |
| DDIM reverse step + `predict_x0_from_eps` (toy) | `app/mechanics.py` |
| DPO loss toy on log-probs | `app/mechanics.py` |
| Optional QLoRA GPU track (plan / dry-run) | `app/qlora_optional.py` |

## Quick Start (required CPU path)

```bash
cd labs/module-2-architecture
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.evidence --output artifacts/evidence.json
python -m app.qlora_optional --output artifacts/qlora_plan.json
```

Expected test result: **27 passed**

Evidence stays honest: `claims.gpu_used` / `qlora_executed` / `diffusion_image_generated` /
`dpo_policy_trained` are **false** on this path. Reverse diffusion and DPO are
algebraic toys — not image generation or RLHF training.

## Optional GPU track (QLoRA)

Only on a CUDA host you control — **not** Cloud Agent / CI:

```bash
pip install -r requirements-gpu.txt
export ACADEMY_GPU=1
python -m app.qlora_optional --output artifacts/qlora_plan.json
# Real train (operator-owned weights; never set in CI):
# export ACADEMY_QLORA_EXECUTE=1 ACADEMY_QLORA_MODEL=<hf-or-local-id>
```

Pytest marker `gpu` is reserved for CUDA-only cases; default `pytest -q` stays green offline.

## Assessment Rubric (100 points)

NumPy mechanics + diffusion forward/reverse toys + DPO loss toy + optional QLoRA
plan honesty + evidence artifact (see `app/evidence.py` for point breakdown).

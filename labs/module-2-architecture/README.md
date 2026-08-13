# Module 2 – LLM Architecture Mechanics Lab

## Overview

Scaffolded NumPy exercises covering the core numerical mechanics of modern LLM
architectures. Fill the TODOs in `app/mechanics.py`; worked examples (causal
mask, KV-cache bytes, LoRA param count) are already complete.

| Topic | Where |
|---|---|
| Causal attention mask (worked example) | `app/mechanics.py` |
| MHA / GQA / MLA KV-cache accounting (worked examples) | `app/mechanics.py` |
| LoRA param count (worked) + **TODO** `lora_forward` | `app/mechanics.py` |
| **TODO** Symmetric int4 quant / dequant | `app/mechanics.py` |
| **TODO** GRPO advantages | `app/mechanics.py` |
| **TODO** Top-k MoE routing | `app/mechanics.py` |
| **TODO** Cosine diffusion schedule + `q_sample` | `app/mechanics.py` |
| **TODO** DDIM reverse step + `predict_x0_from_eps` (toy) | `app/mechanics.py` |
| **TODO** DPO loss toy on log-probs | `app/mechanics.py` |
| Reference solutions (CI / peek only) | `app/mechanics_reference.py` |
| Optional QLoRA GPU track (plan / dry-run) | `app/qlora_optional.py` |

## Learner path (implement TODOs)

```bash
cd labs/module-2-architecture
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Leave ACADEMY_SOLUTION unset so pytest grades your stubs:
pytest -q
python -m app.evidence --output artifacts/evidence.json
python -m app.qlora_optional --output artifacts/qlora_plan.json
```

Until the TODOs are filled, mechanics tests fail with `NotImplementedError`.

After you implement the TODOs, expect **31 passed** (same as CI solution mode).

## Solution mode (CI / peek at reference)

```bash
ACADEMY_SOLUTION=1 pytest -q
ACADEMY_SOLUTION=1 python -m app.evidence --output artifacts/evidence.json
```

`ACADEMY_SOLUTION=1` overlays `mechanics_reference.py` onto `app.mechanics` at
import time. Use this to verify the lab harness, not to skip the exercises.
Do **not** copy-paste the reference into a PR that claims you did the work.

Expected under solution mode: **31 passed**.

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

`ACADEMY_GPU` and `ACADEMY_SOLUTION` are independent gates.

## Assessment Rubric (100 points)

NumPy mechanics + diffusion forward/reverse toys + DPO loss toy + optional QLoRA
plan honesty + evidence artifact (see `app/evidence.py` for point breakdown).

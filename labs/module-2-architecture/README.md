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

## Quick Start

```bash
cd labs/module-2-architecture
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.evidence --output artifacts/evidence.json
```

Expected test result: **16 passed**

## Assessment Rubric (100 points)

1. Causal attention mask (9)
2. MHA KV-cache accounting (9)
3. GQA KV-cache accounting (9)
4. MLA KV-cache accounting (9)
5. LoRA parameter counting (9)
6. LoRA forward pass (9)
7. Symmetric 4-bit quantization (9)
8. GRPO advantage normalisation (9)
9. MoE top-k routing (9)
10. Diffusion schedule numerics (10)
11. Deterministic evidence artifact (9)

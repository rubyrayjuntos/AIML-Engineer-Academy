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

## Quick Start

```bash
cd labs/module-2-architecture
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.evidence --output artifacts/evidence.json
```

Expected test result: **13 passed**

## Assessment Rubric (100 points)

Each of the ten competency areas is worth 10 points:

1. Causal attention mask
2. MHA KV-cache accounting
3. GQA KV-cache accounting
4. MLA KV-cache accounting
5. LoRA parameter counting
6. LoRA forward pass
7. Symmetric 4-bit quantization
8. GRPO advantage normalisation
9. MoE top-k routing
10. Deterministic evidence artifact

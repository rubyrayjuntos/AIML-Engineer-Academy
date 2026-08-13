# Module 5 – Evaluation, Observability, Release, and Rollback Lab

This lab implements the production control plane around a model release. The
**required** path runs locally and in CI without cloud credentials. Optional
DeepEval / Promptfoo / Hugging Face / Render tracks are opt-in and claim-gated.

## Controls exercised

- immutable model versions and artifact checksum verification
- offline EDD helpers (`app/eval_offline.py`) feeding faithfulness/relevancy/safety/latency/reliability gates
- Promptfoo-shaped plan validation (`app/promptfoo_plan.py`) without Node in CI
- candidate → canary → production promotion with an append-only audit trail
- **bad-canary lab** (`app/canary_lab.py`): degraded canary window → block production → `reject_canary` (retire) without changing `active`
- telemetry summaries + SLO/quality alerts and tested rollback
- Azure AI Foundry / Databricks / **Hugging Face** / **Render** deployment plans
- honest evidence claims (`*_deployed` / `*_executed` / `cloud_canary` false by default)

## Run (required)

```bash
cd labs/module-5-production-operations
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.evidence --output artifacts/evidence.json
python -m app.canary_lab --mode quality_regression
```

Expected: **32 passed**

## Optional tracks (never enable in Cloud Agent / default CI)

| Track | Env | Entry |
|---|---|---|
| DeepEval | `ACADEMY_EVAL=1` + `XAI_API_KEY` or `OPENAI_API_KEY` | `pip install -r requirements-eval.txt` then `python -m app.deepeval_optional` |
| Promptfoo | `ACADEMY_PROMPTFOO=1` | `./scripts/run_promptfoo_optional.sh` |
| Hugging Face / Render | `ACADEMY_DEPLOY=1` + `HF_TOKEN` / `RENDER_API_KEY` | `app.deploy_optional.maybe_deploy(...)` |

Claims flip to executed/deployed **only** after a successful live call.

## Cloud execution boundary

Azure/Databricks remain plan adapters here. HF/Render may perform gated live
calls when credentials are present. Never embed secrets in evidence JSON.

## Assessment rubric (100 points)

Immutable registry, artifact integrity, offline evaluation, optional-tool honesty,
promotion gates, canary sequencing, bad-canary reject/retire, telemetry, alerts,
audited rollback, truthful provider claims.

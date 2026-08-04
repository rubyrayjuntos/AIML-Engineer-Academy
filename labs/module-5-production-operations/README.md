# Module 5 – Evaluation, Observability, Release, and Rollback Lab

This lab implements the production control plane around a model release. It runs locally and in CI without cloud credentials, while generating deployment plans that map directly to Azure AI Foundry managed online endpoints and Databricks model-serving endpoints. It never claims that CI deployed paid cloud infrastructure.

## Controls exercised

- immutable model versions and artifact checksum verification
- deterministic faithfulness, relevancy, safety, latency, and reliability gates
- candidate → canary → production promotion with an append-only audit trail
- telemetry summaries for latency, errors, quality, drift, token use, and cost
- alerts tied to SLO and quality thresholds
- tested rollback that restores the prior production version
- credential-free Azure AI Foundry and Databricks deployment plans

## Run

```bash
cd labs/module-5-production-operations
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.evidence --output artifacts/evidence.json
python -m json.tool artifacts/evidence.json >/dev/null
```

## Cloud execution boundary

The local control plane is the acceptance baseline. A real deployment must replace the plan adapter with the official Azure ML/AI Foundry or Databricks SDK, use workload identity rather than embedded secrets, store model versions in the provider registry, export OpenTelemetry to an approved backend, and attach provider-generated deployment IDs to the release audit event. Deployment requires an explicit human approval outside this lab.

## Assessment rubric (100 points)

Ten equally weighted competencies: immutable registry, artifact integrity, offline evaluation, promotion gates, canary sequencing, telemetry, drift/quality alerts, cost evidence, audited rollback, and truthful provider claims.

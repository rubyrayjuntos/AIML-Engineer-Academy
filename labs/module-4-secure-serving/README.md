# Module 4 – Secure Serving and Measured Benchmarking Lab

This lab exposes a real authenticated FastAPI inference path and measures it under concurrent load. Its deterministic CPU engine makes CI reproducible and defines an adapter boundary for a later vLLM deployment. The evidence explicitly records that CI did **not** measure a GPU or vLLM.

## Production controls exercised

- constant-time API-key authentication and strict Pydantic request bounds
- rate limiting, bounded server concurrency, and inference timeouts
- correlation IDs, controlled errors, and no-store/security response headers
- concurrent load generation with p50/p95/p99 latency and throughput
- explicit regression budgets that fail the benchmark process
- machine-readable environment, workload, results, claims, and checksum

## Run

```bash
cd labs/module-4-secure-serving
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.benchmark --requests 40 --concurrency 8 --output artifacts/benchmark.json
python -m app.evidence --output artifacts/evidence.json
```

To exercise the endpoint manually:

```bash
ACADEMY_API_KEY=change-me uvicorn app.service:app --host 127.0.0.1 --port 8000
curl -s http://127.0.0.1:8000/v1/generate -H 'content-type: application/json' -H 'x-api-key: change-me' -d '{"prompt":"Assess account risk","max_tokens":24}'
```

## Measurement contract

Do not compare benchmark runs unless engine, hardware, Python/runtime versions, request distribution, concurrency, warm-up policy, and token limits are recorded. For GPU/vLLM, also record model revision, serving version, accelerator, precision, tensor parallelism, block size, batch limits, TTFT, ITL, tokens/second, and peak GPU memory.

## Assessment rubric (100 points)

Ten equally weighted competencies are recorded in the evidence artifact: authentication, validation, rate limiting, concurrency, timeouts, correlation, load generation, percentile latency, throughput/regression gates, and reproducible evidence/threat modeling.

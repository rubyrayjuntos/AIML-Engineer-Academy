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
ACADEMY_API_KEY=academy-local-key uvicorn app.service:app --host 127.0.0.1 --port 8000
curl -s http://127.0.0.1:8000/v1/generate -H 'content-type: application/json' -H 'x-api-key: academy-local-key' -d '{"prompt":"Assess account risk","max_tokens":24}'
```

## Measurement contract

Do not compare benchmark runs unless engine, hardware, Python/runtime versions, request distribution, concurrency, warm-up policy, and token limits are recorded. For GPU/vLLM, also record model revision, serving version, accelerator, precision, tensor parallelism, block size, batch limits, TTFT, ITL, tokens/second, and peak GPU memory.

## Assessment rubric (100 points)

Ten equally weighted competencies are recorded in the evidence artifact: authentication, validation, rate limiting, concurrency, timeouts, correlation, load generation, percentile latency, throughput/regression gates, and reproducible evidence/threat modeling.

## Speculative decoding teaching helpers

Pure-Python estimates live in `app/speculation.py` (`expected_accepted_length`, `speculative_speedup`). They are **not** GPU/vLLM measurements — see tests in `tests/test_speculation.py`.

## Optional GPU track (vLLM)

Default CI path uses `DeterministicEngine` only. To attach a real OpenAI-compatible vLLM server on a CUDA host:

```bash
pip install -r requirements-gpu.txt   # dedicated env recommended
export ACADEMY_GPU=1
./scripts/start_vllm_optional.sh      # serves on :8001 by default
export ACADEMY_ENGINE=vllm ACADEMY_VLLM_URL=http://127.0.0.1:8001
uvicorn app.serve_optional:app --host 127.0.0.1 --port 8000
```

- Protocol: `app.engine.InferenceEngine`
- Adapter: `app.vllm_adapter.OpenAICompatEngine` (HTTP — does not `import vllm` in the FastAPI process)
- Factory refuses `ACADEMY_ENGINE=vllm` unless `ACADEMY_GPU=1` (prevents silent mislabeling)
- Evidence `claims.vllm_measured` / `gpu_used` stay false unless you intentionally record a live GPU run

Pytest: default suite is CPU-green; `@pytest.mark.gpu` live checks are skipped offline.

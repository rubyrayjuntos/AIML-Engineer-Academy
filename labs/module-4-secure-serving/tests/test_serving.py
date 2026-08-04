import asyncio
import httpx
import pytest
from app.benchmark import evaluate_budgets, percentile, run_benchmark
from app.service import DeterministicEngine, Settings, create_app

async def request(app, method="GET", path="/health", **kwargs):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        return await client.request(method, path, **kwargs)

def test_health_is_public_and_identifies_engine():
    response = asyncio.run(request(create_app()))
    assert response.status_code == 200
    assert response.json()["model"] == "deterministic-cpu-v1"

def test_generate_requires_api_key():
    response = asyncio.run(request(create_app(), "POST", "/v1/generate", json={"prompt": "hello"}))
    assert response.status_code == 401

def test_generate_rejects_wrong_api_key():
    response = asyncio.run(request(create_app(), "POST", "/v1/generate", headers={"x-api-key": "wrong"}, json={"prompt": "hello"}))
    assert response.status_code == 401

def test_generate_returns_typed_measured_response():
    response = asyncio.run(request(create_app(), "POST", "/v1/generate", headers={"x-api-key": "academy-local-key", "x-request-id": "test-123"}, json={"prompt": "customer risk", "max_tokens": 8}))
    body = response.json()
    assert response.status_code == 200
    assert body["request_id"] == "test-123" and body["output_tokens"] == 8
    assert body["elapsed_ms"] > 0

@pytest.mark.parametrize("payload", [{"prompt": ""}, {"prompt": "x" * 513}, {"prompt": "ok", "max_tokens": 0}, {"prompt": "ok", "max_tokens": 129}, {"prompt": "ok", "unexpected": True}])
def test_request_bounds_are_enforced(payload):
    response = asyncio.run(request(create_app(), "POST", "/v1/generate", headers={"x-api-key": "academy-local-key"}, json=payload))
    assert response.status_code == 422

def test_security_headers_are_set():
    response = asyncio.run(request(create_app()))
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-request-id"]

def test_generated_request_id_matches_body_and_header():
    response = asyncio.run(request(create_app(), "POST", "/v1/generate", headers={"x-api-key": "academy-local-key"}, json={"prompt": "correlate"}))
    assert response.json()["request_id"] == response.headers["x-request-id"]

def test_rate_limit_returns_429():
    async def scenario():
        app = create_app(Settings(rate_limit=1))
        headers = {"x-api-key": "academy-local-key"}
        return [await request(app, "POST", "/v1/generate", headers=headers, json={"prompt": "a"}) for _ in range(2)]
    first, second = asyncio.run(scenario())
    assert first.status_code == 200 and second.status_code == 429

def test_timeout_returns_controlled_504():
    class SlowEngine(DeterministicEngine):
        async def generate(self, prompt, max_tokens):
            await asyncio.sleep(0.05)
            return "late", 1
    app = create_app(Settings(request_timeout_seconds=0.001), SlowEngine())
    response = asyncio.run(request(app, "POST", "/v1/generate", headers={"x-api-key": "academy-local-key"}, json={"prompt": "slow"}))
    assert response.status_code == 504 and response.json()["detail"] == "inference timeout"

def test_percentile_uses_nearest_rank():
    assert percentile([1, 2, 3, 4, 100], 0.95) == 100

def test_percentile_rejects_empty_input():
    with pytest.raises(ValueError):
        percentile([], 0.95)

def test_benchmark_measures_all_requests():
    report = asyncio.run(run_benchmark(requests=12, concurrency=6))
    assert report["results"]["successes"] == 12 and report["results"]["errors"] == 0
    assert report["results"]["latency_ms"]["p95"] >= report["results"]["latency_ms"]["p50"]
    assert report["results"]["throughput_rps"] > 0

def test_budget_evaluation_detects_regression():
    report = asyncio.run(run_benchmark(requests=4, concurrency=2))
    report["results"]["latency_ms"]["p95"] = 999
    assert evaluate_budgets(report)["p95_latency"] is False

def test_benchmark_validates_arguments():
    with pytest.raises(ValueError):
        asyncio.run(run_benchmark(requests=0))

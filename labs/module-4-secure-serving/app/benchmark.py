from __future__ import annotations

import argparse
import asyncio
import json
import math
import platform
import statistics
import time
from pathlib import Path

import httpx

from app.service import Settings, create_app


def percentile(values: list[float], quantile: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    ordered = sorted(values)
    rank = max(0, math.ceil(quantile * len(ordered)) - 1)
    return ordered[rank]


async def run_benchmark(requests: int = 40, concurrency: int = 8) -> dict:
    if requests < 1 or concurrency < 1:
        raise ValueError("requests and concurrency must be positive")
    settings = Settings(rate_limit=requests + 1, max_concurrency=4)
    transport = httpx.ASGITransport(app=create_app(settings))
    semaphore = asyncio.Semaphore(concurrency)
    latencies: list[float] = []
    statuses: list[int] = []

    async with httpx.AsyncClient(transport=transport, base_url="http://academy") as client:
        async def one(index: int) -> None:
            async with semaphore:
                start = time.perf_counter()
                response = await client.post(
                    "/v1/generate",
                    headers={"x-api-key": settings.api_key, "x-request-id": f"bench-{index}"},
                    json={"prompt": f"Assess customer churn risk for account {index}", "max_tokens": 24},
                )
                latencies.append((time.perf_counter() - start) * 1000)
                statuses.append(response.status_code)

        started = time.perf_counter()
        await asyncio.gather(*(one(index) for index in range(requests)))
        duration = time.perf_counter() - started

    successes = statuses.count(200)
    return {
        "benchmark_version": 1,
        "engine": "deterministic-cpu-v1",
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "workload": {"requests": requests, "client_concurrency": concurrency, "server_concurrency": settings.max_concurrency},
        "results": {
            "successes": successes,
            "errors": requests - successes,
            "duration_seconds": round(duration, 6),
            "throughput_rps": round(successes / duration, 3),
            "latency_ms": {
                "mean": round(statistics.fmean(latencies), 3),
                "p50": round(percentile(latencies, 0.50), 3),
                "p95": round(percentile(latencies, 0.95), 3),
                "p99": round(percentile(latencies, 0.99), 3),
                "max": round(max(latencies), 3),
            },
        },
        "budgets": {"error_rate_max": 0.0, "p95_ms_max": 250.0, "throughput_rps_min": 20.0},
    }


def evaluate_budgets(report: dict) -> dict[str, bool]:
    results, budgets = report["results"], report["budgets"]
    total = results["successes"] + results["errors"]
    return {
        "error_rate": results["errors"] / total <= budgets["error_rate_max"],
        "p95_latency": results["latency_ms"]["p95"] <= budgets["p95_ms_max"],
        "throughput": results["throughput_rps"] >= budgets["throughput_rps_min"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=40)
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path("artifacts/benchmark.json"))
    args = parser.parse_args()
    result = asyncio.run(run_benchmark(args.requests, args.concurrency))
    result["gates"] = evaluate_budgets(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["results"], indent=2))
    if not all(result["gates"].values()):
        raise SystemExit("benchmark regression budget failed")

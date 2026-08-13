from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from app.benchmark import evaluate_budgets, run_benchmark
from app.speculation import expected_accepted_length, speculative_speedup


def generate(output: Path) -> dict:
    report = asyncio.run(run_benchmark())
    report["gates"] = evaluate_budgets(report)
    report["module"] = "module-4-secure-serving"
    report["security_controls"] = [
        "constant-time API-key comparison", "strict typed request bounds", "rate limiting",
        "bounded concurrency", "inference timeout", "request correlation", "no-store responses",
    ]
    report["speculative_decoding_teaching"] = {
        "gamma": 5,
        "accept_prob": 0.7,
        "expected_tokens_per_cycle": round(expected_accepted_length(5, 0.7), 4),
        "teaching_speedup": round(speculative_speedup(5, 0.7, 0.2, 1.0), 4),
        "note": "CPU closed-form estimate only; not a GPU/vLLM measurement",
    }
    report["optional_gpu_track"] = {
        "default_engine": "deterministic-cpu-v1",
        "adapter": "app.vllm_adapter.OpenAICompatEngine",
        "entrypoint": "uvicorn app.serve_optional:app",
        "start_script": "scripts/start_vllm_optional.sh",
        "env": ["ACADEMY_GPU=1", "ACADEMY_ENGINE=vllm", "ACADEMY_VLLM_URL"],
        "note": "CI never starts vLLM; claims below stay false unless you measure a live server",
    }
    report["claims"] = {"gpu_used": False, "vllm_measured": False, "local_cpu_path_measured": True}
    report["rubric"] = [
        {"competency": name, "points": 10} for name in [
            "authenticated endpoint", "strict input validation", "rate limiting", "bounded concurrency",
            "timeout and safe errors", "request correlation", "concurrent load generation",
            "percentile latency", "throughput and regression budgets", "reproducible evidence and threat model",
        ]
    ]
    report["total_points"] = 100
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"))
    report["checksum"] = hashlib.sha256(canonical.encode()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/evidence.json"))
    args = parser.parse_args()
    result = generate(args.output)
    print(f"Evidence written to {args.output}")
    print(f"Checksum: {result['checksum']}")

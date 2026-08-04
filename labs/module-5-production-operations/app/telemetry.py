from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class Observation:
    latency_ms: float
    success: bool
    quality: float
    input_drift: float
    tokens: int
    cost_usd: float


def summarize(items: list[Observation]) -> dict[str, float | int]:
    if not items:
        raise ValueError("observations are required")
    latencies = sorted(item.latency_ms for item in items)
    p95_index = max(0, min(len(latencies) - 1, int(0.95 * len(latencies) + 0.999) - 1))
    return {
        "requests": len(items),
        "success_rate": sum(item.success for item in items) / len(items),
        "quality": mean(item.quality for item in items),
        "input_drift": mean(item.input_drift for item in items),
        "p95_ms": latencies[p95_index],
        "tokens": sum(item.tokens for item in items),
        "cost_usd": round(sum(item.cost_usd for item in items), 6),
    }


def alerts(summary: dict[str, float | int]) -> list[str]:
    triggered = []
    if summary["success_rate"] < 0.99:
        triggered.append("error_budget_burn")
    if summary["quality"] < 0.90:
        triggered.append("quality_regression")
    if summary["input_drift"] > 0.20:
        triggered.append("input_drift")
    if summary["p95_ms"] > 750:
        triggered.append("latency_slo")
    return triggered

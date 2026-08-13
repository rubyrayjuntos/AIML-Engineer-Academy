"""
Module 5 — Bad Canary Lab
=========================
Teach detecting a degraded canary window, blocking production promotion, and
rejecting/retiring the canary. CPU-only; no cloud deploy claims.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass
from typing import Literal

from app.eval_offline import evaluation_from_case
from app.release import Evaluation, ModelVersion, Policy, ReleaseStore, evaluate_gates
from app.telemetry import Observation, alerts, summarize

_LAB_ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_FIXTURE = _LAB_ROOT / "fixtures" / "canary_cases.json"

CanaryMode = Literal["good", "quality_regression", "latency_regression", "safety_regression"]


@dataclass(frozen=True)
class CanaryPolicy:
    """Absolute Policy gates plus optional deltas vs a healthy baseline."""

    absolute: Policy = Policy()
    max_faithfulness_drop: float = 0.05
    max_relevancy_drop: float = 0.05
    max_safety_drop: float = 0.02
    max_p95_ratio: float = 1.5


def load_canary_cases(path: pathlib.Path = DEFAULT_FIXTURE) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def cases_for_mode(mode: CanaryMode, path: pathlib.Path = DEFAULT_FIXTURE) -> list[dict]:
    return [c for c in load_canary_cases(path) if c["mode"] == mode]


def evaluation_from_canary_case(case: dict) -> Evaluation:
    """Prefer explicit fixture gate metrics; fall back to offline string heuristics."""
    if all(k in case for k in ("faithfulness", "relevancy", "safety")):
        return Evaluation(
            float(case["faithfulness"]),
            float(case["relevancy"]),
            float(case["safety"]),
            float(case.get("p95_ms", 220)),
            float(case.get("error_rate", 0.0)),
        )
    return evaluation_from_case(
        case["question"],
        case["answer"],
        case["context"],
        p95_ms=float(case.get("p95_ms", 220)),
        error_rate=float(case.get("error_rate", 0.0)),
    )


def aggregate_canary_window(evals: list[Evaluation]) -> Evaluation:
    if not evals:
        raise ValueError("canary window requires evaluations")
    n = len(evals)
    return Evaluation(
        faithfulness=round(sum(e.faithfulness for e in evals) / n, 4),
        relevancy=round(sum(e.relevancy for e in evals) / n, 4),
        safety=round(min(e.safety for e in evals), 4),
        p95_ms=max(e.p95_ms for e in evals),
        error_rate=max(e.error_rate for e in evals),
    )


def observations_from_canary_evals(evals: list[Evaluation]) -> list[Observation]:
    return [
        Observation(
            latency_ms=e.p95_ms,
            success=e.error_rate < 0.5,
            quality=(e.faithfulness + e.relevancy + e.safety) / 3.0,
            input_drift=0.05,
            tokens=40,
            cost_usd=0.001,
        )
        for e in evals
    ]


def canary_regression_gates(
    baseline: Evaluation,
    canary: Evaluation,
    policy: CanaryPolicy | None = None,
) -> dict[str, bool]:
    """Absolute release gates plus delta checks vs a healthy baseline."""
    policy = policy or CanaryPolicy()
    absolute = evaluate_gates(canary, policy.absolute)
    deltas = {
        "faithfulness_delta": (baseline.faithfulness - canary.faithfulness)
        <= policy.max_faithfulness_drop,
        "relevancy_delta": (baseline.relevancy - canary.relevancy)
        <= policy.max_relevancy_drop,
        "safety_delta": (baseline.safety - canary.safety) <= policy.max_safety_drop,
        "latency_ratio": canary.p95_ms
        <= max(policy.absolute.max_p95_ms, baseline.p95_ms * policy.max_p95_ratio),
    }
    return {**absolute, **deltas}


def run_bad_canary_scenario(
    store: ReleaseStore,
    *,
    mode: CanaryMode = "quality_regression",
    actor: str = "canary-lab",
) -> dict:
    """
    1) Ship a good baseline to production.
    2) Promote a new candidate to canary with good candidate metrics.
    3) Observe a degraded canary window; block production promotion; reject canary.
    """
    if mode == "good":
        raise ValueError("use mode=good only via the control-path helper")

    good_cases = cases_for_mode("good")
    if not good_cases:
        raise RuntimeError("missing good fixture cases")
    baseline_eval = evaluation_from_canary_case(good_cases[0])
    bad_cases = cases_for_mode(mode)
    if not bad_cases:
        raise RuntimeError(f"missing fixture cases for mode={mode}")

    artifact_v1 = b"bad-canary-baseline-v1"
    artifact_v2 = f"bad-canary-{mode}-v2".encode()
    v1 = ModelVersion(
        "churn-risk",
        "bc-1",
        "models:/churn-risk/bc-1",
        hashlib.sha256(artifact_v1).hexdigest(),
    )
    v2 = ModelVersion(
        "churn-risk",
        "bc-2",
        "models:/churn-risk/bc-2",
        hashlib.sha256(artifact_v2).hexdigest(),
    )

    store.register(v1, actor)
    store.promote(v1.version, baseline_eval, actor, "canary")
    store.promote(v1.version, baseline_eval, actor, "production")

    store.register(v2, actor)
    # Candidate → canary uses healthy metrics (shipped canary looks fine initially).
    store.promote(v2.version, baseline_eval, actor, "canary")

    window_evals = [evaluation_from_canary_case(c) for c in bad_cases]
    # Repeat the bad window a few times to simulate observation samples.
    window_evals = window_evals * 3
    canary_eval = aggregate_canary_window(window_evals)
    gates = canary_regression_gates(baseline_eval, canary_eval)
    obs = observations_from_canary_evals(window_evals)
    telemetry = summarize(obs)
    alert_list = alerts(telemetry)

    blocked = False
    block_error: str | None = None
    try:
        store.promote(v2.version, canary_eval, actor, "production")
    except ValueError as exc:
        blocked = True
        block_error = str(exc)

    if not blocked:
        raise RuntimeError("expected production promotion to fail for bad canary")

    store.reject_canary(v2.version, actor, f"bad canary window: {mode}")
    state = store.state()
    return {
        "mode": mode,
        "baseline": baseline_eval.__dict__,
        "canary_window": canary_eval.__dict__,
        "gates": gates,
        "gates_passed": all(gates.values()),
        "telemetry": telemetry,
        "alerts": alert_list,
        "promotion_blocked": blocked,
        "block_error": block_error,
        "active": state["active"],
        "canary_stage": state["stages"][v2.version]["stage"],
        "events": [e["action"] for e in state["events"]],
        "claims": {
            "cloud_canary": False,
            "production_promoted_bad_canary": False,
            "canary_rejected": True,
        },
    }


def run_good_canary_control(store: ReleaseStore, *, actor: str = "canary-lab") -> dict:
    """Control path: healthy canary window still promotes to production."""
    good_cases = cases_for_mode("good")
    baseline_eval = evaluation_from_canary_case(good_cases[0])
    window = aggregate_canary_window(
        [evaluation_from_canary_case(c) for c in good_cases] * 2
    )
    artifact = b"good-canary-control"
    model = ModelVersion(
        "churn-risk",
        "gc-1",
        "models:/churn-risk/gc-1",
        hashlib.sha256(artifact).hexdigest(),
    )
    store.register(model, actor)
    store.promote(model.version, baseline_eval, actor, "canary")
    store.promote(model.version, window, actor, "production")
    return {
        "mode": "good",
        "active": store.state()["active"],
        "stage": store.state()["stages"][model.version]["stage"],
        "gates": canary_regression_gates(baseline_eval, window),
    }


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Module 5 bad-canary lab")
    parser.add_argument(
        "--mode",
        default="quality_regression",
        choices=["quality_regression", "latency_regression", "safety_regression"],
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--state",
        type=Path,
        default=Path("artifacts/bad-canary-state.json"),
        help="Release store path (replaced each run)",
    )
    args = parser.parse_args()
    if args.state.exists():
        args.state.unlink()
    store = ReleaseStore(args.state)
    result = run_bad_canary_scenario(store, mode=args.mode)  # type: ignore[arg-type]
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "mode": result["mode"],
        "promotion_blocked": result["promotion_blocked"],
        "canary_stage": result["canary_stage"],
        "active": result["active"],
        "alerts": result["alerts"],
        "claims": result["claims"],
    }, sort_keys=True))

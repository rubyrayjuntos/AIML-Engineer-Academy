"""
Optional DeepEval track.

Default: return a CPU-safe plan describing metrics/cases without importing deepeval.
Live path: only when ACADEMY_EVAL=1 and a judge API key is present.
"""
from __future__ import annotations

import os
from typing import Any


def eval_track_requested() -> bool:
    return os.getenv("ACADEMY_EVAL", "").strip() == "1"


def judge_key_present() -> bool:
    return bool(os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY"))


def build_deepeval_plan(
    model: str | None = None,
    cases: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    model_id = model or os.getenv("ACADEMY_EVAL_MODEL", "grok-4.6")
    sample_cases = cases or [
        {
            "input": "When does customer #101 subscription expire?",
            "actual_output": "Customer #101 subscription is active until December 31, 2026.",
            "retrieval_context": "Customer #101 has an active subscription expiring on 2026-12-31.",
        }
    ]
    return {
        "track": "optional-deepeval",
        "framework": "deepeval",
        "model": model_id,
        "metrics": ["FaithfulnessMetric", "AnswerRelevancyMetric"],
        "threshold": 0.8,
        "cases": sample_cases,
        "gate": {
            "academy_eval": eval_track_requested(),
            "judge_key_present": judge_key_present(),
        },
        "claims": {
            "deepeval_executed": False,
            "note": "Install requirements-eval.txt and set ACADEMY_EVAL=1 + judge key to run live metrics",
        },
    }


def maybe_run_deepeval(plan: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = plan or build_deepeval_plan()
    if not eval_track_requested():
        plan["execution"] = {"status": "skipped", "reason": "ACADEMY_EVAL!=1"}
        return plan
    if not judge_key_present():
        plan["execution"] = {"status": "skipped", "reason": "missing XAI_API_KEY/OPENAI_API_KEY"}
        return plan
    try:
        from deepeval import assert_test  # type: ignore
        from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric  # type: ignore
        from deepeval.test_case import LLMTestCase  # type: ignore
    except Exception as exc:  # noqa: BLE001
        plan["execution"] = {
            "status": "skipped",
            "reason": f"deepeval import failed: {exc}",
            "hint": "pip install -r requirements-eval.txt",
        }
        return plan

    model = plan["model"]
    results = []
    for case in plan["cases"]:
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=case["actual_output"],
            retrieval_context=[case["retrieval_context"]],
        )
        metrics = [
            FaithfulnessMetric(threshold=plan["threshold"], model=model),
            AnswerRelevancyMetric(threshold=plan["threshold"], model=model),
        ]
        try:
            assert_test(test_case, metrics)
            results.append({"input": case["input"], "passed": True})
        except Exception as exc:  # noqa: BLE001
            results.append({"input": case["input"], "passed": False, "error": str(exc)})

    plan["execution"] = {"status": "ran", "results": results}
    plan["claims"]["deepeval_executed"] = True
    plan["claims"]["all_passed"] = all(r.get("passed") for r in results)
    return plan


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Optional DeepEval track")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = maybe_run_deepeval(build_deepeval_plan())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": result["claims"], "execution": result.get("execution")}, sort_keys=True))

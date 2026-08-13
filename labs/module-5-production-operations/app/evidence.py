"""
Module 5 evidence generator
============================
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

from app.canary_lab import run_bad_canary_scenario
from app.deepeval_optional import build_deepeval_plan, maybe_run_deepeval
from app.deploy_optional import build_deploy_plan
from app.eval_offline import evaluation_from_case
from app.promptfoo_plan import build_promptfoo_plan
from app.providers import deployment_plan
from app.release import Evaluation, ModelVersion, ReleaseStore
from app.telemetry import Observation, alerts, summarize


def generate(output: Path) -> dict:
    artifact_v1 = b"customer-success-model-v1"
    model_v1 = ModelVersion("churn-risk", "1", "models:/churn-risk/1", hashlib.sha256(artifact_v1).hexdigest())
    artifact_v2 = b"customer-success-model-v2"
    model_v2 = ModelVersion("churn-risk", "2", "models:/churn-risk/2", hashlib.sha256(artifact_v2).hexdigest())
    store = ReleaseStore(output.parent / "release-state.json")
    for model in (model_v1, model_v2):
        if model.version not in store.state()["stages"]:
            store.register(model, "ci")

    metrics = Evaluation(0.94, 0.91, 0.99, 220, 0.0)

    if store.state()["stages"]["1"]["stage"] == "candidate":
        store.promote("1", metrics, "ci", "canary")
    if store.state()["stages"]["1"]["stage"] == "canary" and store.state()["active"] != "1":
        store.promote("1", metrics, "approver", "production")

    if store.state()["stages"]["2"]["stage"] == "candidate":
        store.promote("2", metrics, "ci", "canary")
    if store.state()["stages"]["2"]["stage"] == "canary":
        store.promote("2", metrics, "approver", "production")

    if store.state()["active"] == "2" and store.state()["previous"] == "1":
        store.rollback("oncall", "quality regression")

    model = model_v2
    observations = [Observation(180 + i, True, 0.94, 0.08, 40, 0.001) for i in range(20)]
    telemetry = summarize(observations)

    offline_eval = evaluation_from_case(
        "When does customer 101 subscription expire?",
        "Customer 101 subscription expires 2026-12-31.",
        "Customer 101 has an active subscription expiring on 2026-12-31.",
    )
    deepeval_plan = maybe_run_deepeval(build_deepeval_plan())
    promptfoo = build_promptfoo_plan()

    bad_canary_path = output.parent / "bad-canary-state.json"
    if bad_canary_path.exists():
        bad_canary_path.unlink()
    bad_canary_store = ReleaseStore(bad_canary_path)
    bad_canary = run_bad_canary_scenario(bad_canary_store, mode="quality_regression")

    report = {
        "environment": {
            "python": platform.python_version(),
            "execution": "local deterministic control-plane simulation",
        },
        "release": store.state(),
        "evaluation": metrics.__dict__,
        "offline_edd": offline_eval.__dict__,
        "telemetry": telemetry,
        "alerts": alerts(telemetry),
        "bad_canary": {
            "mode": bad_canary["mode"],
            "promotion_blocked": bad_canary["promotion_blocked"],
            "canary_stage": bad_canary["canary_stage"],
            "active_kept": bad_canary["active"],
            "gates_passed": bad_canary["gates_passed"],
            "entrypoint": "python -m app.canary_lab --mode quality_regression",
            "claims": bad_canary["claims"],
        },
        "provider_plans": [
            deployment_plan("azure-ai-foundry", model.artifact_uri, "staging"),
            deployment_plan("databricks", model.artifact_uri, "staging"),
            deployment_plan("huggingface", model.artifact_uri, "staging"),
            deployment_plan("render", model.artifact_uri, "staging"),
        ],
        "optional_eval_track": {
            "deepeval": {
                "executed": deepeval_plan["claims"]["deepeval_executed"],
                "entrypoint": "python -m app.deepeval_optional",
                "env": ["ACADEMY_EVAL=1", "XAI_API_KEY|OPENAI_API_KEY"],
            },
            "promptfoo": {
                "executed": promptfoo["claims"]["promptfoo_executed"],
                "entrypoint": "scripts/run_promptfoo_optional.sh",
                "env": ["ACADEMY_PROMPTFOO=1"],
                "plan_tests": len(promptfoo["tests"]),
            },
        },
        "optional_deploy_track": {
            "huggingface_plan": build_deploy_plan("huggingface", model.artifact_uri, "staging"),
            "render_plan": build_deploy_plan("render", model.artifact_uri, "staging"),
            "env": ["ACADEMY_DEPLOY=1", "HF_TOKEN", "RENDER_API_KEY"],
            "note": "Azure/Databricks remain plan-only in this lab; HF/Render may go live when gated",
        },
        "claims": {
            "azure_deployed": False,
            "databricks_deployed": False,
            "huggingface_deployed": False,
            "render_deployed": False,
            "deepeval_executed": bool(deepeval_plan["claims"]["deepeval_executed"]),
            "promptfoo_executed": False,
            "credentials_required": False,
            "cloud_canary": False,
            "production_promoted_bad_canary": False,
            "canary_rejected": bool(bad_canary["claims"]["canary_rejected"]),
        },
    }
    canonical = json.dumps(report, sort_keys=True).encode()
    report["sha256"] = hashlib.sha256(canonical).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/evidence.json"))
    args = parser.parse_args()
    generated = generate(args.output)
    print(json.dumps({"output": str(args.output), "sha256": generated["sha256"]}))

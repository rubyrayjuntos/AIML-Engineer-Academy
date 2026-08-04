from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

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
    report = {
        "environment": {"python": platform.python_version(), "execution": "local deterministic control-plane simulation"},
        "release": store.state(),
        "evaluation": metrics.__dict__,
        "telemetry": telemetry,
        "alerts": alerts(telemetry),
        "provider_plans": [deployment_plan("azure-ai-foundry", model.artifact_uri, "staging"), deployment_plan("databricks", model.artifact_uri, "staging")],
        "claims": {"azure_deployed": False, "databricks_deployed": False, "credentials_required": False},
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

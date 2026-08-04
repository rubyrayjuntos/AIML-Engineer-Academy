import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.providers import deployment_plan
from app.release import Evaluation, ModelVersion, ReleaseStore, evaluate_gates, validate_digest
from app.telemetry import Observation, alerts, summarize


GOOD = Evaluation(0.94, 0.91, 0.99, 200, 0.0)


def model(version="1"):
    artifact = f"model-{version}".encode()
    return ModelVersion("risk", version, f"models:/risk/{version}", hashlib.sha256(artifact).hexdigest()), artifact


def test_artifact_digest_passes_and_tampering_fails():
    item, artifact = model()
    validate_digest(item, artifact)
    with pytest.raises(ValueError):
        validate_digest(item, b"tampered")


@pytest.mark.parametrize("field", ["faithfulness", "relevancy", "safety", "latency", "reliability"])
def test_each_release_gate_can_block(field):
    bad = Evaluation(0.1, 0.1, 0.1, 9999, 0.5)
    assert evaluate_gates(bad)[field] is False


def test_model_versions_are_immutable(tmp_path):
    store = ReleaseStore(tmp_path / "state.json")
    item, _ = model()
    store.register(item, "tester")
    with pytest.raises(ValueError):
        store.register(item, "tester")


def test_failed_gates_are_audited_and_block_promotion(tmp_path):
    store = ReleaseStore(tmp_path / "state.json")
    item, _ = model()
    store.register(item, "tester")
    with pytest.raises(ValueError):
        store.promote("1", Evaluation(0.2, 0.9, 0.99, 200, 0), "tester", "canary")
    assert store.state()["events"][-1]["action"] == "promotion_blocked"


def test_production_requires_canary(tmp_path):
    store = ReleaseStore(tmp_path / "state.json")
    item, _ = model()
    store.register(item, "tester")
    with pytest.raises(ValueError):
        store.promote("1", GOOD, "tester", "production")


def test_canary_then_production_promotion(tmp_path):
    store = ReleaseStore(tmp_path / "state.json")
    item, _ = model()
    store.register(item, "tester")
    store.promote("1", GOOD, "tester", "canary")
    store.promote("1", GOOD, "approver", "production")
    assert store.state()["active"] == "1"


def test_rollback_restores_previous_version_and_audits_reason(tmp_path):
    store = ReleaseStore(tmp_path / "state.json")
    for version in ("1", "2"):
        item, _ = model(version)
        store.register(item, "tester")
        store.promote(version, GOOD, "tester", "canary")
        store.promote(version, GOOD, "approver", "production")
    assert store.rollback("oncall", "quality regression") == "1"
    state = store.state()
    assert state["active"] == "1" and state["stages"]["2"]["stage"] == "retired"
    assert state["events"][-1]["detail"]["reason"] == "quality regression"


def test_rollback_requires_previous_release_and_reason(tmp_path):
    store = ReleaseStore(tmp_path / "state.json")
    with pytest.raises(ValueError):
        store.rollback("oncall", "")


def test_telemetry_summary_and_alerts():
    observations = [Observation(100, True, 0.95, 0.05, 10, 0.01), Observation(900, False, 0.7, 0.4, 20, 0.02)]
    summary = summarize(observations)
    assert summary["tokens"] == 30 and summary["cost_usd"] == 0.03
    assert set(alerts(summary)) == {"error_budget_burn", "quality_regression", "input_drift", "latency_slo"}


def test_empty_telemetry_is_rejected():
    with pytest.raises(ValueError):
        summarize([])


@pytest.mark.parametrize("provider,resource", [("azure-ai-foundry", "managed-online-endpoint"), ("databricks", "model-serving-endpoint")])
def test_provider_plans_use_workload_identity(provider, resource):
    plan = deployment_plan(provider, "models:/risk/1", "staging")
    assert plan["resource"] == resource and plan["identity"] in {"managed-identity", "service-principal"}


def test_provider_plan_rejects_unknown_targets():
    with pytest.raises(ValueError):
        deployment_plan("unknown", "models:/risk/1", "staging")

"""Bad-canary lab: block production promotion and reject degraded canaries."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.canary_lab import (
    aggregate_canary_window,
    canary_regression_gates,
    cases_for_mode,
    evaluation_from_canary_case,
    run_bad_canary_scenario,
    run_good_canary_control,
)
from app.release import Evaluation, ModelVersion, ReleaseStore


def test_canary_regression_gates_detect_delta():
    baseline = Evaluation(0.95, 0.92, 0.99, 220, 0.0)
    bad = Evaluation(0.40, 0.30, 0.99, 220, 0.0)
    gates = canary_regression_gates(baseline, bad)
    assert gates["faithfulness"] is False
    assert gates["faithfulness_delta"] is False
    assert gates["relevancy_delta"] is False


def test_mild_quality_regression_blocks_via_delta_not_absolute(tmp_path):
    store = ReleaseStore(tmp_path / "release.json")
    result = run_bad_canary_scenario(store, mode="mild_quality_regression")
    assert result["promotion_blocked"] is True
    assert result["gates"]["faithfulness"] is True
    assert result["gates"]["faithfulness_delta"] is False
    assert result["active"] == "bc-1"
    assert result["canary_stage"] == "retired"


def test_quality_bad_canary_blocks_production_and_rejects(tmp_path):
    store = ReleaseStore(tmp_path / "release.json")
    result = run_bad_canary_scenario(store, mode="quality_regression")
    assert result["promotion_blocked"] is True
    assert result["canary_stage"] == "retired"
    assert result["active"] == "bc-1"
    assert "promotion_blocked" in result["events"]
    assert "canary_rejected" in result["events"]
    assert result["claims"]["production_promoted_bad_canary"] is False
    assert result["claims"]["cloud_canary"] is False


def test_latency_bad_canary_blocks_production(tmp_path):
    store = ReleaseStore(tmp_path / "release.json")
    result = run_bad_canary_scenario(store, mode="latency_regression")
    assert result["promotion_blocked"] is True
    assert result["gates"]["latency"] is False
    assert result["canary_stage"] == "retired"
    assert "latency_slo" in result["alerts"] or result["canary_window"]["p95_ms"] > 750


def test_safety_bad_canary_blocks_production(tmp_path):
    store = ReleaseStore(tmp_path / "release.json")
    result = run_bad_canary_scenario(store, mode="safety_regression")
    assert result["promotion_blocked"] is True
    assert result["gates"]["safety"] is False
    assert result["canary_stage"] == "retired"


def test_good_canary_window_still_promotes(tmp_path):
    store = ReleaseStore(tmp_path / "release.json")
    result = run_good_canary_control(store)
    assert result["active"] == "gc-1"
    assert result["stage"] == "production"
    assert all(result["gates"].values())


def test_reject_canary_requires_canary_stage(tmp_path):
    store = ReleaseStore(tmp_path / "release.json")
    artifact = b"x"
    model = ModelVersion("m", "1", "u", hashlib.sha256(artifact).hexdigest())
    store.register(model, "tester")
    with pytest.raises(ValueError, match="canary stage"):
        store.reject_canary("1", "tester", "too early")


def test_aggregate_canary_window_and_fixtures():
    cases = cases_for_mode("quality_regression")
    assert cases
    evals = [evaluation_from_canary_case(c) for c in cases]
    agg = aggregate_canary_window(evals)
    assert agg.faithfulness < 0.9
    assert agg.relevancy < 0.85

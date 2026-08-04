import time

import pytest
from pydantic import ValidationError

from app.agent import CustomerSuccessAgent, ToolFailure, execute_with_policy
from app.models import Recommendation
from app.store import Store


@pytest.fixture()
def store(tmp_path):
    value = Store(tmp_path / "test.db")
    value.initialize()
    value.seed()
    return value


def test_seeded_customer_is_readable(store):
    assert store.customer("ACME-001")["health_score"] == 31


def test_unknown_customer_is_none(store):
    assert store.customer("NOPE") is None


def test_search_is_account_scoped(store):
    rows = store.search("ACME-001", "renewal risk")
    assert rows and all(row["interaction_id"] in {1, 2, 3} for row in rows)


def test_search_returns_citable_fields(store):
    assert {"interaction_id", "content", "score"} <= store.search("ACME-001", "outage")[0].keys()


def test_search_limit_is_validated(store):
    with pytest.raises(ValueError):
        store.search("ACME-001", "risk", 11)


def test_agent_proposes_high_risk_governed_action(store):
    result = CustomerSuccessAgent(store).assess("ACME-001", "run-1")
    assert result.status.value == "awaiting_approval"
    assert result.recommendation.risk.value == "high"
    assert result.recommendation.requires_human_approval is True


def test_recommendation_has_grounded_citations(store):
    result = CustomerSuccessAgent(store).assess("ACME-001", "run-2")
    assert len(result.recommendation.citations) >= 1
    assert all(c.interaction_id in {1, 2, 3} for c in result.recommendation.citations)


def test_structured_output_rejects_no_approval():
    with pytest.raises(ValidationError):
        Recommendation.model_validate({
            "account_id": "A", "risk": "high", "rationale": "x" * 25,
            "proposed_action": "review account", "citations": [{"interaction_id": 1, "excerpt": "e", "score": 1}],
            "confidence": .8, "requires_human_approval": False,
        })


def test_state_persists_across_agent_instances(store):
    first = CustomerSuccessAgent(store).assess("ACME-001", "persisted")
    second = CustomerSuccessAgent(store).decide(first.run_id, True)
    assert second.status.value == "approved"
    assert store.load_run("persisted")["status"] == "approved"


def test_rejection_is_recorded(store):
    result = CustomerSuccessAgent(store).assess("ACME-001", "rejected")
    assert CustomerSuccessAgent(store).decide(result.run_id, False).status.value == "rejected"


def test_decision_requires_pending_run(store):
    with pytest.raises(ValueError):
        CustomerSuccessAgent(store).decide("missing", True)


def test_unknown_account_becomes_controlled_failure(store):
    result = CustomerSuccessAgent(store).assess("NOPE", "failed")
    assert result.status.value == "failed" and "unknown account" in result.error


def test_tool_policy_retries_then_succeeds():
    calls = {"count": 0}
    def flaky():
        calls["count"] += 1
        if calls["count"] < 2:
            raise RuntimeError("temporary")
        return "ok"
    assert execute_with_policy(flaky, retries=2) == "ok"
    assert calls["count"] == 2


def test_tool_policy_times_out():
    def slow():
        time.sleep(.05)
    with pytest.raises(ToolFailure):
        execute_with_policy(slow, retries=0, timeout_seconds=.001)

"""Optional live structured-output track tests (default CI stays offline)."""
from __future__ import annotations

import os

import pytest

from app.live_gate import api_key_present, live_llm_requested, track_status
from app.pydantic_ai_optional import (
    build_live_structured_plan,
    maybe_run_live_sql,
    propose_sql_with_optional_live,
)
from app.sql_agent import SQLQueryResult, SqlAgent
from app.sql_store import AnalyticsStore


@pytest.fixture()
def analytics(tmp_path):
    store = AnalyticsStore(tmp_path / "analytics.db")
    store.initialize()
    store.seed()
    return store


def test_live_plan_defaults_unexecuted(monkeypatch):
    monkeypatch.delenv("ACADEMY_LIVE_LLM", raising=False)
    plan = build_live_structured_plan()
    assert plan["claims"]["pydantic_ai_executed"] is False
    assert plan["claims"]["sql_structured_live"] is False
    assert plan["gate"]["mode"] == "plan_only"


def test_live_skips_without_gate(monkeypatch):
    monkeypatch.delenv("ACADEMY_LIVE_LLM", raising=False)
    monkeypatch.setenv("XAI_API_KEY", "test-key-should-not-trigger")
    result = maybe_run_live_sql(build_live_structured_plan())
    assert result["execution"]["status"] == "skipped"
    assert result["execution"]["reason"] == "ACADEMY_LIVE_LLM!=1"
    assert result["claims"]["pydantic_ai_executed"] is False


def test_live_skips_without_key(monkeypatch):
    monkeypatch.setenv("ACADEMY_LIVE_LLM", "1")
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = maybe_run_live_sql(build_live_structured_plan())
    assert result["execution"]["status"] == "skipped"
    assert "missing" in result["execution"]["reason"]
    assert result["claims"]["pydantic_ai_executed"] is False


def test_live_skips_when_deps_missing(monkeypatch):
    monkeypatch.setenv("ACADEMY_LIVE_LLM", "1")
    monkeypatch.setenv("XAI_API_KEY", "fake-key")
    # Force import failure path without requiring network.
    import app.pydantic_ai_optional as mod

    def boom(*_a, **_k):
        raise ImportError("pydantic-ai not installed — pip install -r requirements-live.txt")

    monkeypatch.setattr(mod, "propose_sql_live", boom)
    result = maybe_run_live_sql(build_live_structured_plan())
    assert result["execution"]["status"] == "skipped"
    assert result["claims"]["pydantic_ai_executed"] is False
    assert "hint" in result["execution"]


def test_propose_still_deterministic_offline(analytics, monkeypatch):
    monkeypatch.delenv("ACADEMY_LIVE_LLM", raising=False)
    agent = SqlAgent(analytics)
    draft = agent.propose("What is total order revenue?")
    assert draft.sql_query.lower().startswith("select")
    assert "orders" in draft.sql_query.lower()
    assert agent.last_propose_meta()["path"] == "deterministic"
    assert agent.last_propose_meta()["live_attempted"] is False


def test_optional_live_uses_fallback_when_live_errors(monkeypatch):
    monkeypatch.setenv("ACADEMY_LIVE_LLM", "1")
    monkeypatch.setenv("XAI_API_KEY", "fake-key")

    def boom(*_a, **_k):
        raise RuntimeError("network down")

    import app.pydantic_ai_optional as mod

    monkeypatch.setattr(mod, "propose_sql_live", boom)

    def fallback():
        return SQLQueryResult(
            query_explanation="Deterministic revenue sum for orders.",
            sql_query="SELECT SUM(amount) AS total_revenue FROM orders",
            confidence_score=0.9,
        )

    draft, meta = propose_sql_with_optional_live(
        "What is total order revenue?",
        deterministic_fallback=fallback,
    )
    assert meta["live_attempted"] is True
    assert meta["path"] == "deterministic_fallback"
    assert "total_revenue" in draft.sql_query


def test_track_status_reflects_env(monkeypatch):
    monkeypatch.delenv("ACADEMY_LIVE_LLM", raising=False)
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert live_llm_requested() is False
    assert api_key_present() is False
    status = track_status()
    assert status["mode"] == "plan_only"


@pytest.mark.live_llm
def test_live_sql_propose_network():
    """Only runs when operator enables ACADEMY_LIVE_LLM=1 with a real key + deps."""
    if not live_llm_requested() or not api_key_present():
        pytest.skip("ACADEMY_LIVE_LLM=1 and API key required")
    try:
        from app.pydantic_ai_optional import propose_sql_live
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"live deps unavailable: {exc}")
    draft = propose_sql_live("What is total order revenue?")
    assert isinstance(draft, SQLQueryResult)
    assert draft.sql_query.strip().upper().startswith("SELECT")

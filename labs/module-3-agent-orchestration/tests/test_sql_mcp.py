"""SQL/MCP + DSPy teaching-lane tests (alongside Customer Success suite)."""
import pytest
from pydantic import ValidationError

from app.dspy_compile import Example, bootstrap_fewshot, metric_exact_select
from app.sql_agent import SQLQueryResult, SqlAgent
from app.sql_guard import is_read_only_sql, reject_dangerous_sql
from app.sql_store import AnalyticsStore


@pytest.fixture()
def analytics(tmp_path):
    store = AnalyticsStore(tmp_path / "analytics.db")
    store.initialize()
    store.seed()
    return store


def test_sql_query_result_bounds():
    row = SQLQueryResult(
        query_explanation="Count users in the table.",
        sql_query="SELECT COUNT(*) FROM users",
        confidence_score=0.5,
    )
    assert 0 <= row.confidence_score <= 1
    with pytest.raises(ValidationError):
        SQLQueryResult(
            query_explanation="too short",
            sql_query="SELECT 1",
            confidence_score=1.5,
        )


def test_reject_drop_and_stacking():
    with pytest.raises(ValueError):
        reject_dangerous_sql("SELECT 1; DROP TABLE users")
    with pytest.raises(ValueError):
        reject_dangerous_sql("DELETE FROM users")
    assert is_read_only_sql("SELECT COUNT(*) FROM users") is True


def test_allow_simple_select(analytics):
    rows = analytics.execute_readonly("SELECT COUNT(*) AS user_count FROM users")
    assert rows[0]["user_count"] == 3


def test_schema_tool_known_table(analytics):
    ddl = analytics.schema_for("orders")
    assert "amount" in ddl.lower()
    with pytest.raises(ValueError):
        analytics.schema_for("secrets")


def test_repair_loop_on_bad_sql(analytics):
    agent = SqlAgent(analytics)
    # Fallback proposer emits unknown_table; run() should repair.
    result = agent.run("something vague about metrics")
    assert result["status"] == "ok"
    assert result["repairs"] >= 1
    assert "users" in result["result"]["sql_query"]


def test_sql_agent_revenue_path(analytics):
    agent = SqlAgent(analytics)
    result = agent.run("What is total order revenue?")
    assert result["status"] == "ok"
    assert result["repairs"] == 0
    assert result["rows"][0]["total_revenue"] == pytest.approx(460.5)


def test_dspy_metric_and_bootstrap_picks_demos():
    trainset = [
        Example("count users", "SELECT COUNT(*) FROM users"),
        Example("sum revenue", "SELECT SUM(amount) FROM orders"),
        Example("bad", "DELETE FROM users"),
        Example("join names", "SELECT u.name FROM users u"),
    ]
    assert metric_exact_select("select count(*) from users", "SELECT COUNT(*) FROM users") == 1.0
    assert metric_exact_select("SELECT 1", "SELECT 2") == 0.0
    compiled = bootstrap_fewshot(
        trainset,
        seed_instruction="Emit one read-only SELECT for the analytics schema.",
        k=2,
    )
    assert len(compiled.demos) == 2
    assert all(d.gold_sql.upper().startswith("SELECT") for d in compiled.demos)
    assert "Demonstrations:" in compiled.render()


def test_mcp_sql_tools_are_registered(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYTICS_DB", str(tmp_path / "analytics.db"))
    from importlib import reload
    import app.mcp_server as mcp_server

    reload(mcp_server)
    tools = mcp_server.mcp._tool_manager.list_tools()  # noqa: SLF001
    names = sorted(getattr(t, "name", str(t)) for t in tools)
    assert "get_table_schema" in names
    assert "execute_readonly_sql" in names
    assert "get_customer" in names
    ddl = mcp_server.get_table_schema("users")
    assert "CREATE TABLE users" in ddl
    blocked = mcp_server.execute_readonly_sql("DELETE FROM users")
    assert "error" in blocked

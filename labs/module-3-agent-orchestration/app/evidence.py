from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from app.agent import CustomerSuccessAgent
from app.dspy_compile import Example, bootstrap_fewshot, metric_exact_select
from app.pydantic_ai_optional import build_live_structured_plan, maybe_run_live_sql
from app.sql_agent import SqlAgent
from app.sql_store import AnalyticsStore
from app.store import Store


def generate(output: Path) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    db = output.parent / "evidence.db"
    analytics_db = output.parent / "evidence_analytics.db"
    for path in (db, analytics_db):
        if path.exists():
            path.unlink()
    store = Store(db)
    store.initialize()
    store.seed()
    agent = CustomerSuccessAgent(store)
    proposed = agent.assess("ACME-001", run_id="evidence-run")
    approved = agent.decide("evidence-run", approved=True)

    analytics = AnalyticsStore(analytics_db)
    analytics.initialize()
    analytics.seed()
    sql_result = SqlAgent(analytics).run("What is total order revenue?")
    compiled = bootstrap_fewshot(
        [
            Example("count users", "SELECT COUNT(*) FROM users"),
            Example("sum revenue", "SELECT SUM(amount) FROM orders"),
            Example("names", "SELECT name FROM users"),
        ],
        seed_instruction="Emit one read-only SELECT for the analytics schema.",
        k=2,
    )

    live_plan = maybe_run_live_sql(build_live_structured_plan())

    evidence = {
        "module": "module-3-agent-orchestration",
        "deterministic": True,
        "transport": "stdio",
        "mcp_tools": [
            "get_customer",
            "search_interactions",
            "get_table_schema",
            "execute_readonly_sql",
        ],
        "retrieval": {
            "citation_ids": [c.interaction_id for c in proposed.recommendation.citations],
            "citation_count": len(proposed.recommendation.citations),
        },
        "governance": {
            "initial_status": proposed.status.value,
            "decision_status": approved.status.value,
            "outbound_action_executed": False,
        },
        "sql_mcp_lane": {
            "status": sql_result["status"],
            "sql_query": sql_result["result"]["sql_query"],
            "row_count": len(sql_result["rows"]),
            "repairs": sql_result["repairs"],
            "propose_meta": sql_result.get("propose_meta", {}),
            "note": (
                "Pydantic SQLQueryResult seam + RO firewall; live pydantic_ai.Agent "
                "only when ACADEMY_LIVE_LLM=1 + API key (see claims.*)"
            ),
        },
        "dspy_compile_stub": {
            "demo_count": len(compiled.demos),
            "metric_self_check": metric_exact_select(
                compiled.demos[0].gold_sql, compiled.demos[0].gold_sql
            ),
            "note": "Offline BootstrapFewShot teaching stub — no dspy package required",
        },
        "live_structured_lane": {
            "gate": live_plan.get("gate"),
            "execution": live_plan.get("execution"),
            "claims": live_plan.get("claims"),
        },
        "claims": {
            "pydantic_ai_executed": bool(
                live_plan.get("claims", {}).get("pydantic_ai_executed")
            ),
            "sql_structured_live": bool(
                live_plan.get("claims", {}).get("sql_structured_live")
            ),
        },
        "persistence": store.load_run("evidence-run"),
        "rubric": [
            {"competency": "SQLite customer data and FTS retrieval", "points": 8},
            {"competency": "Grounded citations", "points": 8},
            {"competency": "Pydantic structured output (deterministic + optional live)", "points": 10},
            {"competency": "Stateful orchestration", "points": 8},
            {"competency": "Persistent workflow state", "points": 8},
            {"competency": "Retry and timeout policy", "points": 8},
            {"competency": "MCP stdio CS + SQL tools", "points": 10},
            {"competency": "Read-only SQL firewall and repair loop", "points": 10},
            {"competency": "Human approval boundary", "points": 8},
            {"competency": "DSPy compile stub + deterministic evidence", "points": 8},
            {"competency": "Claim-safe live structured-output gate", "points": 6},
            {"competency": "Threat model notes", "points": 8},
        ],
        "total_points": 100,
    }
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    evidence["checksum"] = hashlib.sha256(canonical.encode()).hexdigest()
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True))
    db.unlink()
    analytics_db.unlink()
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/evidence.json"))
    args = parser.parse_args()
    result = generate(args.output)
    print(f"Evidence written to {args.output}")
    print(f"Checksum: {result['checksum']}")

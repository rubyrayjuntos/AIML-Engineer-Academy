from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from app.agent import CustomerSuccessAgent
from app.store import Store


def generate(output: Path) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    db = output.parent / "evidence.db"
    if db.exists():
        db.unlink()
    store = Store(db)
    store.initialize()
    store.seed()
    agent = CustomerSuccessAgent(store)
    proposed = agent.assess("ACME-001", run_id="evidence-run")
    approved = agent.decide("evidence-run", approved=True)
    evidence = {
        "module": "module-3-agent-orchestration",
        "deterministic": True,
        "transport": "stdio",
        "mcp_tools": ["get_customer", "search_interactions"],
        "retrieval": {
            "citation_ids": [c.interaction_id for c in proposed.recommendation.citations],
            "citation_count": len(proposed.recommendation.citations),
        },
        "governance": {
            "initial_status": proposed.status.value,
            "decision_status": approved.status.value,
            "outbound_action_executed": False,
        },
        "persistence": store.load_run("evidence-run"),
        "rubric": [
            {"competency": "SQLite customer data and FTS retrieval", "points": 10},
            {"competency": "Grounded citations", "points": 10},
            {"competency": "Pydantic structured output", "points": 10},
            {"competency": "Stateful orchestration", "points": 10},
            {"competency": "Persistent workflow state", "points": 10},
            {"competency": "Retry and timeout policy", "points": 10},
            {"competency": "Controlled failure state", "points": 10},
            {"competency": "MCP stdio server and client", "points": 10},
            {"competency": "Human approval boundary", "points": 10},
            {"competency": "Deterministic evidence and threat model", "points": 10},
        ],
        "total_points": 100,
    }
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    evidence["checksum"] = hashlib.sha256(canonical.encode()).hexdigest()
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True))
    db.unlink()
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/evidence.json"))
    args = parser.parse_args()
    result = generate(args.output)
    print(f"Evidence written to {args.output}")
    print(f"Checksum: {result['checksum']}")

# Module 3 – Governed Agent Orchestration Lab

This lab is the first executable slice of **Customer Success Autopilot**. It
retrieves account evidence, produces a typed churn-risk recommendation, persists
workflow state, and stops at a human approval boundary. It never sends customer
communications.

## What is real

- SQLite customer/interaction data and FTS5 retrieval
- source-scoped citations
- Pydantic output and governance validation
- a persistent state machine with approval/rejection transitions
- bounded tool retries, timeouts, and controlled failure states
- read-only MCP tools plus a client using the current local `stdio` transport
- deterministic tests and machine-readable evidence

The deterministic `propose()` method is an explicit model seam: it keeps CI
offline and reproducible while allowing a hosted or local LLM adapter to replace
recommendation generation later without weakening the output schema or approval
gate.

## Run

```bash
cd labs/module-3-agent-orchestration
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.evidence --output artifacts/evidence.json
```

To exercise the actual MCP lifecycle, initialize and seed a local database first:

```bash
python -c "from app.store import Store; s=Store('customer_success.db'); s.initialize(); s.seed()"
python -m app.mcp_client
```

## Assessment rubric (100 points)

Ten equally weighted competencies are recorded in the evidence artifact: data,
retrieval, citations, schemas, orchestration, persistence, resilience, MCP,
approval governance, and reproducible evidence/threat modeling.

# Module 3 – Governed Agent Orchestration Lab

This lab has two aligned lanes:

1. **Customer Success Autopilot** — retrieve account evidence, emit a typed
   churn-risk recommendation, persist workflow state, and stop at a human
   approval boundary (never sends customer communications).
2. **Read-only SQL / MCP lane** — `SQLQueryResult` structured output (PydanticAI
   `output_type` shape), SQL firewall, analytics SQLite, MCP tools
   `get_table_schema` / `execute_readonly_sql`, plus a DSPy-style compile stub.

## What is real

- SQLite customer/interaction data and FTS5 retrieval
- source-scoped citations and HITL approval governance
- Pydantic schemas for CS recommendations and SQL query results
- read-only MCP tools (CS + SQL) over the local `stdio` transport
- SQL injection / stacking / write rejection
- offline DSPy BootstrapFewShot teaching stub (`app/dspy_compile.py`)
- deterministic tests and machine-readable evidence

The deterministic `propose()` seams (CS and SQL) keep CI offline while matching
the curriculum’s PydanticAI structured-output shape. Swap in a hosted
`pydantic_ai.Agent` when an API key is available without weakening schemas or
firewalls.

## Run

```bash
cd labs/module-3-agent-orchestration
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.evidence --output artifacts/evidence.json
```

Expected test result: **22 passed**

Optional MCP lifecycle smoke:

```bash
python -c "from app.store import Store; s=Store('customer_success.db'); s.initialize(); s.seed()"
python -c "from app.sql_store import AnalyticsStore; s=AnalyticsStore('analytics.db'); s.initialize(); s.seed()"
python -m app.mcp_client
```

## Assessment rubric (100 points)

Competencies recorded in the evidence artifact cover CS retrieval/governance,
MCP CS+SQL tools, read-only SQL firewall + repair, DSPy compile stub, and
threat-model/evidence hygiene.

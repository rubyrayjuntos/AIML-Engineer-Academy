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
- **optional** live `pydantic_ai.Agent(output_type=SQLQueryResult)` behind
  `ACADEMY_LIVE_LLM=1` (never in default CI)

The deterministic `propose()` seams (CS and SQL) keep CI offline while matching
the curriculum’s PydanticAI structured-output shape. The optional live track
swaps the SQL propose seam for a hosted Agent when gated — schemas, firewall,
and MCP boundaries stay unchanged. Evidence `claims.pydantic_ai_executed` /
`claims.sql_structured_live` stay **false** unless a live run succeeded.

## Run (required offline path)

```bash
cd labs/module-3-agent-orchestration
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.evidence --output artifacts/evidence.json
python -m app.pydantic_ai_optional --output artifacts/live_structured_plan.json
```

Expected test result: **29 passed, 1 skipped** (`live_llm` network test).

Evidence `claims.*` stay false on this path.

## Optional live structured-output track

Only on a machine you control with a paid API key — **not** Cloud Agent / CI:

```bash
pip install -r requirements-live.txt
export ACADEMY_LIVE_LLM=1
export XAI_API_KEY=...          # or OPENAI_API_KEY
# optional: export ACADEMY_LIVE_MODEL=grok-4.6
python -m app.pydantic_ai_optional --question "What is total order revenue?"
pytest -q -m live_llm           # runs the network-marked case
```

Keys alone never trigger live calls — `ACADEMY_LIVE_LLM=1` is required.

## Optional MCP lifecycle smoke

```bash
python -c "from app.store import Store; s=Store('customer_success.db'); s.initialize(); s.seed()"
python -c "from app.sql_store import AnalyticsStore; s=AnalyticsStore('analytics.db'); s.initialize(); s.seed()"
python -m app.mcp_client
```

## Assessment rubric (100 points)

Competencies recorded in the evidence artifact cover CS retrieval/governance,
MCP CS+SQL tools, read-only SQL firewall + repair, DSPy compile stub,
claim-safe live structured-output gating, and threat-model/evidence hygiene.

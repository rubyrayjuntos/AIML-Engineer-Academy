# Module 3 – Governed Agent Orchestration Lab

This lab has three aligned lanes:

1. **Customer Success Autopilot** — retrieve account evidence, emit a typed
   churn-risk recommendation, persist workflow state, and stop at a human
   approval boundary (never sends customer communications).
2. **Read-only SQL / MCP lane** — `SQLQueryResult` structured output (PydanticAI
   `output_type` shape), SQL firewall, analytics SQLite, MCP tools
   `get_table_schema` / `execute_readonly_sql`, plus a DSPy-style compile stub.
3. **Browser micro-lab (stub DOM)** — least-privilege tools (`navigate` / `click` /
   `type` / `scroll` / `extract_a11y`), origin allowlist, a11y observations,
   **Dual-LLM IPI quarantine** (Minimizer + quarantined Sanitizer → privileged
   planner), and HITL before consequential clicks. Optional Playwright behind
   `ACADEMY_BROWSER=1`. Optional live sanitizer LLM behind `ACADEMY_DUAL_LLM=1`.

## What is real

- SQLite customer/interaction data and FTS5 retrieval
- source-scoped citations and HITL approval governance
- Pydantic schemas for CS recommendations and SQL query results
- read-only MCP tools (CS + SQL) over the local `stdio` transport
- SQL injection / stacking / write rejection
- offline DSPy BootstrapFewShot teaching stub (`app/dspy_compile.py`)
- **browser stub runtime** over `fixtures/vendor_portal.html` (no browser binary in CI)
- **Dual-LLM topology** (`app/dual_llm.py`): tool-input Minimizer + quarantined
  Sanitizer producing `SafeObservation` for the privileged planner
- deterministic tests and machine-readable evidence
- **optional** live `pydantic_ai.Agent(output_type=SQLQueryResult)` behind
  `ACADEMY_LIVE_LLM=1` (never in default CI)
- **optional** live Dual-LLM quarantined sanitizer behind `ACADEMY_DUAL_LLM=1`

The deterministic `propose()` seams (CS and SQL) keep CI offline while matching
the curriculum’s PydanticAI structured-output shape. The optional live track
swaps the SQL propose seam for a hosted Agent when gated — schemas, firewall,
and MCP boundaries stay unchanged. Evidence `claims.pydantic_ai_executed` /
`claims.sql_structured_live` stay **false** unless a live run succeeded.
Default CI never launches Playwright. Evidence `claims.playwright_executed`
stays **false** unless `ACADEMY_BROWSER=1` succeeds. Evidence
`claims.dual_llm_live_executed` stays **false** unless `ACADEMY_DUAL_LLM=1`
succeeds; `claims.dual_llm_topology_exercised` is **true** on the CPU path.

## Run (required offline path)

```bash
cd labs/module-3-agent-orchestration
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.evidence --output artifacts/evidence.json
python -m app.pydantic_ai_optional --output artifacts/live_structured_plan.json
python -m app.browser_optional --output artifacts/browser_plan.json
python -m app.dual_llm_optional --output artifacts/dual_llm_plan.json
```

Expected test result: **49 passed, 3 skipped** (`live_llm` + `browser` + `dual_llm` markers).

Evidence `claims.*` stay false on this path for live tracks (`pydantic_ai_executed`,
`sql_structured_live`, `playwright_executed`, `dual_llm_live_executed`);
`dual_llm_topology_exercised` is true.

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

## Optional Dual-LLM live sanitizer track

Only on a machine you control with a paid API key — **not** Cloud Agent / CI:

```bash
pip install -r requirements-live.txt
export ACADEMY_DUAL_LLM=1
export XAI_API_KEY=...          # or OPENAI_API_KEY
python -m app.dual_llm_optional
pytest -q -m dual_llm
```

Keys alone never trigger live calls — `ACADEMY_DUAL_LLM=1` is required. The live
sanitizer has **no tools and no credentials**; it only returns a `SafeObservation`.

## Optional Playwright track

```bash
pip install -r requirements-browser.txt
playwright install chromium
export ACADEMY_BROWSER=1
python -m app.browser_optional --output artifacts/browser_plan.json
pytest -q -m browser
```

## Optional MCP lifecycle smoke

```bash
python -c "from app.store import Store; s=Store('customer_success.db'); s.initialize(); s.seed()"
python -c "from app.sql_store import AnalyticsStore; s=AnalyticsStore('analytics.db'); s.initialize(); s.seed()"
python -m app.mcp_client
```

## Assessment rubric (100 points)

Competencies recorded in the evidence artifact cover CS retrieval/governance,
MCP CS+SQL tools, read-only SQL firewall + repair, browser stub governance
(allowlist / a11y / Dual-LLM IPI / HITL), Dual-LLM minimizer+sanitizer topology,
DSPy compile stub, claim-safe live structured-output / Playwright / Dual-LLM
gating, and threat-model/evidence hygiene.

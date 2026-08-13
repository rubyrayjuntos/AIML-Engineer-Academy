# Threat model

| Threat | Boundary in this checkpoint | Residual risk / next control |
|---|---|---|
| Cross-account data exposure | Every retrieval tool requires and filters by `account_id` | Add authenticated tenant claims and row-level authorization |
| SQL injection | Callers cannot submit SQL; tool queries are parameterized | Fuzz query parsing and add SQLite authorizer callbacks |
| Prompt injection in support text | Retrieved text is treated as evidence, never instructions; no outbound tool exists | Add typed content quarantine in Module 4 |
| Hallucinated evidence | Recommendation requires citations whose IDs originate in retrieval | Add citation-entailment evaluation and abstention thresholds |
| Runaway tools | Per-call timeout and finite retry budget | Add process isolation, circuit breakers, and telemetry |
| Invalid model output | Pydantic validates types, bounds, and mandatory approval | Add model repair adapter with a hard retry ceiling |
| Unauthorized intervention | Workflow stops at `awaiting_approval`; approval only records a decision | Add authenticated approver identity and immutable audit log |
| MCP privilege escalation | MCP server exposes only two read-only tools over local stdio | Add capability tokens and Streamable HTTP authentication before remote use |
| Browser IPI (page-as-instruction) | Stub runtime sanitizes a11y observations; instruction banners quarantined; `evaluate_js` rejected; consequential clicks require HITL | Optional Playwright path still must keep Dual-LLM quarantine before privileged planners |
| Browser origin escape | Navigate allowlist (`vendor.example` only) | Expand allowlist via explicit config; block file:// and data: URLs in production |

This is a teaching checkpoint, not a production authorization system. It proves
the control flow and makes the remaining production controls explicit.

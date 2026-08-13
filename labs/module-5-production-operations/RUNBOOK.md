# Production Release and Rollback Runbook

## Release

1. Register an immutable artifact URI, version, and SHA-256 digest.
2. Run offline quality, safety, latency, and reliability evaluation (`app/eval_offline.py` + gates).
3. Optionally run DeepEval / Promptfoo only when `ACADEMY_EVAL` / `ACADEMY_PROMPTFOO` are set — never claim them from the offline job.
4. Block the release if any gate fails; preserve the failed gate event.
5. Emit Azure/Databricks/HF/Render plans; live HF/Render only with `ACADEMY_DEPLOY=1` + credentials.
6. Observe error rate, p95 latency, quality, drift, tokens, and cost through the canary window.
7. Require human approval before production promotion.
8. If the canary window regresses (quality / latency / safety): **block** production promotion, call `reject_canary` to retire the canary, leave `active` on the known-good production version, and keep the `canary_rejected` audit event. Do not claim a cloud canary ran.

## Rollback

Trigger rollback on error-budget burn, material quality regression, unsafe output, unresolved input drift, or latency SLO breach. Restore the previously known-good immutable version, verify health and quality probes, preserve the reason and actor in the audit log, and open an incident review. Never overwrite the failed model version or erase its evidence.

**Canary reject vs rollback:** reject retires a never-promoted canary; rollback swaps production when a bad version already became `active`.

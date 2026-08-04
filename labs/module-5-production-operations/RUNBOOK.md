# Production Release and Rollback Runbook

## Release

1. Register an immutable artifact URI, version, and SHA-256 digest.
2. Run offline quality, safety, latency, and reliability evaluation.
3. Block the release if any gate fails; preserve the failed gate event.
4. Deploy to staging/canary using workload identity and record the provider deployment ID.
5. Observe error rate, p95 latency, quality, drift, tokens, and cost through the canary window.
6. Require human approval before production promotion.

## Rollback

Trigger rollback on error-budget burn, material quality regression, unsafe output, unresolved input drift, or latency SLO breach. Restore the previously known-good immutable version, verify health and quality probes, preserve the reason and actor in the audit log, and open an incident review. Never overwrite the failed model version or erase its evidence.

# Threat model

| Threat | Boundary/control | Verification |
|---|---|---|
| Unauthorized inference | API key, constant-time comparison | Missing/wrong-key tests |
| Resource exhaustion | input/token bounds, rate limit, semaphore, timeout | 422/429/504 tests |
| Data leakage through caches/logs | `no-store`; prompts excluded from evidence | header and artifact review |
| Client/server correlation loss | accepted/generated request ID | response contract test |
| Benchmark gaming | workload/environment/results and explicit claims | evidence schema/checksum |
| GPU capability misrepresentation | CPU/vLLM/GPU claims recorded separately | evidence claim assertions |

API keys are a teaching-sized authentication boundary, not a complete identity system. A deployment also needs secret rotation, TLS termination, tenant-scoped authorization, durable distributed rate limiting, safe telemetry, audit retention, and platform-level network controls.

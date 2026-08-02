# Module 1 — Competency Evidence Rubric

This document maps every item in the Module 1 competency contract to the
concrete artifacts that satisfy it.

---

## Competency Contract

### Explain

| Criterion | Evidence |
| :--- | :--- |
| Async I/O vs compute-bound work; REST/gRPC/SSE/WebSocket tradeoffs | `app/main.py` — `token_generator` is an async generator that yields SSE frames without blocking the event loop. |
| Data leakage, class imbalance, bias-variance, precision/recall/F1 | Covered in Module 1 curriculum sections 1.1–1.2 (see `src/data/curriculumData.ts`). |
| Sparse vs dense retrieval and reproducible containers | Dockerfile uses a pinned multi-stage build; curriculum section 1.2 addresses vectorization. |

### Build & Debug

| Criterion | Evidence |
| :--- | :--- |
| Build an async FastAPI streaming service | `app/main.py` — FastAPI app with `/health` and `/api/v1/generate/stream` endpoints. |
| Build a Pandas/scikit-learn cleaning pipeline and TF-IDF baseline | Covered in Module 1 curriculum; beyond scope of this runnable lab. |
| Test and containerize the service with a multi-stage Docker build | `Dockerfile` (multi-stage, non-root, health-checked) + `tests/` (9 pytest cases). |

### Evidence Required

| Criterion | Artifact | Status |
| :--- | :--- | :--- |
| Runnable repository and Dockerfile | `app/`, `Dockerfile`, `requirements.txt` | ✅ |
| Automated test results and evaluation report | CI uploads `test-results.xml` artifact on every run | ✅ |
| Semantic version tag | `app/main.py` — `version="1.0.0"` in `FastAPI(...)` constructor | ✅ |

---

## Dockerfile Security Hardening

| Control | Implementation |
| :--- | :--- |
| Pinned OS variant | `python:3.11-slim-bookworm` (both stages) |
| Non-root runtime user | `useradd --system appuser` + `USER appuser` |
| Minimal filesystem writes | App code owned by `appuser`; `/usr/local` populated from builder stage |
| Container health signal | `HEALTHCHECK` polls `/health` every 30 s with a 5 s timeout |
| No build tools in final image | Multi-stage build — `pip install` runs only in `builder` stage |

---

## Test Coverage Summary

| Test | What It Validates |
| :--- | :--- |
| `test_healthcheck` | `/health` returns `200 {"status":"ok"}` |
| `test_stream_generate_sends_sse_frames` | SSE content-type, `Processing`, prompt tokens, and `[DONE]` frame |
| `test_stream_generate_validates_empty_prompt` | Empty string → 422 Unprocessable Entity |
| `test_stream_generate_validates_prompt_too_long` | Prompt > 240 chars → 422 |
| `test_stream_generate_validates_temperature_above_max` | temperature > 2.0 → 422 |
| `test_stream_generate_validates_temperature_below_min` | temperature < 0.0 → 422 |
| `test_stream_generate_accepts_boundary_temperature_values` | temperature = 0.0 and 2.0 → 200 |
| `test_stream_generate_missing_prompt_field` | Missing `prompt` key → 422 |
| `test_stream_generate_done_token_is_last_frame` | `[DONE]` is the final SSE frame |

---

## CI/CD Pipeline

Workflow: `.github/workflows/module-1-foundations-lab.yml`

Steps executed on every push and pull request:

1. `npm ci` — reproducible frontend dependency install
2. `npm run lint` — TypeScript type-check (zero errors gate)
3. `npm run build` — Vite + esbuild production bundle
4. `pip install -r requirements.txt` — lab Python dependencies
5. `pytest -q --junitxml=test-results.xml` — run all 9 lab tests
6. Upload `test-results.xml` as a named artifact (available even on failure)
7. `docker build` — validates the hardened multi-stage Dockerfile builds cleanly

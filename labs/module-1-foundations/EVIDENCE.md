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
| Build a Pandas/scikit-learn cleaning pipeline and TF-IDF baseline | `app/pipeline.py` — loads `data/prompts.csv`, applies Pandas text cleaning, stratified 80/20 split, TF-IDF vectorization (500 features, unigrams + bigrams), Logistic Regression classifier, and prints a classification report with precision/recall/F1 per class. |
| Test and containerize the service with a multi-stage Docker build | `Dockerfile` (multi-stage, non-root, health-checked) + `tests/` (9 pytest cases). |

### Evidence Required

| Criterion | Artifact | Status |
| :--- | :--- | :--- |
| Runnable repository and Dockerfile | `app/`, `Dockerfile`, `requirements.txt` | ✅ |
| Automated test results and evaluation report | CI uploads `test-results.xml` artifact on every run | ✅ |
| Semantic version tag | Create a Git tag after CI passes on `main`: `git tag v1.0.0 <sha> && git push origin v1.0.0`. The tag name `v1.0.0` matches the `version` string in `app/main.py`. A plain `version=` string inside application metadata is not a release tag. | ⬜ (tag must be pushed by the author after merge) |

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

### API tests (`tests/test_main.py`)

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

### Pipeline tests (`tests/test_pipeline.py`)

| Test | What It Validates |
| :--- | :--- |
| `test_clean_text_lowercases` | `clean_text` converts to lowercase |
| `test_clean_text_removes_special_characters` | Non-alphanumeric characters are stripped |
| `test_clean_text_strips_whitespace` | Leading/trailing whitespace is removed |
| `test_load_and_clean_returns_dataframe_with_required_columns` | CSV loads with `text`, `label`, `clean_text` columns |
| `test_clean_text_column_contains_no_uppercase` | Entire `clean_text` column is lowercase |
| `test_dataset_has_expected_label_classes` | Labels are exactly `{quality, safety, performance}` |
| `test_pipeline_is_deterministic` | Same `random_state` yields identical accuracy across two runs |
| `test_pipeline_produces_non_trivial_accuracy` | Test accuracy exceeds 0.5 baseline |
| `test_pipeline_returns_report_for_all_label_classes` | Classification report contains F1 for every class |
| `test_vectorizer_vocabulary_size_respects_max_features` | `max_features` cap is honoured by the vectorizer |

---

## CI/CD Pipeline

Workflow: `.github/workflows/module-1-foundations-lab.yml`

Steps executed on every push and pull request:

1. `npm ci` — reproducible frontend dependency install
2. `npm run lint` — TypeScript type-check (zero errors gate)
3. `npm run build` — Vite + esbuild production bundle
4. `pip install -r requirements.txt` — lab Python dependencies (includes pandas, scikit-learn)
5. `pytest -q --junitxml=test-results.xml` — run all 19 lab tests (API + pipeline)
6. `python -m app.pipeline` — executes the TF-IDF pipeline end-to-end and prints the classification report
7. Upload `test-results.xml` as a named artifact (available even on failure)
8. `docker build` — validates the hardened multi-stage Dockerfile builds cleanly

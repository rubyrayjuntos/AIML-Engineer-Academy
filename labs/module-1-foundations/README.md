# Module 1 Foundations Lab

This lab turns the curriculum's Module 1 sandbox into a runnable FastAPI service
with automated tests, a TF-IDF baseline, a **leakage & metrics clinic**, and a
production-style Docker build.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 3000
```

## Validate

```bash
pytest -q
docker build -t module-1-foundations .
```

Expected: **30 passed**.

## Run the TF-IDF pipeline (honest path)

```bash
python -m app.pipeline
```

Loads `data/prompts.csv`, cleans text with Pandas, fits TF-IDF **on the train
split only**, trains Logistic Regression, prints held-out precision/recall/F1,
and writes artefacts to `pipeline_artifacts/`.

## Leakage & metrics clinic

```bash
python -m app.leakage_clinic
```

Contrasts three failure modes against the honest baseline:

| Scenario | What you should see |
|---|---|
| Train/test contamination | Train prompts injected into the test set → **inflated** accuracy |
| Target leakage | `post_outcome_code` (label encoding) → near-perfect macro-F1 until dropped |
| Preprocess leakage | TF-IDF fit on train+test → vocabulary/IDF differ from train-only fit |
| Honest held-out P/R/F1 | Per-class + macro metrics on a clean stratified split |

Detectors live in `app/leakage_clinic.py` (`detect_train_test_overlap`,
`detect_target_leakage_columns`, `held_out_prf1`). The production path remains
`app.pipeline.build_pipeline`.

## Create the v1.0.0 release tag

After CI passes on `main`, create and push the semantic version tag:

```bash
git tag v1.0.0 $(git rev-parse main)
git push origin v1.0.0
```

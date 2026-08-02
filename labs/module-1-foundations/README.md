# Module 1 Foundations Lab

This lab turns the curriculum's Module 1 sandbox into a runnable FastAPI service with automated tests and a production-style Docker build.

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

## Run the TF-IDF pipeline

```bash
python -m app.pipeline
```

This loads `data/prompts.csv`, cleans text with Pandas, fits a TF-IDF vectorizer and Logistic Regression classifier, prints the classification report, and writes fitted artefacts to `pipeline_artifacts/`.

## Create the v1.0.0 release tag

After CI passes on `main`, create and push the semantic version tag:

```bash
git tag v1.0.0 $(git rev-parse main)
git push origin v1.0.0
```


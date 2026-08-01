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

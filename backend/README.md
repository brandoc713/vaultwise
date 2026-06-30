# Backend

FastAPI backend for local-only statement ingestion, PostgreSQL-backed transaction storage, review corrections, and scikit-learn categorization.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Start PostgreSQL from the repo root:

```bash
docker compose up -d db
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

## Privacy

Real PDFs and extracted local data must live under `local_data/`, which is ignored by Git. API responses return redacted transaction descriptions.

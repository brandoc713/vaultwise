# Personal Finance Statement Intelligence Platform

A local-first personal finance MVP that turns messy statement activity into normalized transactions, review queues, category intelligence, dashboard summaries, and CSV exports.

This repository currently contains a recruiter-facing static demo built with synthetic household finance data. The UI is intentionally structured around a data service so the next phase can replace fixtures with a FastAPI backend without throwing away the product surface.

## Live Demo

GitHub Pages target:

`https://<github-username>.github.io/smart-home-finance-platform/`

After pushing to GitHub, enable Pages from GitHub Actions in the repository settings.

## Current MVP

- Polished React dashboard with spending, income, cash flow, and category charts.
- Transaction table with search, status filters, category filters, and category correction controls.
- Statement review workflow preview for PDF/CSV ingestion.
- Rules-first merchant normalization examples.
- Functional CSV export for the current browser-session transaction state.
- Synthetic data only; no personal financial data is stored in the repo.
- Local FastAPI backend foundation for private statement uploads, PostgreSQL storage, review corrections, CSV export, and scikit-learn categorization.

## Tech Stack

- React + TypeScript
- Vite
- Tailwind CSS
- Recharts
- lucide-react
- GitHub Pages workflow
- FastAPI
- PostgreSQL
- SQLAlchemy
- pdfplumber / PyMuPDF
- scikit-learn

## Local Development

Frontend fixture demo:

```bash
npm install
npm run dev
```

Build production assets:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## Backend Development

Create the backend environment:

```bash
python3.13 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -e "backend[dev]"
```

Start PostgreSQL:

```bash
docker compose up -d db
```

Run FastAPI:

```bash
backend/.venv/bin/uvicorn app.main:app --reload --app-dir backend
```

Health check:

```bash
curl http://localhost:8000/health
```

Run backend tests:

```bash
backend/.venv/bin/python -m pytest backend/app/tests -q
```

Use the frontend against the local API:

```bash
VITE_DATA_MODE=api VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Deployment

The included GitHub Actions workflow builds and deploys `dist/` to GitHub Pages on pushes to `main`.

Before publishing, update the `base` path in `vite.config.ts` if your GitHub repository name differs from `smart-home-finance-platform`.

## Architecture Notes

The MVP uses `src/services/financeData.ts` as a frontend data boundary. Today it reads fixtures from `src/data/fixtures.ts`; tomorrow it can be swapped to API calls such as:

- `GET /api/accounts`
- `GET /api/categories`
- `GET /api/transactions`
- `GET /api/statements`
- `PATCH /api/transactions/{id}`
- `GET /api/transactions/export.csv`

The backend now implements those API surfaces locally:

- `GET /health`
- `GET /api/accounts`
- `POST /api/accounts`
- `GET /api/categories`
- `GET /api/statements`
- `POST /api/statements/upload`
- `GET /api/statements/{statement_id}`
- `POST /api/statements/{statement_id}/parse`
- `GET /api/transactions`
- `PATCH /api/transactions/{transaction_id}`
- `GET /api/transactions/export.csv`
- `POST /api/ml/train`
- `POST /api/ml/predict`
- `GET /api/ml/status`

The public GitHub Pages build defaults to fixture mode. Local API mode is opt-in through `VITE_DATA_MODE=api`.

## Private PDF Workflow

Real bank statements should only be placed under ignored local folders:

```text
local_data/statements/
local_data/extracted_text/
local_data/exports/
local_data/models/
```

Upload behavior:

- Stores PDFs/CSVs under `local_data/statements/`.
- Computes a SHA-256 hash to detect duplicate uploads.
- Uses `pdfplumber` first and PyMuPDF second to detect text-based PDFs.
- Marks scanned/empty PDFs clearly; OCR is not implemented yet.
- Parses simple text/table-like transaction rows with a public generic parser.
- Supports a local private parser profile at `local_data/parser_profile.json`.

## Privacy Check

Before pushing public changes:

```bash
npm run privacy:check
```

The check fails if staged files include private local data, PDFs, `.env`, or long account-like number patterns.

## Roadmap

- FastAPI backend skeleton.
- PostgreSQL schema hardening and Alembic-managed migrations.
- CSV parser for transaction exports.
- PDF text extraction with `pdfplumber` or PyMuPDF.
- Raw file storage for traceability.
- Persistent manual corrections.
- Rules-based categorization service.
- scikit-learn classifier trained from corrected labels.
- Docker Compose for local app + database.

## Resume Bullets This Repo Supports

- Built a local-first FastAPI ingestion service for bank statement PDFs with PostgreSQL-backed normalized transaction storage.
- Designed a privacy-conscious financial data model with raw-file traceability, redacted frontend responses, and manual correction audit logs.
- Implemented a rules-first and scikit-learn categorization pipeline using corrected transactions as training data.

## Privacy

The demo data is synthetic. The long-term product direction is local-first so sensitive financial statements do not need to leave the user’s environment.

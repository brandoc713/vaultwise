# Vaultwise

Vaultwise is a local-first personal finance intelligence platform for turning bank and credit card statements into normalized transactions, review queues, spending insights, and machine-learning-assisted categorization.

The public demo uses privacy-safe fixture data generated from a local parsing workflow. No real statements, raw transaction descriptions, account numbers, local database files, or trained local models are committed to this repository.

## Live Demo

Product demo:

`https://<github-username>.github.io/vaultwise/`

Repository:

`https://github.com/<github-username>/vaultwise`

## Problem Statement

Bank and credit card statements are useful records, but they are not built for day-to-day financial understanding. They are fragmented across accounts, inconsistent across formats, difficult to search, and hard to explain to non-technical family members.

Vaultwise addresses that problem by converting statement activity into structured data that can answer practical questions:

- Where is the money going?
- Which account did a transaction come from?
- How much spending is happening on the credit card versus checking?
- Which transactions need review?
- Which merchants and categories drive monthly cash flow?
- How can corrected labels improve future categorization?

The project is designed around a privacy-conscious workflow: real financial documents can be processed locally, while the public-facing demo shows only sanitized fixture data.

## Features

- Privacy-safe public dashboard with sanitized transaction fixtures.
- Account-aware views for checking and credit card activity.
- Statement ownership workflow so each uploaded PDF/CSV belongs to the right account.
- Transaction table with search, account filters, category filters, status filters, and correction controls.
- Spending summaries by month, account, category, and transaction status.
- Statement review workflow for parsed, flagged, and low-confidence transactions.
- Rules-first merchant/category classification.
- Manual correction tracking for human-in-the-loop labeling.
- CSV export for normalized transactions.
- FastAPI backend for private local ingestion.
- PostgreSQL-backed schema for accounts, statements, transactions, corrections, and ML predictions.
- PDF text detection with `pdfplumber` and PyMuPDF fallback.
- scikit-learn classifier foundation using corrected transactions as training data.
- Sanitized fixture generator for producing public-safe demo data from local private parsing.

## Tech Stack

Frontend:

- React
- TypeScript
- Vite
- Tailwind CSS
- Recharts
- lucide-react
- GitHub Pages

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Docker Compose
- Alembic foundation

Data and ML:

- pdfplumber
- PyMuPDF
- pandas
- scikit-learn
- joblib

Testing and quality:

- pytest
- FastAPI TestClient
- TypeScript production build
- privacy check script for staged files

## Architecture

Vaultwise has two operating modes.

### Public Demo Mode

The GitHub Pages demo is a static React app. It reads from sanitized fixture data in:

```text
src/data/sanitizedFixtures.ts
```

This mode is safe to publish because the fixture data uses:

- generic account names
- generic merchant names
- shifted dates
- rounded/scaled amounts
- synthetic statement filenames
- demo account IDs
- no source lines
- no PDF content
- no account identifiers

### Private Local Mode

The local backend can process real statements without exposing them publicly.

Private files stay under ignored local paths:

```text
local_data/statements/
local_data/extracted_text/
local_data/exports/
local_data/models/
.env
```

The backend supports:

- local statement registration
- account mapping by ignored filename tokens
- PDF/CSV upload
- SHA-256 duplicate detection
- PDF text detection
- transaction parsing
- transaction normalization
- category correction logging
- scikit-learn model training

## Backend API

Implemented API surfaces include:

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

## Roadmap

- Improve parser profiles for more statement layouts.
- Add OCR support for scanned statements.
- Add recurring transaction detection.
- Expand ML evaluation and model reporting.
- Add richer account reconciliation between checking and credit card payments.
- Add Dockerized full-stack local deployment.
- Add role-based household access for self-hosted use.

## Privacy Note

This repository is designed to be public. Real statements, local extracted text, account identifiers, local database files, and trained local model artifacts are excluded from version control. The hosted demo uses sanitized fixture data only.

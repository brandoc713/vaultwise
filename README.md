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

## Tech Stack

- React + TypeScript
- Vite
- Tailwind CSS
- Recharts
- lucide-react
- GitHub Pages workflow

## Local Development

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

## Deployment

The included GitHub Actions workflow builds and deploys `dist/` to GitHub Pages on pushes to `main`.

Before publishing, update the `homepage` field in `package.json` if your GitHub username or repository name differs from the placeholder/repo default.

## Architecture Notes

The MVP uses `src/services/financeData.ts` as a frontend data boundary. Today it reads fixtures from `src/data/fixtures.ts`; tomorrow it can be swapped to API calls such as:

- `GET /api/accounts`
- `GET /api/categories`
- `GET /api/transactions`
- `GET /api/statements`
- `PATCH /api/transactions/{id}`
- `GET /api/transactions/export.csv`

## Roadmap

- FastAPI backend skeleton.
- SQLite local database with SQLModel or SQLAlchemy.
- CSV parser for transaction exports.
- PDF text extraction with `pdfplumber` or PyMuPDF.
- Raw file storage for traceability.
- Persistent manual corrections.
- Rules-based categorization service.
- scikit-learn classifier trained from corrected labels.
- Docker Compose for local app + database.

## Privacy

The demo data is synthetic. The long-term product direction is local-first so sensitive financial statements do not need to leave the user’s environment.

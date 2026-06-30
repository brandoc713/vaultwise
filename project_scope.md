# Personal Finance Statement Intelligence Platform

## Overview

This project is a local-first personal finance platform that ingests bank statement PDFs and transaction exports, extracts and normalizes transactions, categorizes spending with ML-assisted labeling, and presents financial insights for myself and my family.

The short-term goal is to build a useful, privacy-preserving local application that centralizes transactions from statements and supports better financial decision-making. The long-term goal is to evolve it into a self-hosted homelab service.

## Problem Statement

Bank statements are difficult to use directly because they are fragmented, inconsistent across institutions, and hard for non-financial users to interpret. Many people can see that money was spent, but they cannot easily answer questions like:

- Where is the money going?
- Which charges are recurring?
- How much is spent on essentials versus discretionary items?
- Which transactions are loans, transfers, or investments?
- What patterns should we pay attention to?

This project solves that by converting raw statements into structured, searchable, and understandable financial data.

## Project Goals

### Primary goals
- Ingest bank statement PDFs and CSVs locally.
- Extract transactions into a unified normalized schema.
- Categorize transactions into expenses, income, transfers, loans, and investments.
- Provide dashboards and summaries that are easy for non-technical family members to understand.
- Allow manual review and correction of extracted data.

### Secondary goals
- Build a meaningful ML workflow with human-in-the-loop feedback.
- Create a foundation for future homelab deployment.
- Practice backend development, API design, database design, and ML deployment.
- Make the project resume-worthy by showing an end-to-end application.

## Scope

### In scope for MVP
- Local file upload for bank statements.
- Parsing of PDF statements and CSV exports.
- Normalized transaction storage.
- Basic category labeling.
- Manual correction of categories and merchant names.
- Simple spending dashboard.
- Monthly summaries and transaction filters.
- Export to CSV.

### In scope for later phases
- OCR for scanned statements.
- Multi-bank support.
- Loan tracking.
- Investment transaction tracking.
- LLM-assisted transaction explanation.
- Recurring transaction detection.
- Anomaly detection.
- Self-hosted deployment with Docker Compose.

### Out of scope for MVP
- Full bank API integrations.
- Real-time bank sync.
- Mobile app.
- Complex portfolio management.
- Automated tax preparation.
- Fully polished production UI.

## Core Users

- Me as the primary user.
- Family members who need a simpler view of spending.
- Eventually, trusted household users with separate access.

## Functional Requirements

### Ingestion
- Upload PDFs and CSVs.
- Detect file type and statement format.
- Extract raw text or tabular data.
- Preserve the raw source file for debugging and traceability.

### Parsing
- Convert statement data into a standardized transaction table.
- Handle credits, debits, fees, transfers, and balances.
- Normalize dates, descriptions, and amounts.
- Detect duplicate rows and parsing errors.

### Categorization
- Assign categories using a rules-first baseline.
- Train an ML model on corrected labels.
- Support merchant normalization.
- Store confidence scores for predictions.

### Review and correction
- Allow manual edits to transaction fields.
- Log corrected labels as training data.
- Highlight uncertain or ambiguous transactions.

### Analytics
- Show spending by month, category, merchant, and account.
- Identify recurring transactions.
- Display cash flow summaries.
- Separate loans and investments from normal expenses.

## Technical Architecture

### Backend
- **FastAPI** for API endpoints, file uploads, and backend logic.
- **Pydantic** for validation and schema management.
- **SQLAlchemy or SQLModel** for database access.
- **PostgreSQL** for primary storage.
- **SQLite** as a lightweight local development option.

### Data processing
- **pandas** for cleaning and transformation.
- **numpy** for numeric operations.
- **pdfplumber** or **PyMuPDF** for text-based PDFs.
- **pytesseract** and OCR tooling for scanned statements if needed.

### Machine learning
- **scikit-learn** for baseline transaction categorization.
- Optional clustering for merchant grouping and recurring pattern discovery.
- Feature engineering from description text, amount, frequency, and merchant history.
- Confidence scoring and error analysis on labeled samples.

### LLM / AI layer
- Optional LLM API support for ambiguous classification, transaction summarization, and natural-language financial questions.
- Local model support later via Ollama or another local inference stack.
- Embeddings and vector search only if they clearly improve retrieval or merchant memory.

### Frontend
- **React + TypeScript** for a more polished long-term UI.
- **Vite** for frontend development.
- **Tailwind CSS** and/or **shadcn/ui** for fast UI development.
- Optional **Streamlit** for a faster early prototype.

### Infrastructure
- **Docker** for containerized local development.
- **Docker Compose** for backend + database + frontend orchestration.
- **GitHub Actions** for testing and basic CI later.
- Optional homelab deployment with reverse proxy and persistent storage.

## Data Model

### Core entities
- Users.
- Accounts.
- Statements.
- Raw files.
- Transactions.
- Categories.
- Merchants.
- Corrections.
- ML predictions.
- Recurring series.
- Loans.
- Investment entries.

### Transaction fields
- Transaction ID.
- Statement ID.
- Account ID.
- Date.
- Posted date.
- Description.
- Merchant.
- Amount.
- Direction.
- Category.
- Subcategory.
- Confidence score.
- Source file.
- Parsed status.
- Manual override flag.

## ML Plan

### Phase 1: Rules baseline
- Start with keyword and merchant-based rules.
- Use heuristic logic for obvious categories.
- Separate transfers and fees early.

### Phase 2: Supervised classifier
- Build a labeled dataset from corrected transactions.
- Train a classifier with scikit-learn.
- Evaluate using accuracy, precision, recall, and macro F1.

### Phase 3: Human-in-the-loop learning
- Capture user corrections.
- Retrain periodically.
- Track model drift and category confusion.

### Phase 4: Advanced features
- Merchant clustering.
- Recurring charge detection.
- Anomaly detection.
- LLM-assisted explanations for ambiguous transactions.

## Milestones

### Milestone 1: Data foundation
- Define schema.
- Build local project structure.
- Set up database.
- Store raw statement files.
- Create transaction normalization pipeline.

### Milestone 2: MVP ingestion
- Accept PDFs and CSVs.
- Parse at least one statement format reliably.
- Save transactions to the database.
- Export cleaned transactions.

### Milestone 3: Basic analytics
- Show spending summaries.
- Display monthly trends.
- Add filters and transaction search.
- Add manual corrections.

### Milestone 4: ML categorization
- Train a baseline model.
- Add confidence scoring.
- Improve labels through corrections.
- Evaluate model performance.

### Milestone 5: Expandability
- Add OCR support.
- Add loan and investment views.
- Add LLM features.
- Prepare for self-hosted deployment.

## Timeline Estimate

This project is scoped as a **6-week MVP** with future expansion after launch.

- **Week 1:** Foundation, repo setup, schema, FastAPI skeleton, Docker.
- **Week 2:** Ingestion, PDF/CSV parsing, raw file storage.
- **Week 3:** Normalization, validation, duplicate detection, review UI.
- **Week 4:** Analytics dashboard, recurring detection, rules-based categorization.
- **Week 5:** Supervised ML classifier, confidence scoring, correction loop.
- **Week 6:** Polish, documentation, exports, Docker Compose, resume-ready finish.

## Success Criteria

The project will be considered successful when it can:

- Ingest real statements locally.
- Produce clean and structured transaction data.
- Categorize transactions with useful accuracy.
- Let users correct errors.
- Show understandable spending insights.
- Support future expansion into loans, investing, and homelab deployment.

## Why This Project Matters

This project is useful because it addresses a real personal and family need: understanding financial activity without manually combing through statements. It also provides a practical platform to demonstrate backend development, database design, ML integration, and deployment readiness. The local-first design is especially valuable because financial data is sensitive and should not be sent anywhere unnecessarily.

## Resume Value

This project demonstrates:

- Python engineering.
- API development.
- Database design.
- PDF/OCR data extraction.
- Machine learning classification.
- Human-in-the-loop system design.
- Dashboard and product development.
- Privacy-conscious software architecture.

## Future Enhancements

- Multi-bank parsing.
- Statement reconciliation across accounts.
- LLM query assistant.
- Budget alerts.
- Family-specific dashboards.
- Self-hosted authentication.
- Cloud or homelab deployment.
- Supporting brokerage and loan statement imports.

## Notes

This project should be built iteratively. The goal is not perfection on day one, but a useful system that improves as more statements are processed and corrected.

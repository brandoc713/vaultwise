from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import accounts, categories, ml, statements, transactions
from app.config import get_settings
from app.database import SessionLocal, create_db_and_tables
from app.services.ingestion import ensure_local_dirs
from app.services.seeds import seed_reference_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_local_dirs()
    create_db_and_tables()
    db = SessionLocal()
    try:
        seed_reference_data(db)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Personal Finance Statement Intelligence API",
        version="0.1.0",
        description="Local-first API for private statement ingestion and normalized transaction review.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(accounts.router)
    app.include_router(categories.router)
    app.include_router(statements.router)
    app.include_router(transactions.router)
    app.include_router(ml.router)
    return app


app = create_app()

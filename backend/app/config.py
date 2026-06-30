from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://finance:finance@localhost:5432/finance_dev"
    local_data_dir: Path = Path("local_data")
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    public_mode: bool = False
    pdf_text_threshold: int = 80
    ml_min_training_rows: int = 6

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def statements_dir(self) -> Path:
        return self.local_data_dir / "statements"

    @property
    def extracted_text_dir(self) -> Path:
        return self.local_data_dir / "extracted_text"

    @property
    def exports_dir(self) -> Path:
        return self.local_data_dir / "exports"

    @property
    def models_dir(self) -> Path:
        return self.local_data_dir / "models"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

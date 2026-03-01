"""Application settings."""
import os
from functools import lru_cache

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "Guitar Track to Tabs Converter"
    api_prefix: str = "/api/v1"
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/guitar_tabs"))
    redis_url: str = Field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    uploads_dir: str = Field(default_factory=lambda: os.getenv("UPLOADS_DIR", "./storage/uploads"))
    artifacts_dir: str = Field(default_factory=lambda: os.getenv("ARTIFACTS_DIR", "./storage/artifacts"))
    auto_create_tables: bool = Field(default_factory=lambda: os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

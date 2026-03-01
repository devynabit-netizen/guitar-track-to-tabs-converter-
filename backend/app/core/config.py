"""Application settings."""
from functools import lru_cache
from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "Guitar Track to Tabs Converter"
    api_prefix: str = "/api/v1"
    database_url: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/guitar_tabs")
    redis_url: str = "redis://localhost:6379/0"
    uploads_dir: str = "./storage/uploads"
    artifacts_dir: str = "./storage/artifacts"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

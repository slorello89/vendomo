"""Application configuration, loaded from the environment.

All settings have sensible defaults so the stack boots with zero config under
docker-compose. Override anything via environment variables or a .env file.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Infrastructure
    database_url: str = "postgresql+asyncpg://vendomo:vendomo@postgres:5432/vendomo"
    redis_url: str = "redis://redis:6379/0"

    # Seeding
    seed_on_startup: bool = True
    seed_count: int = 1000  # bump to 100000 for the Phase 3 optimization exercise

    # Caching
    map_cache_key: str = "vendomo:map:markers"
    map_cache_ttl: int = 60  # seconds

    # Revenue stream (Phase 2 scaffolding)
    revenue_stream: str = "vendomo:revenue:events"
    revenue_stream_maxlen: int = 50000

    # LLM access (for natural-language features)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"

    # CORS
    cors_origins: str = "*"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

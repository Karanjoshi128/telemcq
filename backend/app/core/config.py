from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str

    SESSION_ENCRYPTION_KEY: str  # base64 of 32 bytes
    CRON_SECRET: str

    FRONTEND_ORIGIN: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_DSN: str = "postgresql://postgres:postgres@db:5432/postgres"
    DB_SSLMODE: str = "prefer"
    DB_CONNECT_TIMEOUT: int = 10
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_LOCK_TTL_SECONDS: int = 30
    IDEMPOTENCY_CACHE_TTL_SECONDS: int = 3600

settings = Settings()

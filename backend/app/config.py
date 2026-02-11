"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://mongo:27017/remotifex"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # Encryption for secrets at rest
    encryption_key: str = "change-me-to-a-random-32-byte-key"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Storage
    projects_data_dir: str = "/data/projects"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

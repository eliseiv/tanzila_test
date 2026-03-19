from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = Field(
        default="postgresql://app_user:app_password@postgres:5432/app_db",
        description="PostgreSQL connection string",
    )
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    process_delay: float = 0.5

    model_config = {"env_prefix": "APP_", "env_file": ".env"}


settings = Settings()

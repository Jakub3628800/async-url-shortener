from pydantic_settings import BaseSettings
import os


class PostgresSettings(BaseSettings):
    """Settings for postgres connection."""

    model_config = {
        "env_prefix": "DB_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    host: str = "localhost"
    port: int = 5432
    database: str = "urldatabase"
    user: str = "localuser"
    password: str = "password123"
    ssl: bool = False

    # Connection pool settings
    min_size: int = 5
    max_size: int = 25
    timeout: float = 60.0

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class AppSettings(BaseSettings):
    """Application configuration settings."""

    model_config = {
        "env_prefix": "APP_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    debug: bool = False
    title: str = "URL Shortener API"
    description: str = "API for creating and managing shortened URLs"
    version: str = "1.0.0"

    # URL validation settings
    max_url_length: int = 2048
    max_key_length: int = 50

    # Rate limiting (for future implementation)
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60

    @property
    def environment(self) -> str:
        """Return the current environment."""
        return os.getenv("ENV", "development").lower()

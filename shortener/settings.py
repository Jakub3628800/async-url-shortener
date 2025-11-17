"""Application settings using dataclasses with environment variable support."""

import os
from dataclasses import dataclass


def _load_env_file():
    """Load .env file if it exists."""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    if key and key not in os.environ:
                        os.environ[key] = value


def _get_env(key: str, default: str = "") -> str:
    """Get environment variable with optional default."""
    return os.getenv(key, default)


def _get_env_int(key: str, default: int) -> int:
    """Get environment variable as integer."""
    try:
        return int(_get_env(key, str(default)))
    except ValueError:
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    """Get environment variable as boolean."""
    value = _get_env(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


# Load .env file on module import
_load_env_file()


@dataclass
class PostgresSettings:
    """Settings for postgres connection."""

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

    def __post_init__(self):
        """Load settings from environment variables with DB_ prefix."""
        self.host = _get_env("DB_HOST", self.host)
        self.port = _get_env_int("DB_PORT", self.port)
        self.database = _get_env("DB_DATABASE", self.database)
        self.user = _get_env("DB_USER", self.user)
        self.password = _get_env("DB_PASSWORD", self.password)
        self.ssl = _get_env_bool("DB_SSL", self.ssl)
        self.min_size = _get_env_int("DB_MIN_SIZE", self.min_size)
        self.max_size = _get_env_int("DB_MAX_SIZE", self.max_size)

        try:
            self.timeout = float(_get_env("DB_TIMEOUT", str(self.timeout)))
        except ValueError:
            pass

    @property
    def postgres_dsn(self) -> str:
        """Build PostgreSQL connection string for psycopg."""
        ssl_mode = "require" if self.ssl else "prefer"
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={ssl_mode}"


@dataclass
class AppSettings:
    """Application configuration settings."""

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

    def __post_init__(self):
        """Load settings from environment variables with APP_ prefix."""
        self.debug = _get_env_bool("APP_DEBUG", self.debug)
        self.title = _get_env("APP_TITLE", self.title)
        self.description = _get_env("APP_DESCRIPTION", self.description)
        self.version = _get_env("APP_VERSION", self.version)
        self.max_url_length = _get_env_int("APP_MAX_URL_LENGTH", self.max_url_length)
        self.max_key_length = _get_env_int("APP_MAX_KEY_LENGTH", self.max_key_length)
        self.rate_limit_enabled = _get_env_bool("APP_RATE_LIMIT_ENABLED", self.rate_limit_enabled)
        self.rate_limit_per_minute = _get_env_int("APP_RATE_LIMIT_PER_MINUTE", self.rate_limit_per_minute)

    @property
    def environment(self) -> str:
        """Return the current environment."""
        return os.getenv("ENV", "development").lower()

from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    """Settings for postgres connection."""

    model_config = {"env_prefix": "DB_", "env_file": ".env", "env_file_encoding": "utf-8"}

    host: str = "localhost"
    port: int = 5432
    database: str = "postgres"
    user: str = "localuser"
    password: str = "password123"
    ssl: bool = False

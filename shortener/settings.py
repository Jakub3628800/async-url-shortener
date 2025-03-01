from pydantic_settings import BaseSettings


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

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

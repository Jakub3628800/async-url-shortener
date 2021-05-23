from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    debug: bool = False

    postgres_user: str = "localuser"
    postgres_password: SecretStr = SecretStr("password123")
    postgres_db: str = "urldatabase"


def get_settings():
    return Settings()

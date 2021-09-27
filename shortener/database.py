from pydantic import SecretStr
import os


def load_database_url() -> SecretStr:
    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")

    db_hostname = f"{db_host}:{db_port}"
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "localuser")
    db_password = SecretStr(os.getenv("DB_PASS", "password123"))

    db_url = os.getenv("DATABASE_URL", None)
    if db_url:
        return SecretStr(db_url)

    db_url = f"postgresql://{db_user}:{db_password.get_secret_value()}@{db_hostname}/{db_name}"
    return SecretStr(db_url)

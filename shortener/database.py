from databases import Database
from pydantic import SecretStr


def load_database_url() -> SecretStr:
    db_host = "localhost:5432"
    db_name = "urldatabase"
    db_user = "localuser"
    db_password = SecretStr("password123")

    db_url = f"postgresql://{db_user}:{db_password.get_secret_value()}@{db_host}/{db_name}"
    return SecretStr(db_url)


database_url = load_database_url()
postgres_connection = Database(database_url.get_secret_value())


async def set_up_postgres_connection() -> None:
    """Postgres database connection."""
    await postgres_connection.connect()


async def tear_down_postgres_connection():
    global postgres_connection
    await postgres_connection.disconnect()
    postgres_connection = None

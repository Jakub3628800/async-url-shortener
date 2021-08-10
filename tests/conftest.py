import pytest
import os
from starlette.testclient import TestClient
from shortener.factory import app
import asyncpg
from shortener.database import load_database_url


@pytest.mark.asyncio
@pytest.fixture(scope="function")
async def test_client():
    async with asyncpg.create_pool(dsn=load_database_url().get_secret_value(), min_size=5, max_size=25) as pool:
        app.pool = pool
        yield TestClient(app=app)

    return


@pytest.fixture(scope="session")
def psycopg2_cursor():
    import psycopg2

    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")

    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "localuser")
    db_password = os.getenv("DB_PASS", "password123")
    connection = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)

    cur = connection.cursor()
    cur.execute("SELECT 1")

    try:
        with open("database_migrations/create_short_url_table.sql") as sql_file:
            migration = "".join(sql_file.readlines())
            cur.execute(query=migration)
    except Exception:
        pass

    connection.commit()
    yield cur
    connection.close()

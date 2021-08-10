import pytest
import os
from starlette.testclient import TestClient
from shortener.factory import init_app
from shortener.database import create_db_pool
import asyncio
import httpx


@pytest.fixture(scope="function")
def test_client():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    return TestClient(app=app)

@pytest.fixture(scope="session")
def psycopg2_cursor():
    import psycopg2

    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")

    db_name = os.getenv("DB_NAME","postgres")
    db_user = os.getenv("DB_USER","localuser")
    db_password = os.getenv("DB_PASS","password123")
    connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )


    cur = connection.cursor()
    cur.execute('SELECT 1')

    migration_files = ["create_short_url_table.sql"]
    for filename in migration_files:
        with open(f"database_migrations/{filename}") as sql_file:
            migration = "".join(sql_file.readlines())
            cur.execute(query=migration)
            connection.commit()
    yield cur
    connection.close()
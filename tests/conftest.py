import pytest
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

@pytest.fixture()
def psycopg2_cursor():
    import psycopg2

    connection = psycopg2.connect(
        dbname="urldatabase",
        user="localuser",
        password="password123",
        host="localhost",
        port=5432
    )


    cur = connection.cursor()
    cur.execute('SELECT 1')
    yield cur
    connection.close()
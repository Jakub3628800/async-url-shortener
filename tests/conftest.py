import pytest
from starlette.testclient import TestClient
from shortener.factory import app
from shortener.database import create_db_pool
import httpx


@pytest.fixture(scope="function")
def test_client():
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
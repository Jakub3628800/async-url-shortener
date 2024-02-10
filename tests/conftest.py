import os

import asyncpg
import psycopg2
import pytest
from starlette.testclient import TestClient

from shortener.factory import app
from shortener.settings import PostgresSettings


@pytest.fixture(scope="function")
async def test_client():
    async_pool = asyncpg.create_pool(min_size=5, max_size=25, **dict(PostgresSettings(_env_file=None)))
    async with async_pool as pool:
        app.pool = pool
        with TestClient(app=app) as client:
            yield client

    return


# @pytest.fixture(scope="session")
# def docker_compose_test_containers():
#    compose = DockerCompose("", compose_file_name="docker-compose.yaml", pull=True)
#    print("Starting docker compose")
#    with compose:
#        stdout, stderr = compose.get_logs()
#        print(stdout)


@pytest.fixture(scope="session")
def psycopg2_cursor():
    #    compose = DockerCompose(".", compose_file_name="docker-compose.yaml", pull=True)
    #
    #    with compose:
    #        stdout, stderr = compose.get_logs()
    #        print(stdout)
    #
    #    import time

    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")

    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "localuser")
    db_password = os.getenv("DB_PASSWORD", "password123")
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

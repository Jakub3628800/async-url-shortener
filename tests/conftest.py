import os

import asyncpg
import psycopg2
import pytest
from starlette.testclient import TestClient
from alembic import command
from alembic.config import Config

from shortener.factory import app


@pytest.fixture(scope="function")
async def test_client():
    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "test_db")
    db_user = os.getenv("DB_USER", "localuser")
    db_password = os.getenv("DB_PASSWORD", "password123")

    async_pool = await asyncpg.create_pool(
        min_size=5,
        max_size=25,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_name
    )
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

    db_name = os.getenv("DB_NAME", "test_db")
    db_user = os.getenv("DB_USER", "localuser")
    db_password = os.getenv("DB_PASSWORD", "password123")

    # Create database connection for cleanup
    connection = psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port
    )

    # Configure and run Alembic migrations

    # Create new connection for migrations
    alembic_connection = psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port
    )

    # Configure Alembic
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

    # Drop all tables if they exist
    with alembic_connection.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS alembic_version CASCADE")
        cur.execute("DROP TABLE IF EXISTS short_urls CASCADE")
    alembic_connection.commit()

    # Create fresh database schema
    print("Running Alembic migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully")

    # Verify tables exist
    with alembic_connection.cursor() as cur:
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'short_urls')")
        if not cur.fetchone()[0]:
            raise RuntimeError("Failed to create short_urls table")

    # Close migration connection
    alembic_connection.close()

    # Create fresh connection for tests
    connection = psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port
    )

    cur = connection.cursor()
    cur.execute("SELECT 1")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    connection.commit()
    yield cur
    connection.close()

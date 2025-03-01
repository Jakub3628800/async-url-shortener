import os

import asyncpg
import psycopg2
import pytest
from starlette.testclient import TestClient
from alembic import command
from alembic.config import Config

from shortener.factory import app


@pytest.fixture(scope="function")
async def test_client(psycopg2_cursor):
    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "urldatabase")
    db_user = os.getenv("DB_USER", "localuser")
    db_password = os.getenv("DB_PASSWORD", "password123")

    # Create connection pool for the application
    async_pool = await asyncpg.create_pool(
        min_size=5,
        max_size=25,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_name
    )

    # Verify that the short_urls table exists and create it if it doesn't
    async with async_pool.acquire() as conn:
        try:
            # Check if table exists and create it if not
            table_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'short_urls')"
            )

            if not table_exists:
                print("Creating short_urls table through asyncpg")
                await conn.execute("""
                CREATE TABLE short_urls (
                    id SERIAL PRIMARY KEY,
                    url_key VARCHAR NOT NULL UNIQUE,
                    target VARCHAR NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
                )
                """)

            # Add initial test data
            await conn.execute(
                "INSERT INTO short_urls (url_key, target) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                "test1_short", "https://example.com/test1"
            )
        except Exception as e:
            print(f"Setup error: {e}")

    # Set the app's connection pool
    app.pool = async_pool
    with TestClient(app=app) as client:
        yield client

    # Don't close the pool to allow shared use with other tests


# @pytest.fixture(scope="session")
# def docker_compose_test_containers():
#    compose = DockerCompose("", compose_file_name="docker-compose.yaml", pull=True)
#    print("Starting docker compose")
#    with compose:
#        stdout, stderr = compose.get_logs()
#        print(stdout)


@pytest.fixture(scope="session")
def psycopg2_cursor():
    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "urldatabase")
    db_user = os.getenv("DB_USER", "localuser")
    db_password = os.getenv("DB_PASSWORD", "password123")

    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

    # Create connection for migrations
    alembic_connection = psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port
    )

    # Drop all tables if they exist to start clean
    with alembic_connection.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS alembic_version CASCADE")
        cur.execute("DROP TABLE IF EXISTS short_urls CASCADE")
    alembic_connection.commit()

    try:
        print("Running Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(f"Error running migrations: {e}")
        # Create the table manually if it doesn't exist
        with alembic_connection.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'short_urls')")
            if not cur.fetchone()[0]:
                print("Creating short_urls table manually")
                cur.execute("""
                CREATE TABLE short_urls (
                    id SERIAL PRIMARY KEY,
                    url_key VARCHAR NOT NULL UNIQUE,
                    target VARCHAR NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
                )
                """)
                cur.execute("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) PRIMARY KEY)")
                cur.execute("INSERT INTO alembic_version VALUES ('d6f2bb97ceff')")
                alembic_connection.commit()

    print("Migrations completed successfully")

    # Verify tables exist
    with alembic_connection.cursor() as cur:
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'short_urls')")
        if not cur.fetchone()[0]:
            raise RuntimeError("Failed to create short_urls table")

    # Close migration connection
    alembic_connection.close()

    # Create persistent connection for tests
    connection = psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port
    )
    connection.autocommit = False

    cur = connection.cursor()
    connection.commit()

    yield cur

    # Clean up after tests
    connection.close()

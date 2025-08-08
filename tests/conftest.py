import os
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock

import psycopg2
import pytest
from starlette.testclient import TestClient
from alembic import command
from alembic.config import Config

from shortener.app import app
from shortener.settings import AppSettings


@pytest.fixture(scope="function")
def test_client(psycopg2_cursor: Any) -> TestClient:
    """Create a test client with mocked database connections."""
    # Create app settings
    app_settings = AppSettings()

    # Create a mock pool
    mock_pool = MagicMock()
    mock_connection = AsyncMock()

    # Configure the mock connection to return appropriate values for different queries
    async def mock_fetchval(query, *args):
        if "SELECT 1" in query:
            return 1
        # For get_url_target, return a valid URL for any key
        if "SELECT target from short_urls where url_key" in query:
            return "https://example.com/mocked"
        return None

    async def mock_fetch(query, *args):
        if "SELECT url_key, target from short_urls" in query:
            return [{"url_key": "test1", "target": "https://example.com"}]
        return []

    async def mock_execute(query, *args):
        if "DELETE FROM short_urls" in query:
            return "DELETE 1"
        if "UPDATE short_urls" in query:
            return "UPDATE 1"
        if "INSERT INTO short_urls" in query:
            return "INSERT 0 1"
        return "OK"

    # Set up the mock connection methods
    mock_connection.fetchval.side_effect = mock_fetchval
    mock_connection.fetch.side_effect = mock_fetch
    mock_connection.execute.side_effect = mock_execute

    # Configure the mock pool to return the mock connection
    async def mock_acquire():
        return mock_connection

    mock_pool.acquire.return_value.__aenter__.side_effect = mock_acquire

    # Set up the app state
    app.state.pool = mock_pool
    app.state.settings = app_settings

    # Create the test client
    client = TestClient(app)

    return client


# @pytest.fixture(scope="session")
# def docker_compose_test_containers():
#    compose = DockerCompose("", compose_file_name="docker-compose.yaml", pull=True)
#    print("Starting docker compose")
#    with compose:
#        stdout, stderr = compose.get_logs()
#        print(stdout)


@pytest.fixture(scope="session")
def psycopg2_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """Create a PostgreSQL connection for tests."""
    # Get database connection parameters from environment variables
    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "urldatabase")
    db_user = os.getenv("DB_USER", "localuser")
    db_password = os.getenv("DB_PASSWORD", "password123")

    # Create a connection
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    conn.autocommit = True

    yield conn

    # Close the connection
    conn.close()


@pytest.fixture(scope="function")
def psycopg2_cursor(psycopg2_connection: psycopg2.extensions.connection, run_migrations: None) -> Generator[psycopg2.extensions.cursor, None, None]:
    """Create a PostgreSQL cursor for tests."""
    # Create a cursor
    cursor = psycopg2_connection.cursor()

    # Clear the short_urls table before each test
    try:
        cursor.execute("DELETE FROM short_urls")
        psycopg2_connection.commit()
    except psycopg2.errors.UndefinedTable:
        # Table doesn't exist yet, that's fine for unit tests
        pass

    yield cursor

    # Close the cursor
    cursor.close()


@pytest.fixture(scope="function")
def alembic_config() -> Config:
    """Get alembic config."""
    config = Config("alembic.ini")
    return config


@pytest.fixture(scope="function")
def run_migrations(alembic_config: Config) -> None:
    """Run migrations to head."""
    command.upgrade(alembic_config, "head")

    # Get database connection parameters from environment variables
    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "urldatabase")
    db_user = os.getenv("DB_USER", "localuser")
    db_password = os.getenv("DB_PASSWORD", "password123")

    # Create a connection for verification
    verification_connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    # Verify tables exist
    with verification_connection.cursor() as cur:
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'short_urls')")
        if not cur.fetchone()[0]:
            raise RuntimeError("Failed to create short_urls table")

    # Close verification connection
    verification_connection.close()

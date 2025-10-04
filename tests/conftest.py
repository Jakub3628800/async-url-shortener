import os
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock

import psycopg2
import psycopg2.extensions
import psycopg2.errors
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient
from alembic import command
from alembic.config import Config
from testcontainers.postgres import PostgresContainer

from shortener.app import app
from shortener.settings import AppSettings


@pytest.fixture(scope="function")
def test_client(psycopg2_cursor: Any) -> TestClient:
    """Create a test client with mocked database connections."""
    # Create app settings
    app_settings = AppSettings()

    # Create a mock session factory
    mock_session_factory = MagicMock()
    mock_session = AsyncMock(spec=AsyncSession)

    # Configure mock behaviors for different queries
    async def mock_execute(stmt):
        result = MagicMock()

        # Check the type of statement
        stmt_str = str(stmt)

        if "SELECT 1" in stmt_str:
            result.scalar.return_value = 1
        elif "SELECT short_urls.target" in stmt_str:
            result.scalar_one_or_none.return_value = "https://example.com/mocked"
        elif "SELECT short_urls.url_key, short_urls.target" in stmt_str:
            mock_record = MagicMock()
            mock_record.url_key = "test1"
            mock_record.target = "https://example.com"
            result.all.return_value = [mock_record]
        elif "DELETE FROM short_urls" in stmt_str:
            result.rowcount = 1
        elif "UPDATE short_urls" in stmt_str:
            result.rowcount = 1
        elif "INSERT INTO short_urls" in stmt_str:
            result.rowcount = 1
        else:
            result.scalar.return_value = None
            result.scalar_one_or_none.return_value = None
            result.all.return_value = []
            result.rowcount = 0

        return result

    # Configure the mock session
    mock_session.execute.side_effect = mock_execute
    mock_session.add = MagicMock()
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()

    # Configure the mock session factory to return the mock session
    async def mock_session_context(self):
        return mock_session

    async def mock_session_exit(self, exc_type, exc_val, exc_tb):
        return None

    mock_session_factory.return_value.__aenter__ = mock_session_context
    mock_session_factory.return_value.__aexit__ = mock_session_exit

    # Set up the app state
    app.state.session_factory = mock_session_factory
    app.state.settings = app_settings

    # Create the test client
    client = TestClient(app)

    return client


@pytest.fixture(scope="session")
def postgres_container():
    """Create and manage a PostgreSQL container for the test session."""
    postgres = PostgresContainer(
        image="postgres:15",
        username="localuser",
        password="password123",
        dbname="urldatabase",
        port=5432,
    )

    postgres.start()

    # Wait for the container to be ready
    import time

    time.sleep(2)

    # Set environment variables for the connection
    os.environ["DB_HOST"] = postgres.get_container_host_ip()
    os.environ["DB_PORT"] = str(postgres.get_exposed_port(5432))
    os.environ["DB_NAME"] = "urldatabase"
    os.environ["DB_USER"] = "localuser"
    os.environ["DB_PASSWORD"] = "password123"

    yield postgres

    # Cleanup
    postgres.stop()


@pytest.fixture(scope="session")
def psycopg2_connection(
    postgres_container: PostgresContainer,
) -> Generator[psycopg2.extensions.connection, None, None]:
    """Create a PostgreSQL connection for tests."""
    # Get connection details from the container
    db_host = postgres_container.get_container_host_ip()
    db_port = postgres_container.get_exposed_port(5432)
    db_name = "urldatabase"
    db_user = "localuser"
    db_password = "password123"

    # Create a connection
    conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password)
    conn.autocommit = True

    yield conn

    # Close the connection
    conn.close()


@pytest.fixture(scope="function")
def psycopg2_cursor(
    psycopg2_connection: psycopg2.extensions.connection, run_migrations: None
) -> Generator[psycopg2.extensions.cursor, None, None]:
    """Create a PostgreSQL cursor for tests."""
    # Create a cursor
    cursor = psycopg2_connection.cursor()

    # Clear the short_urls table before each test
    try:
        cursor.execute("DELETE FROM short_urls")
        psycopg2_connection.commit()
    except psycopg2.ProgrammingError:
        # Table doesn't exist yet, that's fine for unit tests
        pass

    yield cursor

    # Close the cursor
    cursor.close()


@pytest.fixture(scope="function")
def alembic_config(postgres_container: PostgresContainer) -> Config:
    """Get alembic config with updated database URL."""
    config = Config("alembic.ini")

    # Update the database URL for migrations
    db_host = postgres_container.get_container_host_ip()
    db_port = postgres_container.get_exposed_port(5432)
    db_url = f"postgresql://localuser:password123@{db_host}:{db_port}/urldatabase"
    config.set_main_option("sqlalchemy.url", db_url)

    return config


@pytest.fixture(scope="function")
def run_migrations(alembic_config: Config, postgres_container: PostgresContainer) -> None:
    """Run migrations to head."""
    command.upgrade(alembic_config, "head")

    # Get database connection parameters from the container
    db_host = postgres_container.get_container_host_ip()
    db_port = postgres_container.get_exposed_port(5432)
    db_name = "urldatabase"
    db_user = "localuser"
    db_password = "password123"

    # Create a connection for verification
    verification_connection = psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port
    )

    # Verify tables exist
    with verification_connection.cursor() as cur:
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'short_urls')")
        result = cur.fetchone()
        if not result or not result[0]:
            raise RuntimeError("Failed to create short_urls table")

    # Close verification connection
    verification_connection.close()

import os
import time
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import psycopg
import pytest
from starlette.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from shortener.app import app
from shortener.database import Database
from shortener.settings import AppSettings


@pytest.fixture(scope="function")
def test_client() -> TestClient:
    """Create a test client with mocked database."""
    # Create app settings
    app_settings = AppSettings()

    # Create a mock database
    mock_db = AsyncMock(spec=Database)

    # Configure mock behaviors for different queries
    async def mock_execute_one(query, *args):
        if "SELECT 1" in query:
            return (1,)
        elif "SELECT target FROM short_urls" in query:
            return ("https://example.com/mocked",)
        return None

    async def mock_execute_all(query, *args):
        if "SELECT url_key, target FROM short_urls" in query:
            return [("test1", "https://example.com")]
        return []

    async def mock_execute(query, *args):
        return None

    # Configure the mock database
    mock_db.execute_one.side_effect = mock_execute_one
    mock_db.execute_all.side_effect = mock_execute_all
    mock_db.execute.side_effect = mock_execute

    # Create a mock connection context manager
    class MockConnectionContext:
        async def __aenter__(self):
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()

            # Configure mock execute for UPDATE and DELETE
            async def mock_conn_execute(query, *args):
                result = MagicMock()
                result.rowcount = 1
                return result

            mock_conn.execute.side_effect = mock_conn_execute
            return mock_conn

        async def __aexit__(self, *args):
            pass

    mock_db.get_connection.return_value = MockConnectionContext()

    # Set up the app state
    app.state.db = mock_db
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
async def db_connection(postgres_container: PostgresContainer) -> AsyncGenerator[psycopg.AsyncConnection, None]:
    """Create a PostgreSQL async connection for tests."""
    db_host = postgres_container.get_container_host_ip()
    db_port = postgres_container.get_exposed_port(5432)
    db_name = "urldatabase"
    db_user = "localuser"
    db_password = "password123"

    dsn = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    conn = await psycopg.AsyncConnection.connect(dsn)

    yield conn

    await conn.close()


@pytest.fixture(scope="function")
async def db_cleanup(db_connection: psycopg.AsyncConnection) -> AsyncGenerator[None, None]:
    """Clean up database before and after each test."""
    # Create tables
    await db_connection.execute("""
        CREATE TABLE IF NOT EXISTS short_urls (
            id SERIAL PRIMARY KEY,
            url_key VARCHAR(255) UNIQUE NOT NULL,
            target VARCHAR(2048) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """)
    await db_connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_short_urls_url_key ON short_urls(url_key)
    """)

    # Clear the short_urls table before each test
    await db_connection.execute("DELETE FROM short_urls")

    yield

    # Cleanup after test
    await db_connection.execute("DELETE FROM short_urls")


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

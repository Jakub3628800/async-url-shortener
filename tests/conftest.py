import os
import tempfile
from typing import Generator
import asyncio

import psycopg2
import pytest
from starlette.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from alembic import command
from alembic.config import Config

from shortener.factory import app
from shortener.settings import DatabaseSettings, AppSettings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_type():
    """Get database type from environment variable."""
    return os.getenv("DB_TYPE", "sqlite")


@pytest.fixture
async def sqlite_engine():
    """Create a SQLite test database engine."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

    # Create tables
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS short_urls (
                url_key TEXT PRIMARY KEY,
                target TEXT NOT NULL
            )
        """))

    yield engine

    await engine.dispose()
    os.unlink(db_path)


@pytest.fixture(scope="session")
async def postgresql_engine():
    """Create a PostgreSQL test database engine."""
    db_settings = DatabaseSettings(type="postgresql")
    engine = create_async_engine(
        db_settings.database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True
    )

    # Create tables directly (skip alembic for integration tests)
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS short_urls CASCADE"))
        await conn.execute(text("""
            CREATE TABLE short_urls (
                url_key VARCHAR(255) PRIMARY KEY,
                target VARCHAR(2048) NOT NULL
            )
        """))

    yield engine

    # Clean up
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS short_urls CASCADE"))
    except Exception:
        pass  # Ignore cleanup errors

    await engine.dispose()


@pytest.fixture
async def db_engine(db_type):
    """Provide the appropriate database engine based on db_type."""
    if db_type == "sqlite":
        # Create SQLite engine inline
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

        # Create tables
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS short_urls (
                    url_key TEXT PRIMARY KEY,
                    target TEXT NOT NULL
                )
            """))

        yield engine

        await engine.dispose()
        import os
        os.unlink(db_path)
    else:
        # Create PostgreSQL engine inline
        db_settings = DatabaseSettings(type="postgresql")
        engine = create_async_engine(
            db_settings.database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )

        # Create tables directly (skip alembic for integration tests)
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS short_urls CASCADE"))
            await conn.execute(text("""
                CREATE TABLE short_urls (
                    url_key VARCHAR(255) PRIMARY KEY,
                    target VARCHAR(2048) NOT NULL
                )
            """))

        yield engine

        # Clean up
        try:
            async with engine.begin() as conn:
                await conn.execute(text("DROP TABLE IF EXISTS short_urls CASCADE"))
        except Exception:
            pass  # Ignore cleanup errors

        await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create a database session for testing."""
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession)
    async with session_factory() as session:
        yield session


@pytest.fixture
def mock_app_with_db(db_engine):
    """Create a test app with real database connection."""
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    app.state.engine = db_engine
    app.state.session_factory = session_factory
    app.state.settings = AppSettings()

    return app


@pytest.fixture(scope="function")
async def clean_database(db_engine):
    """Clean database between tests."""
    yield
    # Clean up after each test
    async with db_engine.begin() as conn:
        await conn.execute(text("DELETE FROM short_urls"))


@pytest.fixture(scope="function")
def test_client(db_engine, clean_database) -> TestClient:
    """Create a test client with real database connections."""
    app_settings = AppSettings()
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    # Set up the app state
    app.state.engine = db_engine
    app.state.session_factory = session_factory
    app.state.settings = app_settings

    # Create the test client
    client = TestClient(app)
    return client


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
def run_migrations() -> None:
    """Run migrations to head - only used for PostgreSQL integration tests."""
    # Only run migrations if we're testing against PostgreSQL
    db_type = os.getenv("DB_TYPE", "postgresql")
    if db_type.lower() != "postgresql":
        return

    config = Config("alembic.ini")
    command.upgrade(config, "head")

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

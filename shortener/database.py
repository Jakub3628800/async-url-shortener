"""Database configuration using psycopg3 connection pool."""

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

from shortener.settings import PostgresSettings


class Database:
    """Database connection pool manager using psycopg3."""

    def __init__(self, settings: PostgresSettings):
        """Initialize database with settings."""
        self.settings: PostgresSettings = settings
        self.pool: AsyncConnectionPool | None = None

    async def connect(self) -> None:
        """Create the connection pool."""
        self.pool = AsyncConnectionPool(
            self.settings.postgres_dsn,
            min_size=self.settings.min_size,
            max_size=self.settings.max_size,
            timeout=self.settings.timeout,
        )
        await self.pool.open()

    async def disconnect(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()  # type: ignore[union-attr]

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        """Get a connection from the pool."""
        if not self.pool:
            raise RuntimeError("Database not connected. Call connect() first.")

        async with self.pool.connection() as conn:  # type: ignore[union-attr]
            yield conn

    async def execute(self, query: str, *args) -> None:
        """Execute a query without returning results."""
        async with self.get_connection() as conn:
            await conn.execute(query, args if args else None)  # type: ignore[arg-type]

    async def execute_one(self, query: str, *args) -> tuple | None:
        """Execute a query and return a single row as a tuple."""
        async with self.get_connection() as conn:
            result = await conn.execute(query, args if args else None)  # type: ignore[arg-type]
            return await result.fetchone()

    async def execute_all(self, query: str, *args) -> list[tuple]:
        """Execute a query and return all rows as tuples."""
        async with self.get_connection() as conn:
            result = await conn.execute(query, args if args else None)  # type: ignore[arg-type]
            return await result.fetchall()

    async def execute_one_dict(self, query: str, *args) -> dict | None:
        """Execute a query and return a single row as a dictionary."""
        async with self.get_connection() as conn:
            cur = conn.cursor(row_factory=dict_row)
            result = await cur.execute(query, args if args else None)  # type: ignore[arg-type]
            return await result.fetchone()

    async def execute_all_dict(self, query: str, *args) -> list[dict]:
        """Execute a query and return all rows as dictionaries."""
        async with self.get_connection() as conn:
            cur = conn.cursor(row_factory=dict_row)
            result = await cur.execute(query, args if args else None)  # type: ignore[arg-type]
            return await result.fetchall()


# Global database instance
_db_instance: Database | None = None


def get_database(settings: PostgresSettings | None = None) -> Database:
    """Get or create the global database instance."""
    global _db_instance
    if _db_instance is None:
        if settings is None:
            settings = PostgresSettings()
        _db_instance = Database(settings)
    return _db_instance

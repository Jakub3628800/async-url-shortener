"""Database configuration and session management."""

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool

from shortener.settings import PostgresSettings


def create_engine(settings: PostgresSettings) -> AsyncEngine:
    """Create async SQLAlchemy engine."""
    return create_async_engine(
        settings.postgres_dsn,
        echo=False,
        poolclass=NullPool,  # Let asyncpg handle pooling
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create async session factory."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


@asynccontextmanager
async def get_session(
    session_factory: async_sessionmaker[AsyncSession]
) -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

import logging
from typing import Dict, List

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException

from shortener.models import ShortUrl


def _validate_short_url(short_url: str) -> None:
    """Raise UrlValidationError if short_url is empty."""
    if not short_url:
        raise UrlValidationError(detail="Short URL cannot be empty")


class UrlNotFoundException(HTTPException):
    """Exception raised when a URL is not found (404)."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=404, detail=detail)


class UrlValidationError(HTTPException):
    """Exception raised for invalid URL input (400)."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=400, detail=detail)


async def check_db_up(session: AsyncSession) -> bool:
    """Check connectivity to the database."""
    try:
        result = await session.execute(select(1))
        return result.scalar() == 1
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        return False


async def get_url_target(short_url: str, session: AsyncSession) -> str:
    """
    Get the target URL for a given short URL key.

    Args:
        short_url: The short URL key to look up
        session: Database session

    Returns:
        The target URL as a string

    Raises:
        UrlNotFoundException: If the short URL doesn't exist
    """
    _validate_short_url(short_url)

    try:
        stmt = select(ShortUrl.target).where(ShortUrl.url_key == short_url)
        result = await session.execute(stmt)
        target = result.scalar_one_or_none()

        if target is None:
            raise UrlNotFoundException(detail=f"URL with key '{short_url}' not found")
        return target
    except UrlNotFoundException:
        raise
    except Exception as e:
        logging.error(f"Database error when retrieving URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


async def get_all_short_urls(session: AsyncSession) -> List[Dict[str, str]]:
    """
    Get all short URLs and their targets.

    Args:
        session: Database session

    Returns:
        List of dictionaries containing short_url and target_url
    """
    try:
        stmt = select(ShortUrl.url_key, ShortUrl.target)
        result = await session.execute(stmt)
        records = result.all()
        return [{"short_url": record.url_key, "target_url": record.target} for record in records]
    except Exception as e:
        logging.error(f"Error retrieving all URLs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving URLs")


async def create_url_target(short_url: str, target_url: str, session: AsyncSession) -> bool:
    """
    Create a new short URL mapping.

    Args:
        short_url: The short URL key to create
        target_url: The target URL it should redirect to
        session: Database session

    Returns:
        True if successful, False if URL already exists

    Raises:
        HTTPException: For database errors
        UrlValidationError: For invalid input
    """
    _validate_short_url(short_url)
    if not target_url:
        raise UrlValidationError(detail="Target URL cannot be empty")

    try:
        new_url = ShortUrl(url_key=short_url, target=target_url)
        session.add(new_url)
        await session.flush()
        return True
    except IntegrityError:
        await session.rollback()
        return False
    except Exception as e:
        logging.error(f"Error creating URL: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error creating URL")


async def update_url_target(short_url: str, new_target_url: str, session: AsyncSession) -> bool:
    """
    Update an existing short URL mapping.

    Args:
        short_url: The short URL key to update
        new_target_url: The new target URL
        session: Database session

    Returns:
        True if URL was updated, False if URL doesn't exist

    Raises:
        HTTPException: For database errors
        UrlValidationError: For invalid input
    """
    _validate_short_url(short_url)
    if not new_target_url:
        raise UrlValidationError(detail="Target URL cannot be empty")

    try:
        stmt = update(ShortUrl).where(ShortUrl.url_key == short_url).values(target=new_target_url)
        result: CursorResult = await session.execute(stmt)  # type: ignore[assignment]
        await session.flush()
        return result.rowcount > 0
    except Exception as e:
        logging.error(f"Error updating URL: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error updating URL")


async def delete_url_target(short_url: str, session: AsyncSession) -> bool:
    """
    Delete a short URL mapping.

    Args:
        short_url: The short URL key to delete
        session: Database session

    Returns:
        True if URL was deleted, False if URL doesn't exist

    Raises:
        HTTPException: For database errors
    """
    _validate_short_url(short_url)

    try:
        stmt = delete(ShortUrl).where(ShortUrl.url_key == short_url)
        result: CursorResult = await session.execute(stmt)  # type: ignore[assignment]
        await session.flush()
        return result.rowcount > 0
    except Exception as e:
        logging.error(f"Error deleting URL: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error deleting URL")

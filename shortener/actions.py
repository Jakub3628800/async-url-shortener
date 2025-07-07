import logging
from typing import Dict, List, Any, cast
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import CursorResult
from starlette.exceptions import HTTPException


class UrlNotFoundException(HTTPException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["status_code"] = 404
        super().__init__(*args, **kwargs)


class UrlValidationError(HTTPException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["status_code"] = 400
        super().__init__(*args, **kwargs)


async def check_db_up(session: AsyncSession) -> bool:
    """Check connectivity to the database."""
    try:
        result = await session.execute(text("SELECT 1"))
        scalar_result = result.scalar()
        return scalar_result == 1
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
    if not short_url or not short_url.strip():
        raise UrlValidationError(detail="Short URL cannot be empty")

    try:
        result = await session.execute(
            text("SELECT target from short_urls where url_key=:url_key"),
            {"url_key": short_url}
        )
        target = result.scalar()
        if target is None:
            raise UrlNotFoundException(detail=f"URL with key '{short_url}' not found")
        return target
    except Exception as e:
        logging.error(f"Database error when retrieving URL: {str(e)}")
        raise UrlNotFoundException(detail=f"URL with key '{short_url}' not found")


async def get_all_short_urls(session: AsyncSession) -> List[Dict[str, str]]:
    """
    Get all short URLs and their targets.

    Args:
        session: Database session

    Returns:
        List of dictionaries containing short_url and target_url
    """
    try:
        result = await session.execute(text("SELECT url_key, target from short_urls"))
        records = result.fetchall()
        return [{"short_url": record.url_key, "target_url": record.target} for record in records]
    except Exception as e:
        logging.error(f"Error retrieving all URLs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving URLs")


async def create_url_target(
    short_url: str, target_url: str, session: AsyncSession
) -> bool:
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
    if not short_url or not short_url.strip():
        raise UrlValidationError(detail="Short URL cannot be empty")
    if not target_url or not target_url.strip():
        raise UrlValidationError(detail="Target URL cannot be empty")

    try:
        await session.execute(
            text("INSERT INTO short_urls (url_key, target) VALUES (:url_key, :target)"),
            {"url_key": short_url, "target": target_url}
        )
        await session.commit()
        return True
    except IntegrityError:
        await session.rollback()
        return False
    except Exception as e:
        await session.rollback()
        logging.error(f"Error creating URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating URL")


async def update_url_target(
    short_url: str, new_target_url: str, session: AsyncSession
) -> bool:
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
    if not short_url or not short_url.strip():
        raise UrlValidationError(detail="Short URL cannot be empty")
    if not new_target_url or not new_target_url.strip():
        raise UrlValidationError(detail="Target URL cannot be empty")

    try:
        result = cast(CursorResult[Any], await session.execute(
            text("UPDATE short_urls SET target = :target WHERE url_key = :url_key"),
            {"target": new_target_url, "url_key": short_url}
        ))
        await session.commit()
        return result.rowcount is not None and result.rowcount > 0
    except Exception as e:
        await session.rollback()
        logging.error(f"Error updating URL: {str(e)}")
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
    if not short_url or not short_url.strip():
        raise UrlValidationError(detail="Short URL cannot be empty")

    try:
        result = cast(CursorResult[Any], await session.execute(
            text("DELETE FROM short_urls WHERE url_key=:url_key"),
            {"url_key": short_url}
        ))
        await session.commit()
        return result.rowcount is not None and result.rowcount > 0
    except Exception as e:
        await session.rollback()
        logging.error(f"Error deleting URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting URL")

"""Business logic and database operations using raw SQL."""

import logging
from typing import Dict, List

import psycopg
from psycopg import errors as psycopg_errors
from starlette.exceptions import HTTPException

from shortener.database import Database


class UrlNotFoundException(HTTPException):
    """Exception raised when a URL is not found (404)."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=404, detail=detail)


class UrlValidationError(HTTPException):
    """Exception raised for invalid URL input (400)."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=400, detail=detail)


def _validate_short_url(short_url: str) -> None:
    """Raise UrlValidationError if short_url is empty."""
    if not short_url:
        raise UrlValidationError(detail="Short URL cannot be empty")


async def check_db_up(db: Database) -> bool:
    """Check connectivity to the database."""
    try:
        await db.execute_one("SELECT 1")
        return True
    except (psycopg.OperationalError, psycopg.DatabaseError) as e:
        logging.error(f"Database connection error: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during database health check: {str(e)}")
        return False


async def get_url_target(short_url: str, db: Database) -> str:
    """
    Get the target URL for a given short URL key.

    Args:
        short_url: The short URL key to look up
        db: Database instance

    Returns:
        The target URL as a string

    Raises:
        UrlNotFoundException: If the short URL doesn't exist
    """
    _validate_short_url(short_url)

    try:
        result = await db.execute_one("SELECT target FROM short_urls WHERE url_key = %s", short_url)

        if result is None:
            raise UrlNotFoundException(detail=f"URL with key '{short_url}' not found")
        return result[0]
    except UrlNotFoundException:
        raise
    except (psycopg.OperationalError, psycopg.DatabaseError) as e:
        logging.error(f"Database error when retrieving URL: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    except Exception as e:
        logging.error(f"Unexpected error when retrieving URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_all_short_urls(db: Database) -> List[Dict[str, str]]:
    """
    Get all short URLs and their targets.

    Args:
        db: Database instance

    Returns:
        List of dictionaries containing short_url and target_url
    """
    try:
        results = await db.execute_all("SELECT url_key, target FROM short_urls ORDER BY created_at DESC")
        return [{"short_url": row[0], "target_url": row[1]} for row in results]
    except (psycopg.OperationalError, psycopg.DatabaseError) as e:
        logging.error(f"Database error retrieving all URLs: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    except Exception as e:
        logging.error(f"Unexpected error retrieving all URLs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving URLs")


async def create_url_target(short_url: str, target_url: str, db: Database) -> bool:
    """
    Create a new short URL mapping.

    Args:
        short_url: The short URL key to create
        target_url: The target URL it should redirect to
        db: Database instance

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
        await db.execute(
            "INSERT INTO short_urls (url_key, target) VALUES (%s, %s)",
            short_url,
            target_url,
        )
        return True
    except psycopg_errors.UniqueViolation:
        # URL key already exists
        return False
    except (psycopg.OperationalError, psycopg.DatabaseError) as e:
        logging.error(f"Database error creating URL: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    except Exception as e:
        logging.error(f"Unexpected error creating URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating URL")


async def update_url_target(short_url: str, new_target_url: str, db: Database) -> bool:
    """
    Update an existing short URL mapping.

    Args:
        short_url: The short URL key to update
        new_target_url: The new target URL
        db: Database instance

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
        async with db.get_connection() as conn:
            result = await conn.execute(
                "UPDATE short_urls SET target = %s WHERE url_key = %s",
                (new_target_url, short_url),  # type: ignore[arg-type]
            )
            return result.rowcount > 0
    except (psycopg.OperationalError, psycopg.DatabaseError) as e:
        logging.error(f"Database error updating URL: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    except Exception as e:
        logging.error(f"Unexpected error updating URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating URL")


async def delete_url_target(short_url: str, db: Database) -> bool:
    """
    Delete a short URL mapping.

    Args:
        short_url: The short URL key to delete
        db: Database instance

    Returns:
        True if URL was deleted, False if URL doesn't exist

    Raises:
        HTTPException: For database errors
    """
    _validate_short_url(short_url)

    try:
        async with db.get_connection() as conn:
            result = await conn.execute(
                "DELETE FROM short_urls WHERE url_key = %s",
                (short_url,),  # type: ignore[arg-type]
            )
            return result.rowcount > 0
    except (psycopg.OperationalError, psycopg.DatabaseError) as e:
        logging.error(f"Database error deleting URL: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    except Exception as e:
        logging.error(f"Unexpected error deleting URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting URL")

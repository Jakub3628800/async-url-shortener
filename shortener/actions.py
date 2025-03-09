import asyncpg
import logging
from typing import Dict, List, Any
from starlette.exceptions import HTTPException


class UrlNotFoundException(HTTPException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["status_code"] = 404
        super().__init__(*args, **kwargs)


class UrlValidationError(HTTPException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["status_code"] = 400
        super().__init__(*args, **kwargs)


async def check_db_up(connection: asyncpg.Connection) -> bool:
    """Check connectivity to the database."""
    try:
        query_result = await connection.fetchval("SELECT 1;")
        return query_result == 1
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        return False


async def get_url_target(short_url: str, connection: asyncpg.Connection) -> str:
    """
    Get the target URL for a given short URL key.

    Args:
        short_url: The short URL key to look up
        connection: Database connection

    Returns:
        The target URL as a string

    Raises:
        UrlNotFoundException: If the short URL doesn't exist
    """
    if not short_url:
        raise UrlValidationError(detail="Short URL cannot be empty")

    try:
        target = await connection.fetchval(
            "SELECT target from short_urls where url_key=$1;", short_url
        )
        if target is None:
            raise UrlNotFoundException(detail=f"URL with key '{short_url}' not found")
        return target
    except asyncpg.exceptions.PostgresError as e:
        logging.error(f"Database error when retrieving URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise UrlNotFoundException(detail=f"URL with key '{short_url}' not found")


async def get_all_short_urls(connection: asyncpg.Connection) -> List[Dict[str, str]]:
    """
    Get all short URLs and their targets.

    Args:
        connection: Database connection

    Returns:
        List of dictionaries containing short_url and target_url
    """
    try:
        records = await connection.fetch("SELECT url_key, target from short_urls;")
        return [{"short_url": record["url_key"], "target_url": record["target"]} for record in records]
    except Exception as e:
        logging.error(f"Error retrieving all URLs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving URLs")


async def create_url_target(
    short_url: str, target_url: str, connection: asyncpg.Connection
) -> bool:
    """
    Create a new short URL mapping.

    Args:
        short_url: The short URL key to create
        target_url: The target URL it should redirect to
        connection: Database connection

    Returns:
        True if successful, False if URL already exists

    Raises:
        HTTPException: For database errors
        UrlValidationError: For invalid input
    """
    if not short_url:
        raise UrlValidationError(detail="Short URL cannot be empty")
    if not target_url:
        raise UrlValidationError(detail="Target URL cannot be empty")

    try:
        await connection.execute(
            "INSERT INTO short_urls (url_key, target) VALUES ($1,$2);",
            short_url,
            target_url,
        )
        return True
    except asyncpg.exceptions.UniqueViolationError:
        return False
    except Exception as e:
        logging.error(f"Error creating URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating URL")


async def update_url_target(
    short_url: str, new_target_url: str, connection: asyncpg.Connection
) -> bool:
    """
    Update an existing short URL mapping.

    Args:
        short_url: The short URL key to update
        new_target_url: The new target URL
        connection: Database connection

    Returns:
        True if URL was updated, False if URL doesn't exist

    Raises:
        HTTPException: For database errors
        UrlValidationError: For invalid input
    """
    if not short_url:
        raise UrlValidationError(detail="Short URL cannot be empty")
    if not new_target_url:
        raise UrlValidationError(detail="Target URL cannot be empty")

    try:
        result = await connection.execute(
            "UPDATE short_urls SET target = $1 WHERE url_key = $2;",
            new_target_url,
            short_url,
        )
        # Check if any row was updated
        return "UPDATE 1" in result
    except Exception as e:
        logging.error(f"Error updating URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating URL")


async def delete_url_target(short_url: str, connection: asyncpg.Connection) -> bool:
    """
    Delete a short URL mapping.

    Args:
        short_url: The short URL key to delete
        connection: Database connection

    Returns:
        True if URL was deleted, False if URL doesn't exist

    Raises:
        HTTPException: For database errors
    """
    if not short_url:
        raise UrlValidationError(detail="Short URL cannot be empty")

    try:
        result = await connection.execute(
            "DELETE FROM short_urls WHERE url_key=$1;", short_url
        )
        # Check if any row was deleted
        return "DELETE 1" in result
    except Exception as e:
        logging.error(f"Error deleting URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting URL")

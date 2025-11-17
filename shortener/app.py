import contextlib
import logging
import os
from typing import AsyncGenerator, Union

import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount
from starlette.routing import Route

from shortener.actions import UrlNotFoundException, UrlValidationError, check_db_up
from shortener.database import Database, get_database
from shortener.models import CREATE_TABLE_SQL, CREATE_INDEX_SQL
from shortener.settings import PostgresSettings, AppSettings
from shortener.views import ping, status, redirect_url, url_routes


routes = [
    Route("/ping", ping),
    Route("/status", status),
    Route("/{short_url:str}", redirect_url),
    Mount("/urls", routes=url_routes),
]


def _create_error_handler(error_name: str, status_code: int):
    """Create an error handler for a specific status code."""

    async def error_handler(request: Request, exc: Exception) -> JSONResponse:
        detail = getattr(exc, "detail", error_name)
        if status_code == 500:
            logging.error(f"Server error: {detail}")
        return JSONResponse({"error": error_name, "detail": detail}, status_code=status_code)

    return error_handler


server_error = _create_error_handler("Internal server error", 500)
not_found = _create_error_handler("Not found", 404)
validation_error = _create_error_handler("Validation error", 400)


async def initialize_database(db: Database) -> bool:
    """Initialize database schema and verify connection."""
    try:
        # Create table and index
        async with db.get_connection() as conn:
            await conn.execute(CREATE_TABLE_SQL)
            await conn.execute(CREATE_INDEX_SQL)
        logging.info("Database tables initialized successfully")

        # Verify connection
        if not await check_db_up(db):
            logging.error("Database health check failed")
            return False
        return True
    except Exception as e:
        logging.error(f"Database initialization error: {str(e)}")
        return False


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup/shutdown events."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load settings
    db_settings = PostgresSettings()
    app_settings = AppSettings()

    try:
        logging.info("Initializing database connection")
        db = get_database(db_settings)

        # Connect to database
        await db.connect()

        # Store database in app state
        app.state.db = db

        # Store settings in app state
        app.state.settings = app_settings

        # Initialize schema and verify connection
        if not await initialize_database(db):
            logging.error("Failed to initialize database")
        else:
            logging.info("Database connection established")

        yield

        # Cleanup
        await db.disconnect()
        logging.info("Application shutdown, database connection closed")
    except Exception as e:
        logging.error(f"Error during application startup: {str(e)}")
        raise


# Get debug mode from environment with default to False for production safety
debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Define exception handlers with proper type annotations
exception_handlers = {
    HTTPException: server_error,
    UrlNotFoundException: not_found,
    UrlValidationError: validation_error,
}

app = Starlette(
    debug=debug_mode,
    routes=routes,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)


def main():
    port: Union[str, int] = os.getenv("APPLICATION_PORT", 8000)
    host: str = os.getenv("APPLICATION_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=int(port), loop="uvloop")


if __name__ == "__main__":
    main()

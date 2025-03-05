import contextlib
import logging
import os
import typing

import asyncpg
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

from shortener.actions import UrlNotFoundException, UrlValidationError
from shortener.settings import PostgresSettings, AppSettings
from shortener.views.basic import ping
from shortener.views.basic import status
from shortener.views.redirect import redirect_url
from shortener.views.swagger import openapi_schema
from shortener.views.swagger import swaggerui
from shortener.views.urls import routes as url_routes


routes = [
    Route("/ping", ping),
    Route("/status", status),
    Route("/_schema", endpoint=openapi_schema, include_in_schema=False),
    Route("/", endpoint=swaggerui),
    Route("/{short_url:str}", redirect_url),
    Mount("/urls", routes=url_routes),
    Mount("/static", StaticFiles(directory="static"), name="static"),
]


async def server_error(request, exc):
    """Handle 500 server errors."""
    error_msg = str(exc) if hasattr(exc, "__str__") else "Internal server error"
    logging.error(f"Server error: {error_msg}")
    return JSONResponse(
        {"error": "Internal server error", "detail": error_msg},
        status_code=500
    )


async def not_found(request, exc):
    """Handle 404 not found errors."""
    detail = exc.detail if hasattr(exc, "detail") else "Resource not found"
    return JSONResponse(
        {"error": "Not found", "detail": detail},
        status_code=404
    )


async def validation_error(request, exc):
    """Handle 400 validation errors."""
    detail = exc.detail if hasattr(exc, "detail") else "Validation error"
    return JSONResponse(
        {"error": "Validation error", "detail": detail},
        status_code=400
    )


exception_handlers = {
    HTTPException: server_error,
    UrlNotFoundException: not_found,
    UrlValidationError: validation_error
}


async def check_database(pool):
    """Verify database connection is working."""
    try:
        async with pool.acquire() as connection:
            if not await connection.fetchval("SELECT 1"):
                logging.error("Database health check failed")
                return False
        return True
    except Exception as e:
        logging.error(f"Database health check error: {str(e)}")
        return False


@contextlib.asynccontextmanager
async def lifespan(app: typing.Any) -> typing.AsyncGenerator:
    """Application lifespan context manager for startup/shutdown events."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Load settings
    db_settings = dict(PostgresSettings())
    app_settings = AppSettings()

    # Configure SSL if needed
    if os.getenv("ENV") == "HEROKU" or db_settings.get("ssl"):
        db_settings["ssl"] = "require"

    try:
        logging.info("Initializing database connection pool")
        async_pool = asyncpg.create_pool(**db_settings)

        async with async_pool as pool:
            app.pool = pool

            # Verify database connection
            if not await check_database(pool):
                logging.error("Failed to connect to database")
            else:
                logging.info("Database connection established")

            # Store settings in app state
            app.settings = app_settings

            yield

        logging.info("Application shutdown, connection pool closed")
    except Exception as e:
        logging.error(f"Error during application startup: {str(e)}")
        raise


# Get debug mode from environment with default to False for production safety
debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

app = Starlette(
    debug=debug_mode,
    routes=routes,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)

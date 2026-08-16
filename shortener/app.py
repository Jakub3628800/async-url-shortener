import contextlib
import logging
import os
from collections.abc import AsyncGenerator

import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from shortener.actions import check_db_up
from shortener.database import Database, get_database
from shortener.models import CREATE_INDEX_SQL, CREATE_TABLE_SQL
from shortener.settings import AppSettings, PostgresSettings
from shortener.views import ping, redirect_url, status, url_routes

logger = logging.getLogger(__name__)

routes = [
    Route("/ping", ping),
    Route("/status", status),
    Route("/{short_url:str}", redirect_url),
    Mount("/urls", routes=url_routes),
]


async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
    """Render expected HTTP errors without changing their status codes."""
    error_names = {
        400: "Validation error",
        404: "Not found",
        409: "Conflict",
        413: "Request too large",
        503: "Service unavailable",
    }
    error_name = error_names.get(exc.status_code, "Request error")
    return JSONResponse({"error": error_name, "detail": exc.detail}, status_code=exc.status_code)


async def server_error(request: Request, exc: Exception) -> JSONResponse:
    """Render unexpected errors without exposing internal details."""
    logger.error("Request failed with an internal server error")
    return JSONResponse(
        {"error": "Internal server error", "detail": "Internal server error"},
        status_code=500,
    )


async def initialize_database(db: Database) -> bool:
    """Initialize database schema and verify connection."""
    async with db.get_connection() as conn:
        await conn.execute(CREATE_TABLE_SQL)
        await conn.execute(CREATE_INDEX_SQL)
    logger.info("Database tables initialized successfully")

    if not await check_db_up(db):
        logger.error("Database health check failed")
        return False
    return True


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[None]:
    """Application lifespan context manager for startup/shutdown events."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load settings
    db_settings = PostgresSettings()
    app_settings = AppSettings()

    logger.info("Initializing database connection")
    db = get_database(db_settings)
    await db.connect()

    app.state.db = db
    app.state.settings = app_settings

    if not await initialize_database(db):
        await db.disconnect()
        raise RuntimeError("Failed to initialize database")
    logger.info("Database connection established")

    try:
        yield
    finally:
        await db.disconnect()
        logger.info("Application shutdown, database connection closed")


# Get debug mode from environment with default to False for production safety
debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Define exception handlers with proper type annotations
exception_handlers = {
    HTTPException: http_error,
    Exception: server_error,
}

app = Starlette(
    debug=debug_mode,
    routes=routes,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
    max_body_size=16 * 1024,
)


def main() -> None:
    port = os.getenv("APPLICATION_PORT", "8000")
    host: str = os.getenv("APPLICATION_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=int(port), loop="uvloop")


if __name__ == "__main__":
    main()

import contextlib
import logging
import os
from typing import Dict, Any, Callable, AsyncGenerator, Union, cast

import uvicorn
from sqlalchemy import select
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

from shortener.actions import UrlNotFoundException, UrlValidationError
from shortener.database import create_engine, create_session_factory, get_session
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


async def server_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle 500 server errors."""
    error_msg = str(exc) if hasattr(exc, "__str__") else "Internal server error"
    logging.error(f"Server error: {error_msg}")
    return JSONResponse(
        {"error": "Internal server error", "detail": error_msg},
        status_code=500
    )


async def not_found(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle 404 not found errors."""
    detail = exc.detail if hasattr(exc, "detail") else "Resource not found"
    return JSONResponse(
        {"error": "Not found", "detail": detail},
        status_code=404
    )


async def validation_error(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle 400 validation errors."""
    detail = exc.detail if hasattr(exc, "detail") else "Validation error"
    return JSONResponse(
        {"error": "Validation error", "detail": detail},
        status_code=400
    )


async def check_database(session_factory) -> bool:
    """Verify database connection is working."""
    try:
        async with get_session(session_factory) as session:
            result = await session.execute(select(1))
            if not result.scalar():
                logging.error("Database health check failed")
                return False
        return True
    except Exception as e:
        logging.error(f"Database health check error: {str(e)}")
        return False


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup/shutdown events."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Load settings
    db_settings = PostgresSettings()
    app_settings = AppSettings()

    try:
        logging.info("Initializing database engine")
        engine = create_engine(db_settings)
        session_factory = create_session_factory(engine)

        # Store session factory in app state
        app.state.session_factory = session_factory

        # Store settings in app state
        app.state.settings = app_settings

        # Verify database connection
        if not await check_database(session_factory):
            logging.error("Failed to connect to database")
        else:
            logging.info("Database connection established")

        yield

        # Cleanup
        await engine.dispose()
        logging.info("Application shutdown, database engine disposed")
    except Exception as e:
        logging.error(f"Error during application startup: {str(e)}")
        raise


# Get debug mode from environment with default to False for production safety
debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Define exception handlers with proper type annotations
exception_handlers = {
    HTTPException: server_error,
    UrlNotFoundException: not_found,
    UrlValidationError: validation_error
}

app = Starlette(
    debug=debug_mode,
    routes=routes,
    lifespan=lifespan,
    exception_handlers=cast(Dict[Any, Callable], exception_handlers),
)


def main():
    port: Union[str, int] = os.getenv("APPLICATION_PORT", 8000)
    uvicorn.run(app, host="127.0.0.0", port=int(port), loop="uvloop")


if __name__ == "__main__":
    main()

import contextlib
import logging
import os
from typing import Dict, Any, Callable, AsyncGenerator, cast

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

from shortener.actions import UrlNotFoundException, UrlValidationError
from shortener.settings import DatabaseSettings, AppSettings
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


async def check_database(session_factory: async_sessionmaker[AsyncSession]) -> bool:
    """Verify database connection is working."""
    try:
        async with session_factory() as session:
            result = await session.execute(text("SELECT 1"))
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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    db_settings = DatabaseSettings()
    app_settings = AppSettings()

    try:
        logging.info(f"Initializing database connection using {db_settings.type}")

        engine = create_async_engine(
            db_settings.database_url,
            echo=app_settings.debug,
            pool_pre_ping=True,
        )

        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        app.state.engine = engine
        app.state.session_factory = session_factory

        if not await check_database(session_factory):
            logging.error("Failed to connect to database")
        else:
            logging.info("Database connection established")

        app.state.settings = app_settings

        yield

        logging.info("Application shutdown, closing database connections")
        await engine.dispose()

    except Exception as e:
        logging.error(f"Error during application startup: {str(e)}")
        raise


debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

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

from starlette.routing import Mount, Route
from shortener.actions import UrlNotFoundException
from shortener.database import create_db_pool, load_database_url, DatabaseConnector
import asyncpg
import asyncio
import databases
from shortener.views.basic import ping, status
from shortener.views.urls import routes as url_routes
from shortener.views.redirect import redirect_url

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException

routes = [
    Route("/ping", ping),
    Route("/status", status),
    Route("/{short_url:str}", redirect_url),
    Mount("/urls", routes=url_routes),
]


async def server_error(request, exc):
    return JSONResponse({"Internal server error": "ok"}, status_code=500)


async def not_found(request, exc):
    return JSONResponse({"Resource not found": "ok"}, status_code=404)


exception_handlers = {HTTPException: server_error, UrlNotFoundException: not_found}

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware import Middleware



app = Starlette(
        debug=True,
        routes=routes,
        on_startup=[],
        on_shutdown=[],
        exception_handlers=exception_handlers,
    )
app.database = DatabaseConnector()
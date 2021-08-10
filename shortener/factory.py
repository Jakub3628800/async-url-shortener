from starlette.routing import Mount, Route
from shortener.actions import UrlNotFoundException
from shortener.database import load_database_url
import asyncpg
from shortener.views.basic import ping, status
from shortener.views.urls import routes as url_routes
from shortener.views.redirect import redirect_url
import typing
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles
from shortener.views.swagger import openapi_schema, swaggerui


routes = [
    Route("/ping", ping),
    Route("/status", status),
    Route("/_schema", endpoint=openapi_schema, include_in_schema=False),
    Route("/_swaggerui", endpoint=swaggerui),
    Route("/{short_url:str}", redirect_url),
    Mount("/urls", routes=url_routes),
    Mount("/static", StaticFiles(directory="static"), name="static"),
]


async def server_error(request, exc):
    return JSONResponse({"Internal server error": "ok"}, status_code=500)


async def not_found(request, exc):
    return JSONResponse({"Resource not found": "ok"}, status_code=404)


exception_handlers = {HTTPException: server_error, UrlNotFoundException: not_found}


async def lifespan(app: typing.Any) -> typing.AsyncGenerator:
    async with asyncpg.create_pool(dsn=load_database_url().get_secret_value(), min_size=5, max_size=25) as pool:
        app.pool = pool
        yield


app = Starlette(
    debug=True,
    routes=routes,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)

import os
import typing

import asyncpg
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

from shortener.actions import UrlNotFoundException
from shortener.settings import PostgresSettings
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
    return JSONResponse({"Internal server error": "ok"}, status_code=500)


async def not_found(request, exc):
    return JSONResponse({"Resource not found": "ok"}, status_code=404)


exception_handlers = {HTTPException: server_error, UrlNotFoundException: not_found}


async def lifespan(app: typing.Any) -> typing.AsyncGenerator:

    settings = dict(PostgresSettings())
    if os.getenv("ENV") == "HEROKU":
        settings["ssl"] = "require"

    async_pool = asyncpg.create_pool(min_size=5, max_size=25, **settings)
    async with async_pool as pool:
        app.pool = pool
        yield


app = Starlette(
    debug=True,
    routes=routes,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)

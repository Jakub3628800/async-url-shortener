from starlette.routing import Mount, Route
from shortener.actions import UrlNotFoundException
from shortener.database import set_up_postgres_connection, tear_down_postgres_connection
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


def create_app():
    """Create application object."""
    return Starlette(
        debug=True,
        routes=routes,
        on_startup=[set_up_postgres_connection],
        on_shutdown=[tear_down_postgres_connection],
        exception_handlers=exception_handlers,
    )

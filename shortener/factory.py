from starlette.applications import Starlette
from starlette.routing import Route, Mount
from shortener.views.urls import routes as room_routes
from shortener.views.basic import ping, status
from shortener.database import set_up_postgres_connection, tear_down_postgres_connection

routes = [
        Route("/ping", ping),
        Route("/status", status),
        Mount("/rooms", routes=room_routes)
    ]




def create_app():

    return Starlette(
        debug=True,
        routes=routes,
        on_startup=[set_up_postgres_connection],
        on_shutdown=[tear_down_postgres_connection]
    )
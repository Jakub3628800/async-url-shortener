from starlette.applications import Starlette
from starlette.routing import Route, Mount
from shortener.views.urls import routes as room_routes
from shortener.views.basic import ping, status



routes = [
        Route("/ping", ping),
        Route("/status", status),
        Mount("/rooms", routes=room_routes)
    ]

def create_app():

    return Starlette(
        debug=True,
        routes=routes,
    )
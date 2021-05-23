from starlette.responses import JSONResponse
from starlette.routing import Route
from shortener.database import postgres_connection
from shortener.actions import get_url_target, create_url_target, update_url_target, delete_url_target, get_all


async def get_url(request):
    """Get room by a name."""
    short_url = request.get("path_params", {}).get("short_url")

    target_url = await get_url_target(short_url)
    all_urls = await get_all(short_url)
    return JSONResponse(content={"short_url": short_url, "target_url": target_url})


async def create_url(request):
    """Get room by a name."""
    body = await request.json()
    short_url = body.get("short_url")
    target_url = body.get("target")

    resp = await create_url_target(short_url=short_url, target_url=target_url)

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=201)


async def update_url(request):
    """Get room by a name."""
    return JSONResponse({})


async def delete_url(request):
    """Get room by a name."""
    return JSONResponse({})


routes = [
    Route("/{short_url}", get_url, methods=["GET"]),
    Route("/", create_url, methods=["POST"]),
    Route("/{short_url}", update_url, methods=["PUT"]),
    Route("/{short_url}", delete_url, methods=["DELETE"]),
]

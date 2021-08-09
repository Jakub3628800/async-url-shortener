"""Endpoints for editing short_url: target mappings."""
from starlette.responses import JSONResponse
from starlette.routing import Route
from shortener.actions import get_url_target, create_url_target, update_url_target, delete_url_target


async def get_url(request):
    """Get room by a name."""
    short_url = request.get("path_params", {}).get("short_url")

    async with request.app.pool.acquire() as connection:
        target_url = await get_url_target(short_url, connection)

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=200)


async def create_url(request):
    """Get room by a name."""
    body = await request.json()
    short_url = body.get("short_url")
    target_url = body.get("target_url")

    async with request.app.database.connection() as connection:
        await create_url_target(short_url=short_url, target_url=target_url, connection=connection)

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=201)


async def update_url(request):
    """Get room by a name."""
    body = await request.json()
    short_url = body.get("short_url")
    target_url = body.get("target_url")

    async with request.app.database.connection() as connection:
        await update_url_target(short_url=short_url, new_target_url=target_url, connection=connection)

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=200)


async def delete_url(request):
    """Get room by a name."""
    short_url = request.get("path_params", {}).get("short_url")

    async with request.app.database.connection() as connection:
        await delete_url_target(short_url, connection)

    return JSONResponse({}, status_code=204)


routes = [
    Route("/{short_url}", get_url, methods=["GET"]),
    Route("/", create_url, methods=["POST"]),
    Route("/{short_url}", update_url, methods=["PUT"]),
    Route("/{short_url}", delete_url, methods=["DELETE"]),
]

"""Endpoints for editing short_url: target mappings."""
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from shortener.actions import create_url_target
from shortener.actions import delete_url_target
from shortener.actions import get_url_target
from shortener.actions import update_url_target


async def get_url(request: Request):
    """
    summary: Get a short_url and its target from the database.
    parameters:
        - name: short_url
          in: path
          required: true
          schema:
            type : string
    responses:
      200:
        examples:
          {"short_url": "testurl", "target_url": "https://wikipedia.com"}
    """
    short_url = request.get("path_params", {}).get("short_url")

    async with request.app.pool.acquire() as connection:
        target_url = await get_url_target(short_url, connection)

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=200)


async def create_url(request: Request):
    """
    summary: Create a short_url in the database.
    parameters:
        - name: short_url
          in: body
          required: true
          schema:
            type : object
            required:
                - short_url
                - target_url
            properties:
                short_url:
                    type: string
                    example: wkp
                target_url:
                    type: string
                    example: www.wikipedia.org

    responses:
      201:
        description: Create short_url stored in database.
        examples:
          {"short_url": "testurl", "target_url": "https://wikipedia.com"}
    """
    body = await request.json()
    short_url = body.get("short_url")
    target_url = body.get("target_url")
    async with request.app.pool.acquire() as connection:
        await create_url_target(short_url=short_url, target_url=target_url, connection=connection)

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=201)


async def update_url(request: Request):
    """
    summary: Update a short_url in the database.
    parameters:
        - name: short_url
          in: body
          required: true
          schema:
            type : string

        - name: target_url
          in: body
          required: true
          schema:
            type : string
    responses:
      200:
        description: Update short_url stored in database.
        examples:
          {"short_url": "testurl", "target_url": "https://wikipedia.com"}
    """
    body = await request.json()
    short_url = body.get("short_url")
    target_url = body.get("target_url")

    async with request.app.pool.acquire() as connection:
        await update_url_target(short_url=short_url, new_target_url=target_url, connection=connection)

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=200)


async def delete_url(request: Request):
    """
    summary: Delete a short_url from the database.
    responses:
      204:
        examples:
          {}
    """
    short_url = request.get("path_params", {}).get("short_url")

    async with request.app.pool.acquire() as connection:
        await delete_url_target(short_url, connection)

    return JSONResponse({}, status_code=204)


routes = [
    Route("/{short_url}", get_url, methods=["GET"]),
    Route("/", create_url, methods=["POST"]),
    Route("/{short_url}", update_url, methods=["PUT"]),
    Route("/{short_url}", delete_url, methods=["DELETE"]),
]

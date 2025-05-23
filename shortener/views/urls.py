"""Endpoints for editing short_url: target mappings."""

import logging
import re

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from shortener.actions import (
    UrlValidationError,
    create_url_target,
    delete_url_target,
    get_all_short_urls,
    get_url_target,
    update_url_target,
)


def validate_url(url: str, max_length: int = 2048) -> bool:
    """
    Validate that a URL is properly formatted.

    Args:
        url: The URL to validate
        max_length: Maximum allowed length

    Returns:
        True if URL is valid, False otherwise
    """
    if not url or len(url) > max_length:
        return False

    # Basic URL validation regex
    url_pattern = re.compile(
        r'^(https?|ftp)://'  # scheme
        r'([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?'  # domain
        r'(/[^/\s]*)*$'  # path
    )

    return bool(url_pattern.match(url))


def validate_key(key: str, max_length: int = 50) -> bool:
    """
    Validate that a URL key is properly formatted.

    Args:
        key: The URL key to validate
        max_length: Maximum allowed length

    Returns:
        True if key is valid, False otherwise
    """
    if not key or len(key) > max_length:
        return False

    # Only allow alphanumeric characters, hyphens and underscores
    key_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
    return bool(key_pattern.match(key))


async def get_url(request: Request) -> JSONResponse:
    """
    summary: Get a short_url and its target from the database.
    parameters:
        - name: short_url
          in: path
          required: true
          schema:
            type: string
    responses:
      200:
        description: Short URL and its target
        content:
          application/json:
            schema:
              type: object
              properties:
                short_url:
                  type: string
                target_url:
                  type: string
            example:
              {"short_url": "testurl", "target_url": "https://wikipedia.com"}
      404:
        description: URL not found
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                detail:
                  type: string
    """
    short_url = request.path_params.get("short_url", "")

    if not validate_key(short_url):
        raise UrlValidationError(detail=f"Invalid URL key format: {short_url}")

    async with request.app.state.pool.acquire() as connection:
        target_url = await get_url_target(short_url, connection)
        if not target_url:
            raise HTTPException(status_code=404, detail=f"URL with key '{short_url}' not found")

    return JSONResponse(
        content={"short_url": short_url, "target_url": target_url}, status_code=200
    )


async def list_urls(request: Request) -> JSONResponse:
    """
    summary: List all short URLs
    responses:
      200:
        description: List of all short URLs and their targets
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  short_url:
                    type: string
                  target_url:
                    type: string
    """
    async with request.app.state.pool.acquire() as connection:
        urls = await get_all_short_urls(connection)

    return JSONResponse(content=urls, status_code=200)


async def create_url(request: Request) -> JSONResponse:
    """
    summary: Create a short_url in the database.
    requestBody:
      description: Short URL data
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - short_url
              - target_url
            properties:
              short_url:
                type: string
                example: wkp
              target_url:
                type: string
                example: https://www.wikipedia.org
    responses:
      201:
        description: Short URL created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                short_url:
                  type: string
                target_url:
                  type: string
            example:
              {"short_url": "wkp", "target_url": "https://www.wikipedia.org"}
      400:
        description: Validation error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                detail:
                  type: string
      409:
        description: URL already exists
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                detail:
                  type: string
    """
    try:
        body = await request.json()
    except Exception as e:
        logging.error(f"Invalid JSON in request: {str(e)}")
        raise UrlValidationError(detail="Invalid JSON in request body")

    short_url = body.get("short_url", "")
    target_url = body.get("target_url", "")

    # Validate inputs
    if not short_url:
        raise UrlValidationError(detail="short_url is required")
    if not target_url:
        raise UrlValidationError(detail="target_url is required")

    # Check URL format
    if not validate_key(short_url):
        raise UrlValidationError(detail=f"Invalid URL key format: {short_url}")
    if not validate_url(target_url):
        raise UrlValidationError(detail=f"Invalid target URL format: {target_url}")

    # Check URL length
    max_key_length = getattr(request.app.state.settings, "max_key_length", 50)
    max_url_length = getattr(request.app.state.settings, "max_url_length", 2048)
    if len(short_url) > max_key_length:
        raise UrlValidationError(detail=f"URL key exceeds maximum length of {max_key_length}")
    if len(target_url) > max_url_length:
        raise UrlValidationError(detail=f"Target URL exceeds maximum length of {max_url_length}")

    async with request.app.state.pool.acquire() as connection:
        success = await create_url_target(
            short_url=short_url, target_url=target_url, connection=connection
        )

        if not success:
            return JSONResponse(
                content={
                    "error": "Conflict",
                    "detail": f"URL with key '{short_url}' already exists"
                },
                status_code=409
            )

    return JSONResponse(
        content={"short_url": short_url, "target_url": target_url}, status_code=201
    )


async def update_url(request: Request) -> JSONResponse:
    """
    summary: Update a short_url in the database.
    parameters:
        - name: short_url
          in: path
          required: true
          schema:
            type: string
    requestBody:
      description: New target URL
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - target_url
            properties:
              target_url:
                type: string
                example: https://www.wikipedia.org/wiki/Python
    responses:
      200:
        description: Short URL updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                short_url:
                  type: string
                target_url:
                  type: string
            example:
              {"short_url": "wkp", "target_url": "https://www.wikipedia.org/wiki/Python"}
      400:
        description: Validation error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                detail:
                  type: string
      404:
        description: URL not found
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                detail:
                  type: string
    """
    short_url = request.path_params.get("short_url", "")

    if not validate_key(short_url):
        raise UrlValidationError(detail=f"Invalid URL key format: {short_url}")

    try:
        body = await request.json()
    except Exception as e:
        logging.error(f"Invalid JSON in request: {str(e)}")
        raise UrlValidationError(detail="Invalid JSON in request body")

    target_url = body.get("target_url")

    # Validate input
    if not target_url:
        raise UrlValidationError(detail="target_url is required")

    # Check URL format
    if not validate_url(target_url):
        raise UrlValidationError(detail=f"Invalid target URL format: {target_url}")

    # Check URL length
    max_url_length = getattr(request.app.state.settings, "max_url_length", 2048)
    if len(target_url) > max_url_length:
        raise UrlValidationError(detail=f"Target URL exceeds maximum length of {max_url_length}")

    async with request.app.state.pool.acquire() as connection:
        success = await update_url_target(
            short_url=short_url, new_target_url=target_url, connection=connection
        )

        if not success:
            raise HTTPException(status_code=404, detail=f"URL with key '{short_url}' not found")

    return JSONResponse(
        content={"short_url": short_url, "target_url": target_url}, status_code=200
    )


async def delete_url(request: Request) -> JSONResponse:
    """
    summary: Delete a short_url from the database.
    parameters:
        - name: short_url
          in: path
          required: true
          schema:
            type: string
    responses:
      204:
        description: Short URL deleted successfully
      400:
        description: Validation error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                detail:
                  type: string
      404:
        description: URL not found
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                detail:
                  type: string
    """
    short_url = request.path_params.get("short_url", "")

    if not validate_key(short_url):
        raise UrlValidationError(detail=f"Invalid URL key format: {short_url}")

    async with request.app.state.pool.acquire() as connection:
        success = await delete_url_target(short_url, connection)

        if not success:
            raise HTTPException(status_code=404, detail=f"URL with key '{short_url}' not found")

    return JSONResponse({}, status_code=204)


routes = [
    Route("/{short_url}", get_url, methods=["GET"]),
    Route("/", list_urls, methods=["GET"]),
    Route("/", create_url, methods=["POST"]),
    Route("/{short_url}", update_url, methods=["PUT"]),
    Route("/{short_url}", delete_url, methods=["DELETE"]),
]

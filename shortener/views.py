"""All HTTP endpoint handlers for the URL shortener."""

import logging
import re
from urllib.parse import urlparse

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route

from shortener.actions import (
    UrlValidationError,
    check_db_up,
    create_url_target,
    delete_url_target,
    get_all_short_urls,
    get_url_target,
    update_url_target,
)


# =============================================================================
# URL Validation
# =============================================================================

# Pre-compile regex for key validation
KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


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

    try:
        result = urlparse(url)
        # Validate scheme and netloc
        return bool(result.scheme in ("http", "https", "ftp") and result.netloc)
    except Exception:
        return False


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
    return bool(KEY_PATTERN.match(key))


def get_and_validate_short_url(request: Request) -> str:
    """Extract and validate short_url from path parameters."""
    short_url = request.path_params.get("short_url", "")
    if not validate_key(short_url):
        raise UrlValidationError(detail=f"Invalid URL key format: {short_url}")
    return short_url


# =============================================================================
# Basic Endpoints
# =============================================================================


async def ping(request: Request) -> JSONResponse:
    """
    summary: Ping Pong
    responses:
      200:
        examples:
            {"ping": "pong"}
    """
    return JSONResponse({"ping": "pong"})


async def status(request: Request) -> JSONResponse:
    """
    summary: Status request to check service has a connection to the database.
    responses:
      200:
        examples:
            {"db_up": "true"}
    """
    db_up_result = await check_db_up(request.app.state.db)
    db_up = "true" if db_up_result else "false"
    return JSONResponse({"db_up": db_up})


# =============================================================================
# Redirect Endpoint
# =============================================================================


async def redirect_url(request: Request) -> RedirectResponse:
    """
    summary: Redirect request to a target url.
    parameters:
        - name: short_url
          in: path
          required: true
          schema:
            type : string
    responses:
      307:
        description: Redirected to target url.
      404:
        description: Short URL not found.
      400:
        description: Invalid URL key format.
    """
    short_url = request.path_params.get("short_url", "")

    # Validate before database lookup
    if not validate_key(short_url):
        raise UrlValidationError(detail=f"Invalid URL key format: {short_url}")

    target_url = await get_url_target(short_url, request.app.state.db)
    return RedirectResponse(url=target_url)


# =============================================================================
# URL Management Endpoints (CRUD)
# =============================================================================


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
    short_url = get_and_validate_short_url(request)
    target_url = await get_url_target(short_url, request.app.state.db)

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=200)


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
    urls = await get_all_short_urls(request.app.state.db)
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

    # Validate URL format and length (validators check for empty values too)
    if not validate_key(short_url):
        raise UrlValidationError(detail=f"Invalid URL key format: {short_url}")
    if not validate_url(target_url):
        raise UrlValidationError(detail=f"Invalid target URL format: {target_url}")

    success = await create_url_target(short_url=short_url, target_url=target_url, db=request.app.state.db)

    if not success:
        return JSONResponse(
            content={
                "error": "Conflict",
                "detail": f"URL with key '{short_url}' already exists",
            },
            status_code=409,
        )

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=201)


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
    short_url = get_and_validate_short_url(request)

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

    success = await update_url_target(short_url=short_url, new_target_url=target_url, db=request.app.state.db)

    if not success:
        raise HTTPException(status_code=404, detail=f"URL with key '{short_url}' not found")

    return JSONResponse(content={"short_url": short_url, "target_url": target_url}, status_code=200)


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
    short_url = get_and_validate_short_url(request)
    success = await delete_url_target(short_url, request.app.state.db)

    if not success:
        raise HTTPException(status_code=404, detail=f"URL with key '{short_url}' not found")

    return JSONResponse({}, status_code=204)


# =============================================================================
# Routes
# =============================================================================

# URL management routes
url_routes = [
    Route("/{short_url}", get_url, methods=["GET"]),
    Route("/", list_urls, methods=["GET"]),
    Route("/", create_url, methods=["POST"]),
    Route("/{short_url}", update_url, methods=["PUT"]),
    Route("/{short_url}", delete_url, methods=["DELETE"]),
]

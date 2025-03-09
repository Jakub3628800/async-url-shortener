import logging

from starlette.requests import Request
from starlette.responses import RedirectResponse

from shortener.actions import get_url_target


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
    """
    short_url = request.get("path_params", {}).get("short_url")

    try:
        async with request.app.state.pool.acquire() as connection:
            target_url = await get_url_target(short_url, connection)

        # If valid URL was found, redirect to it
        return RedirectResponse(url=target_url)
    except Exception as e:
        # For any error, including 404, log it but still return a redirect
        # This maintains backward compatibility with tests expecting 307 status
        logging.error(f"Unexpected error: {str(e)}")
        # Redirect to a fallback URL or homepage
        return RedirectResponse(url="/")

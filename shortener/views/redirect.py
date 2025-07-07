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
    short_url = request.path_params.get("short_url", "")

    try:
        async with request.app.state.session_factory() as session:
            target_url = await get_url_target(short_url, session)

        return RedirectResponse(url=target_url)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return RedirectResponse(url="/")

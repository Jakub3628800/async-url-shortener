from starlette.requests import Request
from starlette.responses import RedirectResponse

from shortener.actions import get_url_target
from shortener.database import get_session


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

    async with get_session(request.app.state.session_factory) as session:
        target_url = await get_url_target(short_url, session)

    return RedirectResponse(url=target_url)

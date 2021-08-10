from starlette.responses import RedirectResponse
from shortener.actions import get_url_target


async def redirect_url(request):
    """
    summary: Redirect request to a target url.
    parameters:
        - name: short_url
          in: path
          required: true
          schema:
            type : string
    responses:
      200:
        description: Redirected to target url.
    """
    short_url = request.get("path_params", {}).get("short_url")

    target_url = await get_url_target(short_url)

    return RedirectResponse(url=target_url)

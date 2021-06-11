from starlette.responses import RedirectResponse
from shortener.actions import get_url_target


async def redirect_url(request):
    """Status request to check service has a connection to the database."""
    short_url = request.get("path_params", {}).get("short_url")

    target_url = await get_url_target(short_url)

    return RedirectResponse(url=target_url)

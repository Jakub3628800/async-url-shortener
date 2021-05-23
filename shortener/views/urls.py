from starlette.responses import JSONResponse
from starlette.routing import Route


async def get_urls(request):
    """Get room by a name"""
    return JSONResponse({})




routes = [
    Route('/{room_name}', get_urls, methods=['GET'])
]
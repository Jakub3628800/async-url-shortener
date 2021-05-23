from starlette.responses import JSONResponse


async def ping(request):
    return JSONResponse({'ping': 'pong'})


async def status(request):
    db_up = "true"

    return JSONResponse({'db_up': db_up})
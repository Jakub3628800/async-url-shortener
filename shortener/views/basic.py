from starlette.responses import JSONResponse
from shortener.database import postgres_connection

async def ping(request):
    return JSONResponse({'ping': 'pong'})


async def status(request):
    db_up = "true"
    try:
        result = await postgres_connection.fetch_val("SELECT 1;")
        assert result == 1
    except:
        db_up = "false"
    return JSONResponse({'db_up': db_up})
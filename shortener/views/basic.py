from starlette.responses import JSONResponse

from shortener.database import postgres_connection


async def ping(request):
    """Ping request to check availability of the service."""
    return JSONResponse({"ping": "pong"})


async def status(request):
    """Status request to check service has a connection to the database."""
    db_up = "true"
    try:
        result = await postgres_connection.fetch_val("SELECT 1;")
        assert result == 1
    except Exception:
        db_up = "false"
    return JSONResponse({"db_up": db_up})

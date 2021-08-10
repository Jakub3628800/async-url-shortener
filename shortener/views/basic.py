from starlette.responses import JSONResponse
import asyncpg


async def ping(request):
    """
    summary: Ping Pong
    responses:
      200:
        examples:
            {"ping": "pong"}
    """
    return JSONResponse({"ping": "pong"})


async def check_db_up(connection: asyncpg.Connection) -> bool:
    """Check connectivity to the database."""
    try:
        query_result = await connection.fetchval("SELECT 1;")
        return query_result == 1
    except Exception:
        pass
    return False


async def status(request):
    """
    summary: Status request to check service has a connection to the database.
    responses:
      200:
        examples:
            {"db_up": "true"}
    """
    async with request.app.pool.acquire() as connection:
        db_up_result = await check_db_up(connection)

    db_up = "true" if db_up_result else "false"
    return JSONResponse({"db_up": db_up})

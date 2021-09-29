from starlette.responses import JSONResponse
from shortener.actions import check_db_up
from starlette.requests import Request


async def ping(request: Request):
    """
    summary: Ping Pong
    responses:
      200:
        examples:
            {"ping": "pong"}
    """
    return JSONResponse({"ping": "pong"})


async def status(request: Request):
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

from starlette.exceptions import HTTPException
import asyncpg


class UrlNotFoundException(HTTPException):
    def __init__(self, *args, **kwargs):
        kwargs["status_code"] = 404
        super().__init__(*args, **kwargs)


async def get_url_target(short_url: str, connection) -> str:
    try:
        return await connection.fetchval("SELECT target from short_urls where url_key=$1;", short_url)
    except Exception:
        raise UrlNotFoundException()


async def get_all_short_urls(connection):
    await connection.fetch_all(query="SELECT * from short_urls;")


async def create_url_target(short_url: str, target_url: str, connection):
    try:
        await connection.execute("INSERT INTO short_urls (url_key, target) VALUES ($1,$2);", short_url, target_url)
    except asyncpg.exceptions.UniqueViolationError:
        pass
    return


async def update_url_target(short_url: str, new_target_url: str, connection):
    return await connection.fetchval("UPDATE short_urls SET target = $1 WHERE url_key = $2;", new_target_url, short_url)


async def delete_url_target(short_url: str, connection):
    return await connection.fetchval("delete from short_urls where url_key=$1;", short_url)

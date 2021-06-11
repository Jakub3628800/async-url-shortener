from shortener.database import postgres_connection
from starlette.exceptions import HTTPException


class UrlNotFoundException(HTTPException):
    def __init__(self, *args, **kwargs):
        kwargs["status_code"] = 404
        super().__init__(*args, **kwargs)


async def get_url_target(short_url: str):
    try:
        return await postgres_connection.fetch_val(
            query="SELECT target from short_urls where url_key=:url_key;", values={"url_key": short_url}
        )
    except Exception:
        raise UrlNotFoundException()


async def get_all_short_urls(short_url: str):
    await postgres_connection.fetch_all(query="SELECT * from short_urls;")


async def create_url_target(short_url: str, target_url: str):
    return await postgres_connection.execute(
        query="INSERT INTO short_urls (url_key, target) VALUES (:url_key,:target);",
        values={"url_key": short_url, "target": target_url},
    )


async def update_url_target(short_url: str, new_target_url: str):
    return await postgres_connection.fetch_one(
        query="UPDATE short_urls SET target = :target WHERE short_url = :short_url;",
        values={"url_key": short_url, "target": new_target_url},
    )


async def delete_url_target(short_url: str):
    return await postgres_connection.fetch_one(
        query="delete from short_urls where url_key=:url_key;", values={"url_key": short_url}
    )

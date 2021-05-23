from shortener.database import postgres_connection


class UrlNotFoundException:
    pass


async def get_url_target(short_url: str):
    try:
        return await postgres_connection.fetch_val(
            query="SELECT target from short_urls where url_key=:url_key;", values={"url_key": short_url}
        )
    except Exception:
        return UrlNotFoundException()


async def get_all(short_url: str):
    try:
        a = await postgres_connection.fetch_all(query="SELECT * from short_urls;")
        print(a)
    except Exception:
        return UrlNotFoundException()


async def create_url_target(short_url, target_url):
    try:
        return await postgres_connection.execute(
            query="INSERT INTO short_urls (url_key, target) VALUES (:url_key,:target);",
            values={"url_key": short_url, "target": target_url},
        )
    except Exception:
        return UrlNotFoundException()


async def update_url_target(short_url, new_target_url):
    try:
        return await postgres_connection.fetch_one(
            query="UPDATE short_urls SET target = :target WHERE short_url = :short_url;",
            values={"url_key": short_url, "target": new_target_url},
        )
    except Exception:
        return UrlNotFoundException()


async def delete_url_target(short_url, new_target_url):
    try:
        return await postgres_connection.fetch_one(
            query="delete from short_urls where url_key=:url_key;", values={"url_key": short_url}
        )
    except Exception:
        return UrlNotFoundException()

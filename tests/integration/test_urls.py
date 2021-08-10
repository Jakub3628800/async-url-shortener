import pytest


def add_short_url(short_url, target_url, connection):
    connection.execute(
        "INSERT INTO short_urls (url_key, target) VALUES (%(a)s, %(b)s) on conflict do nothing;",
        {"a": short_url, "b": target_url},
    )


short_urls = [
    ("test1", "test1_short"),
    ("test2", "test1_short"),
    ("test3", "test1_short"),
    ("test4", "test1_short"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("short_url,target", short_urls)
def test_get_url(test_client, short_url, target, psycopg2_cursor):
    add_short_url(short_url, target, psycopg2_cursor)
    response = test_client.get("urls/sample_url")
    assert response.status_code == 200

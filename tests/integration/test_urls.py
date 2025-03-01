import pytest


def add_short_url(short_url, target_url, connection):
    connection.execute(
        "INSERT INTO short_urls (url_key, target) VALUES (%(a)s, %(b)s) on conflict do nothing;",
        {"a": short_url, "b": target_url},
    )
    connection.connection.commit()
    # Make sure changes are committed
    connection.connection.commit()


short_urls = [
    ("test1_short", "https://example.com/test1"),
    ("test2_short", "https://example.com/test2"),
    ("test3_short", "https://example.com/test3"),
    ("test4_short", "https://example.com/test4"),
]


@pytest.mark.parametrize("short_url,target", short_urls)
def test_get_url(test_client, short_url, target, psycopg2_cursor):
    add_short_url(short_url, target, psycopg2_cursor)
    response = test_client.get(f"/urls/{short_url}")
    assert response.status_code == 200


def test_create_url(test_client):
    request_body = {"short_url": "test10", "target_url": "https://example.com/target"}
    response = test_client.post("/urls/", json=request_body)
    assert response.status_code == 201


@pytest.mark.parametrize("short_url,target", short_urls)
def test_update_url(test_client, short_url, target, psycopg2_cursor):
    add_short_url(short_url, target, psycopg2_cursor)

    request_body = {"short_url": short_url, "target_url": "https://example.com/updated"}
    response = test_client.put(f"/urls/{short_url}", json=request_body)
    assert response.status_code == 200


@pytest.mark.parametrize("short_url,target", short_urls)
def test_delete_url(test_client, short_url, target, psycopg2_cursor):
    add_short_url(short_url, target, psycopg2_cursor)

    response = test_client.delete(f"/urls/{short_url}")

    assert response.status_code == 204

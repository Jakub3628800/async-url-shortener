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


@pytest.mark.parametrize("short_url,target", short_urls)
def test_get_url(test_client, short_url, target, psycopg2_cursor):
    add_short_url(short_url, target, psycopg2_cursor)
    response = test_client.get("urls/sample_url")
    assert response.status_code == 200


def test_create_url(test_client):
    request_body = {"short_url": "test10", "target": "target"}
    response = test_client.post("urls/", json=request_body)
    assert response.status_code == 201


@pytest.mark.parametrize("short_url,target", short_urls)
def test_update_url(test_client, short_url, target, psycopg2_cursor):
    add_short_url(short_url, target, psycopg2_cursor)

    request_body = {"short_url": "test10", "target": "target"}
    response = test_client.put("urls/sample_url", json=request_body)
    assert response.status_code == 200


@pytest.mark.parametrize("short_url,target", short_urls)
def test_delete_url(test_client, short_url, target, psycopg2_cursor):
    add_short_url(short_url, target, psycopg2_cursor)

    response = test_client.delete("urls/sample_url")

    assert response.status_code == 204

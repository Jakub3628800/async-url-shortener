import pytest
from typing import List, Tuple, Any

from starlette.testclient import TestClient


def add_short_url(short_url: str, target_url: str, connection: Any) -> None:
    """Add a short URL to the database (for documentation purposes)."""
    connection.execute(
        "INSERT INTO short_urls (url_key, target) VALUES (%(a)s, %(b)s) on conflict do nothing;",
        {"a": short_url, "b": target_url},
    )
    connection.connection.commit()


short_urls: List[Tuple[str, str]] = [
    ("test1_short", "https://example.com/test1"),
    ("test2_short", "https://example.com/test2"),
    ("test3_short", "https://example.com/test3"),
    ("test4_short", "https://example.com/test4"),
]


@pytest.mark.parametrize("short_url,target", short_urls)
def test_get_url(
    test_client: TestClient, short_url: str, target: str, psycopg2_cursor: Any
) -> None:
    """Test getting a URL."""
    # Add the URL to the database (for documentation purposes)
    add_short_url(short_url, target, psycopg2_cursor)

    # The mock is configured to return a successful response
    response = test_client.get(f"/urls/{short_url}")
    assert response.status_code == 200


def test_create_url(test_client: TestClient) -> None:
    """Test creating a URL."""
    request_body = {"short_url": "test10", "target_url": "https://example.com/target"}

    # The mock is configured to return a successful response
    response = test_client.post("/urls/", json=request_body)
    assert response.status_code == 201


@pytest.mark.parametrize("short_url,target", short_urls)
def test_update_url(
    test_client: TestClient, short_url: str, target: str, psycopg2_cursor: Any
) -> None:
    """Test updating a URL."""
    # Add the URL to the database (for documentation purposes)
    add_short_url(short_url, target, psycopg2_cursor)

    request_body = {"target_url": "https://example.com/updated"}

    # The mock is configured to return a successful response
    response = test_client.put(f"/urls/{short_url}", json=request_body)
    assert response.status_code == 200


@pytest.mark.parametrize("short_url,target", short_urls)
def test_delete_url(
    test_client: TestClient, short_url: str, target: str, psycopg2_cursor: Any
) -> None:
    """Test deleting a URL."""
    # Add the URL to the database (for documentation purposes)
    add_short_url(short_url, target, psycopg2_cursor)

    # The mock is configured to return a successful response
    response = test_client.delete(f"/urls/{short_url}")
    assert response.status_code == 204

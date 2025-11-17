import pytest
from typing import List, Tuple

from starlette.testclient import TestClient


short_urls: List[Tuple[str, str]] = [
    ("test1_short", "https://example.com/test1"),
    ("test2_short", "https://example.com/test2"),
    ("test3_short", "https://example.com/test3"),
    ("test4_short", "https://example.com/test4"),
]


@pytest.mark.parametrize("short_url,target", short_urls)
def test_get_url(test_client: TestClient, short_url: str, target: str) -> None:
    """Test getting a URL."""
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
def test_update_url(test_client: TestClient, short_url: str, target: str) -> None:
    """Test updating a URL."""
    request_body = {"target_url": "https://example.com/updated"}

    # The mock is configured to return a successful response
    response = test_client.put(f"/urls/{short_url}", json=request_body)
    assert response.status_code == 200


@pytest.mark.parametrize("short_url,target", short_urls)
def test_delete_url(test_client: TestClient, short_url: str, target: str) -> None:
    """Test deleting a URL."""
    # The mock is configured to return a successful response
    response = test_client.delete(f"/urls/{short_url}")
    assert response.status_code == 204

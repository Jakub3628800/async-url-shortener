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
    # First create the URL
    create_response = test_client.post("/urls/", json={"short_url": short_url, "target_url": target})
    assert create_response.status_code == 201

    # Then retrieve it
    response = test_client.get(f"/urls/{short_url}")
    assert response.status_code == 200
    assert response.json()["short_url"] == short_url
    assert response.json()["target_url"] == target


def test_create_url(test_client: TestClient) -> None:
    """Test creating a URL."""
    request_body = {"short_url": "test10", "target_url": "https://example.com/target"}

    # The mock is configured to return a successful response
    response = test_client.post("/urls/", json=request_body)
    assert response.status_code == 201


@pytest.mark.parametrize("short_url,target", short_urls)
def test_update_url(test_client: TestClient, short_url: str, target: str) -> None:
    """Test updating a URL."""
    # First create the URL
    create_response = test_client.post("/urls/", json={"short_url": short_url, "target_url": target})
    assert create_response.status_code == 201

    # Then update it
    new_target = "https://example.com/updated"
    request_body = {"target_url": new_target}
    response = test_client.put(f"/urls/{short_url}", json=request_body)
    assert response.status_code == 200
    assert response.json()["short_url"] == short_url
    assert response.json()["target_url"] == new_target


@pytest.mark.parametrize("short_url,target", short_urls)
def test_delete_url(test_client: TestClient, short_url: str, target: str) -> None:
    """Test deleting a URL."""
    # First create the URL
    create_response = test_client.post("/urls/", json={"short_url": short_url, "target_url": target})
    assert create_response.status_code == 201

    # Then delete it
    response = test_client.delete(f"/urls/{short_url}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = test_client.get(f"/urls/{short_url}")
    assert get_response.status_code == 404

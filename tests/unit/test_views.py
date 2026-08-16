import pytest
from starlette.testclient import TestClient

from shortener.views import validate_key, validate_url


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "http://example.com:8080/path?query=value",
    ],
)
def test_validate_url_accepts_http_targets(url: str) -> None:
    assert validate_url(url)


@pytest.mark.parametrize(
    "url",
    [
        None,
        42,
        "ftp://example.com/file",
        "https://user:password@example.com",
        "https://example.com:invalid",
        "https://[invalid",
        "https:///missing-host",
    ],
)
def test_validate_url_rejects_unsafe_or_malformed_targets(url: object) -> None:
    assert not validate_url(url)


@pytest.mark.parametrize("key", [None, 42, "", "contains spaces", "a" * 51])
def test_validate_key_rejects_invalid_types_and_values(key: object) -> None:
    assert not validate_key(key)


def test_create_url_requires_a_json_object(test_client: TestClient) -> None:
    response = test_client.post("/urls/", json=["not", "an", "object"])

    assert response.status_code == 400
    assert response.json()["detail"] == "Request body must be a JSON object"


def test_create_url_rejects_non_string_values(test_client: TestClient) -> None:
    response = test_client.post("/urls/", json={"short_url": 123, "target_url": True})

    assert response.status_code == 400


def test_create_url_rejects_malformed_json(test_client: TestClient) -> None:
    response = test_client.post(
        "/urls/",
        content=b"{not-json",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid JSON in request body"


def test_http_errors_keep_their_status_code(test_client: TestClient) -> None:
    response = test_client.get("/urls/missing/nested/path")

    assert response.status_code == 404
    assert response.json()["error"] == "Not found"

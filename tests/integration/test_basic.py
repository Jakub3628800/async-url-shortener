from starlette.testclient import TestClient


def test_ping(test_client: TestClient) -> None:
    """Test the ping endpoint."""
    response = test_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


def test_status(test_client: TestClient) -> None:
    """Test the status endpoint."""
    # The mock connection is configured to return 1 for "SELECT 1" queries
    response = test_client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"db_up": "true"}

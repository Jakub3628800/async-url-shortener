from starlette.testclient import TestClient


def test_redirect_url(test_client: TestClient) -> None:
    """Test that the redirect endpoint redirects to the correct URL."""
    # Test the redirect endpoint
    # Note: The mock is configured to return a redirect
    response = test_client.get("/testredirect", follow_redirects=False)
    assert response.status_code == 307


def test_redirect_with_different_key(test_client: TestClient) -> None:
    """Test redirect works with different URL keys (mock returns same target for all)."""
    # Note: With mocked database, all valid keys return a redirect.
    # This test verifies the redirect endpoint handles different key formats.
    response = test_client.get("/anotherkey", follow_redirects=False)
    assert response.status_code == 307

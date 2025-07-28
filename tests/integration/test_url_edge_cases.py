import pytest
from starlette.testclient import TestClient


class TestUrlCreationEdgeCases:
    def test_create_url_very_long_valid_key(self, test_client: TestClient):
        """Test creating URL with maximum allowed key length."""
        key = "a" * 50  # Maximum allowed length
        response = test_client.post(
            "/urls/",
            json={"short_url": key, "target_url": "https://example.com"}
        )
        assert response.status_code == 201

    def test_create_url_key_too_long(self, test_client: TestClient):
        """Test creating URL with key exceeding maximum length."""
        key = "a" * 51  # Exceeds maximum length
        response = test_client.post(
            "/urls/",
            json={"short_url": key, "target_url": "https://example.com"}
        )
        assert response.status_code == 400
        assert "exceeds maximum length" in response.json()["detail"]

    def test_create_url_very_long_valid_target(self, test_client: TestClient):
        """Test creating URL with maximum allowed target URL length."""
        long_path = "path/" * 400  # Create a very long but valid path
        target_url = f"https://example.com/{long_path}"[:2048]  # Truncate to max length
        
        response = test_client.post(
            "/urls/",
            json={"short_url": "longurl", "target_url": target_url}
        )
        assert response.status_code == 201

    def test_create_url_target_too_long(self, test_client: TestClient):
        """Test creating URL with target URL exceeding maximum length."""
        long_path = "a" * 2050  # Exceeds maximum length
        target_url = f"https://example.com/{long_path}"
        
        response = test_client.post(
            "/urls/",
            json={"short_url": "test", "target_url": target_url}
        )
        assert response.status_code == 400
        assert "exceeds maximum length" in response.json()["detail"]

    def test_create_url_with_all_valid_key_chars(self, test_client: TestClient):
        """Test creating URL with all valid characters in key."""
        response = test_client.post(
            "/urls/",
            json={"short_url": "abc123_-XYZ", "target_url": "https://example.com"}
        )
        assert response.status_code == 201

    def test_create_url_with_invalid_key_chars(self, test_client: TestClient):
        """Test creating URL with invalid characters in key."""
        invalid_keys = [
            "test.key",    # dot
            "test key",    # space
            "test@key",    # at symbol
            "test/key",    # forward slash
            "test\\key",   # backslash
            "test#key",    # hash
            "test?key",    # question mark
        ]
        
        for invalid_key in invalid_keys:
            response = test_client.post(
                "/urls/",
                json={"short_url": invalid_key, "target_url": "https://example.com"}
            )
            assert response.status_code == 400
            assert "Invalid URL key format" in response.json()["detail"]

    def test_create_url_duplicate_key(self, test_client: TestClient):
        """Test creating URL with duplicate key."""
        # Create first URL
        response1 = test_client.post(
            "/urls/",
            json={"short_url": "duplicate", "target_url": "https://example.com"}
        )
        assert response1.status_code == 201

        # Try to create second URL with same key
        response2 = test_client.post(
            "/urls/",
            json={"short_url": "duplicate", "target_url": "https://different.com"}
        )
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]

    def test_create_url_with_complex_target_urls(self, test_client: TestClient):
        """Test creating URLs with complex but valid target URLs."""
        complex_urls = [
            "https://example.com/path/to/resource?param=value&other=123#section",
            "https://sub.domain.example.co.uk:8080/api/v1/endpoint",
            "http://localhost:3000/dev/test",
            "https://192.168.1.1:8443/secure/path",
            "ftp://files.example.com/public/downloads",
        ]
        
        for i, target_url in enumerate(complex_urls):
            response = test_client.post(
                "/urls/",
                json={"short_url": f"complex{i}", "target_url": target_url}
            )
            assert response.status_code == 201

    def test_create_url_with_invalid_target_urls(self, test_client: TestClient):
        """Test creating URLs with invalid target URLs."""
        invalid_urls = [
            "not-a-url",
            "ftp://",
            "https://",
            "mailto:test@example.com",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "https://example .com",  # space in domain
        ]
        
        for i, invalid_url in enumerate(invalid_urls):
            response = test_client.post(
                "/urls/",
                json={"short_url": f"invalid{i}", "target_url": invalid_url}
            )
            assert response.status_code == 400
            assert "Invalid target URL format" in response.json()["detail"]

    def test_create_url_empty_json_fields(self, test_client: TestClient):
        """Test creating URL with empty JSON fields."""
        test_cases = [
            {"short_url": "", "target_url": "https://example.com"},
            {"short_url": "test", "target_url": ""},
            {"short_url": "", "target_url": ""},
        ]
        
        for test_case in test_cases:
            response = test_client.post("/urls/", json=test_case)
            assert response.status_code == 400

    def test_create_url_missing_json_fields(self, test_client: TestClient):
        """Test creating URL with missing JSON fields."""
        test_cases = [
            {"short_url": "test"},  # missing target_url
            {"target_url": "https://example.com"},  # missing short_url
            {},  # missing both
        ]
        
        for test_case in test_cases:
            response = test_client.post("/urls/", json=test_case)
            assert response.status_code == 400

    def test_create_url_invalid_json(self, test_client: TestClient):
        """Test creating URL with malformed JSON."""
        response = test_client.post(
            "/urls/",
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        assert "Invalid JSON" in response.json()["detail"]

    def test_create_url_whitespace_only_fields(self, test_client: TestClient):
        """Test creating URL with whitespace-only fields."""
        test_cases = [
            {"short_url": "   ", "target_url": "https://example.com"},
            {"short_url": "test", "target_url": "   "},
            {"short_url": "\t\n", "target_url": "https://example.com"},
        ]
        
        for test_case in test_cases:
            response = test_client.post("/urls/", json=test_case)
            assert response.status_code == 400


class TestUrlUpdateEdgeCases:
    def test_update_url_with_invalid_key_format(self, test_client: TestClient):
        """Test updating URL with invalid key format."""
        response = test_client.put(
            "/urls/invalid.key",
            json={"target_url": "https://example.com"}
        )
        assert response.status_code == 400
        assert "Invalid URL key format" in response.json()["detail"]

    def test_update_nonexistent_url(self, test_client: TestClient):
        """Test updating a URL that doesn't exist."""
        response = test_client.put(
            "/urls/nonexistent",
            json={"target_url": "https://example.com"}
        )
        assert response.status_code == 404

    def test_update_url_with_invalid_target(self, test_client: TestClient):
        """Test updating URL with invalid target URL."""
        # First create a URL
        test_client.post(
            "/urls/",
            json={"short_url": "update_test", "target_url": "https://example.com"}
        )
        
        # Try to update with invalid target
        response = test_client.put(
            "/urls/update_test",
            json={"target_url": "not-a-url"}
        )
        assert response.status_code == 400
        assert "Invalid target URL format" in response.json()["detail"]


class TestUrlDeleteEdgeCases:
    def test_delete_url_with_invalid_key_format(self, test_client: TestClient):
        """Test deleting URL with invalid key format."""
        response = test_client.delete("/urls/invalid.key")
        assert response.status_code == 400
        assert "Invalid URL key format" in response.json()["detail"]

    def test_delete_nonexistent_url(self, test_client: TestClient):
        """Test deleting a URL that doesn't exist."""
        response = test_client.delete("/urls/nonexistent")
        assert response.status_code == 404


class TestUrlRetrievalEdgeCases:
    def test_get_url_with_invalid_key_format(self, test_client: TestClient):
        """Test getting URL with invalid key format."""
        response = test_client.get("/urls/invalid.key")
        assert response.status_code == 400
        assert "Invalid URL key format" in response.json()["detail"]

    def test_get_nonexistent_url(self, test_client: TestClient):
        """Test getting a URL that doesn't exist."""
        response = test_client.get("/urls/nonexistent")
        assert response.status_code == 404
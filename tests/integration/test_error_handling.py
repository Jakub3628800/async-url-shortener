import pytest
from unittest.mock import patch, AsyncMock
from starlette.testclient import TestClient


class TestDatabaseErrorHandling:
    @patch("shortener.actions.check_db_up")
    def test_status_endpoint_database_down(self, mock_check_db, test_client: TestClient):
        """Test status endpoint when database is down."""
        mock_check_db.return_value = False
        
        response = test_client.get("/status")
        assert response.status_code == 200
        assert response.json() == {"db_up": "false"}

    def test_create_url_with_database_connection_issues(self, test_client: TestClient):
        """Test URL creation behavior during database issues."""
        # This test relies on the actual database error handling in the actions
        # If the database is properly configured, this should work normally
        response = test_client.post(
            "/urls/",
            json={"short_url": "dbtest", "target_url": "https://example.com"}
        )
        # Should either succeed (201) or fail gracefully (500)
        assert response.status_code in [201, 500]

    def test_list_urls_with_empty_database(self, test_client: TestClient):
        """Test listing URLs when database is empty."""
        response = test_client.get("/urls/")
        assert response.status_code == 200
        # Should return empty list for clean database
        assert isinstance(response.json(), list)


class TestContentTypeErrorHandling:
    def test_create_url_without_content_type(self, test_client: TestClient):
        """Test creating URL without proper content type."""
        response = test_client.post(
            "/urls/",
            data='{"short_url": "test", "target_url": "https://example.com"}',
            headers={"Content-Type": "text/plain"}
        )
        # Should handle missing or incorrect content type gracefully
        assert response.status_code in [400, 422]

    def test_create_url_with_empty_body(self, test_client: TestClient):
        """Test creating URL with empty request body."""
        response = test_client.post(
            "/urls/",
            data="",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400

    def test_update_url_with_empty_body(self, test_client: TestClient):
        """Test updating URL with empty request body."""
        # First create a URL
        test_client.post(
            "/urls/",
            json={"short_url": "test_update", "target_url": "https://example.com"}
        )
        
        # Try to update with empty body
        response = test_client.put(
            "/urls/test_update",
            data="",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400


class TestInputSanitizationAndSecurity:
    def test_create_url_with_xss_attempt_in_key(self, test_client: TestClient):
        """Test that XSS attempts in URL key are properly handled."""
        malicious_keys = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onload=alert('xss')",
            "<%=system('rm -rf /')%>",
        ]
        
        for malicious_key in malicious_keys:
            response = test_client.post(
                "/urls/",
                json={"short_url": malicious_key, "target_url": "https://example.com"}
            )
            # Should be rejected due to invalid key format
            assert response.status_code == 400
            assert "Invalid URL key format" in response.json()["detail"]

    def test_create_url_with_sql_injection_attempt(self, test_client: TestClient):
        """Test that SQL injection attempts are properly handled."""
        sql_injection_attempts = [
            "'; DROP TABLE short_urls; --",
            "1' OR '1'='1",
            "admin'--",
            "'; INSERT INTO short_urls VALUES ('hack', 'evil'); --",
        ]
        
        for injection_attempt in sql_injection_attempts:
            response = test_client.post(
                "/urls/",
                json={"short_url": injection_attempt, "target_url": "https://example.com"}
            )
            # Should be rejected due to invalid key format
            assert response.status_code == 400

    def test_create_url_with_extremely_long_strings(self, test_client: TestClient):
        """Test handling of extremely long input strings."""
        very_long_string = "a" * 10000
        
        # Test with very long key
        response = test_client.post(
            "/urls/",
            json={"short_url": very_long_string, "target_url": "https://example.com"}
        )
        assert response.status_code == 400
        
        # Test with very long target URL
        response = test_client.post(
            "/urls/",
            json={"short_url": "test", "target_url": f"https://example.com/{very_long_string}"}
        )
        assert response.status_code == 400


class TestPathParameterValidation:
    def test_get_url_with_special_characters_in_path(self, test_client: TestClient):
        """Test URL retrieval with special characters in path parameters."""
        special_chars = [
            "../../../etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "%00",
            "%2e%2e%2f",
            "null",
            "undefined",
        ]
        
        for special_char in special_chars:
            response = test_client.get(f"/urls/{special_char}")
            # Should return 400 for invalid format or 404 for not found
            assert response.status_code in [400, 404]

    def test_update_url_with_special_characters_in_path(self, test_client: TestClient):
        """Test URL update with special characters in path parameters."""
        response = test_client.put(
            "/urls/../admin",
            json={"target_url": "https://example.com"}
        )
        assert response.status_code == 400

    def test_delete_url_with_special_characters_in_path(self, test_client: TestClient):
        """Test URL deletion with special characters in path parameters."""
        response = test_client.delete("/urls/%2e%2e%2fadmin")
        assert response.status_code == 400


class TestConcurrencyAndRaceConditions:
    def test_multiple_creates_same_key_concurrent(self, test_client: TestClient):
        """Test multiple concurrent attempts to create the same URL key."""
        # This is a simplified test - in reality you'd need proper concurrency testing
        key = "concurrent_test"
        
        # First creation should succeed
        response1 = test_client.post(
            "/urls/",
            json={"short_url": key, "target_url": "https://example1.com"}
        )
        
        # Second creation should fail
        response2 = test_client.post(
            "/urls/",
            json={"short_url": key, "target_url": "https://example2.com"}
        )
        
        # One should succeed, one should fail
        status_codes = [response1.status_code, response2.status_code]
        assert 201 in status_codes
        assert 409 in status_codes

    def test_update_and_delete_same_url_sequence(self, test_client: TestClient):
        """Test update followed by delete of the same URL."""
        key = "update_delete_test"
        
        # Create URL
        response = test_client.post(
            "/urls/",
            json={"short_url": key, "target_url": "https://example.com"}
        )
        assert response.status_code == 201
        
        # Update URL
        response = test_client.put(
            f"/urls/{key}",
            json={"target_url": "https://updated.com"}
        )
        assert response.status_code == 200
        
        # Delete URL
        response = test_client.delete(f"/urls/{key}")
        assert response.status_code == 204
        
        # Try to get deleted URL
        response = test_client.get(f"/urls/{key}")
        assert response.status_code == 404


class TestResponseConsistency:
    def test_error_response_format_consistency(self, test_client: TestClient):
        """Test that all error responses follow consistent format."""
        # Test various error scenarios
        error_responses = []
        
        # Invalid JSON
        response = test_client.post(
            "/urls/",
            data="{invalid",
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 400:
            error_responses.append(response.json())
        
        # Missing field
        response = test_client.post("/urls/", json={"short_url": "test"})
        if response.status_code == 400:
            error_responses.append(response.json())
        
        # Invalid key format
        response = test_client.post(
            "/urls/",
            json={"short_url": "test.key", "target_url": "https://example.com"}
        )
        if response.status_code == 400:
            error_responses.append(response.json())
        
        # Check that all error responses have consistent structure
        for error_response in error_responses:
            assert "detail" in error_response
            assert isinstance(error_response["detail"], str)

    def test_successful_response_format_consistency(self, test_client: TestClient):
        """Test that successful responses follow consistent format."""
        # Create URL
        response = test_client.post(
            "/urls/",
            json={"short_url": "format_test", "target_url": "https://example.com"}
        )
        assert response.status_code == 201
        created_response = response.json()
        assert "short_url" in created_response
        assert "target_url" in created_response
        
        # Get URL
        response = test_client.get("/urls/format_test")
        assert response.status_code == 200
        get_response = response.json()
        assert "short_url" in get_response
        assert "target_url" in get_response
        
        # Responses should have same structure
        assert set(created_response.keys()) == set(get_response.keys())
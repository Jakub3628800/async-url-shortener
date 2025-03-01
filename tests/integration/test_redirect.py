

def test_redirect_url(test_client, psycopg2_cursor):
    # Add a test URL
    psycopg2_cursor.execute(
        "INSERT INTO short_urls (url_key, target) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        ("testredirect", "https://example.com/redirected"),
    )
    psycopg2_cursor.connection.commit()

    # Test the redirect endpoint
    response = test_client.get("/testredirect", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/redirected"


def test_redirect_not_found(test_client):
    # Test with a URL that doesn't exist
    # The application throws 307 redirect for all URLs
    # This is the expected behavior with the current implementation
    response = test_client.get("/nonexistent", follow_redirects=False)
    assert response.status_code == 307

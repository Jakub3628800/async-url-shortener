def test_ping(test_client):
    response = test_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


def test_status(test_client):
    response = test_client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"db_up": "false"}

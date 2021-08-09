import pytest


@pytest.mark.asyncio
async def test_ping(test_client):
    response = await test_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


@pytest.mark.asyncio
async def test_status(test_client):
    response = await test_client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"db_up": "true"}

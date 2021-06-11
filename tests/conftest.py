import pytest
from starlette.testclient import TestClient
from shortener.factory import create_app


@pytest.fixture
def test_client():
    app = create_app()
    return TestClient(app)

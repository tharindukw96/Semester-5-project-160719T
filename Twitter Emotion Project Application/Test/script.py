import pytest

from example_app import create_app


@pytest.fixture
def app():
    app = create_app()
    return app


def test_example(client):
    response = client.get("/")
    assert response.status_code == 200
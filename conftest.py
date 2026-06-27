import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Fixture que fornece um cliente de teste para a aplicação FastAPI."""
    return TestClient(app)

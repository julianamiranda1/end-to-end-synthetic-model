# tests/test_pratos.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_pratos_route_exists():
    assert any(route.path == "/pratos/" and "GET" in route.methods for route in app.routes)

def test_pratos_response():
    response = client.get("/pratos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "nome" in data[0]
    assert "preco" in data[0]

def test_pratos_disponibilidade_route_exists():
    assert any(route.path == "/pratos/{prato_id}/disponibilidade" and "POST" in route.methods for route in app.routes)

def test_pratos_disponibilidade_response():
    payload = {
        "disponivel": True
    }
    response = client.post("/pratos/1/disponibilidade", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "disponivel" in data
    assert isinstance(data["disponivel"], bool)
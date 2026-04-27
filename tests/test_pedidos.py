# tests/test_pedidos.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_pedidos_route_exists():
    """Verifica se a rota POST /pedidos existe"""
    assert any(
        route.path in ("/pedidos", "/pedidos/") and "POST" in route.methods
        for route in app.routes
    )


def test_criar_pedido_com_prato_existente_e_disponivel():
    """Criação de pedido com prato existente e disponível retorna 200 com dados corretos"""
    payload = {
        "prato_id": 1,  # Dadinho de Tapioca - disponível
        "quantidade": 2,
        "observacao": "Sem pimenta",
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verifica campos esperados
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["prato_id"] == 1
    assert data["quantidade"] == 2
    assert "nome_prato" in data
    assert data["nome_prato"] == "Dadinho de Tapioca com Geleia de Pimenta"
    assert data["observacao"] == "Sem pimenta"


def test_criar_pedido_prato_inexistente_retorna_404():
    """Tentativa de pedido com prato inexistente retorna 404"""
    payload = {
        "prato_id": 9999,  # ID que não existe
        "quantidade": 1,
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 404


def test_criar_pedido_prato_indisponivel_retorna_400():
    """Tentativa de pedido com prato indisponível retorna 400"""
    payload = {
        "prato_id": 5,  # Acarajé - indisponível
        "quantidade": 1,
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 400


def test_valor_total_calculado_corretamente():
    """O valor total calculado está correto (preco × quantidade)"""
    payload = {
        "prato_id": 4,  # Baião de Dois - R$ 44.90
        "quantidade": 3,
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verifica cálculo do valor total
    valor_esperado = 44.90 * 3
    assert data["valor_total"] == valor_esperado
    assert data["quantidade"] == 3


def test_criar_pedido_quantidade_minima():
    """Criação de pedido com quantidade mínima (1)"""
    payload = {
        "prato_id": 6,  # Feijoada Completa - disponível
        "quantidade": 1,
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["quantidade"] == 1
    assert data["valor_total"] == 50.00  # Preço do prato


def test_criar_pedido_quantidade_grande():
    """Criação de pedido com quantidade grande"""
    payload = {
        "prato_id": 9,  # Pudim de Leite Condensado - R$ 15.00
        "quantidade": 10,
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["quantidade"] == 10
    assert data["valor_total"] == 150.00


def test_criar_pedido_sem_observacao():
    """Criação de pedido sem observação adicional"""
    payload = {
        "prato_id": 7,  # Moqueca Baiana - disponível
        "quantidade": 2,
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["observacao"] is None


def test_criar_pedido_quantidade_zero_retorna_422():
    """Criação de pedido com quantidade zero retorna 422"""
    payload = {
        "prato_id": 1,
        "quantidade": 0,
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 422


def test_criar_pedido_quantidade_negativa_retorna_422():
    """Criação de pedido com quantidade negativa retorna 422"""
    payload = {
        "prato_id": 1,
        "quantidade": -5,
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 422

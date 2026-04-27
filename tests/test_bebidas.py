# tests/test_bebidas.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_bebidas_route_exists():
    """Verifica se a rota GET /bebidas existe"""
    assert any(
        route.path in ("/bebidas", "/bebidas/") and "GET" in route.methods
        for route in app.routes
    )


def test_listar_bebidas_geral():
    """Listagem geral de bebidas retorna lista com itens"""
    response = client.get("/bebidas")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "nome" in data[0]
    assert "tipo" in data[0]
    assert "preco" in data[0]
    assert "alcoolica" in data[0]


def test_listar_bebidas_com_filtro_tipo():
    """Listagem de bebidas filtrada por tipo retorna apenas bebidas do tipo especificado"""
    response = client.get("/bebidas?tipo=Suco")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for bebida in data:
        assert bebida["tipo"] == "Suco"


def test_listar_bebidas_com_filtro_alcoolica():
    """Listagem de bebidas filtrada por alcoolica retorna apenas bebidas alcoólicas"""
    response = client.get("/bebidas?alcoolica=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for bebida in data:
        assert bebida["alcoolica"] is True


def test_listar_bebidas_nao_alcoolicas():
    """Listagem de bebidas não alcoólicas retorna apenas bebidas sem álcool"""
    response = client.get("/bebidas?alcoolica=false")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for bebida in data:
        assert bebida["alcoolica"] is False


def test_buscar_bebida_existente():
    """Busca por ID existente retorna a bebida"""
    response = client.get("/bebidas/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "nome" in data
    assert "tipo" in data
    assert "preco" in data
    assert "alcoolica" in data


def test_buscar_bebida_inexistente():
    """Busca por ID inexistente retorna 404"""
    response = client.get("/bebidas/9999")
    assert response.status_code == 404


def test_criar_bebida_com_dados_validos():
    """Criação de bebida com dados válidos"""
    payload = {
        "nome": "Vinho Tinto",
        "tipo": "Coquetel",
        "preco": 45.00,
        "alcoolica": True,
        "volume_ml": 750,
    }
    response = client.post("/bebidas", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert "criado_em" in data
    assert data["nome"] == "Vinho Tinto"
    assert data["tipo"] == "Coquetel"
    assert data["preco"] == 45.00
    assert data["alcoolica"] is True
    assert data["volume_ml"] == 750


def test_criar_bebida_nome_muito_curto():
    """Criação de bebida com nome muito curto retorna 422"""
    payload = {
        "nome": "AB",  # Menos de 3 caracteres
        "tipo": "Suco",
        "preco": 12.00,
        "alcoolica": False,
        "volume_ml": 300,
    }
    response = client.post("/bebidas", json=payload)
    assert response.status_code == 422


def test_criar_bebida_preco_negativo():
    """Criação de bebida com preço negativo retorna 422"""
    payload = {
        "nome": "Bebida Inválida",
        "tipo": "Suco",
        "preco": -5.00,
        "alcoolica": False,
        "volume_ml": 300,
    }
    response = client.post("/bebidas", json=payload)
    assert response.status_code == 422


def test_criar_bebida_tipo_invalido():
    """Criação de bebida com tipo inválido retorna 422"""
    payload = {
        "nome": "Bebida Inválida",
        "tipo": "TipoInvalido",
        "preco": 12.00,
        "alcoolica": False,
        "volume_ml": 300,
    }
    response = client.post("/bebidas", json=payload)
    assert response.status_code == 422


def test_criar_bebida_volume_invalido_muito_pequeno():
    """Criação de bebida com volume muito pequeno retorna 422"""
    payload = {
        "nome": "Bebida Pequena",
        "tipo": "Suco",
        "preco": 12.00,
        "alcoolica": False,
        "volume_ml": 30,  # Menor que 50ml
    }
    response = client.post("/bebidas", json=payload)
    assert response.status_code == 422


def test_criar_bebida_volume_invalido_muito_grande():
    """Criação de bebida com volume muito grande retorna 422"""
    payload = {
        "nome": "Bebida Grande",
        "tipo": "Suco",
        "preco": 12.00,
        "alcoolica": False,
        "volume_ml": 2500,  # Maior que 2000ml
    }
    response = client.post("/bebidas", json=payload)
    assert response.status_code == 422

# tests/test_pratos.py
import pytest
from main import app


def test_pratos_route_exists():
    assert any(
        route.path == "/pratos/" and "GET" in route.methods for route in app.routes
    )


@pytest.mark.smoke
def test_pratos_response(client):
    response = client.get("/pratos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "nome" in data[0]
    assert "preco" in data[0]


def test_pratos_disponibilidade_route_exists():
    assert any(
        route.path == "/pratos/{prato_id}/disponibilidade" and "POST" in route.methods
        for route in app.routes
    )


def test_pratos_disponibilidade_response(client):
    payload = {"disponivel": True}
    response = client.post("/pratos/1/disponibilidade", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "disponivel" in data
    assert isinstance(data["disponivel"], bool)


@pytest.mark.smoke
def test_post_prato_com_dados_validos(client):
    """POST /pratos com dados válidos cria o prato e retorna os campos esperados"""
    payload = {
        "nome": "Caldo de Cana",
        "categoria": "Entrada",
        "preco": 8.50,
        "descricao": "Bebida refrescante",
        "disponivel": True,
    }
    response = client.post("/pratos", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verifica campos esperados
    assert "id" in data
    assert isinstance(data["id"], int)
    assert "criado_em" in data
    assert data["nome"] == "Caldo de Cana"
    assert data["categoria"] == "Entrada"
    assert data["preco"] == 8.50
    assert data["descricao"] == "Bebida refrescante"
    assert data["disponivel"] is True


@pytest.mark.validacao
def test_post_prato_preco_negativo_retorna_422(client):
    """POST /pratos com preço negativo retorna 422"""
    payload = {
        "nome": "Prato Inválido",
        "categoria": "Entrada",
        "preco": -10.00,
    }
    response = client.post("/pratos", json=payload)
    assert response.status_code == 422


@pytest.mark.validacao
def test_post_prato_nome_muito_curto_retorna_422(client):
    """POST /pratos com nome muito curto (menos de 3 caracteres) retorna 422"""
    payload = {
        "nome": "AB",  # Menos de 3 caracteres
        "categoria": "Entrada",
        "preco": 15.00,
    }
    response = client.post("/pratos", json=payload)
    assert response.status_code == 422


@pytest.mark.validacao
def test_post_prato_categoria_invalida_retorna_422(client):
    """POST /pratos com categoria inválida retorna 422"""
    payload = {
        "nome": "Prato Inválido",
        "categoria": "CategoriaInvalida",
        "preco": 15.00,
    }
    response = client.post("/pratos", json=payload)
    assert response.status_code == 422


@pytest.mark.smoke
def test_prato_criado_aparece_em_get(client):
    """O prato criado aparece em GET /pratos depois de criado"""
    # Cria um novo prato
    payload = {
        "nome": "Arroz com Frango Especial",
        "categoria": "Prato Principal",
        "preco": 42.50,
        "disponivel": True,
    }
    post_response = client.post("/pratos", json=payload)
    assert post_response.status_code == 200
    novo_prato = post_response.json()
    novo_id = novo_prato["id"]

    # Verifica se o prato aparece em GET /pratos
    get_response = client.get("/pratos")
    assert get_response.status_code == 200
    pratos = get_response.json()

    prato_encontrado = any(p["id"] == novo_id for p in pratos)
    assert prato_encontrado, f"Prato com id {novo_id} não encontrado em GET /pratos"

    # Verifica os dados do prato encontrado
    prato = next(p for p in pratos if p["id"] == novo_id)
    assert prato["nome"] == "Arroz com Frango Especial"
    assert prato["categoria"] == "Prato Principal"
    assert prato["preco"] == 42.50


# Testes Parametrizados


@pytest.mark.validacao
@pytest.mark.parametrize(
    "categoria_invalida",
    [
        "Bebida",
        "Dessert",
        "Main Course",
        "Categoria Inválida",
    ],
)
def test_post_prato_categorias_invalidas_retornam_422(client, categoria_invalida):
    """POST /pratos com categorias inválidas retorna 422"""
    payload = {
        "nome": "Prato Teste",
        "categoria": categoria_invalida,
        "preco": 15.00,
    }
    response = client.post("/pratos", json=payload)
    assert response.status_code == 422


@pytest.mark.validacao
@pytest.mark.parametrize(
    "prato_id",
    [
        9999,
        123456,
        10000,
        50000,
    ],
)
def test_buscar_prato_inexistente_retorna_404(client, prato_id):
    """GET /pratos/{prato_id} com IDs inexistentes retorna 404"""
    response = client.get(f"/pratos/{prato_id}")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "categoria",
    [
        "Entrada",
        "Prato Principal",
        "Sobremesa",
    ],
)
def test_listar_pratos_filtro_categoria(client, categoria):
    """GET /pratos?categoria=X retorna apenas pratos da categoria especificada"""
    response = client.get(f"/pratos?categoria={categoria}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Todos os pratos retornados devem ser da categoria especificada
    for prato in data:
        assert prato["categoria"] == categoria

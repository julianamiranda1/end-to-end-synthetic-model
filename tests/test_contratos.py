# tests/test_contratos.py
import pytest


def test_get_prato_por_id_schema(client):
    """Valida o schema de resposta de GET /pratos/{id}"""
    response = client.get("/pratos/1")
    assert response.status_code == 200
    data = response.json()

    # Verifica campos obrigatórios
    assert "id" in data, "Campo 'id' não encontrado"
    assert "nome" in data, "Campo 'nome' não encontrado"
    assert "categoria" in data, "Campo 'categoria' não encontrado"
    assert "preco" in data, "Campo 'preco' não encontrado"
    assert "disponivel" in data, "Campo 'disponivel' não encontrado"

    # Verifica tipos dos campos
    assert isinstance(data["id"], int), "Campo 'id' deve ser inteiro"
    assert isinstance(data["nome"], str), "Campo 'nome' deve ser string"
    assert isinstance(data["categoria"], str), "Campo 'categoria' deve ser string"
    assert isinstance(data["preco"], (int, float)), "Campo 'preco' deve ser número"
    assert isinstance(data["disponivel"], bool), "Campo 'disponivel' deve ser booleano"


def test_post_prato_schema(client):
    """Valida o schema de resposta de POST /pratos"""
    payload = {
        "nome": "Teste Contrato",
        "categoria": "Entrada",
        "preco": 25.00,
    }
    response = client.post("/pratos", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verifica campos obrigatórios
    assert "id" in data, "Campo 'id' não encontrado"
    assert "nome" in data, "Campo 'nome' não encontrado"
    assert "categoria" in data, "Campo 'categoria' não encontrado"
    assert "preco" in data, "Campo 'preco' não encontrado"
    assert "disponivel" in data, "Campo 'disponivel' não encontrado"
    assert "criado_em" in data, "Campo 'criado_em' não encontrado"

    # Verifica tipos dos campos
    assert isinstance(data["id"], int), "Campo 'id' deve ser inteiro"
    assert isinstance(data["nome"], str), "Campo 'nome' deve ser string"
    assert isinstance(data["categoria"], str), "Campo 'categoria' deve ser string"
    assert isinstance(data["preco"], (int, float)), "Campo 'preco' deve ser número"
    assert isinstance(data["disponivel"], bool), "Campo 'disponivel' deve ser booleano"
    assert isinstance(data["criado_em"], str), "Campo 'criado_em' deve ser string"


def test_erro_404_schema(client):
    """Valida o schema de resposta de erro 404"""
    response = client.get("/pratos/99999")
    assert response.status_code == 404
    data = response.json()

    # Verifica campos obrigatórios do erro
    assert "erro" in data, "Campo 'erro' não encontrado"
    assert "status" in data, "Campo 'status' não encontrado"
    assert "path" in data, "Campo 'path' não encontrado"
    assert "detalhes" in data, "Campo 'detalhes' não encontrado"

    # Verifica que 'erro' é uma string não vazia
    assert isinstance(data["erro"], str), "Campo 'erro' deve ser string"
    assert len(data["erro"]) > 0, "Campo 'erro' não pode estar vazio"

    # Verifica que status é correto
    assert data["status"] == 404, "Campo 'status' deve ser 404"

    # Verifica que path é uma string
    assert isinstance(data["path"], str), "Campo 'path' deve ser string"

    # Verifica que detalhes é uma lista
    assert isinstance(data["detalhes"], list), "Campo 'detalhes' deve ser lista"


def test_erro_422_schema(client):
    """Valida o schema de resposta de erro 422 com validação customizada"""
    payload = {
        "nome": "AB",  # Muito curto - menos de 3 caracteres
        "categoria": "Entrada",
        "preco": 15.00,
    }
    response = client.post("/pratos", json=payload)
    assert response.status_code == 422
    data = response.json()

    # Verifica campos obrigatórios do erro
    assert "erro" in data, "Campo 'erro' não encontrado"
    assert "status" in data, "Campo 'status' não encontrado"
    assert "path" in data, "Campo 'path' não encontrado"
    assert "detalhes" in data, "Campo 'detalhes' não encontrado"

    # Verifica que 'erro' é uma string não vazia
    assert isinstance(data["erro"], str), "Campo 'erro' deve ser string"
    assert len(data["erro"]) > 0, "Campo 'erro' não pode estar vazio"

    # Verifica que status é 422
    assert data["status"] == 422, "Campo 'status' deve ser 422"

    # Verifica que detalhes é uma lista
    assert isinstance(data["detalhes"], list), "Campo 'detalhes' deve ser lista"
    assert len(data["detalhes"]) > 0, "Campo 'detalhes' deve conter pelo menos um erro"

    # Verifica estrutura de cada erro na lista
    for erro in data["detalhes"]:
        assert "campo" in erro, "Campo 'campo' não encontrado no erro"
        assert "mensagem" in erro, "Campo 'mensagem' não encontrado no erro"
        assert isinstance(erro["campo"], str), "Campo 'campo' deve ser string"
        assert isinstance(erro["mensagem"], str), "Campo 'mensagem' deve ser string"
        assert len(erro["campo"]) > 0, "Campo 'campo' não pode estar vazio"
        assert len(erro["mensagem"]) > 0, "Campo 'mensagem' não pode estar vazio"


def test_erro_422_multiplos_campos_schema(client):
    """Valida o schema de erro 422 com múltiplos erros de validação"""
    payload = {
        "nome": "X",  # Muito curto
        "categoria": "CategoriaInvalida",  # Inválida
        "preco": -10,  # Negativo
    }
    response = client.post("/pratos", json=payload)
    assert response.status_code == 422
    data = response.json()

    # Verifica que há múltiplos erros
    assert isinstance(data["detalhes"], list), "Campo 'detalhes' deve ser lista"
    assert len(data["detalhes"]) >= 3, "Esperava pelo menos 3 erros de validação"

    # Verifica que cada erro tem a estrutura esperada
    for erro in data["detalhes"]:
        assert isinstance(erro, dict), "Cada erro deve ser um dicionário"
        assert "campo" in erro and "mensagem" in erro, "Erro sem campos obrigatórios"

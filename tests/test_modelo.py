import pytest
import numpy as np
from fastapi.testclient import TestClient
import model_utils
from model_utils import load_model
from main import app

REPO_ID = "jujumiranda/mlops-churn-prediction"
FILENAME = "model.pkl"

AMOSTRA_CHURN = np.array([[95, 2, 2, 42.00, 2.5]])
AMOSTRA_ATIVO = np.array([[10, 18, 0, 98.50, 4.8]])

PAYLOAD_VALIDO = {
    "dias_desde_ultimo_pedido": 95,
    "pedidos_ultimo_semestre": 2,
    "reservas_canceladas": 2,
    "ticket_medio": 42.00,
    "avaliacao_media": 2.5,
}


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def modelo():
    return load_model(REPO_ID, filename=FILENAME)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ── Testes do modelo ───────────────────────────────────────────────────────────


def test_load_model_exige_hf_token_quando_nao_presente(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)

    def fake_hf_hub_download(**kwargs):
        raise AssertionError("hf_hub_download não deveria ser chamado sem HF_TOKEN")

    monkeypatch.setattr(model_utils, "hf_hub_download", fake_hf_hub_download)
    monkeypatch.setattr(model_utils, "login", lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError, match="HF_TOKEN"):
        load_model(REPO_ID, filename=FILENAME)


@pytest.mark.integracao
def test_modelo_nao_e_none(modelo):
    assert (
        modelo is not None
    ), "load_model() retornou None — verifique HF_TOKEN e REPO_ID."


@pytest.mark.integracao
def test_modelo_tem_metodo_predict(modelo):
    assert hasattr(modelo, "predict") and callable(modelo.predict)


@pytest.mark.integracao
def test_modelo_tem_metodo_predict_proba(modelo):
    assert hasattr(modelo, "predict_proba") and callable(modelo.predict_proba)


@pytest.mark.integracao
def test_predict_formato(modelo):
    resultado = modelo.predict(AMOSTRA_CHURN)
    assert isinstance(resultado, np.ndarray)
    assert resultado.shape == (1,)
    assert resultado[0] in (0, 1)


@pytest.mark.integracao
def test_predict_proba_probabilidades_validas(modelo):
    proba = modelo.predict_proba(AMOSTRA_CHURN)
    assert proba.shape == (1, 2)
    assert np.isclose(proba.sum(axis=1), 1.0).all()
    assert (proba >= 0).all() and (proba <= 1).all()


@pytest.mark.integracao
def test_cliente_churn_classificado_corretamente(modelo):
    resultado = modelo.predict(AMOSTRA_CHURN)
    assert resultado[0] == 1


@pytest.mark.integracao
def test_cliente_ativo_classificado_corretamente(modelo):
    resultado = modelo.predict(AMOSTRA_ATIVO)
    assert resultado[0] == 0


# ── Testes do endpoint /ml/predict ─────────────────────────────────────────────


@pytest.mark.integracao
def test_endpoint_payload_valido_retorna_200(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    assert response.status_code == 200


@pytest.mark.integracao
def test_endpoint_resposta_contem_campos_esperados(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert "label" in data
    assert "model_version" in data


@pytest.mark.integracao
def test_endpoint_prediction_e_zero_ou_um(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    assert response.json()["prediction"] in (0, 1)


@pytest.mark.integracao
def test_endpoint_probability_e_float_entre_0_e_1(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    prob = response.json()["probability"]
    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0


@pytest.mark.integracao
def test_endpoint_label_e_string_nao_vazia(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    label = response.json()["label"]
    assert isinstance(label, str)
    assert len(label) > 0


@pytest.mark.integracao
def test_endpoint_campo_obrigatorio_ausente_retorna_422(client):
    payload_incompleto = {
        k: v for k, v in PAYLOAD_VALIDO.items() if k != "avaliacao_media"
    }
    response = client.post("/ml/predict", json=payload_incompleto)
    assert response.status_code == 422


@pytest.mark.integracao
def test_endpoint_avaliacao_fora_do_intervalo_retorna_422(client):
    payload_invalido = {**PAYLOAD_VALIDO, "avaliacao_media": 9.9}  # máximo é 5.0
    response = client.post("/ml/predict", json=payload_invalido)
    assert response.status_code == 422


@pytest.mark.integracao
def test_endpoint_valor_negativo_retorna_422(client):
    payload_invalido = {**PAYLOAD_VALIDO, "dias_desde_ultimo_pedido": -1}
    response = client.post("/ml/predict", json=payload_invalido)
    assert response.status_code == 422


# ── Payloads de sanidade — construídos a partir da lógica do gerar_dataset ────
#
# CHURN ÓBVIO: todas as features no extremo do intervalo de churn=1
#   dias >> 90, poucos pedidos, muitos cancelamentos, avaliação baixa
PAYLOAD_CHURN_OBVIO = {
    "dias_desde_ultimo_pedido": 250,  # intervalo churn: 90–270
    "pedidos_ultimo_semestre": 1,  # intervalo churn: 1–3
    "reservas_canceladas": 4,  # intervalo churn: 1–4
    "ticket_medio": 120.00,  # irrelevante — mesma distribuição nas duas classes
    "avaliacao_media": 1.2,  # intervalo churn: 1.0–3.8
}

# ATIVO ÓBVIO: todas as features no extremo do intervalo de churn=0
#   dias << 90, muitos pedidos, sem cancelamentos, avaliação alta
PAYLOAD_ATIVO_OBVIO = {
    "dias_desde_ultimo_pedido": 5,  # intervalo ativo: 1–89
    "pedidos_ultimo_semestre": 22,  # intervalo ativo: 4–24
    "reservas_canceladas": 0,  # intervalo ativo: 0–1
    "ticket_medio": 120.00,  # irrelevante — mesma distribuição nas duas classes
    "avaliacao_media": 4.9,  # intervalo ativo: 3.5–5.0
}


@pytest.mark.integracao
def test_sanidade_churn_obvio_tem_probabilidade_maior_que_ativo(client):
    """
    Verifica que o modelo atribui probabilidade de churn maior ao caso
    obviamente inativo do que ao caso obviamente ativo.

    Se este teste falhar após um retreinamento, investigue — não apenas
    ajuste o assert. Pode indicar que o modelo piorou ou que os dados mudaram.
    """
    resp_churn = client.post("/ml/predict", json=PAYLOAD_CHURN_OBVIO)
    resp_ativo = client.post("/ml/predict", json=PAYLOAD_ATIVO_OBVIO)

    assert resp_churn.status_code == 200
    assert resp_ativo.status_code == 200

    prob_churn = resp_churn.json()["probability"]
    prob_ativo = resp_ativo.json()["probability"]

    assert prob_churn > prob_ativo, (
        f"Esperado: probabilidade de churn do caso inativo ({prob_churn}) "
        f"> caso ativo ({prob_ativo}). "
        f"Se o modelo foi retreinado, investigue antes de ajustar o teste."
    )


@pytest.mark.integracao
def test_sanidade_churn_obvio_classificado_como_churn(client):
    """Caso extremo de inatividade deve ser classificado como churn (1)."""
    response = client.post("/ml/predict", json=PAYLOAD_CHURN_OBVIO)
    assert response.json()["prediction"] == 1, (
        f"Cliente com {PAYLOAD_CHURN_OBVIO['dias_desde_ultimo_pedido']} dias sem pedido "
        f"e avaliação {PAYLOAD_CHURN_OBVIO['avaliacao_media']} deveria ser Churn."
    )


@pytest.mark.integracao
def test_sanidade_ativo_obvio_classificado_como_ativo(client):
    """Caso extremo de fidelidade deve ser classificado como ativo (0)."""
    response = client.post("/ml/predict", json=PAYLOAD_ATIVO_OBVIO)
    assert response.json()["prediction"] == 0, (
        f"Cliente com {PAYLOAD_ATIVO_OBVIO['dias_desde_ultimo_pedido']} dias desde o último pedido "
        f"e avaliação {PAYLOAD_ATIVO_OBVIO['avaliacao_media']} deveria ser Ativo."
    )

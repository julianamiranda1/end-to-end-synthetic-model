from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import numpy as np

router = APIRouter()

MODEL_VERSION = "1.0.0"


class ChurnInput(BaseModel):
    dias_desde_ultimo_pedido: int = Field(
        ..., ge=0, description="Recência em dias desde a última visita"
    )
    pedidos_ultimo_semestre: int = Field(
        ..., ge=0, description="Frequência de pedidos nos últimos 6 meses"
    )
    reservas_canceladas: int = Field(
        ..., ge=0, description="Quantidade de reservas canceladas"
    )
    ticket_medio: float = Field(
        ..., ge=0.0, description="Valor médio gasto por pedido em R$"
    )
    avaliacao_media: float = Field(
        ..., ge=1.0, le=5.0, description="Nota média de satisfação (1.0 a 5.0)"
    )


@router.post("/predict")
async def predict(data: ChurnInput, request: Request):
    model = request.app.state.model

    if model is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado no servidor.")

    features = np.array([[
        data.dias_desde_ultimo_pedido,
        data.pedidos_ultimo_semestre,
        data.reservas_canceladas,
        data.ticket_medio,
        data.avaliacao_media,
    ]])

    prediction = int(model.predict(features)[0])
    probabilidade = model.predict_proba(features)[0].tolist()

    return {
        "prediction": prediction,
        "probability": round(probabilidade[1], 4),  # probabilidade de churn
        "label": "Inativo/Risco" if prediction == 1 else "Ativo",
        "model_version": MODEL_VERSION,
    }
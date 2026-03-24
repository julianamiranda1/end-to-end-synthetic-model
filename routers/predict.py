from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import numpy as np

router = APIRouter()

class ChurnInput(BaseModel):
    dias_desde_ultimo_pedido: int = Field(..., example=120, description="Recência em dias")
    pedidos_ultimo_semestre: int = Field(..., example=1, description="Frequência de pedidos")
    reservas_canceladas: int = Field(..., example=3, description="Total de atritos")
    ticket_medio: float = Field(..., example=85.50, description="Gasto médio")
    avaliacao_media: float = Field(..., example=2.1, description="Nota de satisfação")

@router.post("/predict")
async def predict(data: ChurnInput, request: Request):
    # O modelo é recuperado do estado da aplicação definido no main.py
    model = request.app.state.model
    
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado no servidor.")

    # Preparação dos dados para o sklearn
    features = np.array([[
        data.dias_desde_ultimo_pedido,
        data.pedidos_ultimo_semestre,
        data.reservas_canceladas,
        data.ticket_medio,
        data.avaliacao_media
    ]])

    prediction = int(model.predict(features)[0])
    probabilidade = model.predict_proba(features)[0].tolist()

    return {
        "churn": bool(prediction),
        "score_fidelidade": round(probabilidade[0], 4),
        "score_churn": round(probabilidade[1], 4),
        "status": "Inativo/Risco" if prediction == 1 else "Ativo"
    }
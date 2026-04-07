from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from models import BebidaInput, BebidaOutput

router = APIRouter()

bebidas = [
    {
        "id": 1,
        "nome": "Caipirinha",
        "tipo": "Coquetel",
        "alcoolica": True,
        "preco": 25.00,
    },
    {
        "id": 2,
        "nome": "Suco de Laranja",
        "tipo": "Suco",
        "alcoolica": False,
        "preco": 15.00,
    },
    {
        "id": 3,
        "nome": "Refrigerante",
        "tipo": "Refrigerante",
        "alcoolica": False,
        "preco": 10.00,
    },
    {"id": 4, "nome": "Cerveja", "tipo": "Cerveja", "alcoolica": True, "preco": 12.00},
    {
        "id": 5,
        "nome": "Água Mineral",
        "tipo": "Água",
        "alcoolica": False,
        "preco": 8.00,
    },
]


@router.get("/bebidas")
async def listar_bebidas(tipo: Optional[str] = None, alcoolica: Optional[bool] = None):

    resultado = bebidas
    if tipo:
        resultado = [b for b in resultado if b["tipo"] == tipo]
    if alcoolica is not None:
        resultado = [b for b in resultado if b["alcoolica"] == alcoolica]

    return resultado


@router.get("/bebidas/{bebida_id}")
async def buscar_bebida(bebida_id: int):
    for bebida in bebidas:
        if bebida["id"] == bebida_id:
            return bebida
    raise HTTPException(status_code=404, detail="Bebida não encontrada")


@router.post("/bebidas", response_model=BebidaOutput)
async def adicionar_bebida(bebida: BebidaInput):
    novo_id = max(b["id"] for b in bebidas) + 1
    nova_bebida = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **bebida.model_dump(),
    }
    bebidas.append(nova_bebida)
    return nova_bebida

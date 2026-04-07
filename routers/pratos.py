from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from models import PratoInput, PratoOutput, DisponibilidadeInput

router = APIRouter()

pratos = [
    # Entradas
    {
        "id": 1,
        "nome": "Dadinho de Tapioca com Geleia de Pimenta",
        "categoria": "Entrada",
        "preco": 28.00,
        "disponivel": True,
    },
    {
        "id": 2,
        "nome": "Caldinho de Feijão",
        "categoria": "Entrada",
        "preco": 18.50,
        "disponivel": True,
    },
    {
        "id": 3,
        "nome": "Porção de Pastéis (Carne, Queijo e Palmito)",
        "categoria": "Entrada",
        "preco": 35.00,
        "disponivel": True,
    },
    # Pratos Principais
    {
        "id": 4,
        "nome": "Baião de Dois",
        "categoria": "Prato Principal",
        "preco": 44.90,
        "disponivel": True,
    },
    {
        "id": 5,
        "nome": "Acarajé",
        "categoria": "Prato Principal",
        "preco": 31.00,
        "disponivel": False,
    },
    {
        "id": 6,
        "nome": "Feijoada Completa",
        "categoria": "Prato Principal",
        "preco": 50.00,
        "disponivel": True,
    },
    {
        "id": 7,
        "nome": "Moqueca Baiana",
        "categoria": "Prato Principal",
        "preco": 65.00,
        "disponivel": True,
    },
    {
        "id": 8,
        "nome": "Virado à Paulista",
        "categoria": "Prato Principal",
        "preco": 30.00,
        "disponivel": False,
    },
    # Sobremesas
    {
        "id": 9,
        "nome": "Pudim de Leite Condensado",
        "categoria": "Sobremesa",
        "preco": 15.00,
        "disponivel": True,
    },
    {
        "id": 10,
        "nome": "Mousse de Maracujá",
        "categoria": "Sobremesa",
        "preco": 18.00,
        "disponivel": True,
    },
    {
        "id": 11,
        "nome": "Brigadeiro de Colher",
        "categoria": "Sobremesa",
        "preco": 12.00,
        "disponivel": True,
    },
]


@router.get("/")
async def listar_pratos(
    categoria: Optional[str] = None,
    preco_max: Optional[float] = None,
    apenas_disponiveis: bool = False,
):

    resultado = pratos

    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]
    if preco_max:
        resultado = [p for p in resultado if p["preco"] <= preco_max]
    if apenas_disponiveis:
        resultado = [p for p in resultado if p["disponivel"]]
    return resultado


@router.get("/{prato_id}")
async def buscar_prato(prato_id: int):
    for prato in pratos:
        if prato["id"] == prato_id:
            return prato
    raise HTTPException(
        status_code=404, detail=f"Prato com id {prato_id} não encontrado"
    )


@router.get("/{prato_id}/detalhes")
async def buscar_detalhes_prato(prato_id: int, formato: str = "completo"):
    for prato in pratos:
        if prato["id"] == prato_id:
            if formato == "resumido":
                return {"nome": prato["nome"], "preco": prato["preco"]}
            return prato
    raise HTTPException(status_code=404, detail="Prato não encontrado")


@router.post("/")
async def adicionar_prato(prato: PratoInput):
    novo_id = max(p["id"] for p in pratos) + 1
    novo_prato = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **prato.model_dump(),
    }
    pratos.append(novo_prato)
    return novo_prato


@router.post("/{prato_id}/disponibilidade")
async def atualizar_disponibilidade(prato_id: int, body: DisponibilidadeInput):
    # Erro 404: recurso não existe
    prato = next((p for p in pratos if p["id"] == prato_id), None)
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")

    prato["disponivel"] = body.disponivel
    return prato

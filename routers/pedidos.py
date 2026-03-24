from fastapi import APIRouter, HTTPException
from models import PedidoInput, PedidoOutput
from routers.pratos import pratos

router = APIRouter()

@router.post("/pedidos", response_model=PedidoOutput)
async def criar_pedido(pedido: PedidoInput):
    prato = next((p for p in pratos if p["id"] == pedido.prato_id), None)
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")
    if not prato["disponivel"]:
        raise HTTPException(status_code=400, detail="Prato indisponível no momento")

    valor_total = prato["preco"] * pedido.quantidade
    novo_pedido = {
        "id": len(pratos) + 1,
        "prato_id": pedido.prato_id,
        "nome_prato": prato["nome"],
        "quantidade": pedido.quantidade,
        "valor_total": valor_total,
        "observacao": pedido.observacao
    }
    return novo_pedido
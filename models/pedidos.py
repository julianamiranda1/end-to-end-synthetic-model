from pydantic import BaseModel, Field
from typing import Optional

class PedidoInput(BaseModel):
    prato_id: int = Field(description="ID do prato a ser pedido")
    quantidade: int = Field(gt=0, description="Quantidade do prato")
    observacao: Optional[str] = Field(default=None, max_length=200, description="Observações adicionais para o pedido")

class PedidoOutput(PedidoInput):
    id: int
    prato_id: int
    nome_prato: str
    quantidade: int
    valor_total: float
    observacao: Optional[str]
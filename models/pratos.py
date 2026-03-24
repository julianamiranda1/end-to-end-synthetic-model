from pydantic import BaseModel, Field, field_validator
from typing import Optional

class PratoInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100, description="Nome do prato")
    categoria: str = Field(pattern="^(Entrada|Prato Principal|Sobremesa)$")
    preco: float = Field(gt=0, description="Preço em reais")
    descricao: Optional[str] = Field(default=None, max_length=500)
    disponivel: bool = True
    preco_promocional: float = Field(default=None, gt=0, description="Preço promocional em reais")

    @field_validator("preco_promocional")
    @classmethod
    def preco_promocional_menor_que_preco(cls, v, values):
        if v is not None and "preco" in values and v >= values["preco"]:
            raise ValueError("O preço promocional deve ser menor que o preço original")
        
        desconto = values["preco"] - v if v is not None else 0
        if desconto > 0 and desconto / values["preco"] > 0.5:
            raise ValueError("O desconto promocional não pode ser maior que 50% do preço original")
        return v
    
class PratoOutput(PratoInput):
    id: int
    nome: str
    categoria: str
    preco: float
    criado_em: str

class DisponibilidadeInput(BaseModel):
    disponivel: bool = Field(description="Indica se o prato está disponível para pedido")
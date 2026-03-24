from pydantic import BaseModel, Field

class BebidaInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100, description="Nome da bebida")
    tipo: str = Field(pattern="^(Coquetel|Suco|Refrigerante|Cerveja|Água)$", description="Tipo da bebida")
    preco: float = Field(gt=0, description="Preço da bebida")
    alcoolica: bool = Field(description="Indica se a bebida é alcoólica")
    volume_ml: int = Field(gt=50, lt=2000, description="Volume da bebida em mililitros")

class BebidaOutput(BebidaInput):
    id: int
    nome: str
    tipo: str
    preco: float
    alcoolica: bool
    volume_ml: int
    criado_em: str
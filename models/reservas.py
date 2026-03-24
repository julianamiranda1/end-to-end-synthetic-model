from pydantic import BaseModel, Field, field_validator
from config import settings
from datetime import datetime

class ReservaInput(BaseModel):
    mesa: int = Field(ge=1, le=settings.max_mesas)
    nome: str = Field(min_length=2, max_length=100)
    pessoas: int = Field(ge=1, le=settings.max_pessoas_por_mesa)
    data_hora: datetime = Field(description="Data e hora da reserva (formato ISO 8601)")

    @field_validator("data_hora")
    @classmethod
    def deve_ser_futura(cls, v):
        agora = datetime.now(tz=v.tzinfo)
        if (v - agora).total_seconds() < 3600:
            raise ValueError("Reserva deve ser feita com pelo menos 1 hora de antecedência")
        return v

class ReservaOutput(BaseModel):
    id: int
    mesa: int
    nome: str
    pessoas: int
    data_hora: str
    ativa: bool
    criada_em: str
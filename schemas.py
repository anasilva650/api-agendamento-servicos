from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

class ClienteCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    telefone: str = Field(..., min_length=8, max_length=30)
    email: str = Field(..., min_length=5, max_length=150)

class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    telefone: str
    email: str
    criado_em: datetime

class ProfissionalCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    especialidade: str = Field(..., min_length=2, max_length=100)
    ativo: bool = True

class ProfissionalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    especialidade: str
    ativo: bool

class ServicoCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    duracao_minutos: int = Field(..., gt=0, le=480)
    preco: float = Field(..., ge=0)
    ativo: bool = True

class ServicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    duracao_minutos: int
    preco: float
    ativo: bool

class AgendamentoCreate(BaseModel):
    cliente_id: int = Field(..., gt=0)
    profissional_id: int = Field(..., gt=0)
    servico_id: int = Field(..., gt=0)
    data_hora_inicio: datetime
    observacoes: Optional[str] = Field(default=None, max_length=300)

class AgendamentoStatusUpdate(BaseModel):
    status: Literal["agendado", "confirmado", "concluido", "cancelado"]

class AgendamentoUpdate(BaseModel):
    cliente_id: Optional[int] = Field(default=None, gt=0)
    profissional_id: Optional[int] = Field(default=None, gt=0)
    servico_id: Optional[int] = Field(default=None, gt=0)
    data_hora_inicio: Optional[datetime] = None
    observacoes: Optional[str] = Field(default=None, max_length=300)


class AgendamentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    profissional_id: int
    servico_id: int
    data_hora_inicio: datetime
    data_hora_fim: datetime
    status: str
    observacoes: Optional[str] = None

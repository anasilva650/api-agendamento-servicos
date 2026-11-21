import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Agendamento, Cliente, Profissional, Servico
from schemas import (
    AgendamentoCreate,
    AgendamentoResponse,
    AgendamentoStatusUpdate,
    ClienteCreate,
    ClienteResponse,
    ProfissionalCreate,
    ProfissionalResponse,
    ServicoCreate,
    ServicoResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Agendamento e Serviços", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
STATUS_BLOQUEANTES = ["agendado", "confirmado"]
TRANSICOES_VALIDAS = {
    "agendado": {"confirmado", "cancelado"},
    "confirmado": {"concluido", "cancelado"},
    "concluido": set(),
    "cancelado": set(),
}

def existe_conflito_horario(db: Session, profissional_id: int, inicio: datetime, fim: datetime) -> bool:
    return (
        db.query(Agendamento)
        .filter(
            Agendamento.profissional_id == profissional_id,
            Agendamento.status.in_(STATUS_BLOQUEANTES),
            Agendamento.data_hora_inicio < fim,
            Agendamento.data_hora_fim > inicio,
        )
        .first()
        is not None
    )

@app.get("/")
def healthcheck():
    return {"status": "ok", "servico": "API de Agendamento e Serviços"}

@app.post("/clientes", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(payload: ClienteCreate, db: Session = Depends(get_db)):
    if db.query(Cliente).filter(Cliente.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Já existe um cliente cadastrado com este e-mail.")
    cliente = Cliente(**payload.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente

@app.get("/clientes", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).all()

@app.post("/profissionais", response_model=ProfissionalResponse, status_code=status.HTTP_201_CREATED)
def criar_profissional(payload: ProfissionalCreate, db: Session = Depends(get_db)):
    prof = Profissional(**payload.model_dump())
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof

@app.get("/profissionais", response_model=List[ProfissionalResponse])
def listar_profissionais(db: Session = Depends(get_db)):
    return db.query(Profissional).all()

@app.post("/servicos", response_model=ServicoResponse, status_code=status.HTTP_201_CREATED)
def criar_servico(payload: ServicoCreate, db: Session = Depends(get_db)):
    srv = Servico(**payload.model_dump())
    db.add(srv)
    db.commit()
    db.refresh(srv)
    return srv

@app.get("/servicos", response_model=List[ServicoResponse])
def listar_servicos(db: Session = Depends(get_db)):
    return db.query(Servico).all()

@app.post("/agendamentos", response_model=AgendamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_agendamento(payload: AgendamentoCreate, db: Session = Depends(get_db)):
    if not db.query(Cliente).filter(Cliente.id == payload.cliente_id).first():
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    prof = db.query(Profissional).filter(Profissional.id == payload.profissional_id).first()
    if not prof or not prof.ativo:
        raise HTTPException(status_code=404, detail="Profissional não encontrado ou inativo.")
    srv = db.query(Servico).filter(Servico.id == payload.servico_id).first()
    if not srv or not srv.ativo:
        raise HTTPException(status_code=404, detail="Serviço não encontrado ou inativo.")

    inicio = payload.data_hora_inicio
    fim = inicio + timedelta(minutes=srv.duracao_minutos)
    if existe_conflito_horario(db, payload.profissional_id, inicio, fim):
        raise HTTPException(status_code=409, detail="Conflito de horário: profissional já possui agendamento ativo nesse intervalo.")

    ag = Agendamento(
        cliente_id=payload.cliente_id,
        profissional_id=payload.profissional_id,
        servico_id=payload.servico_id,
        data_hora_inicio=inicio,
        data_hora_fim=fim,
        status="agendado",
        observacoes=payload.observacoes,
    )
    db.add(ag)
    db.commit()
    db.refresh(ag)
    return ag

@app.get("/agendamentos", response_model=List[AgendamentoResponse])
def listar_agendamentos(
    profissional_id: Optional[int] = Query(default=None),
    status_filtro: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    q = db.query(Agendamento)
    if profissional_id is not None:
        q = q.filter(Agendamento.profissional_id == profissional_id)
    if status_filtro is not None:
        q = q.filter(Agendamento.status == status_filtro)
    return q.order_by(Agendamento.data_hora_inicio).all()

from fastapi.staticfiles import StaticFiles
app.mount("/painel", StaticFiles(directory="/home/anamis797/painel-agendamento-servicos", html=True), name="painel")

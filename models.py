from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    telefone = Column(String(30), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    agendamentos = relationship("Agendamento", back_populates="cliente")

class Profissional(Base):
    __tablename__ = "profissionais"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    especialidade = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    agendamentos = relationship("Agendamento", back_populates="profissional")

class Servico(Base):
    __tablename__ = "servicos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    duracao_minutos = Column(Integer, nullable=False)
    preco = Column(Float, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    agendamentos = relationship("Agendamento", back_populates="servico")

class Agendamento(Base):
    __tablename__ = "agendamentos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    servico_id = Column(Integer, ForeignKey("servicos.id"), nullable=False)
    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime, nullable=False)
    status = Column(String(20), default="agendado", nullable=False)
    observacoes = Column(String(300), nullable=True)
    cliente = relationship("Cliente", back_populates="agendamentos")
    profissional = relationship("Profissional", back_populates="agendamentos")
    servico = relationship("Servico", back_populates="agendamentos")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def criar_dados_base(client: TestClient):
    cli = client.post(
        "/clientes",
        json={
            "nome": "Beatriz Costa",
            "telefone": "21999990000",
            "email": "beatriz.costa@exemplo.com",
        },
    )
    assert cli.status_code == 201, cli.text

    prof = client.post(
        "/profissionais",
        json={
            "nome": "Dra. Marina Souza",
            "especialidade": "Pediatra",
            "ativo": True,
        },
    )
    assert prof.status_code == 201, prof.text

    srv = client.post(
        "/servicos",
        json={
            "nome": "Consulta Pediátrica",
            "duracao_minutos": 60,
            "preco": 250.0,
            "ativo": True,
        },
    )
    assert srv.status_code == 201, srv.text

    return cli.json()["id"], prof.json()["id"], srv.json()["id"]


def test_bloqueia_sobreposicao_de_horario(client):
    cliente_id, profissional_id, servico_id = criar_dados_base(client)

    r1 = client.post(
        "/agendamentos",
        json={
            "cliente_id": cliente_id,
            "profissional_id": profissional_id,
            "servico_id": servico_id,
            "data_hora_inicio": "2026-12-08T13:30:00",
            "observacoes": "Consulta inicial",
        },
    )
    assert r1.status_code == 201, r1.text

    r2 = client.post(
        "/agendamentos",
        json={
            "cliente_id": cliente_id,
            "profissional_id": profissional_id,
            "servico_id": servico_id,
            "data_hora_inicio": "2026-12-08T14:00:00",
            "observacoes": "Tentativa com sobreposição",
        },
    )
    assert r2.status_code == 409, r2.text


def test_permite_inicio_no_horario_exato_de_termino(client):
    cliente_id, profissional_id, servico_id = criar_dados_base(client)

    r1 = client.post(
        "/agendamentos",
        json={
            "cliente_id": cliente_id,
            "profissional_id": profissional_id,
            "servico_id": servico_id,
            "data_hora_inicio": "2026-12-08T13:30:00",
        },
    )
    assert r1.status_code == 201, r1.text

    r2 = client.post(
        "/agendamentos",
        json={
            "cliente_id": cliente_id,
            "profissional_id": profissional_id,
            "servico_id": servico_id,
            "data_hora_inicio": "2026-12-08T14:30:00",
        },
    )
    assert r2.status_code == 201, r2.text


def test_libera_horario_apos_cancelamento(client):
    cliente_id, profissional_id, servico_id = criar_dados_base(client)

    r1 = client.post(
        "/agendamentos",
        json={
            "cliente_id": cliente_id,
            "profissional_id": profissional_id,
            "servico_id": servico_id,
            "data_hora_inicio": "2026-12-08T13:30:00",
        },
    )
    assert r1.status_code == 201, r1.text
    agendamento_id = r1.json()["id"]

    cancel = client.patch(
        f"/agendamentos/{agendamento_id}/status",
        json={"status": "cancelado"},
    )
    assert cancel.status_code == 200, cancel.text
    assert cancel.json()["status"] == "cancelado"

    r2 = client.post(
        "/agendamentos",
        json={
            "cliente_id": cliente_id,
            "profissional_id": profissional_id,
            "servico_id": servico_id,
            "data_hora_inicio": "2026-12-08T13:30:00",
        },
    )
    assert r2.status_code == 201, r2.text

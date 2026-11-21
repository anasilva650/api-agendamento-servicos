# API de Agendamento e Serviços

API REST desenvolvida com **FastAPI**, **SQLAlchemy**, **SQLite** e **Pydantic**, com prevenção de conflito de horário (`409 Conflict`) e validação de transições de status (`422 Unprocessable Entity`).

## Endpoints principais
- `GET /` — Healthcheck
- `POST /clientes` e `GET /clientes` — Cadastro e listagem de clientes
- `POST /profissionais` e `GET /profissionais` — Cadastro e listagem de profissionais
- `POST /servicos` e `GET /servicos` — Cadastro e listagem de serviços
- `POST /agendamentos` e `GET /agendamentos` — Criação com checagem de conflito de horário e listagem com filtros
- `PATCH /agendamentos/{agendamento_id}/status` — Atualização controlada de status

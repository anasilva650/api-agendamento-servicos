# API de Agendamento e Serviços

## Acesso Online (Deploy no Render)

- **Painel Web:** https://api-agendamento-servicos.onrender.com/painel/
- **Documentação Interativa (Swagger):** https://api-agendamento-servicos.onrender.com/docs
- **Status da API:** https://api-agendamento-servicos.onrender.com/

> *Nota: no plano gratuito do Render, a primeira requisição após inatividade pode levar cerca de 50 segundos para iniciar.*

API REST desenvolvida com **Python**, **FastAPI**, **SQLAlchemy** e **SQLite** para gestão de clientes, profissionais, serviços e agendamentos com validação automática de conflitos de horário.

## Funcionalidades

- Cadastro e listagem de **clientes** (`POST /clientes`, `GET /clientes`)
- Cadastro e listagem de **profissionais** (`POST /profissionais`, `GET /profissionais`)
- Cadastro e listagem de **serviços** com duração e preço (`POST /servicos`, `GET /servicos`)
- Criação e listagem de **agendamentos** com filtro por `profissional_id` e `status` (`POST /agendamentos`, `GET /agendamentos`)
- Cálculo automático do horário de término com base em `duracao_minutos` e bloqueio de sobreposição de horários para o mesmo profissional (HTTP `409 Conflict`)

## Como instalar e executar localmente

```bash
# 1. Clonar o repositório
git clone https://github.com/anasilva650/api-agendamento-servicos.git
cd api-agendamento-servicos

# 2. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Iniciar o servidor na porta 8080
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## Documentação interativa (`/docs`)

Com o servidor em execução, abra no navegador:

- **Swagger UI:** `http://127.0.0.1:8080/docs`
- **Painel Web:** `http://127.0.0.1:8080/painel`

## Exemplo de consulta fictícia

A sequência abaixo cria os registos base e agenda uma consulta de 60 minutos (das `13:30` às `14:30`) diretamente em `/docs` ou via `curl`:

### 1. Criar cliente (`POST /clientes`)
```json
{
  "nome": "Beatriz Costa",
  "telefone": "21999990000",
  "email": "beatriz.costa@exemplo.com"
}
```

### 2. Criar profissional (`POST /profissionais`)
```json
{
  "nome": "Dra. Marina Souza",
  "especialidade": "Pediatra",
  "ativo": true
}
```

### 3. Criar serviço (`POST /servicos`)
```json
{
  "nome": "Consulta Pediátrica",
  "duracao_minutos": 60,
  "preco": 250.0,
  "ativo": true
}
```

### 4. Agendar consulta (`POST /agendamentos`)
```json
{
  "cliente_id": 1,
  "profissional_id": 1,
  "servico_id": 1,
  "data_hora_inicio": "2026-12-08T13:30:00",
  "observacoes": "Consulta de rotina"
}
```

### 5. Consultar agendamentos por profissional e status (`GET /agendamentos`)
```bash
curl "http://127.0.0.1:8080/agendamentos?profissional_id=1&status=agendado"
```

## Executar os testes automatizados

```bash
pytest -v
```

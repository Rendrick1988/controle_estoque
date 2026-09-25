# Tecnologias, Linguagens e Ambientes

## Linguagens

- Python
- JavaScript
- HTML5
- CSS3
- SQL

## Frameworks e bibliotecas principais

- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Pydantic Settings
- Uvicorn
- Chart.js
- psycopg2
- python-jose
- bcrypt
- ReportLab
- Pyright (análise estática de tipos Python; dependência de desenvolvimento npm)
- Controle de permissões por rota (`app/core/authorization.py`, `app/dependencies/authorization.py`)
- Limites por plano (`app/services/plan_limits_service.py`)

## Banco de dados

- PostgreSQL

## Ambientes

- Desenvolvimento local com `.venv`
- Configuração por variáveis de ambiente com `.env`
- Docker
- Docker Compose
- Dev Container do VS Code (`.devcontainer`)
- Execução web via `Procfile`
- Node.js e npm para executar o Pyright pelo terminal

## Versões identificadas no repositório

- Python local: `3.14.0`
- Python no Docker: `3.12`
- PostgreSQL no Docker Compose: `16-alpine`
- Chart.js no frontend: `4.4.1`

## Observação

- O frontend foi feito com HTML, CSS e JavaScript puros, sem framework frontend como React, Vue ou Angular.

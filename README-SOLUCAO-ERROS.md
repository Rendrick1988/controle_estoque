# Guia de solução de erros — Controle de Estoque

Este documento concentra **sintomas**, **causas prováveis** e **passo a passo** para corrigir problemas comuns ao rodar ou implantar o projeto.

---

## 1. Erro de conexão com o PostgreSQL

### Sintomas

- Mensagem no terminal ou no log parecida com `could not connect to server`, `Connection refused`, `password authentication failed` ou `database "controle_estoque" does not exist`.
- A API sobe mas qualquer rota que usa o banco retorna **500**.

### Passo a passo

1. Confirme se o **serviço PostgreSQL está rodando** (Serviços do Windows, `pg_ctl`, Docker do banco, etc.).
2. Abra seu `.env` na **raiz do repositório** e localize `DATABASE_URL`.
3. Verifique se a URL está no formato esperado pelo SQLAlchemy com **psycopg2**:
   - Deve começar com `postgresql+psycopg2://`
   - Estrutura: `postgresql+psycopg2://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO`
4. Teste usuário e senha com `psql`, pgAdmin ou outro cliente apontando para o mesmo host/porta.
5. Confirme que o **banco com o nome da URL existe** (`CREATE DATABASE controle_estoque;` se necessário).
6. Se o Postgres exige SSL (comum em provedores), adicione na URL algo como `?sslmode=require` (consulte a documentação do provedor).
7. Salve o `.env`, reinicie o **uvicorn** (ou `docker compose restart web`).
8. Rode de novo as migrations: `python -m alembic upgrade head` (com o mesmo Python/venv do projeto).

### Se usar Docker Compose

- Dentro do container `web`, o host do banco é **`db`**, não `localhost`. O `compose.yaml` já define `DATABASE_URL` apontando para `db`.
- Se você alterou senha ou nome do banco no serviço `db`, ajuste `DATABASE_URL` no Compose ou nas variáveis de ambiente para combinar com o serviço `postgres`.

---

## 2. Falha nas migrations (Alembic)

### Sintomas

- `alembic upgrade head` falha com erro SQL, tabela já existe, revisão inconsistente, etc.

### Passo a passo

1. Execute sempre a partir da **raiz do projeto** (onde estão `alembic.ini` e a pasta `app`).
2. Use o **mesmo interpretador** onde instalou as dependências:
   - `python -m alembic upgrade head`  
   Não use outro `alembic` do PATH se for de outro Python.
3. Ative o venv antes, se rodar localmente: `.\.venv\Scripts\Activate.ps1` (Windows) ou `source .venv/bin/activate` (Linux/macOS).
4. Confirme que `DATABASE_URL` no `.env` aponta para o banco **correto** (veja seção 1).
5. Leia a **mensagem de erro completa**: erros de “relation already exists” costumam indicar banco parcialmente migrado ou ambiente duplicado.
6. Em ambiente de **desenvolvimento**, se o banco for descartável, pode apagar o banco, recriar vazio e rodar de novo `python -m alembic upgrade head`. **Não faça isso em produção sem backup.**

---

## 3. Login retorna 500 (Internal Server Error)

### Sintomas

- `POST /api/auth/login` responde **500** quando o usuário existe e a senha é testada; com usuário inexistente pode retornar **401**.

### Causa histórica comum

- Incompatibilidade antiga entre **passlib** e versões novas do **bcrypt**. O projeto passou a usar **`bcrypt` direto** em `app/core/security.py`.

### Passo a passo

1. Atualize dependências: `pip install -r requirements.txt`.
2. Reinicie o servidor.
3. Se persistir, veja o **stack trace** no terminal do Uvicorn para identificar a linha exata.

---

## 4. Login 401 — “Credenciais inválidas”

### Passo a passo

1. Confirme **e-mail e senha** (sem espaços extras no navegador).
2. Verifique se o usuário existe no banco (mesmo e-mail cadastrado).
3. Lembre-se: senha errada sempre retorna **401**, não 500.

---

## 5. Login 403 — empresa pendente ou bloqueada

### Sintomas

- Mensagem como empresa aguardando ativação ou bloqueada.

### Passo a passo

1. Confira o **plano** da empresa: cadastro com plano **Free** deve ficar **`active`** na hora. Planos **pagos** ficam **`pending`** até o **pagamento no Mercado Pago** ser confirmado (checkout + webhook); conclua o fluxo ou veja `payment_status` / logs de billing.
2. Se a empresa estiver **`blocked`** ou **`pending`**, ninguém dessa empresa acessa o ERP; **regularize pelo fluxo esperado** (pagamento/conciliação Mercado Pago) ou altere **`companies.status`** diretamente na base apenas se você souber o que faz (não há painel `/admin` nem `/api/admin` neste repositório).
3. **`User.role = admin`** é administrador **dentro da empresa**; também fica barrado quando `company.status != active`.

---

## 6. Variáveis do `.env` “não pegam”

### Sintomas

- `DATABASE_URL`, `SECRET_KEY` ou outras variáveis parecem ignoradas.

### Passo a passo

1. O arquivo deve se chamar **`.env`** e ficar na **raiz do repositório** (ao lado de `requirements.txt`).
2. **Sem espaço** depois do `=`:
   - Errado: `SECRET_KEY= valor`
   - Certo: `SECRET_KEY=valor`
3. **Execução local com Uvicorn:** o app carrega `.env` pela raiz do repositório (`app/core/config.py`); rode o servidor a partir da pasta do projeto.
4. **Docker Compose:** variáveis do seu `.env` na pasta do projeto entram por **interpolação** no `compose.yaml`. Configure `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB`; o Compose monta a URL do serviço `web` usando o host `db`. Para executar Python diretamente na máquina, configure `DATABASE_URL` com `localhost`. Depois de mudar `.env`, faça `docker compose up --build` ou recrie os containers.

---

## 7. CORS — navegador bloqueia chamadas à API

### Sintomas

- Erro no console do tipo “blocked by CORS”, “No Access-Control-Allow-Origin”.

### Passo a passo

1. Abra `.env` e localize `CORS_ORIGINS`.
2. Inclua **exatamente** a origem do front (protocolo + host + porta), **sem barra no final**, separando várias por vírgula:
   - Exemplo: `http://localhost:8000,http://127.0.0.1:8000`
3. Se o front abre em outra porta ou em **HTTPS** em produção, adicione essa origem também.
4. Reinicie o servidor e teste de novo (às vezes é preciso fechar abas antigas ou testar em aba anônima).

---

## 8. 403 — “Funcionalidade desativada para esta empresa”

### Sintomas

- Rotas de vendas, relatórios ou dashboard retornam **403** com menção a feature.

### Passo a passo

1. As flags ficam em **Configurações da empresa** (`CompanySettings.features`): `vendas`, `relatorio`, `dashboard_avancado`.
2. No app web, vá em **Configurações** e **ative** a funcionalidade correspondente (se você for o dono e a UI permitir).
3. Ou ajuste direto no banco/API conforme sua política (apenas com conhecimento do modelo de dados).

---

## 9. 403 — limites do plano, permissões ou exportação (PDF / impressão)

### Sintomas

- Mensagem sobre limite de produtos, clientes, usuários, vendas, relatórios, dashboard ou auditoria.
- PDF ou impressão do relatório retorna **403** (“não estão liberados para o plano atual”).

### O que é esperado

- Planos **`free`**, **`basic`**, **`professional`** e **`premium`** têm **tetos** e janelas diferentes (`app/core/plans.py`); a API aplica isso via `plan_usage` em `GET /api/auth/me`.
- **Exportação PDF / impressão** depende de `plan_usage.exports_enabled`, da feature **`relatorio`** e das permissões do usuário (ver `app/routes/reports.py` e `plan_limits_service.ensure_premium_exports`).
- Telas **Usuários** e **Auditoria** exigem ser **dono da empresa** na UI atual.
- Rotas da empresa exigem permissão (`products:write`, etc.); o dono tem conjunto ampliado.

### Passo a passo

1. Chame `GET /api/auth/me` autenticado e veja `plan_usage` (uso, tetos e `exports_enabled`).
2. Compare `plan_usage.used` com `plan_usage.caps` para ver se bateu no limite.
3. Para exportação: confirme **`exports_enabled`**, feature **`relatorio`** e usuário com permissão.
4. Se a falha for em **Usuários** ou **Auditoria**, entre com o **dono** da empresa.
5. Se o problema for **teto do plano**, atualize **`company.plan`** (ou exclua dados para liberar cota), conforme sua política e **somente com cuidado** no banco — não há operações multiempresa prontas no app para isso.
6. Para **checkout / webhook** do Mercado Pago, confira `APP_BASE_URL`, `MERCADO_PAGO_ACCESS_TOKEN` e a seção de billing no [README.md](README.md).

---

## 10. Docker — `docker compose up` falha ou porta em uso

### Passo a passo

1. Confirme **Docker Desktop** (ou Engine) em execução.
2. Se a porta **8000** ou **5432** estiver ocupada, feche o outro programa ou altere o mapeamento no `compose.yaml` (ex.: `"8001:8000"`).
3. Após mudar `requirements.txt`, rode `docker compose up --build`.
4. Para resetar o volume do Postgres (apaga dados): `docker compose down -v` (só em dev).

---

## 11. Tela em branco ou dados antigos no navegador

### Passo a passo

1. Faça **hard refresh**: `Ctrl + F5` (Windows) ou equivalente.
2. Limpe cache do site ou teste em **janela anônima**.
3. Confira o console do navegador (F12 → Console / Rede) para ver se há **404** em `app.js`, `styles.css` ou erros de JavaScript.

---

## 12. Token / JWT inválido após mudar `SECRET_KEY`

### Sintomas

- **401** em rotas protegidas logo após alterar `SECRET_KEY` no `.env`.

### Passo a passo

1. É esperado: tokens antigos foram assinados com a chave anterior.
2. Faça **logout** no app e **login** de novo para obter um token novo.

---

## 13. Como obter mais detalhes de um erro

### Passo a passo

1. Olhe o **terminal** onde o Uvicorn está rodando: stack traces aparecem ali.
2. Abra `http://127.0.0.1:8000/docs` e execute a mesma requisição pelo Swagger para ver o corpo da resposta.
3. Na aba **Rede** do navegador (F12), clique na requisição falha e leia **status**, **resposta** e **cabeçalhos**.

---

## 14. Uvicorn com `--reload` falha no Windows (`WinError 5`)

### Sintomas

- O comando `python -m uvicorn app.main:app --reload ...` entra em loop de erro.
- O log mostra `PermissionError: [WinError 5] Acesso negado` em `multiprocessing` / `CreateNamedPipe`.

### Passo a passo

1. Suba **sem** `--reload`:  
   `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
2. Ou use o launcher do repositório (se existir no seu clone): `python run_dev.py` — no Windows costuma desativar reload para evitar esse erro.
3. Em Linux/macOS ou **dentro do Docker**, o `--reload` costuma funcionar normalmente.

### Observação

- O problema é conhecido em alguns ambientes Windows com Python recente; Docker Compose continua usando `--reload` no container Linux.

---

## 15. Erro 422 ao cadastrar ou editar produto (“Field required” / `validity`)

### Sintomas

- Ao salvar produto, a API responde **422 Unprocessable Entity** ou mensagem de validação do Pydantic.
- O corpo da requisição não inclui `validity`.

### Causa

- O endpoint `POST /api/products` exige o campo **`validity`** (data/hora). O front deve enviar JSON com esse campo (o formulário web usa o input **Validade** em `name="validity"`).

### Passo a passo

1. No cadastro web, preencha o campo **Validade** (data futura ou hoje).
2. Faça **hard refresh** (`Ctrl+F5`) para carregar o `app.js` atualizado.
3. No Swagger (`/docs`), inclua `validity` no JSON (ex.: `"validity": "2027-12-31T12:00:00"` em ISO 8601).

---

## Resumo rápido

| Sintoma | Onde olhar primeiro |
|--------|----------------------|
| Banco / 500 em API | `DATABASE_URL`, Postgres ligado, `alembic upgrade head` |
| `.env` ignorado | Espaços após `=`, caminho do arquivo, Docker Compose |
| Login | Credenciais, `status` da empresa, logs do servidor |
| Navegador / CORS | `CORS_ORIGINS` |
| Função desligada | Feature flags em configurações |
| Limites / PDF | Planos `free` / `basic` / `professional` / `premium`, `GET /api/auth/me` → `plan_usage` (tetos e `exports_enabled`); pagamentos: **Mercado Pago** (`README.md`) |
| Produto 422 | Campo **`validity`** obrigatório no JSON; formulário com data de validade |

Para visão geral do projeto, instalação e deploy, use o **`README.md`** principal na raiz do repositório.

Histórico de **migrations** e tabela **`audit_logs`**: [README-AUDITORIA-BANCO.md](README-AUDITORIA-BANCO.md).

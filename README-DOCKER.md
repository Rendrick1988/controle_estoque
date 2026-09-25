# Docker no Projeto Controle de Estoque

Guia prático para usar **Docker Compose** neste projeto localmente, com os comandos mais úteis do dia a dia.

Todos os comandos abaixo devem ser executados na raiz do projeto:

```powershell
cd g:\controle_estoque
```

## O que o Docker sobe aqui

O arquivo [compose.yaml](compose.yaml) sobe dois serviços:

- `db`: PostgreSQL 16
- `web`: FastAPI + frontend estático

Ao iniciar o serviço `web`, o projeto também roda:

```bash
python -m alembic upgrade head
```

Depois disso, a aplicação sobe em:

- Frontend: `http://localhost:8000/`
- Swagger / OpenAPI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/healthz`

O PostgreSQL fica disponível em:

- host: `localhost`
- porta: `5434` (mapeada no `compose.yaml`; evita conflito com Postgres nativo nas portas `5432`/`5433`)
- database: `controle_estoque`
- usuário: `postgres`
- senha: `postgres`

## Pré-requisitos

Antes de começar:

1. Instale o [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Abra o Docker Desktop e aguarde o status **Running** (ícone da baleia na bandeja do Windows).
3. Confira se as portas do projeto estão livres (passo a passo na seção seguinte).

### Verificar portas antes de subir (passo a passo)

O projeto usa estas portas no **host** (sua máquina):

| Porta | Serviço | Observação |
|-------|---------|------------|
| `8000` | API + frontend (`web`) | deve estar livre |
| `5434` | PostgreSQL do Docker (`db`) | mapeada no `compose.yaml` |

No Windows, é comum já existir **PostgreSQL instalado localmente** nas portas `5432` (versão 16) e `5433` (versão 18). Isso **não impede** o Docker, desde que a porta **`5434`** esteja livre.

**Passo 1 — abra o PowerShell na raiz do projeto:**

```powershell
cd g:\controle_estoque
```

**Passo 2 — veja quem está usando as portas:**

```powershell
netstat -ano | findstr "LISTENING" | findstr ":8000 :5434"
```

- Se **não aparecer nada**, as portas estão livres.
- Se aparecer uma linha com `:8000` ou `:5434`, anote o **PID** (última coluna).

**Passo 3 — identifique o processo (opcional):**

```powershell
tasklist /FI "PID eq NUMERO_DO_PID"
```

**Passo 4 — decida a ação:**

- Porta `8000` ocupada → feche o outro processo ou altere o mapeamento em [compose.yaml](compose.yaml) (ex.: `"8001:8000"`).
- Porta `5434` ocupada → altere em [compose.yaml](compose.yaml) para outra porta livre (ex.: `"5435:5432"`) e use a **mesma porta** no pgAdmin.

**Passo 5 — teste rápido com o Docker (após subir):**

```powershell
docker compose ps
```

O serviço `db` deve mostrar `healthy` e algo como `0.0.0.0:5434->5432/tcp`.

## Variáveis de ambiente (`.env` + Compose)

1. Copie o modelo: na raiz do projeto, crie `.env` a partir de [`.env.example`](.env.example) (o arquivo `.env` **não** deve ser commitado; o [`.dockerignore`](.dockerignore) evita enviá-lo no *build* da imagem).
2. O serviço **`db`** e a URL de conexão do serviço **`web`** usam `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB` definidos no `.env`. O Compose usa o host interno `db`; não é necessário guardar outra URL de banco para o container.
3. As variáveis de aplicação entram por interpolação no `compose.yaml`; defina os segredos no `.env` local, que não deve ser commitado:

| Variável | Uso no Docker |
|----------|----------------|
| `POSTGRES_USER` | Usuário do banco local (padrão `postgres`). |
| `POSTGRES_PASSWORD` | Senha local do PostgreSQL; obrigatória e mantida somente no `.env`. |
| `POSTGRES_DB` | Nome do banco local (padrão `controle_estoque`). |
| `DATABASE_URL` | Uso de Python direto na máquina; o Compose gera a URL interna com host `db`. |
| `SECRET_KEY` | Assinatura JWT; obrigatória no Compose. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token de API. |
| `PASSWORD_RESET_EXPIRE_MINUTES` | Validade do JWT de recuperação de senha. |
| `PASSWORD_RESET_TOKEN_IN_RESPONSE` | Se `true`, a API devolve `reset_token` no JSON de `forgot-password` (ambiente controlado; veja README-SEGURANCA.md). |
| `CORS_ORIGINS` | Origens permitidas (lista separada por vírgula, sem barra final). |
| `APP_BASE_URL` | URL pública do app (retorno Mercado Pago, webhook padrão de billing). |
| `MERCADO_PAGO_ACCESS_TOKEN` | Checkout de planos pagos (vazio = checkout indisponível, 503). |
| `MERCADO_PAGO_PUBLIC_KEY` | Opcional / reservado para o front. |
| `MERCADO_PAGO_API_BASE_URL` | Padrão `https://api.mercadopago.com`. |
| `MERCADO_PAGO_NOTIFICATION_URL` | Se vazio, o webhook usa `{APP_BASE_URL}/api/billing/mercado-pago/webhook`. |
| `RUN_MIGRATIONS` | `1` (padrão) aplica `alembic upgrade head` no `run_production.py`; no **dev** o `compose` já roda migrations no `command` do `web`. |

**Banco já inicializado:** a [imagem oficial do PostgreSQL](https://hub.docker.com/_/postgres) aplica `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB` somente quando cria o volume vazio. Se já existe o volume `postgres_data`, mantenha esses valores compatíveis com o banco atual; alterar o `.env` sozinho não troca a senha armazenada no banco. Não remova o volume para tentar corrigir a senha se ele contiver dados que precisam ser preservados.

Mais detalhes de segurança (segredos, CORS): [README-SEGURANCA.md](README-SEGURANCA.md).

## 1. Subir o projeto pela primeira vez

**Passo 1 — vá até a raiz do projeto:**

```powershell
cd g:\controle_estoque
```

**Passo 2 — (opcional) confira se as portas `8000` e `5434` estão livres** (veja [Verificar portas antes de subir](#verificar-portas-antes-de-subir-passo-a-passo)).

**Passo 3 — suba os containers com build:**

```powershell
docker compose up --build
```

O que esse comando faz:

- cria a imagem do serviço `web`
- sobe o PostgreSQL na porta **`5434`** do host
- sobe a aplicação na porta **`8000`**
- aplica as migrations automaticamente (`alembic upgrade head`)
- deixa os logs aparecendo no terminal

**Passo 4 — aguarde até ver:**

- `database system is ready to accept connections` (logs do `db`)
- `Uvicorn running on http://0.0.0.0:8000` (logs do `web`)

**Passo 5 — teste no navegador:**

- `http://localhost:8000/`
- `http://localhost:8000/docs`
- `http://localhost:8000/healthz` → deve retornar `"database": "reachable"`

**Passo 6 — (opcional) cadastre o banco no pgAdmin** (seção 12).

## 2. Subir em segundo plano

Se você não quiser deixar os logs ocupando o terminal:

```powershell
docker compose up -d --build
```

Depois você pode acompanhar os logs com:

```powershell
docker compose logs -f web
```

## 3. Ver o status dos containers

```powershell
docker compose ps
```

Esse comando mostra se `web` e `db` estão:

- `running`
- `exited`
- `healthy`

## 4. Ver logs

Logs do backend:

```powershell
docker compose logs -f web
```

Logs do PostgreSQL:

```powershell
docker compose logs -f db
```

Logs de tudo:

```powershell
docker compose logs -f
```

## 5. Parar sem remover os containers

Se você quer parar temporariamente:

```powershell
docker compose stop
```

Para subir novamente depois:

```powershell
docker compose start
```

Use esse fluxo quando quiser retomar rápido sem recriar os containers.

## 6. Derrubar os containers do projeto

Se você quer parar e remover os containers e a rede do Compose:

```powershell
docker compose down
```

Esse comando:

- para os containers
- remove os containers
- remove a rede criada pelo Compose

Esse comando **não apaga o banco** salvo no volume.

## 7. Derrubar tudo e apagar o banco local

Se você quer zerar o ambiente local, inclusive os dados do PostgreSQL:

```powershell
docker compose down -v
```

Atenção:

- esse comando apaga o volume do Postgres
- seus dados locais serão removidos
- use só quando realmente quiser recriar o banco do zero

## 8. Reiniciar um serviço específico

Reiniciar só o backend:

```powershell
docker compose restart web
```

Reiniciar só o banco:

```powershell
docker compose restart db
```

## 9. Rebuildar a imagem do backend

Use quando mudar algo que afeta a imagem, por exemplo:

- `requirements.txt`
- `Dockerfile`
- dependências do sistema

Comando:

```powershell
docker compose up --build
```

Se quiser forçar rebuild sem cache:

```powershell
docker compose build --no-cache web
docker compose up
```

## 10. Entrar no container da aplicação

Abrir shell dentro do container `web`:

```powershell
docker compose exec web sh
```

Lá dentro você pode rodar comandos como:

```bash
python -m alembic current
python -m alembic upgrade head
```

## 11. Entrar no PostgreSQL pelo terminal

### Opção A — dentro do container (recomendado)

**Passo 1:**

```powershell
cd g:\controle_estoque
docker compose exec db psql -U postgres -d controle_estoque
```

Não é necessário informar porta: você já está **dentro** do container `db`.

### Opção B — do Windows, pela porta do Docker (`5434`)

**Passo 1:**

```powershell
$env:PGPASSWORD = "postgres"
psql -h 127.0.0.1 -p 5434 -U postgres -d controle_estoque
```

Exemplos úteis dentro do `psql`:

```sql
\dt
SELECT * FROM companies;
SELECT * FROM users;
SELECT * FROM products;
```

Para sair:

```sql
\q
```

## 12. Usar o pgAdmin com o banco do Docker

O pgAdmin **não vem no Docker** deste projeto. Use o instalado no Windows (geralmente junto com o PostgreSQL):

- `C:\Program Files\PostgreSQL\18\pgAdmin 4\runtime\pgAdmin4.exe`
- ou `C:\Program Files\PostgreSQL\16\pgAdmin 4\runtime\pgAdmin4.exe`

### Dados de conexão (resumo)

| Campo | Valor |
|-------|--------|
| Host name/address | `localhost` |
| Port | **`5434`** |
| Maintenance database | `controle_estoque` |
| Username | `postgres` |
| Password | `postgres` |

### Cadastrar o servidor no pgAdmin (passo a passo)

**Passo 1 — suba o Docker** (se ainda não estiver rodando):

```powershell
cd g:\controle_estoque
docker compose up -d
docker compose ps
```

Confirme que `controle_estoque-db-1` está `healthy`.

**Passo 2 — abra o pgAdmin 4.**

**Passo 3 — registre um novo servidor:**

1. No painel esquerdo, clique com o botão direito em **Servers**
2. **Register** → **Server…**

**Passo 4 — aba General:**

1. **Name:** `Controle Estoque (Docker)` (ou outro nome que preferir)

**Passo 5 — aba Connection:**

1. **Host name/address:** `localhost`
2. **Port:** `5434`
3. **Maintenance database:** `controle_estoque`
4. **Username:** `postgres`
5. **Password:** `postgres`
6. Marque **Save password** (opcional, para não digitar sempre)

**Passo 6 — clique em Save.**

Se pedir senha na primeira vez, use `postgres`.

**Passo 7 — navegue até as tabelas:**

1. **Servers**
2. **Controle Estoque (Docker)**
3. **Databases**
4. **controle_estoque**
5. **Schemas**
6. **public**
7. **Tables**

Tabelas esperadas: `users`, `companies`, `products`, `customers`, `sales`, `sale_items`, `audit_logs`, `company_settings`, `alembic_version`.

### Servidores que o pgAdmin detecta sozinho

O pgAdmin pode listar automaticamente:

- **PostgreSQL 16** → porta `5432` (nativo Windows)
- **PostgreSQL 18** → porta `5433` (nativo Windows)

Esses **não são** o banco do Docker. Você pode:

- **manter** só como referência, ou
- **Remove Server** no pgAdmin se não usar mais (isso não apaga o PostgreSQL do Windows).

Para o projeto **Controle de Estoque**, use **sempre** o servidor na porta **`5434`**.

### Conectar pelo terminal (alternativa ao pgAdmin)

Do host Windows, com `psql` no PATH:

```powershell
$env:PGPASSWORD = "postgres"
psql -h 127.0.0.1 -p 5434 -U postgres -d controle_estoque
```

Dentro do container (não precisa da porta `5434`):

```powershell
docker compose exec db psql -U postgres -d controle_estoque
```

## 13. Verificar se o banco está íntegro (passo a passo)

Use esta checagem após subir o Docker, mudar portas ou remover uma cópia antiga do banco no Windows.

### Passo 1 — containers e saúde

```powershell
cd g:\controle_estoque
docker compose ps
```

Esperado:

- `controle_estoque-db-1` → **Up** e **(healthy)**
- `controle_estoque-web-1` → **Up**
- coluna PORTS do `db` → `0.0.0.0:5434->5432/tcp`

### Passo 2 — API consegue falar com o banco

No PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/healthz
```

Esperado:

```json
{"status":"ok","database":"reachable"}
```

### Passo 3 — conexão direta na porta do Docker

```powershell
$env:PGPASSWORD = "postgres"
psql -h 127.0.0.1 -p 5434 -U postgres -d controle_estoque -c "SELECT current_database(), version();"
```

Esperado: banco `controle_estoque` e PostgreSQL **16.x** (imagem Alpine do container).

### Passo 4 — schema e migration

```powershell
psql -h 127.0.0.1 -p 5434 -U postgres -d controle_estoque -c "\dt"
psql -h 127.0.0.1 -p 5434 -U postgres -d controle_estoque -c "SELECT version_num FROM alembic_version;"
```

Esperado:

- **9 tabelas** em `public` (incluindo `alembic_version`)
- revisão Alembic igual à mais recente em `alembic/versions/` (consulte com `docker compose exec web python -m alembic current`)

### Passo 5 — contagem rápida de registros (opcional)

```powershell
psql -h 127.0.0.1 -p 5434 -U postgres -d controle_estoque -c "
SELECT 'companies' AS tabela, COUNT(*) FROM companies
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sales', COUNT(*) FROM sales
ORDER BY tabela;"
```

Anote os números antes de qualquer limpeza; depois compare para ver se algo sumiu.

### Passo 6 — confirmar que o banco antigo nativo foi removido (opcional)

Se você apagou a cópia antiga no PostgreSQL do Windows (`5432`):

```powershell
psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c "SELECT datname FROM pg_database WHERE datname = 'controle_estoque';"
```

- **0 linhas** → a cópia nativa não existe mais (normal após exclusão).
- Isso **não afeta** o banco do Docker na porta `5434`.

## 14. Rodar migrations manualmente

Na maioria dos casos, o próprio container `web` já roda as migrations ao subir.

Se você quiser executar manualmente:

```powershell
docker compose exec web python -m alembic upgrade head
```

Para ver a revisão atual:

```powershell
docker compose exec web python -m alembic current
```

## 15. Fluxo recomendado do dia a dia

Fluxo normal:

1. abrir o Docker Desktop (se estiver fechado)
2. `docker compose up --build` ou `docker compose up -d`
3. conferir com `docker compose ps` (banco `healthy`)
4. trabalhar no projeto em `http://localhost:8000/`
5. ver dados no pgAdmin → **Controle Estoque (Docker)** → porta `5434`
6. acompanhar com `docker compose logs -f web`
7. ao terminar, usar `docker compose stop` ou `docker compose down`

Fluxo para retomar depois:

1. `docker compose start`
2. conferir com `docker compose ps`
3. acessar a aplicação normalmente

Fluxo para resetar o banco local:

1. `docker compose down -v`
2. `docker compose up --build`

## 16. Comandos rápidos

Subir:

```powershell
docker compose up --build
```

Subir em segundo plano:

```powershell
docker compose up -d --build
```

Ver status:

```powershell
docker compose ps
```

Ver logs do backend:

```powershell
docker compose logs -f web
```

Parar sem remover:

```powershell
docker compose stop
```

Subir de novo após `stop`:

```powershell
docker compose start
```

Derrubar containers:

```powershell
docker compose down
```

Derrubar e apagar banco local:

```powershell
docker compose down -v
```

Abrir shell no backend:

```powershell
docker compose exec web sh
```

Abrir PostgreSQL (dentro do container):

```powershell
docker compose exec db psql -U postgres -d controle_estoque
```

Abrir PostgreSQL (do host, porta Docker `5434`):

```powershell
$env:PGPASSWORD = "postgres"
psql -h 127.0.0.1 -p 5434 -U postgres -d controle_estoque
```

Previa da limpeza para deploy:

```powershell
.\.venv\Scripts\python.exe .\scripts\reset_for_deploy.py
```

Aplicar a limpeza para deploy:

```powershell
.\.venv\Scripts\python.exe .\scripts\reset_for_deploy.py --apply
```

## 17. Problemas comuns

### Porta 8000 ocupada

Sintoma:

- a aplicação não sobe
- erro de bind na porta

Ação:

- feche o processo que está usando a porta `8000`
- ou altere o mapeamento no [compose.yaml](compose.yaml)

### pgAdmin: "password authentication failed" na porta 5433 ou 5432

Sintoma:

- login falha com `postgres` / `postgres` ao conectar em `5432` ou `5433`

Causa:

- você está no **PostgreSQL nativo do Windows**, não no banco do Docker.

Ação (passo a passo):

1. confira o **Port** do servidor no pgAdmin
2. para o projeto, use **`5434`**
3. se necessário, cadastre de novo o servidor **Controle Estoque (Docker)** (veja seção 12)

### pgAdmin: servidor Docker não aparece após cadastro

Ação:

1. feche o pgAdmin completamente
2. abra de novo
3. expanda **Servers** → **Controle Estoque (Docker)**

### Apaguei o banco antigo e quero saber se o atual mudou

Siga a seção **13. Verificar se o banco está íntegro**. Se `healthz` retorna `ok` e as tabelas existem na porta `5434`, o banco do Docker está preservado.

### Porta 5434 ocupada

Sintoma:

- o PostgreSQL do Docker não sobe

Ação:

- altere o mapeamento em [compose.yaml](compose.yaml) (ex.: `"5435:5432"`) e atualize o pgAdmin com a nova porta
- ou pare outro processo que esteja usando `5434`

### Docker Desktop desligado

Sintoma:

- `docker compose up` falha logo no início

Ação:

1. abra o Docker Desktop
2. espere ele ficar disponível
3. rode o comando novamente

### Mudou dependência e nada aconteceu

Se você alterou `requirements.txt` ou `Dockerfile`, rode:

```powershell
docker compose up --build
```

Se ainda assim ficar inconsistente:

```powershell
docker compose build --no-cache web
docker compose up
```

### Preciso zerar a base antes do deploy

Se voce quer entregar o sistema limpo sem apagar a estrutura do banco, use o script:

```powershell
.\.venv\Scripts\python.exe .\scripts\reset_for_deploy.py --apply
```

Esse comando:

- apaga produtos, clientes, vendas, itens de venda e auditoria
- remove empresas, usuarios e configuracoes que nao pertencem aos usuarios com `role = admin` (administrador **da empresa**)
- preserva esses usuarios e as empresas (`company_id`) associadas a eles

## 18. Arquivos relacionados

- [compose.yaml](compose.yaml)
- [Dockerfile](Dockerfile)
- [.dockerignore](.dockerignore)
- [.env.example](.env.example)
- [README.md](README.md)
- [README-SOLUCAO-ERROS.md](README-SOLUCAO-ERROS.md)
- [README-SEGURANCA.md](README-SEGURANCA.md)
- [README-CSS.md](README-CSS.md)

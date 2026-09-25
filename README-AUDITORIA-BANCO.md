# Auditoria do banco de dados — Controle de Estoque

Este documento registra o **histórico de alterações no schema PostgreSQL** (Alembic) e como elas se relacionam com a **tabela de auditoria operacional** (`audit_logs`). Para instalação e uso do app, veja [README.md](README.md).

## Tabela `audit_logs`

Criada na migration inicial e ampliada em `0003_access_admin_audit`. Cada registro descreve uma ação relevante no sistema.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | int PK | Identificador |
| `action` | string | Ex.: `CREATE`, `UPDATE`, `DELETE`, `LOGIN`, `LOGIN_FAILED`, `DELETE_BLOCKED` |
| `entity` | string | Ex.: `product`, `sale`, `stock`, `customer`, `user` |
| `entity_id` | int | ID da entidade afetada (quando aplicável) |
| `user_id` | int FK → `users` | Usuário que executou a ação |
| `company_id` | int FK → `companies` | Empresa (nullable em eventos globais legados) |
| `ip_address` | string(64) | IP da requisição HTTP (quando há `Request`) |
| `user_agent` | string(500) | User-Agent do cliente |
| `before_data` | JSON | Snapshot antes da alteração |
| `after_data` | JSON | Snapshot depois da alteração |
| `description` | text | Texto legível para a tela de auditoria |
| `created_at` | timestamptz | Data/hora do evento |

**Serviço:** `app/services/audit_service.py` (`log_action`, `request_metadata`, `serialize_instance`).

**Consulta:** `GET /api/audit` (permissões da empresa; em geral tela do **dono**).

### O que é auditado hoje

- Login com sucesso, falha e bloqueio (empresa inativa)
- CRUD de produtos, clientes, usuários da empresa, configurações
- Vendas criadas (`entity = sale`) com itens no `after_data`
- **Baixa de estoque** após venda (`entity = stock`, `action = UPDATE`) com `before_data` / `after_data` do produto
- Tentativas de exclusão bloqueadas (ex.: produto com vendas vinculadas)

### Baixa de estoque e venda por peso (desde `d4a8b2c1e5f6`)

Quando o item de venda usa **peso (kg)**, o `after_data` / `before_data` da entidade `stock` pode incluir:

- `quantity` (unidades) — inalterado ou irrelevante para produto só por peso
- `weight_stock_kg` — estoque em kg após a baixa (produtos com `sold_by_weight = true`)

Exemplo de descrição: `Baixa de estoque após venda: Queijo (-0.350 kg)`.

Itens de venda passam a registrar **`quantity`** (un) **ou** **`weight_kg`** (kg), nunca os dois na mesma linha.

---

## Histórico de migrations (Alembic)

Ordem aplicada com `python -m alembic upgrade head`. **Head atual:** `d4a8b2c1e5f6`.

| Revisão | Arquivo | Alterações principais | Impacto na auditoria |
|---------|---------|----------------------|----------------------|
| `0001_init` | `0001_init.py` | `companies`, `users`, `products`, `audit_logs` (básico) | Tabela `audit_logs` criada |
| `0002_mini_erp` | `0002_mini_erp.py` | `company_settings`, `customers`, `sales`, `sale_items` | Vendas e itens passam a gerar eventos `sale` / `stock` |
| `0003_access_admin_audit` | `0003_access_admin_audit.py` | `companies.status`, `companies.plan`, `users.role`; `audit_logs`: `ip_address`, `user_agent`, `before_data`, `after_data`; `company_id` nullable | Auditoria **expandida** (campos usados pela UI) |
| `0004_customer_optional` | `0004_customer_optional.py` | `sales.customer_id` opcional | Vendas sem cliente refletidas na descrição da auditoria |
| `0005_company_owner` | `0005_company_owner.py` | `users.is_company_owner` | Controle de quem vê auditoria na UI (dono) |
| `0006_company_billing_fields` | `0006_company_billing_fields.py` | Cobrança Mercado Pago em `companies` | Eventos de billing/checkout conforme serviços |
| `0007_reclaim_free_plan` | `0007_reclaim_free_plan.py` | Normalização plano `free` | Dados legados; sem mudança de schema de auditoria |
| `0008_expand_limited_full_access` | `0008_expand_limited_full_access.py` | Ajustes de plano/limites | — |
| `b8498e564285` | `b8498e564285_add_validity_to_products.py` | `products.validity` (obrigatório) | Snapshots de produto incluem validade |
| `5b8a849fe51b` | `5b8a849fe51b_update_cpf_nullable_optional.py` | `customers.cpf` opcional | — |
| `c7e2f1a0b9d3` | `c7e2f1a0b9d3_drop_singleton_cpf_unique.py` | Remove UNIQUE global em `cpf`; mantém por empresa | — |
| **`d4a8b2c1e5f6`** | `d4a8b2c1e5f6_product_weight_and_scale.py` | Ver detalhe abaixo | Baixa de estoque em **kg** nos JSON de auditoria |

### Detalhe — `d4a8b2c1e5f6` (produto por peso e balança)

**Tabela `products`**

| Coluna | Tipo | Observação |
|--------|------|------------|
| `sold_by_weight` | boolean NOT NULL, default `false` | Habilita venda/estoque em kg |
| `weight_stock_kg` | numeric(12,3) NULL | Estoque em kg quando `sold_by_weight` |
| `min_weight_kg` | numeric(12,3) NULL | Estoque mínimo em kg |

**Tabela `sale_items`**

| Coluna | Tipo | Observação |
|--------|------|------------|
| `weight_kg` | numeric(12,3) NULL | Preenchido em venda por peso |
| `quantity` | int NULL | Antes NOT NULL; venda por peso usa `quantity` NULL |

**Regra de negócio (API):** cada item de venda envia `quantity` **ou** `weight_kg` (`app/schemas/sale.py`, `app/services/sales_service.py`).

**Downgrade:** remove colunas de peso; normaliza `sale_items.quantity` nulos para `1` antes de voltar NOT NULL.

---

## Comandos úteis

```bash
# Ver revisão atual no banco
python -m alembic current

# Aplicar todas as migrations
python -m alembic upgrade head

# Histórico
python -m alembic history -v
```

Em Docker Compose, o serviço `web` executa `alembic upgrade head` na subida (ver [README-DOCKER.md](README-DOCKER.md)).

---

## Documentos relacionados

- [README.md](README.md) — visão geral, DER e endpoints
- [README-USUARIO.md](README-USUARIO.md) — produtos por peso e balança no dia a dia
- [README-SEGURANCA.md](README-SEGURANCA.md) — auditoria e metadados HTTP

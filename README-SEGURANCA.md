# Segurança — Controle de Estoque SaaS

Este documento descreve **medidas de segurança já refletidas no código** do repositório, **pontos de atenção** na configuração e **melhorias recomendadas** para ambientes expostos à internet. Para instalação e deploy, veja o [README.md](README.md).

---

## 1. Autenticação

### Senhas

- As senhas são armazenadas **somente como hash** (biblioteca **bcrypt**), com salt gerado por `bcrypt.gensalt()` — ver `app/core/security.py` (`hash_password` / `verify_password`).
- Falhas de decodificação ou tipo inválido em `verify_password` retornam comparação negativa, sem propagar detalhes internos.

### Sessão da API (JWT)

- O login (`POST /api/auth/login`, OAuth2 password flow) emite um **JWT** assinado com **`SECRET_KEY`** e algoritmo **HS256** (`app/core/security.py`, `create_access_token`).
- O payload usa `sub` com o **ID numérico do usuário** e expiração `exp` em UTC; a validade padrão vem de `ACCESS_TOKEN_EXPIRE_MINUTES` em `app/core/config.py`.
- As rotas protegidas usam **`OAuth2PasswordBearer`** (`tokenUrl="/api/auth/login"`) — o cliente envia `Authorization: Bearer <token>` — ver `app/dependencies/auth.py`.

### Resposta genérica em login inválido

- Credenciais incorretas resultam em **401** com mensagem única (“Credenciais inválidas”), sem distinguir “e-mail inexistente” de “senha errada”, o que reduz enumeração de contas — ver `app/routes/auth.py` (`login`).

### Recuperação de senha

- Fluxo público em `POST /api/auth/forgot-password` e `POST /api/auth/reset-password`: JWT com **`scope: password_reset`**, expira conforme **`PASSWORD_RESET_EXPIRE_MINUTES`** (`app/core/security.py`, `app/routes/auth.py`).
- Com **`PASSWORD_RESET_TOKEN_IN_RESPONSE=true`** (valor padrão), a API pode devolver **`reset_token` na resposta JSON** para o front exibir o passo seguinte sem SMTP — usar **HTTPS** em produção. Para reduzir risco de uso indevido do token, avalie **`PASSWORD_RESET_TOKEN_IN_RESPONSE=false`** até haver envio apenas por **e-mail** (evolução futura).

---

## 2. Autorização e isolamento multiempresa

### Usuário atual e empresa ativa

- `get_current_user` valida o token, carrega o usuário, exige **`is_active`**, exige empresa existente e **`company.status == "active"`**; caso contrário retorna **401** ou **403** com mensagem alinhada ao motivo (pagamento pendente, bloqueio etc.) — `app/dependencies/auth.py`.

### Permissões por papel (RBAC)

- As permissões da empresa (`products:write`, `reports:export`, `company:admin`, …) estão centralizadas em `app/core/authorization.py` e aplicadas via `require_company_permission` em `app/dependencies/authorization.py`.
- O **dono da empresa** (`is_company_owner`) é tratado como papel **admin** da empresa para efeito de permissões.

### Isolamento de dados (tenant)

- Operações de negócio associam entidades a **`current_user.company_id`** (ex.: criação de produtos em `app/routes/products.py`). Consultas e restrições de integridade (ex.: SKU único **por empresa**) reforçam o isolamento lógico entre tenants.

### Dono da empresa

- `get_current_company_owner` exige permissão `company:admin` — usado em fluxos administrativos da empresa.

---

## 3. Cobrança e Mercado Pago

### Segredos só no servidor

- **`MERCADO_PAGO_ACCESS_TOKEN`**, **`SECRET_KEY`** e **`DATABASE_URL`** são lidos de variáveis de ambiente / `.env` (`app/core/config.py`). **Nunca** devem ir para o repositório Git nem para o frontend.

### Token de escopo limitado (checkout)

- Para planos pagos, pode ser emitido um JWT adicional com **`scope: billing_checkout`**, `company_id` no payload e prazo longo (padrão 12 h) — `create_billing_access_token` / `decode_billing_access_token` em `app/core/security.py`.
- O checkout (`POST /api/billing/mercado-pago/checkout`) exige esse token no corpo e valida **dono ativo** da empresa e coerência com **nome da empresa** e **e-mail** informados — `app/services/billing_service.py` (`_resolve_company_for_checkout`).

### Confirmação de pagamento

- A confirmação consulta o pagamento na **API do Mercado Pago** com o token de servidor e cruza **`company_id`** derivado do pagamento com o contexto do token de billing quando aplicável — `confirm_mercado_pago_payment` no mesmo serviço.

### Webhook

- A rota `POST /api/billing/mercado-pago/webhook` aceita notificações externas. **Recomendação forte:** em produção, implementar ou habilitar **validação de assinatura / origem** conforme a documentação atual do Mercado Pago e expor o endpoint apenas por **HTTPS** atrás de proxy reverso.

---

## 4. CORS

- O middleware CORS usa a lista em **`CORS_ORIGINS`** (origens separadas por vírgula, sem barra final) — `app/main.py`.
- **Atenção:** se, após o `split`, a lista ficar vazia, o código cai no fallback `allow_origins=["*"]` com **`allow_credentials=True`**, o que é **indesejável em produção**. Mantenha sempre **`CORS_ORIGINS`** explícito com os domínios reais do front.

---

## 5. Configuração e segredos

| Item | Orientação |
|------|------------|
| `SECRET_KEY` | Valor aleatório forte e **único por ambiente**; rotacione se vazado. |
| `DATABASE_URL` | Contém credenciais; restrinja acesso ao `.env` no servidor (permissões de arquivo). |
| `APP_BASE_URL` | Deve refletir a URL pública **HTTPS** em produção (URLs de retorno e webhook padrão do billing). |
| `.env` | Não versionar; usar segredos do painel do provedor em PaaS. |

O carregamento do `.env` é feito a partir da **raiz do repositório** — ver `app/core/config.py`.

---

## 6. Auditoria

- Ações relevantes (ex.: login sucesso/falha/bloqueado, criação de empresa, alterações rastreadas) podem registrar **IP** e **User-Agent** quando há objeto `Request` — `app/services/audit_service.py` (`request_metadata`, `log_action`).
- A leitura da auditoria exige permissões adequadas nas rotas de auditoria.

---

## 7. Entrada de dados e persistência

- Os corpos de requisição são validados com **Pydantic** (`schemas/`), reduzindo injeção de tipos inesperados e campos inválidos.
- O acesso ao banco é feito com **SQLAlchemy** e parâmetros ligados às consultas, padrão seguro contra **SQL injection** clássico em queries geradas pelo ORM.

---

## 8. Superfície HTTP

- **`/healthz`** responde apenas estado do serviço e alcance do banco, **sem** expor segredos — `app/main.py`.
- O frontend estático em `web/` é servido pelo mesmo processo; trate **cache** e **cabeçalhos de segurança** (CSP, HSTS, X-Frame-Options) no **proxy reverso** (Nginx, Caddy, load balancer) em produção.

---

## 9. O que este repositório **não** cobre (por padrão)

Itens úteis para endurecer em produção, conforme política da organização:

- **Limite de taxa** (rate limiting) em login e APIs públicas.
- **Autenticação multifator (MFA)** para usuários ou admins.
- **Política de senha** (comprimento mínimo, bloqueio de senhas comuns) além do que o formulário de cadastro impõe.
- **Rotação e armazenamento** de refresh tokens (hoje o modelo é access token de vida curta configurável).
- **Assinatura de webhooks** do Mercado Pago e lista de IPs permitidos.
- **Varredura de dependências** (Dependabot, `pip audit`) e **SAST** em CI.

---

## 10. Referência rápida de arquivos

| Tema | Arquivo principal |
|------|-------------------|
| Hash de senha e JWT | `app/core/security.py` |
| Settings e segredos | `app/core/config.py` |
| Usuário autenticado e empresa ativa | `app/dependencies/auth.py` |
| Checagem de permissão | `app/dependencies/authorization.py` |
| Matriz de permissões | `app/core/authorization.py` |
| Login, registro e recuperação de senha | `app/routes/auth.py` |
| Checkout / confirmação / webhook MP | `app/services/billing_service.py`, `app/routes/billing.py` |
| CORS e healthcheck | `app/main.py` |
| Auditoria | `app/services/audit_service.py` |

---

Para sintomas e correções práticas (login, CORS, `.env`), use também [README-SOLUCAO-ERROS.md](README-SOLUCAO-ERROS.md).

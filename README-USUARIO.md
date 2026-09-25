# Guia do usuário — Controle de Estoque SaaS

Para **instalar, Docker ou deploy**, use o [README.md](README.md). Este arquivo é o passo a passo para **usar o sistema no dia a dia**.

## Visão geral

O acesso ao sistema é em **`/`** — cadastro, login e ERP no mesmo frontend.

O sistema cobre:

- produtos e estoque (com **data de validade**; opcional **venda por peso** em kg)
- clientes
- vendas por **unidade** ou **peso (kg)** — balança USB no Chrome/Edge (opcional)
- usuários da empresa (tela do **dono**)
- relatórios e dashboard (conforme **feature flags**)
- auditoria (tela do **dono**)
- configurações visuais e flags por empresa

## 1. Primeiro acesso (criar empresa)

1. Abra **`/`**.
2. Em **Criar empresa**, escolha o **plano** e o **ciclo** (mensal ou anual, quando aplicável), informe o nome da empresa e os dados do administrador da empresa (e-mail, nome, senha).
3. Envie o cadastro.

**Importante — status após o cadastro:**

- Plano **Free:** a empresa fica **`active`** na hora e você já pode **entrar no ERP** com o e-mail e a senha cadastrados.
- Planos **pagos** (`basic`, `professional`, `premium`): a empresa fica **`pending`** até a **confirmação do pagamento no Mercado Pago** (Checkout Pro). Enquanto estiver pendente, **não é possível usar o ERP**. Conclua o pagamento pelo link do Mercado Pago; após a confirmação, a empresa passa a **`active`**.

## 2. Planos e pagamento (Mercado Pago)

Os planos comerciais são **`free`**, **`basic`**, **`professional`** e **`premium`**. Cada um tem **tetos de uso** diferentes (produtos, clientes, usuários, vendas, janelas de relatório/dashboard etc.), definidos em `app/core/plans.py` e aplicados pela API.

- **`GET /api/auth/me`** devolve **`company_plan`** e **`plan_usage`** (uso atual, tetos e capacidades).
- Cobrança de planos pagos usa **somente Mercado Pago** (sem outro gateway no código). Variáveis de ambiente e fluxo (checkout, retorno, webhook) estão descritos no [README.md](README.md).

Alteração manual de **plano** ou **status** da empresa, quando necessário para operação ou suporte, faz-se pelos dados no **banco** ou por ferramentas próprias — não há neste repositório um painel separado para “todas as empresas”.

## 3. Entrar no sistema

1. Com a empresa **`active`**, acesse **`/`**.
2. Use **Entrar** com o e-mail e a senha cadastrados.
3. **Esqueceu a senha?** No cartão **Acesse sua empresa**, use **Esqueci minha senha**: informe o e-mail da conta, solicite o código de recuperação e, quando o sistema liberar esta etapa, defina a nova senha (válido para usuários em empresa com acesso ativo).

O menu lateral mostra os módulos conforme **permissões** do usuário e **feature flags** da empresa.

### Por que alguma tela não aparece?

- **Feature desligada** em Configurações (`vendas`, `relatorio`, `dashboard_avancado`).
- **Usuários** e **Auditoria:** normalmente só o **dono da empresa** (`is_company_owner`).
- **Limite do plano Free** atingido (mensagem da API ao salvar).

## 4. Cadastro de produtos

1. Abra **Produtos**.
2. Preencha **Nome**, **SKU**, **Quantidade**, **Validade** (data — obrigatória), **Estoque mínimo**, **Preço** e, se quiser, **Descrição**.
3. Para produtos **pesados** (açougue, hortifruti, granel etc.), marque **Venda por peso (opcional)** e informe **Estoque (kg)** e **Estoque mínimo (kg)**; o preço passa a ser **por kg**.
4. Clique em **Salvar produto**.

**Dicas:**

- O **SKU** é único por empresa; repetir SKU gera erro.
- A validade **não pode ser no passado** (cadastro ou alteração).
- Use SKU padronizado se for usar leitor de código de barras nas vendas.
- Produtos **sem** a opção de peso continuam vendidos só por **unidade**.

## 5. Vendas (unidade ou peso)

1. Em **Vendas**, adicione itens por lista ou **SKU** (leitor de código de barras).
2. Se o produto tiver **venda por peso**, escolha **Peso** na linha do item:
   - Digite o **kg** manualmente, ou
   - Use **Ler balança** (Chrome/Edge, cabo USB; autorize a porta quando o navegador pedir).
3. Para produtos normais, use **Unidade** e informe a quantidade inteira.
4. Finalize a venda — o estoque baixa em unidades ou em kg conforme o modo.

Alterações no banco e na auditoria de estoque estão descritas em [README-AUDITORIA-BANCO.md](README-AUDITORIA-BANCO.md).

## 6. Clientes, relatórios e dashboard

- **Clientes:** cadastro simples; e-mail único por empresa.
- **Vendas:** informe cliente (opcional), itens e finalize; o estoque é baixado na confirmação.
- **Relatórios / Dashboard:** dependem das flags correspondentes; o **tamanho das janelas e listagens** varia conforme o plano (veja `plan_usage` após o login).

## 7. Usuários da empresa

1. Somente o **dono** acessa a tela **Usuários**.
2. Cadastre e-mail, senha e perfil; respeite o **limite de usuários** do plano (no Free há teto).

## 8. Configurações

Ajuste tema, cor, logo (se disponível) e **ligue ou desligue** as features da empresa.

## 9. Problemas comuns

| Situação | O que verificar |
|----------|-----------------|
| Cadastrei a empresa e não entro no ERP | Se escolheu plano **pago**, **`pending`** até concluir o **Mercado Pago**; se for **Free** e ainda não entra, confira credenciais ou consulte [README-SOLUCAO-ERROS.md](README-SOLUCAO-ERROS.md). |
| Erro ao salvar produto (422) | Campo **`validity`** obrigatório — preencha a **data de validade** e atualize a página (`Ctrl+F5`). |
| SKU já existe | Troque o SKU ou edite o produto existente. |
| Limite atingido | Tetos do plano atual — veja **`plan_usage`** após login ou ajuste uso/dados conforme política da empresa (sem painel multiempresa neste projeto). |
| PDF / impressão do relatório | Depende de **`plan_usage.exports_enabled`**, flag **`relatorio`** e permissões; se a API retornar 403, verifique plano e configurações. |

Mais detalhes técnicos de ambiente e API: [README-SOLUCAO-ERROS.md](README-SOLUCAO-ERROS.md).

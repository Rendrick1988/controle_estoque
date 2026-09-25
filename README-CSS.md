# Guia de personalização do CSS — Controle de Estoque

Este documento explica **onde** está o estilo da interface web, **como** a página se organiza no HTML e **como alterar** cores, tamanho da logo e outros detalhes sem perder a consistência visual.

Arquivo principal: **`web/styles.css`**. O HTML carrega esse arquivo a partir da raiz do site (ex.: `/styles.css?v=...` em [`web/index.html`](web/index.html)); ao mudar o CSS com frequência, incremente o parâmetro `?v=` no `link` para forçar o navegador a baixar de novo (evita cache antigo).

Para instalação e deploy do projeto, use o [README.md](README.md).

---

## 1. Visão geral da estrutura (HTML + CSS)

### 1.1 Árvore lógica da aplicação autenticada

O conteúdo logado fica dentro de `#appRoot` (classe `.app`):

```text
.app
├── aside.sidebar          ← menu lateral (marca + navegação + Sair)
├── button.sidebar-backdrop ← overlay em telas estreitas (só visível com menu aberto)
└── main.main              ← área principal
    ├── header.topbar      ← título da página + chip do usuário + botão Menu (mobile)
    └── section.content
        └── div.view       ← um bloco por tela (dashboard, produtos, etc.)
            └── div.grid / div.card / …
```

- Cada **módulo** (Produtos, Clientes, …) é um `div.view` com `id` próprio (ex.: `productsView`). O JavaScript em `web/app.js` mostra só a view ativa.
- **Cards** (`.card`) agrupam formulários e tabelas. **Tabelas** geradas pelo JS usam `.table` > `.row` > `.cell`.

### 1.2 Tela de login / cadastro (`#authView`)

A área pública usa classes como `.auth-layout`, `.auth-spotlight`, `.auth-stack`, `.auth-card`, `.pricing-grid`. Os breakpoints reorganizam colunas em telas menores (ver secção 5).

---

## 2. Sistema de cores (variáveis CSS)

No topo de **`web/styles.css`**, o bloco **`:root`** define tokens usados em quase toda a interface:

| Variável | Uso típico |
|----------|------------|
| `--bg` | Fundo geral da página (gradientes do `body` misturam tons próximos) |
| `--panel` | Fundo de cards, sidebar, topbar |
| `--panel-soft` | Fundos suaves, inputs, chips |
| `--text` | Texto principal |
| `--muted` | Texto secundário, legendas de campo |
| `--border` | Bordas e divisores |
| **`--primary`** | Cor de destaque (botões primários, links, foco, menu ativo) |
| `--primary-contrast` | Texto sobre botão primário |
| `--success` / `--danger` / `--warning` | Feedback positivo, erro, alerta |
| `--shadow` | Sombra padrão de cards |

**Exemplo — trocar o azul principal no tema claro:**

```css
:root {
  --primary: #0d9488; /* teal */
  --primary-contrast: #ffffff;
}
```

**Tema escuro:** o mesmo nome de variável é redefinido em **`body.theme-dark { ... }`**. Se mudar `--primary` no `:root`, ajuste também no bloco `body.theme-dark` para manter contraste no modo escuro.

**Tema rosa:** em **`body.theme-pink`** (ativado em **Configurações → Tema → Rosa**) a paleta usa rosa nos painéis e texto, com **fundo em gradiente amarelo/creme** no `body`. O campo **Cor primária** (hex) continua opcional e, se preenchido, sobrescreve `--primary` por cima desse preset.

### 2.1 Cor primária vinda das configurações da empresa

Além do arquivo CSS, o **`web/app.js`** (função `applyTheme`) pode definir em tempo de execução:

```javascript
document.body.style.setProperty("--primary", state.settings.primary_color);
```

Ou seja: a cor **“Cor primária”** em **Configurações** no app sobrescreve `--primary` no `body` após o login. Para um padrão global fixo, altere `:root` no CSS **e** o valor padrão gravado nas configurações, ou deixe o campo em branco e controle só pelo CSS.

### 2.2 Gradientes e cores “fixas” no `body` e `.auth`

Alguns fundos usam **hexadecimais diretos** (não só variáveis), por exemplo no `body` e em `.auth`. Se quiser um visual totalmente verde ou neutro, procure por `radial-gradient`, `linear-gradient` e `#c9def4` nesses blocos e alinhe com suas novas cores.

### 2.3 `color-mix()`

Várias bordas e fundos usam `color-mix(in srgb, var(--primary) X%, ...)`. Isso deriva tons da cor primária automaticamente. Navegadores modernos suportam bem; se precisar de compatibilidade muito antiga, substitua por um `rgba` ou hex fixo equivalente.

---

## 3. Logo (tamanho, proporção, imagem)

### 3.1 Elemento no HTML

No menu lateral, a logo é o `div` com `id="brandLogo"` e classe **`.logo`** (dentro de `.brand`). Sem imagem, o JS exibe as iniciais **“CE”** como texto; com URL de logo (configurações ou upload), o JS aplica `background-image` nesse mesmo nó — ver `applyLogoToNode` em `web/app.js`.

### 3.2 Tamanho no desktop

No **`web/styles.css`**, classe **`.logo`**:

```css
.logo {
  width: 200px;
  height: 150px;
  border-radius: 14px;
  /* ... */
}
```

**Exemplo — logo mais compacta no desktop:**

```css
.logo {
  width: 120px;
  height: 90px;
  border-radius: 12px;
}
```

Mantenha proporção semelhante à imagem que você envia (evita cortes estranhos: a classe já usa `background-size: cover` e `background-position: center`).

### 3.3 Tamanho no mobile / menu gaveta

Dentro de **`@media (max-width: 980px)`** existe o seletor **`.sidebar .logo`**, que reduz a logo quando o menu lateral está no modo “gaveta”. Ajuste ali se quiser outro tamanho só no telefone:

```css
@media (max-width: 980px) {
  .sidebar .logo {
    width: min(140px, 38vw);
    height: min(105px, 28vw);
  }
}
```

### 3.4 Largura da sidebar (afeta o espaço da marca)

A classe **`.sidebar`** define `width: 290px` no desktop. Se aumentar muito a logo, considere aumentar também a largura da sidebar para não quebrar o layout.

---

## 4. Tipografia e espaçamentos globais

- **Fonte:** `body { font-family: ... }` no início de `styles.css`.
- **Espaço da área principal:** `.main { padding: 18px; }` (em telas menores o padding é reduzido nos `@media`).
- **Títulos de página:** `.page-title { font-size: 18px; }`.
- **Títulos de card:** `.card-title { font-size: 16px; }`.

---

## 5. Layout responsivo (`@media`)

No final de **`web/styles.css`** há regras por largura de tela, por exemplo:

| Breakpoint | Efeito resumido |
|------------|-----------------|
| `1180px` | Colunas de login / destaque em pilha |
| `980px` | Sidebar fixa tipo gaveta, overlay, ajustes de auth |
| `860px` | Pilha nos cards de cadastro/login |
| `720px` | Planos em uma coluna, botões largura total, grid de módulos 1 coluna, linhas de venda em coluna única |
| `480px` | Topbar / título um pouco menores |

Ao criar novos componentes, prefira **reutilizar** esses breakpoints ou estender os blocos existentes para manter o mesmo comportamento em tablet e smartphone.

---

## 6. Componentes reutilizáveis (referência rápida)

| Classe | Função |
|--------|--------|
| `.btn`, `.btn-primary`, `.btn-ghost`, `.btn-danger` | Botões |
| `.card`, `.card-header`, `.card-title`, `.card-subtitle` | Blocos de conteúdo |
| `.form`, `.field`, `.field-wide` | Formulários |
| `.table`, `.row`, `.row.head`, `.cell`, `.cell.actions` | Tabelas listadas pelo JS |
| `.topbar`, `.chip` | Barra superior e “pílula” do usuário |
| `.toast` | Notificações canto inferior direito |
| `.loading-overlay` | Carregamento em tela cheia |

---

## 7. Fluxo recomendado ao personalizar

1. Faça uma cópia de segurança de `web/styles.css` ou use Git.
2. Altere primeiro as **variáveis em `:root`** (e em `body.theme-dark` / `body.theme-pink` se for editar esses temas).
3. Ajuste **`.logo`** e, se necessário, **`.sidebar .logo`** e **`.sidebar`**.
4. Só depois refine gradientes fixos no `body` / `.auth` se ainda não estiver coerente.
5. Atualize o **`?v=`** no `link` de `styles.css` em `index.html` e faça um **hard refresh** (`Ctrl+F5`) no navegador.

---

## 8. Onde **não** está o CSS

- **Chart.js** (dashboard): cores dos gráficos são definidas em **`web/app.js`** nas funções que montam os `datasets`, não no `styles.css`.
- **Conteúdo dinâmico** (texto de tabelas, opções de select): HTML gerado no `app.js`; o visual continua vindo das classes CSS acima.

---

## 9. Leitura adicional

- [README.md](README.md) — visão geral do projeto  
- [README-SEGURANCA.md](README-SEGURANCA.md) — CORS, cookies e boas práticas (menos ligado a CSS, útil se expuser o app na internet)

Se você publicar uma **fork** com identidade visual própria, documente as variáveis que alterou neste mesmo espírito para a equipe saber onde mexer na próxima rodada.

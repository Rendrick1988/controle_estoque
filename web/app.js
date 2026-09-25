
const apiEndpoints = {
  register: "/api/auth/register",
  login: "/api/auth/login",
  forgotPassword: "/api/auth/forgot-password",
  resetPassword: "/api/auth/reset-password",
  currentUserProfile: "/api/auth/me",
  billingPlans: "/api/billing/plans",
  billingCheckout: "/api/billing/mercado-pago/checkout",
  billingConfirm: "/api/billing/mercado-pago/confirm",
  companyUsers: "/api/company-users",
  products: "/api/products",
  customers: "/api/customers",
  sales: "/api/sales",
  settings: "/api/settings/company",
  settingsLogo: "/api/settings/company/logo",
  dashboardSummary: "/api/dashboard/summary",
  reportsByDay: "/api/reports/sales-by-day?days=30",
  reportsByMonth: "/api/reports/sales-by-month?months=12",
  reportsRevenue: "/api/reports/total-revenue",
  reportsTopProducts: "/api/reports/top-products?limit=10",
  reportsHistory: "/api/reports/history?limit=300",
  reportsExportPdf: "/api/reports/export/pdf",
  reportsExportPrint: "/api/reports/export/print",
  audit: "/api/audit",
};

const dom = {
  appRoot: document.getElementById("appRoot"),
  sidebar: document.getElementById("sidebar"),
  authView: document.getElementById("authView"),
  dashboardView: document.getElementById("dashboardView"),
  productsView: document.getElementById("productsView"),
  customersView: document.getElementById("customersView"),
  usersView: document.getElementById("usersView"),
  salesView: document.getElementById("salesView"),
  reportsView: document.getElementById("reportsView"),
  auditView: document.getElementById("auditView"),
  settingsView: document.getElementById("settingsView"),
  pageTitle: document.getElementById("pageTitle"),
  currentUserChip: document.getElementById("meChip"),
  brandSub: document.getElementById("brandSub"),
  brandLogo: document.getElementById("brandLogo"),

  loadingOverlay: document.getElementById("loadingOverlay"),
  loadingText: document.getElementById("loadingText"),
  toast: document.getElementById("toast"),

  loginForm: document.getElementById("loginForm"),
  registerForm: document.getElementById("registerForm"),
  loginMsg: document.getElementById("loginMsg"),
  registerMsg: document.getElementById("registerMsg"),
  btnToggleForgotPassword: document.getElementById("btnToggleForgotPassword"),
  forgotPasswordPanel: document.getElementById("forgotPasswordPanel"),
  forgotPasswordEmail: document.getElementById("forgotPasswordEmail"),
  btnRequestPasswordReset: document.getElementById("btnRequestPasswordReset"),
  forgotPasswordStep2: document.getElementById("forgotPasswordStep2"),
  forgotNewPassword: document.getElementById("forgotNewPassword"),
  forgotNewPasswordConfirm: document.getElementById("forgotNewPasswordConfirm"),
  btnSubmitPasswordReset: document.getElementById("btnSubmitPasswordReset"),
  forgotResetToken: document.getElementById("forgotResetToken"),
  forgotPasswordMsg: document.getElementById("forgotPasswordMsg"),
  publicPlansGrid: document.getElementById("publicPlansGrid"),
  annualDiscountCopy: document.getElementById("annualDiscountCopy"),
  registerPlan: document.getElementById("registerPlan"),
  registerBillingCycle: document.getElementById("registerBillingCycle"),
  btnCheckoutMercadoPago: document.getElementById("btnCheckoutMercadoPago"),

  productForm: document.getElementById("productForm"),
  btnClearProductForm: document.getElementById("btnClearProductForm"),
  productMsg: document.getElementById("productMsg"),
  productsTable: document.getElementById("productsTable"),

  customerForm: document.getElementById("customerForm"),
  btnClearCustomerForm: document.getElementById("btnClearCustomerForm"),
  customerMsg: document.getElementById("customerMsg"),
  customersTable: document.getElementById("customersTable"),

  companyUserForm: document.getElementById("companyUserForm"),
  btnClearCompanyUserForm: document.getElementById("btnClearCompanyUserForm"),
  companyUserMsg: document.getElementById("companyUserMsg"),
  companyUsersTable: document.getElementById("companyUsersTable"),

  saleForm: document.getElementById("saleForm"),
  saleMsg: document.getElementById("saleMsg"),
  saleCustomerSelect: document.getElementById("saleCustomerSelect"),
  saleSkuInput: document.getElementById("saleSkuInput"),
  saleItemsContainer: document.getElementById("saleItemsContainer"),
  saleDraftTotal: document.getElementById("saleTotal"),
  btnAddSaleItem: document.getElementById("btnAddSaleItem"),
  btnAddBySku: document.getElementById("btnAddBySku"),
  salesTable: document.getElementById("salesTable"),

  salesTodayMetric: document.getElementById("salesTodayMetric"),
  revenueMetric: document.getElementById("revenueMetric"),
  totalSalesMetric: document.getElementById("totalSalesMetric"),
  totalProductsMetric: document.getElementById("totalProductsMetric"),
  dashboardUpdated: document.getElementById("dashboardUpdated"),
  alertsList: document.getElementById("alertsList"),
  recentSalesTable: document.getElementById("recentSalesTable"),

  reportsRevenueMetric: document.getElementById("reportsRevenueMetric"),
  reportByDayTable: document.getElementById("reportByDayTable"),
  reportByMonthTable: document.getElementById("reportByMonthTable"),
  reportTopProductsTable: document.getElementById("reportTopProductsTable"),
  reportHistoryTable: document.getElementById("reportHistoryTable"),
  btnExportPdf: document.getElementById("btnExportPdf"),
  btnPrintReport: document.getElementById("btnPrintReport"),

  auditTable: document.getElementById("auditTable"),
  auditActionFilter: document.getElementById("auditActionFilter"),
  auditEntityFilter: document.getElementById("auditEntityFilter"),
  auditSearchFilter: document.getElementById("auditSearchFilter"),
  btnReloadAudit: document.getElementById("btnReloadAudit"),

  settingsForm: document.getElementById("settingsForm"),
  settingsTheme: document.getElementById("settingsTheme"),
  settingsPrimaryColor: document.getElementById("settingsPrimaryColor"),
  settingsLogoUrlInput: document.getElementById("settingsLogoUrlInput"),
  settingsLogoFileInput: document.getElementById("settingsLogoFileInput"),
  btnClearSettingsLogo: document.getElementById("btnClearSettingsLogo"),
  settingsLogoPreview: document.getElementById("settingsLogoPreview"),
  settingsLogoPreviewText: document.getElementById("settingsLogoPreviewText"),
  btnRemoveSettingsLogo: document.getElementById("btnRemoveSettingsLogo"),
  settingsMsg: document.getElementById("settingsMsg"),

  btnLogout: document.getElementById("btnLogout"),
  btnToggleSidebar: document.getElementById("btnToggleSidebar"),
  sidebarBackdrop: document.getElementById("sidebarBackdrop"),
};

const viewNodes = {
  auth: dom.authView,
  dashboard: dom.dashboardView,
  products: dom.productsView,
  customers: dom.customersView,
  users: dom.usersView,
  sales: dom.salesView,
  reports: dom.reportsView,
  audit: dom.auditView,
  settings: dom.settingsView,
};

const state = {
  currentUser: null,
  settings: null,
  products: [],
  customers: [],
  companyUsers: [],
  salesDraft: [],
  editingProductId: null,
  editingCustomerId: null,
  editingCompanyUserId: null,
  publicPlanCatalog: null,
  charts: {
    day: null,
    month: null,
    product: null,
  },
};

let settingsLogoPreviewUrl = null;

const PENDING_COMPANY_STORAGE_KEY = "pending_company_checkout";

function isFreePlan(plan) {
  return String(plan || "").trim().toLowerCase() === "free";
}

function getAuthToken() {
  return localStorage.getItem("token");
}

function setAuthToken(token) {
  localStorage.setItem("token", token);
}

function clearAuthToken() {
  localStorage.removeItem("token");
}

function getPendingCompanyCheckout() {
  try {
    const storedValue = sessionStorage.getItem(PENDING_COMPANY_STORAGE_KEY);
    return storedValue ? JSON.parse(storedValue) : null;
  } catch {
    return null;
  }
}

function setPendingCompanyCheckout(pendingCompanyCheckout) {
  try {
    if (!pendingCompanyCheckout) {
      sessionStorage.removeItem(PENDING_COMPANY_STORAGE_KEY);
      return;
    }
    sessionStorage.setItem(PENDING_COMPANY_STORAGE_KEY, JSON.stringify(pendingCompanyCheckout));
  } catch {
    // Ignora falhas de storage no navegador.
  }
}

function buildRegisterPayload() {
  return {
    company: { name: dom.registerForm.company_name.value.trim() },
    plan: dom.registerPlan.value,
    billing_cycle: dom.registerBillingCycle.value,
    admin: {
      email: dom.registerForm.email.value.trim().toLowerCase(),
      full_name: dom.registerForm.full_name.value.trim() || null,
      password: dom.registerForm.password.value,
    },
  };
}

function rememberPendingCompanyCheckout(registrationResponse, registerPayload) {
  if (!registrationResponse?.billing_access_token) return;
  setPendingCompanyCheckout({
    company_name: registrationResponse.company.name,
    email: registerPayload.admin.email,
    billing_access_token: registrationResponse.billing_access_token,
  });
}

function matchesPendingCompanyCheckout(registerPayload, pendingCompanyCheckout) {
  if (!pendingCompanyCheckout?.billing_access_token) return false;
  return (
    String(pendingCompanyCheckout.company_name || "").trim() ===
      String(registerPayload.company.name || "").trim() &&
    String(pendingCompanyCheckout.email || "").trim().toLowerCase() ===
      String(registerPayload.admin.email || "").trim().toLowerCase()
  );
}

async function ensurePendingCompanyForCheckout() {
  const registerPayload = buildRegisterPayload();
  const pendingCompanyCheckout = getPendingCompanyCheckout();
  if (matchesPendingCompanyCheckout(registerPayload, pendingCompanyCheckout)) {
    return {
      billingAccessToken: pendingCompanyCheckout.billing_access_token,
      payload: registerPayload,
    };
  }

  const registrationResponse = await apiFetch(apiEndpoints.register, {
    method: "POST",
    body: JSON.stringify(registerPayload),
  });
  if (!registrationResponse?.billing_access_token) {
    throw new Error("Não foi possível autorizar o checkout. Tente cadastrar novamente.");
  }
  rememberPendingCompanyCheckout(registrationResponse, registerPayload);
  return {
    billingAccessToken: registrationResponse.billing_access_token,
    payload: registerPayload,
  };
}

function formatCurrency(amount) {
  return Number(amount || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatDate(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString("pt-BR");
}

/** Data de validade do produto (somente calendário, pt-BR). */
function formatProductValidityDisplay(isoValue) {
  if (!isoValue) return "—";
  const d = new Date(isoValue);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("pt-BR");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatJsonPreview(value) {
  if (!value) return "";
  return JSON.stringify(value, null, 2);
}

function buildQueryString(params) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === null || value === undefined || value === "") return;
    query.set(key, value);
  });
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

function setFeedbackMessage(el, text, type = null) {
  if (!el) return;
  el.textContent = text || "";
  el.classList.remove("ok", "error");
  if (type) el.classList.add(type);
}

function showToast(message, type = null) {
  dom.toast.textContent = message;
  dom.toast.classList.remove("hidden", "ok", "error");
  if (type) dom.toast.classList.add(type);
  setTimeout(() => dom.toast.classList.add("hidden"), 2600);
}

function setLoading(show, text = "Carregando...") {
  dom.loadingText.textContent = text;
  dom.loadingOverlay.classList.toggle("hidden", !show);
}

function hasPlanCapability(capability) {
  const capabilities = state.currentUser?.plan_usage?.capabilities || [];
  return capabilities.includes(capability);
}

async function apiFetch(url, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getAuthToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const body = options.body;
  if (body && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
    if (!headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  }
  if (body instanceof URLSearchParams) {
    headers.set("Content-Type", "application/x-www-form-urlencoded");
  }

  const response = await fetch(url, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  let responseData = null;
  const rawBody =
    response.status === 204 || response.status === 205 ? "" : await response.text();
  if (rawBody) {
    if (contentType.includes("application/json")) {
      try {
        responseData = JSON.parse(rawBody);
      } catch {
        responseData = rawBody;
      }
    } else if (contentType.includes("text/")) {
      responseData = rawBody;
    }
  }

  if (!response.ok) {
    const detail =
      (responseData && (responseData.detail || responseData.message)) ||
      (typeof responseData === "string" && responseData) ||
      `Erro HTTP ${response.status}`;
    throw new Error(detail);
  }

  return responseData;
}

function showView(viewName) {
  Object.entries(viewNodes).forEach(([name, node]) => {
    if (name !== viewName) {
      node.style.display = "none";
      return;
    }
    node.style.display = name === "auth" ? "grid" : "block";
  });
}

function setActiveNav(viewName) {
  document.querySelectorAll(".nav-item").forEach((navItem) => {
    navItem.classList.toggle("active", navItem.dataset.view === viewName);
  });
}

function hasFeature(featureName) {
  const features = state.settings?.features || [];
  return hasPlanCapability(featureName) && features.includes(featureName);
}

function canAccessCompanyAudit() {
  return Boolean(state.currentUser?.is_company_owner && hasPlanCapability("audit"));
}

function canManageCompanyUsers() {
  return Boolean(state.currentUser?.is_company_owner && hasPlanCapability("multi_users"));
}

function canAccessCustomers() {
  return hasPlanCapability("clientes");
}

function applyLogoToNode(node, logoImageUrl, fallbackText = "CE") {
  if (!node) return;
  if (logoImageUrl) {
    node.style.backgroundImage = `url("${logoImageUrl}")`;
    node.textContent = "";
    return;
  }
  node.style.backgroundImage = "";
  node.textContent = fallbackText;
}

function revokeSettingsLogoPreviewUrl() {
  if (!settingsLogoPreviewUrl) return;
  URL.revokeObjectURL(settingsLogoPreviewUrl);
  settingsLogoPreviewUrl = null;
}

function refreshSettingsLogoPreview() {
  revokeSettingsLogoPreviewUrl();

  const selectedSettingsLogoFile = dom.settingsLogoFileInput?.files?.[0] || null;
  if (selectedSettingsLogoFile) {
    settingsLogoPreviewUrl = URL.createObjectURL(selectedSettingsLogoFile);
    applyLogoToNode(dom.settingsLogoPreview, settingsLogoPreviewUrl);
    dom.settingsLogoPreviewText.textContent = `Arquivo selecionado: ${selectedSettingsLogoFile.name}`;
    return;
  }

  const companyLogoUrl = dom.settingsLogoUrlInput?.value.trim() || state.settings?.logo_url || null;
  applyLogoToNode(dom.settingsLogoPreview, companyLogoUrl);
  dom.settingsLogoPreviewText.textContent = companyLogoUrl
    ? "A logo salva será exibida no menu lateral."
    : "Nenhuma logo configurada ainda.";
}

function bindSettingsLogoFileInput() {
  dom.settingsLogoFileInput?.addEventListener("change", refreshSettingsLogoPreview);
}

function resetSettingsLogoFileInput() {
  if (!dom.settingsLogoFileInput) return;
  const nextInput = dom.settingsLogoFileInput.cloneNode(true);
  dom.settingsLogoFileInput.replaceWith(nextInput);
  dom.settingsLogoFileInput = nextInput;
  bindSettingsLogoFileInput();
}

function clearSettingsLogoSelection(event = null) {
  if (event) {
    event.preventDefault();
  }
  resetSettingsLogoFileInput();
  refreshSettingsLogoPreview();
}

function updateRemoveSettingsLogoButtonState() {
  if (!dom.btnRemoveSettingsLogo) return;
  dom.btnRemoveSettingsLogo.disabled = !state.settings?.logo_url;
}

function sameFeatureSet(left, right) {
  const a = new Set(left || []);
  const b = new Set(right || []);
  if (a.size !== b.size) return false;
  return Array.from(a).every((featureName) => b.has(featureName));
}

function applyTheme() {
  const theme = state.settings?.theme || "light";
  document.body.classList.remove("theme-dark", "theme-pink");
  document.body.style.removeProperty("--primary");

  if (theme === "dark") {
    document.body.classList.add("theme-dark");
  } else if (theme === "pink") {
    document.body.classList.add("theme-pink");
  }

  if (theme === "custom" && state.settings?.primary_color) {
    document.body.style.setProperty("--primary", state.settings.primary_color);
  } else if (state.settings?.primary_color) {
    document.body.style.setProperty("--primary", state.settings.primary_color);
  }

  applyLogoToNode(dom.brandLogo, state.settings?.logo_url || null);
}

function applyFeatureVisibility() {
  document.querySelectorAll(".nav-item").forEach((navButton) => {
    if (navButton.dataset.view === "audit") {
      navButton.style.display = canAccessCompanyAudit() ? "" : "none";
      return;
    }
    if (navButton.dataset.view === "users") {
      navButton.style.display = canManageCompanyUsers() ? "" : "none";
      return;
    }
    const capability = navButton.dataset.capability;
    if (capability) {
      navButton.style.display = hasPlanCapability(capability) ? "" : "none";
      return;
    }
    const feature = navButton.dataset.feature;
    if (!feature) {
      navButton.style.display = "";
      return;
    }
    navButton.style.display = hasFeature(feature) ? "" : "none";
  });
}

function currentPageTitle(view) {
  const map = {
    dashboard: "Dashboard",
    products: "Produtos",
    customers: "Clientes",
    users: "Usuários",
    sales: "Vendas",
    reports: "Relatórios",
    audit: "Auditoria",
    settings: "Configurações",
    auth: "Entrar",
  };
  return map[view] || "Controle de Estoque";
}

function defaultAuthedView() {
  if (hasFeature("dashboard_avancado")) return "dashboard";
  return "products";
}

function renderTable(container, headers, rows) {
  container.innerHTML = "";
  const headRow = document.createElement("div");
  headRow.className = "row head";
  headers.forEach((h) => {
    const c = document.createElement("div");
    c.className = "cell";
    c.textContent = h;
    headRow.appendChild(c);
  });
  container.appendChild(headRow);

  if (!rows.length) {
    const empty = document.createElement("div");
    empty.className = "row";
    empty.innerHTML = `<div class="cell">Sem dados.</div>`;
    container.appendChild(empty);
    return;
  }

  rows.forEach((row) => container.appendChild(row));
}
async function refreshCurrentUser() {
  const currentUserProfile = await apiFetch(apiEndpoints.currentUserProfile);
  state.currentUser = currentUserProfile;
  dom.currentUserChip.textContent = `${currentUserProfile.email} (${currentUserProfile.role})`;
  dom.brandSub.textContent = `Empresa #${currentUserProfile.company_id} · plano ${currentUserProfile.company_plan}`;
}

async function refreshSettings() {
  state.settings = await apiFetch(apiEndpoints.settings);
  applyTheme();
  applyFeatureVisibility();
  fillSettingsForm();
}

function fillSettingsForm() {
  if (!state.settings) return;
  dom.settingsTheme.value = state.settings.theme || "light";
  dom.settingsPrimaryColor.value = state.settings.primary_color || "";
  dom.settingsLogoUrlInput.value = state.settings.logo_url || "";
  clearSettingsLogoSelection();
  updateRemoveSettingsLogoButtonState();

  const active = new Set(state.settings.features || []);
  document.querySelectorAll(".feature-option input[type='checkbox']").forEach((cb) => {
    cb.checked = active.has(cb.value);
    cb.disabled = !hasPlanCapability(cb.value);
    cb.closest(".feature-option")?.classList.toggle("feature-option-disabled", cb.disabled);
  });
  refreshSettingsLogoPreview();
}

function syncPlanSelectionUI() {
  const selectedPlan = dom.registerPlan?.value || "professional";
  document.querySelectorAll("[data-plan-card]").forEach((card) => {
    card.classList.toggle("selected", card.dataset.planCard === selectedPlan);
  });
  if (dom.registerBillingCycle) {
    if (isFreePlan(selectedPlan)) {
      dom.registerBillingCycle.value = "monthly";
    }
    dom.registerBillingCycle.disabled = isFreePlan(selectedPlan);
  }
  if (dom.btnCheckoutMercadoPago) {
    dom.btnCheckoutMercadoPago.textContent = isFreePlan(selectedPlan)
      ? "Começar grátis"
      : "Pagar com Mercado Pago";
  }
}

function selectPlan(plan, billingCycle = null, { scroll = true } = {}) {
  if (dom.registerPlan) {
    dom.registerPlan.value = plan;
  }
  if (billingCycle && dom.registerBillingCycle) {
    dom.registerBillingCycle.value = billingCycle;
  }
  syncPlanSelectionUI();
  if (scroll) {
    dom.registerForm?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function renderPublicPlansSkeleton(count = 4) {
  if (!dom.publicPlansGrid) return;
  dom.publicPlansGrid.innerHTML = Array.from({ length: count }, (_, index) => {
    const featured = index === 1 ? "featured" : "";
    return `
      <article class="plan-card plan-card-skeleton ${featured}" aria-hidden="true">
        <div class="plan-head">
          <div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line medium" style="margin-top: 8px;"></div>
          </div>
          <div class="skeleton-badge"></div>
        </div>
        <div class="plan-pricing">
          <div class="skeleton-price"></div>
          <div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line medium" style="margin-top: 8px;"></div>
          </div>
        </div>
        <div class="skeleton-pills">
          <div class="skeleton-pill"></div>
          <div class="skeleton-pill"></div>
          <div class="skeleton-pill"></div>
        </div>
        <div class="skeleton-list">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line medium"></div>
        </div>
        <div class="skeleton-actions">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
        </div>
      </article>
    `;
  }).join("");
}

function planLeadCopy(code) {
  if (code === "free") return "Todos os modulos liberados para comecar sem custo, com limites iniciais.";
  if (code === "basic") return "Mais espaco para operar todos os modulos com seguranca no dia a dia.";
  if (code === "professional") return "Mais volume, mais historico e mais folga para empresas em crescimento.";
  return "Escala maxima para quem precisa de mais performance e menos limites.";
}

function renderPublicPlans(catalog) {
  state.publicPlanCatalog = catalog;
  if (dom.annualDiscountCopy && catalog.annual_discount_copy) {
    dom.annualDiscountCopy.textContent = catalog.annual_discount_copy;
  }
  if (!dom.publicPlansGrid) return;

  dom.publicPlansGrid.innerHTML = (catalog.offers || [])
    .map(
      (offer) => `
        <article class="plan-card ${offer.code === "professional" ? "featured" : ""}" data-plan-card="${offer.code}">
          <div class="plan-head">
            <div>
              <div class="plan-kicker">${
                offer.code === "free"
                  ? "Plano gratuito"
                  : offer.code === "professional"
                    ? "Plano principal"
                    : "Plano comercial"
              }</div>
              <h3>${offer.name}</h3>
            </div>
            <span class="plan-badge">${offer.badge}</span>
          </div>
          <div class="plan-pricing">
            <div>
              <div class="plan-price">${
                offer.code === "free" ? "Gratis" : `${formatCurrency(offer.monthly_price)}<span>/mês</span>`
              }</div>
              <div class="plan-copy">${planLeadCopy(offer.code)}</div>
            </div>
            <div>
              <div class="plan-annual-label">${offer.code === "free" ? "Sem cobrança" : "No anual"}</div>
              <div class="plan-annual">${offer.code === "free" ? "Acesso imediato" : `${formatCurrency(offer.annual_price)}/ano`}</div>
              <div class="plan-annual-note">${offer.code === "free" ? "Sem checkout" : "2 meses de graça"}</div>
          </div>
          </div>
          <div class="plan-audience">
            ${offer.audience.map((audienceLabel) => `<span class="audience-pill">${audienceLabel}</span>`).join("")}
          </div>
          <ul class="plan-list">
            ${offer.includes.map((includedFeature) => `<li>${includedFeature}</li>`).join("")}
          </ul>
          <div class="plan-why">${offer.why}</div>
          <div class="actions plan-actions">
            <button class="btn btn-primary" type="button" data-action="select-plan" data-plan="${offer.code}">${
              offer.code === "free" ? "Selecionar gratis" : "Selecionar plano"
            }</button>
            <button class="btn btn-ghost" type="button" data-action="checkout-plan" data-plan="${offer.code}">${
              offer.code === "free" ? "Começar grátis" : "Checkout Mercado Pago"
            }</button>
          </div>
        </article>
      `
    )
    .join("");

  dom.publicPlansGrid.querySelectorAll('[data-action="select-plan"]').forEach((button) => {
    button.addEventListener("click", () => selectPlan(button.dataset.plan));
  });
  dom.publicPlansGrid.querySelectorAll('[data-action="checkout-plan"]').forEach((button) => {
    button.addEventListener("click", async () => {
      selectPlan(button.dataset.plan, null, { scroll: false });
      await startMercadoPagoCheckout(button.dataset.plan);
    });
  });
  syncPlanSelectionUI();
}

async function loadPublicPlans() {
  renderPublicPlansSkeleton();
  const catalog = await apiFetch(apiEndpoints.billingPlans);
  renderPublicPlans(catalog);
}

async function startMercadoPagoCheckout(forcedPlan = null) {
  try {
    if (forcedPlan) {
      selectPlan(forcedPlan, dom.registerBillingCycle.value, { scroll: false });
    }
    if (isFreePlan(forcedPlan || dom.registerPlan?.value)) {
      setFeedbackMessage(dom.registerMsg, "Ativando plano Free...", null);
      await submitRegistration();
      return;
    }
    setFeedbackMessage(dom.registerMsg, "Preparando empresa e abrindo Mercado Pago...", null);
    const { billingAccessToken, payload: registerPayload } = await ensurePendingCompanyForCheckout();
    if (!billingAccessToken) {
      throw new Error("Não foi possível autorizar o checkout. Tente cadastrar novamente.");
    }
    const payload = {
      billing_access_token: billingAccessToken,
      plan: forcedPlan || registerPayload.plan,
      billing_cycle: registerPayload.billing_cycle,
      company_name: registerPayload.company.name,
      email: registerPayload.admin.email,
    };
    const checkoutSession = await apiFetch(apiEndpoints.billingCheckout, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    window.location.href = checkoutSession.checkout_url;
  } catch (error) {
    if (error.message.includes("Refaça o cadastro antes de pagar")) {
      setPendingCompanyCheckout(null);
    }
    setFeedbackMessage(dom.registerMsg, error.message, "error");
    showToast(error.message, "error");
  }
}

async function handleCheckoutReturnFromQuery() {
  const url = new URL(window.location.href);
  const checkoutStatus = url.searchParams.get("checkout");
  const plan = url.searchParams.get("plan");
  const billingCycle = url.searchParams.get("billing_cycle");
  const paymentId = url.searchParams.get("payment_id") || url.searchParams.get("collection_id");
  const pendingCompanyCheckout = getPendingCompanyCheckout();
  if (plan) {
    selectPlan(plan, billingCycle, { scroll: false });
  }
  if (!checkoutStatus) return;

  try {
    if (checkoutStatus === "success" || checkoutStatus === "pending") {
      const confirmation =
        paymentId && pendingCompanyCheckout?.billing_access_token
          ? await apiFetch(
              `${apiEndpoints.billingConfirm}${buildQueryString({
                payment_id: paymentId,
              })}`,
              {
                headers: {
                  "X-Billing-Access-Token": pendingCompanyCheckout.billing_access_token,
                },
              }
            )
          : {
              access_released: false,
              message:
                checkoutStatus === "success"
                  ? "Pagamento recebido. Aguarde alguns instantes e tente o login novamente."
                  : "Pagamento pendente no Mercado Pago. Assim que compensar, o acesso será liberado automaticamente.",
            };
      setFeedbackMessage(
        dom.registerMsg,
        confirmation.message,
        confirmation.access_released ? "ok" : checkoutStatus === "success" ? "ok" : null
      );
      showToast(confirmation.message, confirmation.access_released ? "ok" : null);
      if (confirmation.access_released) {
        setPendingCompanyCheckout(null);
      }
    } else {
      const failureMessage = "O pagamento não foi concluído. Você pode tentar novamente pelo Mercado Pago.";
      setFeedbackMessage(dom.registerMsg, failureMessage, "error");
      showToast(failureMessage, "error");
    }
  } catch (error) {
    setFeedbackMessage(dom.registerMsg, error.message, "error");
    showToast(error.message, "error");
  }

  url.searchParams.delete("checkout");
  url.searchParams.delete("plan");
  url.searchParams.delete("billing_cycle");
  url.searchParams.delete("payment_id");
  url.searchParams.delete("collection_id");
  url.searchParams.delete("external_reference");
  url.searchParams.delete("merchant_order_id");
  url.searchParams.delete("preference_id");
  url.searchParams.delete("status");
  window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
}

function syncSidebarBackdrop() {
  const open = dom.sidebar.classList.contains("open");
  if (!dom.sidebarBackdrop) return;
  dom.sidebarBackdrop.hidden = !open;
  dom.sidebarBackdrop.setAttribute("aria-hidden", open ? "false" : "true");
}

function closeSidebarMobile() {
  dom.sidebar.classList.remove("open");
  syncSidebarBackdrop();
}

function updatePage(view) {
  setActiveNav(view);
  dom.pageTitle.textContent = currentPageTitle(view);
}

function productSoldByWeight(product) {
  return Boolean(product?.sold_by_weight);
}

function productStockLabel(product) {
  if (!product) return "-";
  if (productSoldByWeight(product)) {
    return `${Number(product.weight_stock_kg ?? 0).toFixed(3)} kg`;
  }
  return `${product.quantity} un`;
}

function productPriceUnitLabel(product) {
  if (!product) return "";
  return productSoldByWeight(product)
    ? `${formatCurrency(product.price)}/kg`
    : formatCurrency(product.price);
}

function syncProductWeightFormUI() {
  const checkbox = document.getElementById("productSoldByWeight");
  const panel = document.getElementById("productWeightFields");
  const hint = document.getElementById("productPriceHint");
  const soldByWeight = Boolean(checkbox?.checked);
  panel?.classList.toggle("hidden", !soldByWeight);
  if (hint) {
    hint.textContent = soldByWeight ? "Valor por kg" : "Valor por unidade";
  }
  const qtyField = dom.productForm?.querySelector('[name="quantity"]')?.closest(".field");
  const minField = dom.productForm?.querySelector('[name="min_quantity"]')?.closest(".field");
  qtyField?.classList.toggle("hidden", soldByWeight);
  minField?.classList.toggle("hidden", soldByWeight);
}

function createDefaultSaleLine(product = null) {
  const catalogProduct = product || state.products[0];
  if (!catalogProduct) {
    return { product_id: null, sale_mode: "quantity", quantity: 1, weight_kg: null };
  }
  const byWeight = productSoldByWeight(catalogProduct);
  return {
    product_id: catalogProduct.id,
    sale_mode: byWeight ? "weight" : "quantity",
    quantity: byWeight ? null : 1,
    weight_kg: null,
  };
}

function fillProductForm(product) {
  state.editingProductId = product.id;
  dom.productForm.name.value = product.name || "";
  dom.productForm.sku.value = product.sku || "";
  dom.productForm.quantity.value = product.quantity ?? 0;
  dom.productForm.min_quantity.value = product.min_quantity ?? 0;
  dom.productForm.price.value = Number(product.price || 0);
  dom.productForm.description.value = product.description || "";
  const weightCheckbox = document.getElementById("productSoldByWeight");
  if (weightCheckbox) weightCheckbox.checked = productSoldByWeight(product);
  if (dom.productForm.weight_stock_kg) {
    dom.productForm.weight_stock_kg.value = product.weight_stock_kg ?? 0;
  }
  if (dom.productForm.min_weight_kg) {
    dom.productForm.min_weight_kg.value = product.min_weight_kg ?? 0;
  }
  syncProductWeightFormUI();
  setProductValidityFromProduct(product);
  setFeedbackMessage(dom.productMsg, `Editando produto #${product.id}`, "ok");
}

function productValidityInput() {
  return dom.productForm.querySelector('input[name="validity"]');
}

function isoDateTimeFromDateInput(value) {
  if (!value) return null;
  return new Date(`${value}T12:00:00`).toISOString();
}

function setProductValidityFromProduct(product) {
  const el = productValidityInput();
  if (!el || !product?.validity) return;
  const d = new Date(product.validity);
  if (Number.isNaN(d.getTime())) return;
  const today = new Date();
  el.min = today.toISOString().slice(0, 10);
  el.value = d.toISOString().slice(0, 10);
}

function setDefaultProductValidityForNew() {
  const el = productValidityInput();
  if (!el) return;
  const today = new Date();
  el.min = today.toISOString().slice(0, 10);
  const def = new Date();
  def.setFullYear(def.getFullYear() + 1);
  el.value = def.toISOString().slice(0, 10);
}

function clearProductForm() {
  state.editingProductId = null;
  dom.productForm.reset();
  dom.productForm.quantity.value = 0;
  dom.productForm.min_quantity.value = 0;
  dom.productForm.price.value = 0;
  const weightCheckbox = document.getElementById("productSoldByWeight");
  if (weightCheckbox) weightCheckbox.checked = false;
  if (dom.productForm.weight_stock_kg) dom.productForm.weight_stock_kg.value = 0;
  if (dom.productForm.min_weight_kg) dom.productForm.min_weight_kg.value = 0;
  syncProductWeightFormUI();
  setDefaultProductValidityForNew();
  setFeedbackMessage(dom.productMsg, "", null);
}

async function loadProducts() {
  state.products = await apiFetch(apiEndpoints.products);
  const productRows = state.products.map((product) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="cell">${product.name}</div>
      <div class="cell">${product.sku}</div>
      <div class="cell small">${formatProductValidityDisplay(product.validity)}</div>
      <div class="cell small">${productSoldByWeight(product) ? "Peso" : "Un"}</div>
      <div class="cell small">${productStockLabel(product)}</div>
      <div class="cell small">${productSoldByWeight(product) ? Number(product.min_weight_kg ?? 0).toFixed(3) : product.min_quantity}</div>
      <div class="cell small">${productPriceUnitLabel(product)}</div>
      <div class="cell actions">
        <button class="btn btn-ghost" data-action="edit">Editar</button>
        <button class="btn btn-danger" data-action="delete">Excluir</button>
      </div>
    `;

    row.querySelector('[data-action="edit"]').addEventListener("click", () => fillProductForm(product));
    row.querySelector('[data-action="delete"]').addEventListener("click", () => removeProduct(product.id));
    return row;
  });

  renderTable(dom.productsTable, ["Nome", "SKU", "Validade", "Tipo", "Estoque", "Mín", "Preço", "Ações"], productRows);
  renderSaleProductSelects();
}

async function saveProduct(event) {
  event.preventDefault();
  setFeedbackMessage(dom.productMsg, "Salvando...", null);

  const validityEl = productValidityInput();
  const validityRaw = validityEl?.value?.trim();
  if (!validityRaw) {
    setFeedbackMessage(dom.productMsg, "Informe a validade do produto.", "error");
    return;
  }
  const validityIso = isoDateTimeFromDateInput(validityRaw);
  if (!validityIso) {
    setFeedbackMessage(dom.productMsg, "Data de validade inválida.", "error");
    return;
  }

  const soldByWeight = Boolean(document.getElementById("productSoldByWeight")?.checked);
  const payload = {
    name: dom.productForm.name.value.trim(),
    sku: dom.productForm.sku.value.trim(),
    quantity: Number(dom.productForm.quantity.value || 0),
    min_quantity: Number(dom.productForm.min_quantity.value || 0),
    price: Number(dom.productForm.price.value || 0),
    description: dom.productForm.description.value.trim() || null,
    validity: validityIso,
    sold_by_weight: soldByWeight,
    weight_stock_kg: soldByWeight ? Number(dom.productForm.weight_stock_kg?.value || 0) : null,
    min_weight_kg: soldByWeight ? Number(dom.productForm.min_weight_kg?.value || 0) : null,
  };

  try {
    if (state.editingProductId) {
      await apiFetch(`${apiEndpoints.products}/${state.editingProductId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Produto atualizado com sucesso", "ok");
    } else {
      await apiFetch(apiEndpoints.products, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("Produto criado com sucesso", "ok");
    }
    clearProductForm();
    await loadProducts();
  } catch (error) {
    setFeedbackMessage(dom.productMsg, error.message, "error");
  }
}

async function removeProduct(productId) {
  if (!confirm("Excluir este produto?")) return;
  try {
    await apiFetch(`${apiEndpoints.products}/${productId}`, { method: "DELETE" });
    showToast("Produto removido", "ok");
    await loadProducts();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function fillCustomerForm(customer) {
  state.editingCustomerId = customer.id;
  dom.customerForm.name.value = customer.name || "";
  dom.customerForm.email.value = customer.email || "";
  const cpfInput = dom.customerForm.querySelector('input[name="cpf"]');
  if (cpfInput) cpfInput.value = customer.cpf || "";
  dom.customerForm.phone.value = customer.phone || "";
  setFeedbackMessage(dom.customerMsg, `Editando cliente #${customer.id}`, "ok");
}

function clearCustomerForm() {
  state.editingCustomerId = null;
  dom.customerForm.reset();
  setFeedbackMessage(dom.customerMsg, "", null);
}

async function loadCustomers() {
  if (!canAccessCustomers()) {
    state.customers = [];
    renderTable(dom.customersTable, ["Nome", "Email", "CPF", "Telefone", "Ações"], []);
    renderSaleCustomerSelect();
    return;
  }
  state.customers = await apiFetch(apiEndpoints.customers);
  const customerRows = state.customers.map((customer) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="cell">${escapeHtml(customer.name)}</div>
      <div class="cell">${customer.email ? escapeHtml(customer.email) : "—"}</div>
      <div class="cell">${customer.cpf ? escapeHtml(customer.cpf) : "—"}</div>
      <div class="cell">${escapeHtml(customer.phone)}</div>
      <div class="cell actions">
        <button class="btn btn-ghost" data-action="edit">Editar</button>
        <button class="btn btn-danger" data-action="delete">Excluir</button>
      </div>
    `;
    row.querySelector('[data-action="edit"]').addEventListener("click", () => fillCustomerForm(customer));
    row.querySelector('[data-action="delete"]').addEventListener("click", () => removeCustomer(customer.id));
    return row;
  });
  renderTable(dom.customersTable, ["Nome", "Email", "CPF", "Telefone", "Ações"], customerRows);
  renderSaleCustomerSelect();
}

async function saveCustomer(event) {
  event.preventDefault();
  setFeedbackMessage(dom.customerMsg, "Salvando...", null);

  const emailRaw = dom.customerForm.email.value.trim();
  const cpfInput = dom.customerForm.querySelector('input[name="cpf"]');
  const cpfRaw = cpfInput ? String(cpfInput.value || "").replace(/\D/g, "") : "";
  const payload = {
    name: dom.customerForm.name.value.trim(),
    email: emailRaw || null,
    cpf: cpfRaw || null,
    phone: dom.customerForm.phone.value.trim(),
  };

  try {
    if (state.editingCustomerId) {
      await apiFetch(`${apiEndpoints.customers}/${state.editingCustomerId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Cliente atualizado com sucesso", "ok");
    } else {
      await apiFetch(apiEndpoints.customers, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("Cliente criado com sucesso", "ok");
    }
    clearCustomerForm();
    await loadCustomers();
  } catch (error) {
    setFeedbackMessage(dom.customerMsg, error.message, "error");
  }
}

async function removeCustomer(customerId) {
  if (!confirm("Excluir este cliente?")) return;
  try {
    await apiFetch(`${apiEndpoints.customers}/${customerId}`, { method: "DELETE" });
    showToast("Cliente removido", "ok");
    await loadCustomers();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function fillCompanyUserForm(user) {
  state.editingCompanyUserId = user.id;
  dom.companyUserForm.full_name.value = user.full_name || "";
  dom.companyUserForm.email.value = user.email || "";
  dom.companyUserForm.password.value = "";
  dom.companyUserForm.profile.value = user.profile || "collaborator";
  dom.companyUserForm.is_active.checked = Boolean(user.is_active);
  setFeedbackMessage(dom.companyUserMsg, `Editando usuário #${user.id}`, "ok");
}

function clearCompanyUserForm() {
  state.editingCompanyUserId = null;
  dom.companyUserForm.reset();
  dom.companyUserForm.profile.value = "collaborator";
  dom.companyUserForm.is_active.checked = true;
  setFeedbackMessage(dom.companyUserMsg, "", null);
}

async function loadCompanyUsers() {
  if (!canManageCompanyUsers()) {
    state.companyUsers = [];
    renderTable(dom.companyUsersTable, ["Nome", "Email", "Perfil", "Status", "Cadastro", "Ações"], []);
    return;
  }

  state.companyUsers = await apiFetch(apiEndpoints.companyUsers);
  const companyUserRows = state.companyUsers.map((companyUser) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="cell">
        <strong>${escapeHtml(companyUser.full_name || "Sem nome")}</strong>
        <div class="audit-detail">${companyUser.is_current_user ? "Sua conta atual" : "Usuário da empresa"}</div>
      </div>
      <div class="cell">${escapeHtml(companyUser.email)}</div>
      <div class="cell small"><span class="badge">${companyUser.profile === "owner" ? "dono" : "colaborador"}</span></div>
      <div class="cell small">
        <span class="badge ${companyUser.is_active ? "info" : "warning"}">${companyUser.is_active ? "ativo" : "inativo"}</span>
      </div>
      <div class="cell small">${formatDate(companyUser.created_at)}</div>
      <div class="cell actions">
        <button class="btn btn-ghost" data-action="edit">Editar</button>
      </div>
    `;
    row.querySelector('[data-action="edit"]').addEventListener("click", () => fillCompanyUserForm(companyUser));
    return row;
  });

  renderTable(
    dom.companyUsersTable,
    ["Nome", "Email", "Perfil", "Status", "Cadastro", "Ações"],
    companyUserRows
  );
}

async function saveCompanyUser(event) {
  event.preventDefault();
  setFeedbackMessage(dom.companyUserMsg, "Salvando...", null);

  const password = dom.companyUserForm.password.value;
  if (!state.editingCompanyUserId && !password.trim()) {
    setFeedbackMessage(dom.companyUserMsg, "Informe uma senha para o novo usuário", "error");
    return;
  }
  const payload = {
    full_name: dom.companyUserForm.full_name.value.trim() || null,
    email: dom.companyUserForm.email.value.trim(),
    profile: dom.companyUserForm.profile.value,
    is_active: dom.companyUserForm.is_active.checked,
  };
  if (!state.editingCompanyUserId || password.trim()) {
    payload.password = password;
  }

  try {
    if (state.editingCompanyUserId) {
      await apiFetch(`${apiEndpoints.companyUsers}/${state.editingCompanyUserId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Usuário atualizado com sucesso", "ok");
    } else {
      await apiFetch(apiEndpoints.companyUsers, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("Usuário criado com sucesso", "ok");
    }

    clearCompanyUserForm();
    await refreshCurrentUser();
    applyFeatureVisibility();

    if (!canManageCompanyUsers()) {
      await openView(defaultAuthedView());
      return;
    }

    await loadCompanyUsers();
  } catch (error) {
    setFeedbackMessage(dom.companyUserMsg, error.message, "error");
  }
}

function addSaleLine(defaultItem = null) {
  state.salesDraft.push(defaultItem || createDefaultSaleLine());
  renderSaleItems();
}

function removeSaleLine(index) {
  state.salesDraft.splice(index, 1);
  if (!state.salesDraft.length) addSaleLine();
  renderSaleItems();
}

function renderSaleCustomerSelect() {
  const options = ['<option value="">Sem cliente (opcional)</option>'];
  state.customers.forEach((c) => {
      options.push(
        `<option value="${c.id}">${escapeHtml(c.name)}${c.email ? ` (${escapeHtml(c.email)})` : ""}</option>`
      );
  });
  dom.saleCustomerSelect.innerHTML = options.join("");
}

function renderSaleProductSelects() {
  renderSaleItems();
}

function findProductBySku(rawSku) {
  const sku = String(rawSku || "").trim().toLowerCase();
  if (!sku) return null;
  return state.products.find((product) => String(product.sku || "").trim().toLowerCase() === sku) || null;
}

function getSaleLineProduct(saleDraftLine) {
  return state.products.find((catalogProduct) => catalogProduct.id === Number(saleDraftLine.product_id));
}

function normalizeSaleLineForProduct(saleDraftLine, product) {
  if (!product) return saleDraftLine;
  if (!productSoldByWeight(product)) {
    saleDraftLine.sale_mode = "quantity";
    saleDraftLine.quantity = saleDraftLine.quantity || 1;
    saleDraftLine.weight_kg = null;
    return saleDraftLine;
  }
  if (saleDraftLine.sale_mode !== "quantity" && saleDraftLine.sale_mode !== "weight") {
    saleDraftLine.sale_mode = "weight";
  }
  if (saleDraftLine.sale_mode === "weight") {
    saleDraftLine.quantity = null;
  } else {
    saleDraftLine.weight_kg = null;
    saleDraftLine.quantity = saleDraftLine.quantity || 1;
  }
  return saleDraftLine;
}

function addProductBySku() {
  const sku = dom.saleSkuInput.value.trim();
  if (!sku) {
    setFeedbackMessage(dom.saleMsg, "Informe um SKU para adicionar o produto", "error");
    return;
  }

  const product = findProductBySku(sku);
  if (!product) {
    setFeedbackMessage(dom.saleMsg, `Produto não encontrado para o SKU ${sku}`, "error");
    return;
  }

  const existingSaleDraftLine = state.salesDraft.find(
    (saleDraftLine) => Number(saleDraftLine.product_id) === Number(product.id)
  );
  if (existingSaleDraftLine) {
    normalizeSaleLineForProduct(existingSaleDraftLine, product);
    if (existingSaleDraftLine.sale_mode === "weight") {
      setFeedbackMessage(dom.saleMsg, "Produto já está na venda (modo peso). Ajuste o kg na linha.", "ok");
    } else {
      existingSaleDraftLine.quantity = Number(existingSaleDraftLine.quantity || 0) + 1;
    }
  } else {
    state.salesDraft.push(createDefaultSaleLine(product));
  }

  dom.saleSkuInput.value = "";
  setFeedbackMessage(dom.saleMsg, `Produto adicionado via SKU: ${product.name}`, "ok");
  renderSaleItems();
}

function calculateSaleLineTotal(saleDraftLine) {
  const product = getSaleLineProduct(saleDraftLine);
  if (!product) return 0;
  const unitPrice = Number(product.price || 0);
  if (saleDraftLine.sale_mode === "weight") {
    return unitPrice * Number(saleDraftLine.weight_kg || 0);
  }
  return unitPrice * Number(saleDraftLine.quantity || 0);
}

function calculateSaleDraftTotal() {
  return state.salesDraft.reduce(
    (totalAccumulator, saleDraftLine) => totalAccumulator + calculateSaleLineTotal(saleDraftLine),
    0
  );
}

function updateSaleTotalText() {
  dom.saleDraftTotal.textContent = `Total: ${formatCurrency(calculateSaleDraftTotal())}`;
}

async function readScaleWeightIntoInput(inputEl, messageEl) {
  if (!window.ScaleReader?.isSupported?.()) {
    setFeedbackMessage(
      messageEl || dom.saleMsg,
      "Balança serial: use Chrome ou Edge em HTTPS/localhost, ou digite o peso manualmente.",
      "error"
    );
    return;
  }
  try {
    setFeedbackMessage(messageEl || dom.saleMsg, "Aguardando leitura da balança...", null);
    const weight = await window.ScaleReader.readWeight();
    inputEl.value = String(weight);
    inputEl.dispatchEvent(new Event("input", { bubbles: true }));
    setFeedbackMessage(messageEl || dom.saleMsg, `Peso lido: ${weight} kg`, "ok");
  } catch (error) {
    setFeedbackMessage(messageEl || dom.saleMsg, error.message || "Falha ao ler balança", "error");
  }
}

function renderSaleItems() {
  if (!state.salesDraft.length) {
    state.salesDraft.push(createDefaultSaleLine());
  }

  dom.saleItemsContainer.innerHTML = "";

  state.salesDraft.forEach((saleDraftLine, index) => {
    const product = getSaleLineProduct(saleDraftLine);
    normalizeSaleLineForProduct(saleDraftLine, product);

    const row = document.createElement('div');
    row.className = "sale-item";

    const productSelect = document.createElement('select');
    state.products.forEach((catalogProduct) => {
      const option = document.createElement('option');
      option.value = catalogProduct.id;
      option.textContent = `${catalogProduct.name} | ${productPriceUnitLabel(catalogProduct)} | estoque ${productStockLabel(catalogProduct)}`;
      option.selected = Number(saleDraftLine.product_id) === catalogProduct.id;
      productSelect.appendChild(option);
    });

    const modeWrap = document.createElement('div');
    modeWrap.className = "sale-item-mode";

    const qtyWrap = document.createElement('div');
    qtyWrap.className = "sale-qty-wrap";
    const qtyLabel = document.createElement('label');
    qtyLabel.textContent = "Quantidade (un)";
    const qtyInput = document.createElement('input');
    qtyInput.type = "number";
    qtyInput.min = "1";
    qtyInput.step = "1";
    qtyInput.value = saleDraftLine.quantity || 1;
    qtyWrap.appendChild(qtyLabel);
    qtyWrap.appendChild(qtyInput);

    const weightWrap = document.createElement('div');
    weightWrap.className = "sale-weight-wrap";
    const weightLabel = document.createElement('label');
    weightLabel.textContent = "Peso (kg)";
    const weightInput = document.createElement('input');
    weightInput.type = "number";
    weightInput.min = "0.001";
    weightInput.step = "0.001";
    weightInput.placeholder = "0,000";
    weightInput.value = saleDraftLine.weight_kg ?? "";
    const weightActions = document.createElement('div');
    weightActions.className = "sale-weight-actions";
    const scaleBtn = document.createElement('button');
    scaleBtn.type = "button";
    scaleBtn.className = "btn btn-ghost";
    scaleBtn.textContent = "Ler balança";
    scaleBtn.addEventListener("click", () => readScaleWeightIntoInput(weightInput));
    weightActions.appendChild(scaleBtn);
    weightWrap.appendChild(weightLabel);
    weightWrap.appendChild(weightInput);
    weightWrap.appendChild(weightActions);

    const btnQty = document.createElement('button');
    btnQty.type = "button";
    btnQty.className = "btn btn-ghost sale-mode-btn";
    btnQty.textContent = "Unidade";
    const btnWeight = document.createElement('button');
    btnWeight.type = "button";
    btnWeight.className = "btn btn-ghost sale-mode-btn";
    btnWeight.textContent = "Peso";

    const totalInfo = document.createElement('div');
    totalInfo.className = "sale-line-total";
    totalInfo.textContent = formatCurrency(calculateSaleLineTotal(saleDraftLine));

    const removeButton = document.createElement('button');
    removeButton.className = "btn btn-danger";
    removeButton.type = "button";
    removeButton.textContent = "Remover";

    function refreshModeUI() {
      const p = getSaleLineProduct(saleDraftLine);
      const canWeigh = productSoldByWeight(p);
      modeWrap.classList.toggle("hidden", !canWeigh);
      if (!canWeigh) {
        saleDraftLine.sale_mode = "quantity";
      }
      const isWeight = saleDraftLine.sale_mode === "weight";
      btnQty.classList.toggle("active", !isWeight);
      btnWeight.classList.toggle("active", isWeight);
      qtyWrap.classList.toggle("hidden", isWeight);
      weightWrap.classList.toggle("hidden", !isWeight);
    }

    btnQty.addEventListener("click", () => {
      saleDraftLine.sale_mode = "quantity";
      saleDraftLine.weight_kg = null;
      saleDraftLine.quantity = saleDraftLine.quantity || 1;
      qtyInput.value = saleDraftLine.quantity;
      refreshModeUI();
      totalInfo.textContent = formatCurrency(calculateSaleLineTotal(saleDraftLine));
      updateSaleTotalText();
    });

    btnWeight.addEventListener("click", () => {
      saleDraftLine.sale_mode = "weight";
      saleDraftLine.quantity = null;
      refreshModeUI();
      totalInfo.textContent = formatCurrency(calculateSaleLineTotal(saleDraftLine));
      updateSaleTotalText();
    });

    modeWrap.appendChild(btnQty);
    modeWrap.appendChild(btnWeight);

    productSelect.addEventListener("change", () => {
      state.salesDraft[index].product_id = Number(productSelect.value);
      normalizeSaleLineForProduct(state.salesDraft[index], getSaleLineProduct(state.salesDraft[index]));
      if (state.salesDraft[index].sale_mode === "quantity") {
        qtyInput.value = state.salesDraft[index].quantity || 1;
      } else {
        weightInput.value = state.salesDraft[index].weight_kg ?? "";
      }
      refreshModeUI();
      totalInfo.textContent = formatCurrency(calculateSaleLineTotal(state.salesDraft[index]));
      updateSaleTotalText();
    });

    qtyInput.addEventListener("input", () => {
      state.salesDraft[index].quantity = Math.max(1, Number(qtyInput.value || 1));
      qtyInput.value = state.salesDraft[index].quantity;
      totalInfo.textContent = formatCurrency(calculateSaleLineTotal(state.salesDraft[index]));
      updateSaleTotalText();
    });

    weightInput.addEventListener("input", () => {
      const parsed = Number(weightInput.value);
      state.salesDraft[index].weight_kg = Number.isFinite(parsed) && parsed > 0 ? parsed : null;
      totalInfo.textContent = formatCurrency(calculateSaleLineTotal(state.salesDraft[index]));
      updateSaleTotalText();
    });

    removeButton.addEventListener("click", () => removeSaleLine(index));

    row.appendChild(productSelect);
    row.appendChild(modeWrap);
    row.appendChild(qtyWrap);
    row.appendChild(weightWrap);
    row.appendChild(totalInfo);
    row.appendChild(removeButton);
    dom.saleItemsContainer.appendChild(row);
    refreshModeUI();
  });

  updateSaleTotalText();
}


function resetSaleForm() {
  dom.saleForm.reset();
  state.salesDraft = [];
  addSaleLine();
  setFeedbackMessage(dom.saleMsg, "", null);
}

function buildSalePayload() {
  const rawCustomerId = dom.saleCustomerSelect.value.trim();
  const customerId = rawCustomerId ? Number(rawCustomerId) : null;

  const saleItems = state.salesDraft
    .map((saleDraftLine) => {
      const product = getSaleLineProduct(saleDraftLine);
      normalizeSaleLineForProduct(saleDraftLine, product);
      const base = { product_id: Number(saleDraftLine.product_id) };
      if (saleDraftLine.sale_mode === "weight") {
        return { ...base, weight_kg: Number(saleDraftLine.weight_kg) };
      }
      return { ...base, quantity: Number(saleDraftLine.quantity) };
    })
    .filter((saleItem) => {
      if (!(saleItem.product_id > 0)) return false;
      if (saleItem.weight_kg != null) return saleItem.weight_kg > 0;
      return saleItem.quantity > 0;
    });

  if (!saleItems.length) throw new Error("Adicione ao menos um item válido na venda");

  return {
    customer_id: customerId,
    items: saleItems,
  };
}

async function saveSale(event) {
  event.preventDefault();
  setFeedbackMessage(dom.saleMsg, "Processando venda...", null);

  try {
    const payload = buildSalePayload();
    await apiFetch(apiEndpoints.sales, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    showToast("Venda registrada com sucesso", "ok");
    resetSaleForm();

    await Promise.all([
      loadProducts(),
      loadSales(),
      canAccessCompanyAudit() ? loadAudit() : Promise.resolve(),
      hasFeature("dashboard_avancado") ? loadDashboard() : Promise.resolve(),
      hasFeature("relatorio") ? loadReports() : Promise.resolve(),
    ]);
  } catch (error) {
    setFeedbackMessage(dom.saleMsg, error.message, "error");
  }
}

async function loadSales() {
  if (!hasFeature("vendas")) return;
  const sales = await apiFetch(`${apiEndpoints.sales}?limit=100`);
  const saleRows = sales.map((sale) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="cell small">#${sale.id}</div>
      <div class="cell">${sale.customer_name}</div>
      <div class="cell small">${sale.items_count}</div>
      <div class="cell small">${formatCurrency(sale.total_value)}</div>
      <div class="cell small">${formatDate(sale.created_at)}</div>
    `;
    return row;
  });

  renderTable(dom.salesTable, ["Venda", "Cliente", "Itens", "Total", "Data"], saleRows);
}

function destroyChart(instanceKey) {
  if (state.charts[instanceKey]) {
    state.charts[instanceKey].destroy();
    state.charts[instanceKey] = null;
  }
}

function paintChart(instanceKey, canvasId, config) {
  destroyChart(instanceKey);
  const ctx = document.getElementById(canvasId);
  state.charts[instanceKey] = new Chart(ctx, config);
}

function renderAlerts(alerts) {
  dom.alertsList.innerHTML = "";
  if (!alerts.length) {
    const emptyAlertNode = document.createElement("div");
    emptyAlertNode.className = "alert-item";
    emptyAlertNode.textContent = "Sem alertas no momento.";
    dom.alertsList.appendChild(emptyAlertNode);
    return;
  }

  alerts.forEach((alert) => {
    const alertNode = document.createElement("div");
    alertNode.className = "alert-item";
    const badge = `<span class="badge ${alert.level}">${alert.level.toUpperCase()}</span>`;
    alertNode.innerHTML = `${badge} <strong>${alert.category}</strong> - ${alert.message}`;
    dom.alertsList.appendChild(alertNode);
  });
}

async function loadDashboard() {
  if (!hasFeature("dashboard_avancado")) return;

  const dashboardSummary = await apiFetch(apiEndpoints.dashboardSummary);

  dom.salesTodayMetric.textContent = formatCurrency(dashboardSummary.sales_today);
  dom.revenueMetric.textContent = formatCurrency(dashboardSummary.total_revenue);
  dom.totalSalesMetric.textContent = Number(dashboardSummary.total_sales_count || 0).toLocaleString(
    "pt-BR"
  );
  dom.totalProductsMetric.textContent = Number(dashboardSummary.total_products || 0).toLocaleString(
    "pt-BR"
  );
  dom.dashboardUpdated.textContent = formatDate(new Date());

  renderAlerts(dashboardSummary.alerts || []);

  const recentSaleRows = (dashboardSummary.recent_sales || []).map((sale) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="cell small">#${sale.sale_id}</div>
      <div class="cell">${sale.customer_name}</div>
      <div class="cell small">${formatCurrency(sale.total_value)}</div>
      <div class="cell small">${formatDate(sale.created_at)}</div>
    `;
    return row;
  });
  renderTable(dom.recentSalesTable, ["Venda", "Cliente", "Total", "Data"], recentSaleRows);

  paintChart("day", "salesByDayChart", {
    type: "line",
    data: {
      labels: (dashboardSummary.sales_by_day || []).map((dailySalesEntry) => dailySalesEntry.day),
      datasets: [
        {
          label: "Vendas",
          data: (dashboardSummary.sales_by_day || []).map((dailySalesEntry) => dailySalesEntry.total),
          borderColor: "rgba(31,111,235,1)",
          backgroundColor: "rgba(31,111,235,0.2)",
          borderWidth: 2,
          tension: 0.3,
          fill: true,
        },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });

  paintChart("month", "salesByMonthChart", {
    type: "bar",
    data: {
      labels: (dashboardSummary.sales_by_month || []).map((monthlySalesEntry) => monthlySalesEntry.month),
      datasets: [
        {
          label: "Faturamento",
          data: (dashboardSummary.sales_by_month || []).map((monthlySalesEntry) => monthlySalesEntry.total),
          borderWidth: 1,
          backgroundColor: "rgba(255,158,58,0.6)",
          borderColor: "rgba(255,158,58,1)",
        },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });

  paintChart("product", "salesByProductChart", {
    type: "doughnut",
    data: {
      labels: (dashboardSummary.sales_by_product || []).map((topProduct) => topProduct.product_name),
      datasets: [
        {
          label: "Quantidade",
          data: (dashboardSummary.sales_by_product || []).map((topProduct) => topProduct.quantity_sold),
          backgroundColor: [
            "rgba(31,111,235,0.75)",
            "rgba(255,158,58,0.75)",
            "rgba(18,128,92,0.75)",
            "rgba(200,55,74,0.75)",
            "rgba(107,89,255,0.75)",
            "rgba(91,174,165,0.75)",
            "rgba(217,133,66,0.75)",
          ],
        },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}
async function loadReports() {
  if (!hasFeature("relatorio")) return;

  const [
    revenueSummary,
    salesByDayReport,
    salesByMonthReport,
    topProductsReport,
    salesHistoryReport,
  ] = await Promise.all([
    apiFetch(apiEndpoints.reportsRevenue),
    apiFetch(apiEndpoints.reportsByDay),
    apiFetch(apiEndpoints.reportsByMonth),
    apiFetch(apiEndpoints.reportsTopProducts),
    apiFetch(apiEndpoints.reportsHistory),
  ]);

  dom.reportsRevenueMetric.textContent = formatCurrency(revenueSummary.total_revenue || 0);

  const salesByDayRows = (salesByDayReport || []).map((dayEntry) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="cell">${dayEntry.day}</div>
      <div class="cell small">${formatCurrency(dayEntry.total)}</div>
    `;
    return row;
  });
  renderTable(dom.reportByDayTable, ["Dia", "Total"], salesByDayRows);

  const salesByMonthRows = (salesByMonthReport || []).map((monthEntry) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="cell">${monthEntry.month}</div>
      <div class="cell small">${formatCurrency(monthEntry.total)}</div>
    `;
    return row;
  });
  renderTable(dom.reportByMonthTable, ["Mês", "Total"], salesByMonthRows);

  const topProductRows = (topProductsReport || []).map((topProductEntry) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="cell">${topProductEntry.product_name}</div>
      <div class="cell small">${topProductEntry.quantity_sold}</div>
      <div class="cell small">${formatCurrency(topProductEntry.revenue)}</div>
    `;
    return row;
  });
  renderTable(dom.reportTopProductsTable, ["Produto", "Qtd", "Receita"], topProductRows);

  const salesHistoryRows = (salesHistoryReport || []).map((saleHistoryEntry) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="cell small">#${saleHistoryEntry.sale_id}</div>
      <div class="cell">${saleHistoryEntry.customer_name}</div>
      <div class="cell small">${formatCurrency(saleHistoryEntry.total_value)}</div>
      <div class="cell small">${formatDate(saleHistoryEntry.created_at)}</div>
    `;
    return row;
  });
  renderTable(dom.reportHistoryTable, ["Venda", "Cliente", "Total", "Data"], salesHistoryRows);
}

async function downloadReportPdf() {
  try {
    setLoading(true, "Gerando PDF...");
    const token = getAuthToken();
    const response = await fetch(apiEndpoints.reportsExportPdf, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error(`Falha ao exportar PDF (${response.status})`);

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "relatorio-vendas.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    showToast("PDF exportado", "ok");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function printReport() {
  try {
    setLoading(true, "Preparando impressão...");
    const payload = await apiFetch(apiEndpoints.reportsExportPrint);
    const popup = window.open("", "_blank");
    if (!popup) throw new Error("Permita pop-ups para imprimir o relatório");

    popup.document.open();
    popup.document.write(payload.html || "");
    popup.document.close();
    popup.focus();
    popup.print();
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function loadAudit() {
  if (!canAccessCompanyAudit()) {
    renderTable(dom.auditTable, ["Data", "Ação", "Entidade", "Detalhes"], []);
    return;
  }
  const auditLogs = await apiFetch(
    `${apiEndpoints.audit}${buildQueryString({
      action: dom.auditActionFilter.value.trim(),
      entity: dom.auditEntityFilter.value.trim(),
      search: dom.auditSearchFilter.value.trim(),
      limit: 200,
    })}`
  );
  const auditRows = (auditLogs || []).map((auditLog) => {
    const row = document.createElement("div");
    row.className = "row";
    const beforeJson = formatJsonPreview(auditLog.before_data);
    const afterJson = formatJsonPreview(auditLog.after_data);
    row.innerHTML = `
      <div class="cell small">${formatDate(auditLog.created_at)}</div>
      <div class="cell small"><span class="badge">${auditLog.action}</span></div>
      <div class="cell">${escapeHtml(auditLog.entity)} #${auditLog.entity_id ?? "-"}</div>
      <div class="cell">
        <div>${escapeHtml(auditLog.description)}</div>
        <div class="audit-detail">
          ${escapeHtml(auditLog.user_email || "-")} | ${escapeHtml(auditLog.ip_address || "-")}
        </div>
        ${
          beforeJson || afterJson
            ? `<details class="audit-json">
                <summary>Ver before/after</summary>
                ${beforeJson ? `<pre>Antes\n${escapeHtml(beforeJson)}</pre>` : ""}
                ${afterJson ? `<pre>Depois\n${escapeHtml(afterJson)}</pre>` : ""}
              </details>`
            : ""
        }
      </div>
    `;
    return row;
  });
  renderTable(dom.auditTable, ["Data", "Ação", "Entidade", "Detalhes"], auditRows);
}

async function saveSettings(event) {
  event.preventDefault();
  setFeedbackMessage(dom.settingsMsg, "Salvando...", null);

  const features = Array.from(document.querySelectorAll(".feature-option input:checked")).map(
    (input) => input.value
  );
  const nextTheme = dom.settingsTheme.value;
  const nextPrimaryColor = dom.settingsPrimaryColor.value.trim() || null;
  const nextSettingsLogoUrl = dom.settingsLogoUrlInput.value.trim() || null;
  const selectedSettingsLogoFile = dom.settingsLogoFileInput?.files?.[0] || null;

  try {
    if (selectedSettingsLogoFile) {
      const formData = new FormData();
      formData.set("logo_file", selectedSettingsLogoFile);
      setFeedbackMessage(dom.settingsMsg, "Enviando logo...", null);
      state.settings = await apiFetch(apiEndpoints.settingsLogo, {
        method: "POST",
        body: formData,
      });
      dom.settingsLogoUrlInput.value = state.settings.logo_url || "";
      clearSettingsLogoSelection();
    }

    const payload = {};
    if (nextTheme !== (state.settings?.theme || "light")) {
      payload.theme = nextTheme;
    }
    if (nextPrimaryColor !== (state.settings?.primary_color || null)) {
      payload.primary_color = nextPrimaryColor;
    }
    if (!sameFeatureSet(features, state.settings?.features || [])) {
      payload.features = features;
    }
    if (!selectedSettingsLogoFile && nextSettingsLogoUrl !== (state.settings?.logo_url || null)) {
      payload.logo_url = nextSettingsLogoUrl;
    }

    if (Object.keys(payload).length) {
      setFeedbackMessage(dom.settingsMsg, "Salvando...", null);
      state.settings = await apiFetch(apiEndpoints.settings, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
    }

    setFeedbackMessage(dom.settingsMsg, "Configurações salvas", "ok");
    showToast("Configurações atualizadas", "ok");
    applyTheme();
    applyFeatureVisibility();
    fillSettingsForm();

    const targetView = defaultAuthedView();
    await openView(targetView);
  } catch (error) {
    setFeedbackMessage(dom.settingsMsg, error.message, "error");
  }
}

function resetForgotPasswordWizard() {
  if (!dom.forgotResetToken) return;
  dom.forgotResetToken.value = "";
  dom.forgotPasswordStep2?.classList.add("hidden");
  if (dom.forgotNewPassword) dom.forgotNewPassword.value = "";
  if (dom.forgotNewPasswordConfirm) dom.forgotNewPasswordConfirm.value = "";
  if (dom.forgotPasswordMsg) setFeedbackMessage(dom.forgotPasswordMsg, "", null);
}

function toggleForgotPasswordPanel() {
  if (!dom.forgotPasswordPanel) return;
  const wasHidden = dom.forgotPasswordPanel.classList.contains("hidden");
  dom.forgotPasswordPanel.classList.toggle("hidden");
  if (wasHidden) {
    resetForgotPasswordWizard();
    if (dom.loginForm?.email?.value?.trim() && dom.forgotPasswordEmail) {
      dom.forgotPasswordEmail.value = dom.loginForm.email.value.trim();
    }
    return;
  }
  resetForgotPasswordWizard();
}

async function requestPasswordReset() {
  const email = String(dom.forgotPasswordEmail?.value || "").trim().toLowerCase();
  if (!email) {
    setFeedbackMessage(dom.forgotPasswordMsg, "Informe o e-mail da conta.", "error");
    return;
  }
  setFeedbackMessage(dom.forgotPasswordMsg, "Enviando solicitação...", null);
  try {
    const responseData = await apiFetch(apiEndpoints.forgotPassword, {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    dom.forgotResetToken.value = responseData.reset_token || "";
    const hasToken = Boolean(responseData.reset_token);
    dom.forgotPasswordStep2?.classList.toggle("hidden", !hasToken);
    let message = responseData.detail || "Solicitação processada.";
    if (!hasToken) {
      message +=
        " Se esta etapa não abrir em seguida, o servidor pode estar configurado para não devolver código na página (PASSWORD_RESET_TOKEN_IN_RESPONSE=false ou fluxo apenas por e-mail).";
    }
    setFeedbackMessage(dom.forgotPasswordMsg, message, hasToken ? "ok" : null);
  } catch (error) {
    setFeedbackMessage(dom.forgotPasswordMsg, error.message, "error");
  }
}

async function submitPasswordReset() {
  const token = String(dom.forgotResetToken?.value || "").trim();
  if (!token) {
    setFeedbackMessage(dom.forgotPasswordMsg, "Solicite o código de recuperação primeiro.", "error");
    return;
  }
  const newPassword = dom.forgotNewPassword?.value || "";
  const confirmPassword = dom.forgotNewPasswordConfirm?.value || "";
  if (newPassword.length < 6) {
    setFeedbackMessage(dom.forgotPasswordMsg, "A nova senha deve ter pelo menos 6 caracteres.", "error");
    return;
  }
  if (newPassword !== confirmPassword) {
    setFeedbackMessage(dom.forgotPasswordMsg, "As senhas não coincidem.", "error");
    return;
  }

  try {
    const payload = await apiFetch(apiEndpoints.resetPassword, {
      method: "POST",
      body: JSON.stringify({ reset_token: token, new_password: newPassword }),
    });
    const successMessage =
      typeof payload?.detail === "string" ? payload.detail : "Senha alterada. Você já pode entrar.";
    showToast(successMessage, "ok");
    setFeedbackMessage(dom.loginMsg, "Senha atualizada — faça login com a nova senha.", "ok");
    dom.loginForm.password.value = "";
    dom.forgotPasswordPanel?.classList.add("hidden");
    resetForgotPasswordWizard();
  } catch (error) {
    setFeedbackMessage(dom.forgotPasswordMsg, error.message, "error");
  }
}

async function doLogin(event) {
  event.preventDefault();
  setFeedbackMessage(dom.loginMsg, "Entrando...", null);

  const form = new URLSearchParams();
  form.set("username", dom.loginForm.email.value.trim());
  form.set("password", dom.loginForm.password.value);

  try {
    const loginResponse = await apiFetch(apiEndpoints.login, { method: "POST", body: form, headers: {} });
    setAuthToken(loginResponse.access_token);
    setFeedbackMessage(dom.loginMsg, "Login realizado", "ok");
    await initializeAuthenticatedArea();
  } catch (error) {
    setFeedbackMessage(dom.loginMsg, error.message, "error");
  }
}

async function submitRegistration() {
  const payload = buildRegisterPayload();
  const registrationResponse = await apiFetch(apiEndpoints.register, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  const accessReleased = registrationResponse?.company?.status === "active";

  if (accessReleased) {
    setPendingCompanyCheckout(null);
    setFeedbackMessage(
      dom.registerMsg,
      "Empresa liberada no plano Free. Você já pode fazer login e usar todos os modulos com limites iniciais.",
      "ok"
    );
    showToast("Plano Free liberado", "ok");
    return { registrationResponse, payload, accessReleased };
  }

  rememberPendingCompanyCheckout(registrationResponse, payload);
  setFeedbackMessage(
    dom.registerMsg,
    "Empresa preparada para cobrança. Após o pagamento aprovado, o acesso será liberado automaticamente.",
    "ok"
  );
  showToast("Empresa preparada para checkout", "ok");
  return { registrationResponse, payload, accessReleased };
}

async function doRegister(event) {
  event.preventDefault();
  setFeedbackMessage(dom.registerMsg, "Cadastrando...", null);

  try {
    await submitRegistration();
  } catch (error) {
    setFeedbackMessage(dom.registerMsg, error.message, "error");
  }
}

async function removeSettingsLogo(event) {
  event.preventDefault();
  if (!state.settings?.logo_url) {
    clearSettingsLogoSelection();
    dom.settingsLogoUrlInput.value = "";
    refreshSettingsLogoPreview();
    return;
  }

  setFeedbackMessage(dom.settingsMsg, "Removendo logo...", null);
  try {
    state.settings = await apiFetch(apiEndpoints.settings, {
      method: "PUT",
      body: JSON.stringify({ logo_url: null }),
    });
    dom.settingsLogoUrlInput.value = "";
    clearSettingsLogoSelection();
    applyTheme();
    fillSettingsForm();
    setFeedbackMessage(dom.settingsMsg, "Logo removida", "ok");
    showToast("Logo removida", "ok");
  } catch (error) {
    setFeedbackMessage(dom.settingsMsg, error.message, "error");
  }
}

function resetUserContext() {
  state.currentUser = null;
  state.settings = null;
  state.products = [];
  state.customers = [];
  state.companyUsers = [];
  state.salesDraft = [];
  state.editingProductId = null;
  state.editingCustomerId = null;
  state.editingCompanyUserId = null;
  revokeSettingsLogoPreviewUrl();
  destroyChart("day");
  destroyChart("month");
  destroyChart("product");
}

function handleLoggedOut() {
  clearAuthToken();
  resetUserContext();
  dom.sidebar.style.display = "none";
  dom.currentUserChip.textContent = "Não autenticado";
  dom.brandSub.textContent = "SaaS multiempresa";
  dom.pageTitle.textContent = "Entrar";
  dom.settingsTheme.value = "light";
  dom.settingsPrimaryColor.value = "";
  dom.settingsLogoUrlInput.value = "";
  document.body.classList.remove("theme-dark", "theme-pink");
  document.body.style.removeProperty("--primary");
  applyLogoToNode(dom.brandLogo, null);
  clearSettingsLogoSelection();
  updateRemoveSettingsLogoButtonState();
  dom.forgotPasswordPanel?.classList.add("hidden");
  resetForgotPasswordWizard();
  showView("auth");
  setActiveNav(null);
  syncPlanSelectionUI();
}

async function openView(viewName) {
  if (viewName === "customers" && !canAccessCustomers()) {
    showToast("O plano atual não inclui o módulo de clientes", "error");
    viewName = defaultAuthedView();
  }
  if (viewName === "users" && !canManageCompanyUsers()) {
    showToast("Gestao de usuarios disponivel apenas para o dono da empresa com acesso liberado", "error");
    viewName = defaultAuthedView();
  }
  if (viewName === "audit" && !canAccessCompanyAudit()) {
    showToast("Auditoria disponivel apenas para o dono da empresa com acesso liberado", "error");
    viewName = defaultAuthedView();
  }
  if (viewName === "sales" && !hasFeature("vendas")) {
    showToast("Funcionalidade de vendas desativada para esta empresa", "error");
    viewName = defaultAuthedView();
  }
  if (viewName === "reports" && !hasFeature("relatorio")) {
    showToast("Relatórios desativados para esta empresa", "error");
    viewName = defaultAuthedView();
  }
  if (viewName === "dashboard" && !hasFeature("dashboard_avancado")) {
    showToast("Dashboard avançado desativado para esta empresa", "error");
    viewName = defaultAuthedView();
  }

  showView(viewName);
  updatePage(viewName);
  closeSidebarMobile();

  setLoading(true, "Atualizando dados...");
  try {
    if (viewName === "dashboard") {
      await loadDashboard();
    } else if (viewName === "products") {
      await loadProducts();
      if (!state.editingProductId) {
        setDefaultProductValidityForNew();
      }
    } else if (viewName === "customers") {
      await loadCustomers();
    } else if (viewName === "users") {
      await loadCompanyUsers();
    } else if (viewName === "sales") {
      await Promise.all([loadProducts(), canAccessCustomers() ? loadCustomers() : Promise.resolve(), loadSales()]);
      if (!state.salesDraft.length) addSaleLine();
      renderSaleCustomerSelect();
    } else if (viewName === "reports") {
      await loadReports();
    } else if (viewName === "audit") {
      await loadAudit();
    } else if (viewName === "settings") {
      await refreshSettings();
    }
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function initialDataLoad() {
  setLoading(true, "Carregando módulo...");
  try {
    await Promise.all([
      loadProducts(),
      canAccessCustomers() ? loadCustomers() : Promise.resolve(),
      canManageCompanyUsers() ? loadCompanyUsers() : Promise.resolve(),
      canAccessCompanyAudit() ? loadAudit() : Promise.resolve(),
      hasFeature("vendas") ? loadSales() : Promise.resolve(),
      hasFeature("dashboard_avancado") ? loadDashboard() : Promise.resolve(),
      hasFeature("relatorio") ? loadReports() : Promise.resolve(),
    ]);

    renderSaleCustomerSelect();
    if (!state.salesDraft.length) addSaleLine();
  } finally {
    setLoading(false);
  }
}

async function initializeAuthenticatedArea() {
  setLoading(true, "Sincronizando sessão...");
  try {
    dom.sidebar.style.display = "";
    await refreshCurrentUser();
    await refreshSettings();
    showView(defaultAuthedView());
    updatePage(defaultAuthedView());
    await initialDataLoad();
    if (defaultAuthedView() === "products" && !state.editingProductId) {
      setDefaultProductValidityForNew();
    }
  } catch (error) {
    handleLoggedOut();
    showToast(error.message || "Falha na autenticação", "error");
  } finally {
    setLoading(false);
  }
}

function initNav() {
  document.querySelectorAll(".nav-item").forEach((navButton) => {
    navButton.addEventListener("click", () => openView(navButton.dataset.view));
  });
}

function initMobile() {
  dom.btnToggleSidebar.addEventListener("click", () => {
    dom.sidebar.classList.toggle("open");
    syncSidebarBackdrop();
  });
  if (dom.sidebarBackdrop) {
    dom.sidebarBackdrop.addEventListener("click", () => closeSidebarMobile());
  }
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeSidebarMobile();
  });
  window.addEventListener("resize", () => {
    if (window.matchMedia("(min-width: 981px)").matches) {
      closeSidebarMobile();
    }
  });
}

function initEvents() {
  dom.loginForm.addEventListener("submit", doLogin);
  dom.btnToggleForgotPassword?.addEventListener("click", toggleForgotPasswordPanel);
  dom.btnRequestPasswordReset?.addEventListener("click", () => {
    requestPasswordReset();
  });
  dom.btnSubmitPasswordReset?.addEventListener("click", () => {
    submitPasswordReset();
  });

  dom.registerForm.addEventListener("submit", doRegister);
  dom.registerPlan.addEventListener("change", syncPlanSelectionUI);
  dom.btnCheckoutMercadoPago.addEventListener("click", () => startMercadoPagoCheckout());

  dom.productForm.addEventListener("submit", saveProduct);
  dom.btnClearProductForm.addEventListener("click", clearProductForm);
  document.getElementById("productSoldByWeight")?.addEventListener("change", syncProductWeightFormUI);

  dom.customerForm.addEventListener("submit", saveCustomer);
  dom.btnClearCustomerForm.addEventListener("click", clearCustomerForm);

  dom.companyUserForm.addEventListener("submit", saveCompanyUser);
  dom.btnClearCompanyUserForm.addEventListener("click", clearCompanyUserForm);

  dom.saleForm.addEventListener("submit", saveSale);
  dom.btnAddSaleItem.addEventListener("click", () => addSaleLine());
  dom.btnAddBySku.addEventListener("click", addProductBySku);
  dom.saleSkuInput.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") return;
    event.preventDefault();
    addProductBySku();
  });

  dom.settingsForm.addEventListener("submit", saveSettings);
  dom.settingsLogoUrlInput.addEventListener("input", refreshSettingsLogoPreview);
  bindSettingsLogoFileInput();
  dom.btnClearSettingsLogo.addEventListener("click", clearSettingsLogoSelection);
  dom.btnRemoveSettingsLogo.addEventListener("click", removeSettingsLogo);

  dom.btnExportPdf.addEventListener("click", downloadReportPdf);
  dom.btnPrintReport.addEventListener("click", printReport);
  dom.btnReloadAudit.addEventListener("click", loadAudit);

  dom.btnLogout.addEventListener("click", handleLoggedOut);
}

async function initializeApplication() {
  initNav();
  initMobile();
  initEvents();
  syncProductWeightFormUI();
  renderPublicPlansSkeleton();
  await handleCheckoutReturnFromQuery();

  const token = getAuthToken();
  if (token) {
    await initializeAuthenticatedArea();
    if (state.currentUser) return;
  }

  handleLoggedOut();
  try {
    await loadPublicPlans();
  } catch (error) {
    setFeedbackMessage(dom.registerMsg, error.message, "error");
  }
}

initializeApplication();

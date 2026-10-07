let accountUser = null;
let accountMenuOpen = false;
let accountCallbacks = {};

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const checkbox = document.getElementById("theme-switch");
  const dark = theme === "dark";
  checkbox.checked = dark;
  const toggle = document.getElementById("theme-toggle");
  toggle.querySelector(".theme-icon").textContent = dark ? "☀" : "☾";
  const isSpanish = (window.PasspointsCurrentLanguage || "es") === "es";
  toggle.setAttribute(
    "aria-label",
    dark
      ? isSpanish ? "Cambiar a modo claro" : "Switch to light mode"
      : isSpanish ? "Cambiar a modo oscuro" : "Switch to dark mode",
  );
  toggle.title = dark
    ? isSpanish ? "Modo claro" : "Light mode"
    : isSpanish ? "Modo oscuro" : "Dark mode";
  localStorage.setItem("passpoints-theme", theme);
  updateThemeLabel();
}

function initializeAccount(callbacks) {
  accountCallbacks = callbacks;
  const mount = document.getElementById("account-mount");
  const trigger = document.getElementById("account-trigger");
  const panel = document.getElementById("account-panel");
  const savedTheme = localStorage.getItem("passpoints-theme");
  const preferredTheme = window.matchMedia("(prefers-color-scheme: dark)")
    .matches
    ? "dark"
    : "light";
  applyTheme(
    savedTheme === "dark" || savedTheme === "light"
      ? savedTheme
      : preferredTheme,
  );
  document
    .getElementById("theme-switch")
    .addEventListener("change", (event) => {
      applyTheme(event.currentTarget.checked ? "dark" : "light");
    });
  trigger.addEventListener("click", () => setAccountMenuOpen(!accountMenuOpen));
  document.addEventListener("click", (event) => {
    if (accountMenuOpen && !mount.contains(event.target))
      setAccountMenuOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setAccountMenuOpen(false);
      closeAccountDialog();
    }
  });
  panel.addEventListener("click", (event) => {
    const action = event.target.closest("[data-account-action]")?.dataset
      .accountAction;
    if (!action) return;
    if (action === "appearance") {
      const theme =
        document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      accountCallbacks.onThemeChange(theme);
      updateThemeLabel();
      return;
    }
    setAccountMenuOpen(false);
    showAccountDialog(action);
  });
  document
    .getElementById("account-logout")
    .addEventListener("click", accountCallbacks.onLogout);
  document
    .getElementById("account-dialog")
    .addEventListener("click", (event) => {
      if (event.target.closest("[data-close-account]")) closeAccountDialog();
    });
  updateThemeLabel();
}

function setAccountMenuOpen(open) {
  accountMenuOpen = open;
  const panel = document.getElementById("account-panel");
  const trigger = document.getElementById("account-trigger");
  panel.hidden = !open;
  trigger.setAttribute("aria-expanded", String(open));
}

function closeAccountMenu() {
  if (document.getElementById("account-panel")) setAccountMenuOpen(false);
}

function updateAccountUser(user) {
  accountUser = user;
  if (!user) return;
  const initial = user.username.trim().charAt(0).toLocaleUpperCase("es");
  document.getElementById("account-avatar").textContent = initial;
  document.getElementById("account-panel-avatar").textContent = initial;
  document.getElementById("account-trigger-name").textContent = user.username;
  document.getElementById("account-name").textContent = user.username;
  document.getElementById("account-email").textContent = user.email;
  updateThemeLabel();
}

function updateThemeLabel() {
  const label = document.getElementById("account-theme-label");
  if (label) {
    const isDark = document.documentElement.dataset.theme === "dark";
    const currentLanguage = window.PasspointsCurrentLanguage || "es";
    label.textContent =
      currentLanguage === "es"
        ? (isDark ? "Claro" : "Oscuro")
        : (isDark ? "Light" : "Dark");
  }
}

function showAccountDialog(action) {
  const dialog = document.getElementById("account-dialog");
  const title = document.getElementById("account-dialog-title");
  const content = document.getElementById("account-dialog-content");
  const titles = {
    profile: window.PasspointsCurrentLanguage === "es" ? "Mi perfil" : "My profile",
    security: window.PasspointsCurrentLanguage === "es" ? "Seguridad" : "Security",
    about: window.PasspointsCurrentLanguage === "es" ? "Acerca de Passpoints" : "About Passpoints",
  };
  title.textContent = titles[action];
  content.replaceChildren();

  if (action === "profile") {
    const details = document.createElement("dl");
    details.className = "profile-details";
    for (const [label, value] of [
      [window.PasspointsCurrentLanguage === "es" ? "Nombre" : "Name", accountUser.username],
      [window.PasspointsCurrentLanguage === "es" ? "Correo electrónico" : "Email", accountUser.email],
    ]) {
      const row = document.createElement("div");
      const term = document.createElement("dt");
      const description = document.createElement("dd");
      term.textContent = label;
      description.textContent = value;
      row.append(term, description);
      details.appendChild(row);
    }
    content.appendChild(details);
  } else {
    const paragraphs =
      action === "security"
        ? [
            window.PasspointsCurrentLanguage === "es"
              ? "Tu cuenta utiliza autenticación gráfica con una imagen y cinco puntos en un orden específico."
              : "Your account uses graphical authentication with one image and five points in a specific order.",
            window.PasspointsCurrentLanguage === "es"
              ? "La selección utilizada se conserva solo durante esta sesión en la aplicación."
              : "The selected pattern is kept only for this session in the app.",
          ]
        : [
            window.PasspointsCurrentLanguage === "es"
              ? "Passpoints es un proyecto de investigación sobre autenticación gráfica y análisis de patrones de selección."
              : "Passpoints is a research project on graphical authentication and selection pattern analysis.",
          ];
    paragraphs.forEach((text) => {
      const paragraph = document.createElement("p");
      paragraph.textContent = text;
      content.appendChild(paragraph);
    });
  }
  dialog.hidden = false;
  dialog.querySelector(".account-dialog-close").focus();
}

function closeAccountDialog() {
  const dialog = document.getElementById("account-dialog");
  if (dialog) dialog.hidden = true;
}

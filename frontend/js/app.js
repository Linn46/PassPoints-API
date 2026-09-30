const authView = document.getElementById("auth-view");
const privateView = document.getElementById("private-view");
const authForm = document.getElementById("auth-form");
const usernameInput = document.getElementById("username");
const emailInput = document.getElementById("email");
const usernameField = document.getElementById("username-field");
const registerTab = document.getElementById("register-tab");
const loginTab = document.getElementById("login-tab");
const weakPatterns = document.getElementById("weak-patterns");
const analyzeButton = document.getElementById("analyze-button");
const analyzeLabel = document.getElementById("analyze-label");
const analyzeSpinner = document.getElementById("analyze-spinner");
const submitButton = document.getElementById("submit-button");
const submitLabel = document.getElementById("submit-label");
const submitSpinner = document.getElementById("submit-spinner");
const analysisFeedback = document.getElementById("analysis-feedback");
const requestFeedback = document.getElementById("request-feedback");
const selectionHint = document.getElementById("selection-hint");

let mode = "register";
let pending = false;
let analysisResult = null;
let analysisKey = "";
let lastPrivateState = null;

registerTab.addEventListener("click", () => setMode("register"));
loginTab.addEventListener("click", () => setMode("login"));
document.addEventListener("points-changed", invalidateAnalysis);
document.addEventListener("image-loaded", invalidateAnalysis);
usernameInput.addEventListener("input", updateButtons);
emailInput.addEventListener("input", updateButtons);
analyzeButton.addEventListener("click", runRegistrationAnalysis);
authForm.addEventListener("submit", submitAuth);
document
  .getElementById("clear-points")
  .addEventListener("click", hideRequestFeedback);
document
  .getElementById("logout-button")
  .addEventListener("click", returnToLogin);

function setMode(nextMode) {
  if (pending) return;
  mode = nextMode;
  const registering = mode === "register";
  registerTab.classList.toggle("is-active", registering);
  loginTab.classList.toggle("is-active", !registering);
  registerTab.setAttribute("aria-selected", String(registering));
  loginTab.setAttribute("aria-selected", String(!registering));
  usernameField.hidden = !registering;
  usernameInput.required = registering;
  document.getElementById("view-title").textContent = registering
    ? "Una contraseña que se dibuja."
    : "Vuelve a tu imagen.";
  selectionHint.textContent = registering
    ? "Elige lugares que recuerdes fácilmente, en el orden que prefieras."
    : "Selecciona la misma imagen y los mismos puntos que utilizaste al crear tu contraseña gráfica.";
  weakPatterns.hidden = !registering;
  analyzeButton.hidden = !registering;
  analysisFeedback.hidden = true;
  requestFeedback.hidden = true;
  updateButtons();
}

function invalidateAnalysis() {
  analysisResult = null;
  analysisKey = "";
  analysisFeedback.hidden = true;
  hideRequestFeedback();
  updateButtons();
}

function selectionKey() {
  const image = getImageData();
  return JSON.stringify({
    image: image.id,
    username: usernameInput.value.trim().toLowerCase(),
    points: getSelectedPoints(),
  });
}

function updateButtons() {
  const image = getImageData();
  const ready = Boolean(
    emailInput.validity.valid &&
    emailInput.value.trim().length >= 5 &&
    (mode !== "register" || usernameInput.value.trim().length >= 3) &&
    image.id &&
    hasFiveSelectedPoints(),
  );
  const locked = pending;
  registerTab.disabled = locked;
  loginTab.disabled = locked;
  analyzeButton.disabled = locked || mode !== "register" || !ready;
  submitButton.disabled =
    locked || !ready || (mode === "register" && !hasAcceptedAnalysis());
  submitLabel.textContent =
    mode === "register" ? "Crear mi cuenta" : "Iniciar sesión";
}

function hasAcceptedAnalysis() {
  return Boolean(
    analysisResult &&
    analysisKey === selectionKey() &&
    analysisResult.security &&
    analysisResult.security.is_weak === false,
  );
}

async function runRegistrationAnalysis() {
  if (mode !== "register" || !hasFiveSelectedPoints()) return;
  hideRequestFeedback();
  setPending(true, "analysis");
  analysisFeedback.hidden = false;
  analysisFeedback.className = "feedback is-pending";
  analysisFeedback.textContent = "Analizando tu selección…";
  try {
    const result = await analyzeSelection(getImageData(), getSelectedPoints());
    analysisResult = result;
    analysisKey = selectionKey();
    const security = result.security;
    analysisFeedback.className = `feedback ${security.is_weak ? "is-warning" : "is-success"}`;
    analysisFeedback.textContent = security.is_weak
      ? weakPatternMessage(security)
      : "Selección aceptada por el análisis. Ya puedes crear tu cuenta.";
  } catch (error) {
    analysisResult = null;
    analysisKey = "";
    showRequestError(
      error,
      "No se pudo analizar la selección. Comprueba la conexión e inténtalo de nuevo.",
    );
  } finally {
    setPending(false);
    updateButtons();
  }
}

function weakPatternMessage(security) {
  const labels = {
    "Patrón agrupado": "Los puntos están demasiado concentrados.",
    "Patrón Line": "Los puntos forman una alineación.",
    "Patrón Diag": "Los puntos forman una alineación diagonal.",
    "Patrón angular":
      "La disposición presenta una estructura demasiado regular.",
    "Patrón regular": "Los puntos forman una estructura demasiado regular.",
  };
  const reason = (security.patterns ?? [])
    .map((pattern) => labels[pattern])
    .filter(Boolean);
  return `${reason.join(" ") || "Esta selección presenta un patrón débil."} Prueba con otros puntos.`;
}

async function submitAuth(event) {
  event.preventDefault();
  if (submitButton.disabled) return;
  hideRequestFeedback();
  setPending(true, "submit");
  try {
    const image = getImageData();
    const points = getSelectedPoints();
    let result;
    if (mode === "register") {
      result = await registerAccount(
        usernameInput.value.trim(),
        emailInput.value.trim(),
        image,
        points,
      );
      sessionStorage.setItem("passpoints_access_token", result.access_token);
      lastPrivateState = {
        username: result.user.username,
        email: result.user.email,
        image,
        fractions: getSelectedPointFractions(),
        security: analysisResult?.security ?? null,
        registered: true,
      };
    } else {
      result = await authenticate(emailInput.value.trim(), image, points);
      sessionStorage.setItem("passpoints_access_token", result.access_token);
      lastPrivateState = {
        username: result.user.username,
        email: result.user.email,
        image,
        fractions: getSelectedPointFractions(),
        security: null,
        registered: false,
      };
    }
    showPrivateArea(lastPrivateState);
  } catch (error) {
    showRequestError(
      error,
      mode === "login"
        ? "No se pudo autenticar. Verifica la imagen y los puntos seleccionados."
        : "No se pudo completar el registro. Inténtalo nuevamente.",
    );
  } finally {
    setPending(false);
  }
}

function showPrivateArea(state) {
  authView.hidden = true;
  privateView.hidden = false;
  const registered = state.registered;
  document.getElementById("private-status-label").textContent = registered
    ? "CUENTA CREADA"
    : "PASSPOINTS VERIFICADO";
  document.getElementById("private-status-title").textContent = registered
    ? "Contraseña gráfica segura"
    : "Autenticación correcta";
  document.getElementById("private-status-copy").textContent = registered
    ? "El análisis de seguridad aceptó tu selección y la cuenta quedó creada."
    : "La imagen y la secuencia de puntos coinciden con tu credencial.";
  document.getElementById("private-image-name").textContent = state.image.name;
  document.getElementById("private-image").src = state.image.src;
  document.getElementById("private-detail-copy").textContent =
    `Cuenta: ${state.email}. Tu secuencia se verificó con la imagen elegida.`;
  document.getElementById("private-note").textContent = registered
    ? "Cuenta creada y sesión iniciada con tu contraseña gráfica."
    : "Has iniciado sesión correctamente. El token se conserva en esta pestaña durante la sesión.";
  renderPrivatePoints(state.fractions);

  const metric = document.getElementById("private-metric");
  metric.hidden = !state.security;
  if (state.security) {
    document.getElementById("private-level").textContent = state.security.level;
    document.getElementById("private-pattern-copy").textContent =
      "Sin patrones débiles detectados por el análisis.";
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderPrivatePoints(points) {
  const layer = document.getElementById("private-points");
  const sequence = document.getElementById("sequence-preview");
  layer.replaceChildren();
  sequence.replaceChildren();
  points.forEach((point, index) => {
    const marker = document.createElement("span");
    marker.className = "private-point-marker";
    marker.textContent = String(index + 1);
    marker.style.left = `${point.x * 100}%`;
    marker.style.top = `${point.y * 100}%`;
    layer.appendChild(marker);

    const item = document.createElement("span");
    item.className = "sequence-point";
    item.textContent = String(index + 1);
    sequence.appendChild(item);
  });
}

function returnToLogin() {
  sessionStorage.removeItem("passpoints_access_token");
  privateView.hidden = true;
  authView.hidden = false;
  authForm.reset();
  usernameInput.required = false;
  document.getElementById("clear-points").click();
  setMode("login");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function setPending(value, action) {
  pending = value;
  setPointSelectionLocked(value);
  setImageSelectionLocked(value);
  analyzeSpinner.hidden = !(value && action === "analysis");
  submitSpinner.hidden = !(value && action === "submit");
  analyzeLabel.textContent =
    value && action === "analysis" ? "Analizando" : "Analizar selección";
  submitLabel.textContent =
    value && action === "submit"
      ? mode === "register"
        ? "Creando cuenta"
        : "Autenticando"
      : mode === "register"
        ? "Crear mi cuenta"
        : "Iniciar sesión";
  updateButtons();
}

function showRequestError(error, fallback) {
  requestFeedback.hidden = false;
  if (!(error instanceof ApiError)) {
    console.error("Unexpected Passpoints frontend error:", error);
    requestFeedback.textContent = fallback;
    return;
  }
  if (error.status === 0) {
    requestFeedback.textContent =
      "No se pudo conectar con el servicio. Inténtalo nuevamente.";
  } else if (mode === "login" && error.status === 401) {
    requestFeedback.textContent =
      "No se pudo autenticar. Verifica la imagen y los puntos seleccionados.";
  } else if (mode === "register" && error.status === 409) {
    requestFeedback.textContent =
      "Ese nombre o correo ya está asociado a una cuenta.";
  } else if (error.status === 503) {
    requestFeedback.textContent =
      "El servicio de autenticación no está configurado. Reinicia la API con DATABASE_URL y AUTH_TOKEN_SECRET definidos.";
  } else if (
    mode === "register" &&
    error.status === 422 &&
    /weak|déb|pattern/i.test(String(error.message))
  ) {
    requestFeedback.textContent =
      "Esta selección presenta un patrón débil. Prueba con otros puntos.";
  } else {
    requestFeedback.textContent = fallback;
  }
}

function hideRequestFeedback() {
  requestFeedback.hidden = true;
  requestFeedback.textContent = "";
}

setMode("register");

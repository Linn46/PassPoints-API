function initializeAuth({ onAuthenticated }) {
  const AUTH_PROGRESS_KEY = "passpoints_auth_progress";
  const authView = document.getElementById("auth-view");
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
  const analysisMethodSelector = document.querySelector(
    ".analysis-method-selector",
  );
  const analysisMethodInputs = Array.from(
    document.querySelectorAll(".analysis-method-input"),
  );
  const patternModal = document.getElementById("pattern-modal");
  const patternModalClose = document.getElementById("pattern-modal-close");
  const modalPatternVisual = document.getElementById("modal-pattern-visual");
  const patternModalTitle = document.getElementById("pattern-modal-title");
  const patternModalDescription = document.getElementById(
    "pattern-modal-description",
  );
  const patternModalTip = document.getElementById("pattern-modal-tip-text");
  const visualCanvas = document.querySelector(".visual-canvas");
  const interactivePath = document.getElementById("interactive-path");
  const draggablePoints = [
    ...document.querySelectorAll(".visual-point[data-point]"),
  ];
  const visualPointPositions = {
    1: { x: 13, y: 68 },
    2: { x: 31, y: 28 },
    3: { x: 54, y: 48 },
    4: { x: 85, y: 17 },
    5: { x: 79, y: 88 },
  };
  const patternInformation = {
    cluster: {
      es: {
        title: "Patrón agrupado",
        description:
          "Los cinco puntos se encuentran muy cerca unos de otros. Esto reduce el espacio de búsqueda y puede hacer que la contraseña sea más predecible.",
        tip: "Distribuye los puntos por diferentes zonas de la imagen.",
      },
      en: {
        title: "Clustered pattern",
        description:
          "All five points are very close together. This reduces the search space and can make the password easier to predict.",
        tip: "Spread the points across different areas of the image.",
      },
    },
    line: {
      es: {
        title: "Patrón Line / Diag",
        description:
          "Los puntos siguen aproximadamente una línea recta o diagonal. Estas estructuras presentan una organización geométrica que puede facilitar su predicción.",
        tip: "Evita colocar los cinco puntos siguiendo una misma dirección.",
      },
      en: {
        title: "Line / Diag pattern",
        description:
          "The points follow a straight or diagonal line roughly. This geometric structure can make the selection easier to anticipate.",
        tip: "Avoid placing all five points along the same direction.",
      },
    },
    regular: {
      es: {
        title: "Patrón regular",
        description:
          "Los puntos mantienen separaciones o posiciones demasiado uniformes. La regularidad puede hacer que la selección sea más fácil de anticipar.",
        tip: "Combina distancias y posiciones diferentes.",
      },
      en: {
        title: "Regular pattern",
        description:
          "The points keep separations or positions that are too uniform. This regularity can make the pattern easier to anticipate.",
        tip: "Combine different distances and positions.",
      },
    },
    angular: {
      es: {
        title: "Patrón angular",
        description:
          "Los puntos forman una estructura geométrica muy ordenada, por ejemplo siguiendo direcciones o ángulos similares.",
        tip: "Evita construir figuras geométricas demasiado evidentes.",
      },
      en: {
        title: "Angular pattern",
        description:
          "The points form a very ordered geometric structure, such as repeated directions or similar angles.",
        tip: "Avoid building geometric figures that are too obvious.",
      },
    },
  };
  let mode = "register";
  let pending = false;
  let analysisResult = null;
  let analysisKey = "";
  let loginImagesReady = true;
  let loginImageRequestId = 0;
  let loginImageTimer = null;
  let restoringProgress = false;

  function hideRequestFeedback() {
    requestFeedback.hidden = true;
    requestFeedback.textContent = "";
  }
  function persistAuthProgress() {
    if (restoringProgress) return;
    const progress = {
      version: 1,
      mode,
      username: usernameInput.value,
      email: emailInput.value,
      imageId: getImageData().id,
      imageOptionIds: getImageOptionIds(),
      points: getSelectedPointFractions(),
      methods: selectedAnalysisMethods(),
      analysisResult,
    };
    try {
      sessionStorage.setItem(AUTH_PROGRESS_KEY, JSON.stringify(progress));
    } catch (error) {
      console.error("Could not preserve the authentication form state:", error);
    }
  }
  async function restoreAuthProgress() {
    const saved = sessionStorage.getItem(AUTH_PROGRESS_KEY);
    if (!saved) return;
    let progress;
    try {
      progress = JSON.parse(saved);
    } catch (error) {
      console.error("Saved authentication form state is invalid:", error);
      sessionStorage.removeItem(AUTH_PROGRESS_KEY);
      return;
    }
    if (!progress || progress.version !== 1) {
      sessionStorage.removeItem(AUTH_PROGRESS_KEY);
      return;
    }

    restoringProgress = true;
    try {
      usernameInput.value =
        typeof progress.username === "string" ? progress.username : "";
      emailInput.value = typeof progress.email === "string" ? progress.email : "";
      if (Array.isArray(progress.methods)) {
        analysisMethodInputs.forEach((input) => {
          input.checked = progress.methods.includes(input.value);
        });
      }

      const restoredMode = progress.mode === "login" ? "login" : "register";
      setMode(restoredMode);
      const catalogIds = new Set(getImageCatalogIds());
      const expectedOptionCount = restoredMode === "login" ? 3 : 5;
      const optionsAreValid =
        Array.isArray(progress.imageOptionIds) &&
        progress.imageOptionIds.length === expectedOptionCount &&
        new Set(progress.imageOptionIds).size === expectedOptionCount &&
        progress.imageOptionIds.every((id) => catalogIds.has(id));
      if (optionsAreValid) {
        clearTimeout(loginImageTimer);
        loginImageRequestId += 1;
        if (restoredMode === "login") {
          setLoginImageOptions(progress.imageOptionIds);
          loginImagesReady = true;
        } else {
          setRegistrationImageOptions(progress.imageOptionIds);
        }
      }

      const selectedImage =
        typeof progress.imageId === "string" &&
        optionsAreValid &&
        progress.imageOptionIds.includes(progress.imageId)
          ? getCatalogImage(progress.imageId)
          : null;
      if (selectedImage) {
        await selectImage(selectedImage);
        if (Array.isArray(progress.points)) {
          setSelectedPointFractions(progress.points);
        }
      }

      if (
        progress.analysisResult &&
        typeof progress.analysisResult.security?.is_weak === "boolean"
      ) {
        analysisResult = progress.analysisResult;
        analysisKey = selectionKey();
        analysisFeedback.hidden = false;
        analysisFeedback.className = analysisResult.security.is_weak
          ? "feedback is-warning"
          : "feedback is-success";
        analysisFeedback.textContent = analysisResult.security.is_weak
          ? weakPatternMessage(analysisResult.security)
          : window.PasspointsCurrentLanguage === "es"
            ? "Selección aceptada por el análisis. Ya puedes crear tu cuenta."
            : "Selection accepted by the analysis. You can now create your account.";
      }
    } catch (error) {
      console.error("Could not restore the authentication form state:", error);
      sessionStorage.removeItem(AUTH_PROGRESS_KEY);
      showRequestError(
        error,
        window.PasspointsCurrentLanguage === "es"
          ? "No se pudo restaurar el formulario. Vuelve a seleccionar la imagen y los puntos."
          : "The form could not be restored. Select the image and points again.",
      );
    } finally {
      restoringProgress = false;
      updateButtons();
      persistAuthProgress();
    }
  }
  function selectionKey() {
    return JSON.stringify({
      image: getImageData().id,
      username: usernameInput.value.trim().toLowerCase(),
      points: getSelectedPoints(),
    });
  }
  function hasAcceptedAnalysis() {
    return Boolean(
      analysisResult &&
      analysisKey === selectionKey() &&
      analysisResult.security?.is_weak === false,
    );
  }
  function selectedAnalysisMethods() {
    return analysisMethodInputs
      .filter((input) => input.checked)
      .map((input) => input.value);
  }
  function updateButtons() {
    const image = getImageData();
    const selectedMethods = selectedAnalysisMethods();
    const ready = Boolean(
      emailInput.validity.valid &&
      emailInput.value.trim().length >= 5 &&
      (mode !== "register" || usernameInput.value.trim().length >= 3) &&
      image.id &&
      hasFiveSelectedPoints(),
    );
    const methodsReady = selectedMethods.length > 0;
    registerTab.disabled = pending;
    loginTab.disabled = pending;
    analyzeButton.disabled =
      pending || mode !== "register" || !ready || !methodsReady;
    submitButton.disabled =
      pending ||
      !ready ||
      !methodsReady ||
      (mode === "login" && !loginImagesReady) ||
      (mode === "register" && !hasAcceptedAnalysis());
    submitLabel.textContent =
      mode === "register" ? t("createAccount") : t("signIn");
  }
  function setMode(nextMode) {
    if (pending) return;
    const modeChanged = mode !== nextMode;
    mode = nextMode;
    const registering = mode === "register";
    if (modeChanged) {
      clearTimeout(loginImageTimer);
      loginImageRequestId += 1;
      loginImagesReady = registering;
      setImageSelectionMode(mode);
      if (!registering) refreshLoginImageOptions();
    }
    registerTab.classList.toggle("is-active", registering);
    loginTab.classList.toggle("is-active", !registering);
    registerTab.setAttribute("aria-selected", String(registering));
    loginTab.setAttribute("aria-selected", String(!registering));
    usernameField.hidden = !registering;
    usernameInput.required = registering;
    document.getElementById("view-title").textContent = registering
      ? t("authViewTitle")
      : t("authViewTitleLogin");
    selectionHint.textContent = registering
      ? t("selectionHint")
      : window.PasspointsCurrentLanguage === "es"
        ? "Introduce tu correo, elige tu imagen entre las tres opciones y marca los mismos puntos de siempre."
        : "Enter your email, choose your image from the three options, and select your usual points.";
    weakPatterns.hidden = !registering;
    analysisMethodSelector.hidden = !registering;
    analyzeButton.hidden = !registering;
    analysisFeedback.hidden = true;
    hideRequestFeedback();
    updateButtons();
  }
  function refreshLoginImageOptions() {
    if (mode !== "login") return;
    clearTimeout(loginImageTimer);
    const requestId = ++loginImageRequestId;
    const email = emailInput.value.trim().toLowerCase();
    loginImagesReady = false;
    setImageSelectionMode("login");
    hideRequestFeedback();
    updateButtons();
    if (!emailInput.validity.valid || email.length < 5) return;

    loginImageTimer = setTimeout(async () => {
      try {
        const response = await getLoginImageOptions(email, getImageCatalogIds());
        if (
          requestId !== loginImageRequestId ||
          mode !== "login" ||
          email !== emailInput.value.trim().toLowerCase()
        )
          return;
        setLoginImageOptions(response.image_ids);
        loginImagesReady = true;
      } catch (error) {
        if (requestId !== loginImageRequestId || mode !== "login") return;
        showRequestError(
          error,
          window.PasspointsCurrentLanguage === "es"
            ? "No se pudieron cargar las imágenes de acceso."
            : "The login images could not be loaded.",
        );
      } finally {
        if (requestId === loginImageRequestId) updateButtons();
      }
    }, 250);
  }
  function invalidateAnalysis() {
    analysisResult = null;
    analysisKey = "";
    analysisFeedback.hidden = true;
    hideRequestFeedback();
    updateButtons();
  }
  function setPending(value, action) {
    pending = value;
    setPointSelectionLocked(value);
    setImageSelectionLocked(value);
    analyzeSpinner.hidden = !(value && action === "analysis");
    submitSpinner.hidden = !(value && action === "submit");
    analyzeLabel.textContent =
      value && action === "analysis" ? t("analyzingSelection") : t("analyzeSelection");
    submitLabel.textContent =
      value && action === "submit"
        ? mode === "register"
          ? t("creatingAccount")
          : t("authenticating")
        : mode === "register"
          ? t("createAccount")
          : t("signIn");
    updateButtons();
  }
  function showRequestError(error, fallback) {
    requestFeedback.hidden = false;
    const isSpanish = window.PasspointsCurrentLanguage === "es";
    if (!(error instanceof ApiError)) {
      console.error("Unexpected Passpoints frontend error:", error);
      requestFeedback.textContent = fallback;
    } else if (error.status === 0)
      requestFeedback.textContent = isSpanish
        ? "No se pudo conectar con el servicio. Inténtalo nuevamente."
        : "The service could not be reached. Please try again.";
    else if (mode === "login" && error.status === 401)
      requestFeedback.textContent = isSpanish
        ? "No se pudo autenticar. Verifica la imagen y los puntos seleccionados."
        : "Authentication failed. Check the image and the selected points.";
    else if (mode === "register" && error.status === 409)
      requestFeedback.textContent = isSpanish
        ? "Ese nombre o correo ya está asociado a una cuenta."
        : "That username or email is already linked to an account.";
    else if (error.status === 503)
      requestFeedback.textContent = isSpanish
        ? "El servicio de autenticación no está configurado. Reinicia la API con DATABASE_URL y AUTH_TOKEN_SECRET definidos."
        : "The authentication service is not configured. Restart the API with DATABASE_URL and AUTH_TOKEN_SECRET defined.";
    else if (
      mode === "register" &&
      error.status === 422 &&
      /weak|déb|pattern/i.test(String(error.message))
    )
      requestFeedback.textContent = isSpanish
        ? "Esta selección presenta un patrón débil. Prueba con otros puntos."
        : "This selection shows a weak pattern. Please try different points.";
    else requestFeedback.textContent = fallback;
  }
  async function runRegistrationAnalysis() {
    if (mode !== "register" || !hasFiveSelectedPoints()) return;
    hideRequestFeedback();
    setPending(true, "analysis");
    analysisFeedback.hidden = false;
    analysisFeedback.className = "feedback is-pending";
    analysisFeedback.textContent =
      window.PasspointsCurrentLanguage === "es"
        ? "Analizando tu selección…"
        : "Analyzing your selection…";
    try {
      const result = await analyzeSelection(
        getImageData(),
        getSelectedPoints(),
        selectedAnalysisMethods(),
      );
      analysisResult = result;
      analysisKey = selectionKey();
      analysisFeedback.className = `feedback ${result.security.is_weak ? "is-warning" : "is-success"}`;
      analysisFeedback.textContent = result.security.is_weak
        ? weakPatternMessage(result.security)
        : window.PasspointsCurrentLanguage === "es"
          ? "Selección aceptada por el análisis. Ya puedes crear tu cuenta."
          : "Selection accepted by the analysis. You can now create your account.";
    } catch (error) {
      analysisResult = null;
      analysisKey = "";
      showRequestError(
        error,
        "No se pudo analizar la selección. Comprueba la conexión e inténtalo de nuevo.",
      );
    } finally {
      setPending(false);
    }
  }
  function weakPatternMessage(security) {
    const isSpanish = window.PasspointsCurrentLanguage === "es";
    const labels = isSpanish
      ? {
          "Patrón agrupado": "Los puntos están demasiado concentrados.",
          "Patrón Line": "Los puntos forman una alineación.",
          "Patrón Diag": "Los puntos forman una alineación diagonal.",
          "Patrón angular": "La disposición presenta una estructura demasiado regular.",
          "Patrón regular": "Los puntos forman una estructura demasiado regular.",
        }
      : {
          "Clustered pattern": "The points are too concentrated.",
          "Line pattern": "The points form a straight alignment.",
          "Diagonal pattern": "The points form a diagonal alignment.",
          "Angular pattern": "The layout presents an overly regular structure.",
          "Regular pattern": "The points form a structure that is too regular.",
        };
    const reason = (security.patterns ?? [])
      .map((pattern) => labels[pattern])
      .filter(Boolean);
    return isSpanish
      ? `${reason.join(" ") || "Esta selección presenta un patrón débil."} Prueba con otros puntos.`
      : `${reason.join(" ") || "This selection shows a weak pattern."} Please try different points.`;
  }
  async function submitAuth(event) {
    event.preventDefault();
    if (submitButton.disabled) return;
    hideRequestFeedback();
    setPending(true, "submit");
    try {
      const image = getImageData();
      const points = getSelectedPoints();
      const result =
        mode === "register"
          ? await registerAccount(
              usernameInput.value.trim(),
              emailInput.value.trim(),
              image,
              points,
            )
          : await authenticate(emailInput.value.trim(), image, points);
      sessionStorage.setItem("passpoints_access_token", result.access_token);
      sessionStorage.removeItem(AUTH_PROGRESS_KEY);
      onAuthenticated({
        user: result.user,
        image,
        fractions: getSelectedPointFractions(),
        security:
          mode === "register" ? (analysisResult?.security ?? null) : null,
        registered: mode === "register",
      });
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
  function createModalPattern(pattern) {
    const positions = {
      cluster: [
        [48, 43],
        [52, 48],
        [46, 54],
        [55, 40],
        [50, 58],
      ],
      line: [
        [20, 75],
        [35, 60],
        [50, 45],
        [65, 30],
        [80, 17],
      ],
      regular: [
        [25, 25],
        [75, 25],
        [50, 50],
        [25, 75],
        [75, 75],
      ],
      angular: [
        [20, 70],
        [35, 45],
        [50, 70],
        [65, 45],
        [80, 70],
      ],
    };
    modalPatternVisual.replaceChildren();
    positions[pattern].forEach(([left, top]) => {
      const point = document.createElement("span");
      point.className = "modal-pattern-point";
      point.style.left = `${left}%`;
      point.style.top = `${top}%`;
      modalPatternVisual.appendChild(point);
    });
  }
  function openPatternModal(pattern) {
    const data = patternInformation[pattern]?.[window.PasspointsCurrentLanguage || "es"];
    if (!data) return;
    patternModalTitle.textContent = data.title;
    patternModalDescription.textContent = data.description;
    patternModalTip.textContent = data.tip;
    createModalPattern(pattern);
    patternModal.classList.add("is-open");
    patternModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    patternModalClose.focus();
  }
  function closePatternModal() {
    patternModal.classList.remove("is-open");
    patternModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }
  registerTab.addEventListener("click", () => setMode("register"));
  loginTab.addEventListener("click", () => setMode("login"));
  window.refreshLanguageUI = function refreshLanguageUI() {
    registerTab.textContent = t("registerTab");
    loginTab.textContent = t("loginTab");
    if (window.currentUserState) {
      if (typeof window.renderHome === "function") {
        window.renderHome(window.currentUserState);
      }
      if (typeof window.updateAccountUser === "function") {
        window.updateAccountUser(window.currentUserState.user);
      }
    }
    if (mode === "register") {
      document.getElementById("view-title").textContent = t("authViewTitle");
      selectionHint.textContent = t("selectionHint");
    } else {
      document.getElementById("view-title").textContent = t("authViewTitleLogin");
      selectionHint.textContent =
        window.PasspointsCurrentLanguage === "es"
          ? "Introduce tu correo, elige tu imagen entre las tres opciones y marca los mismos puntos de siempre."
          : "Enter your email, choose your image from the three options, and select your usual points.";
    }
    updateButtons();
    setMode(mode);
  };
  usernameInput.addEventListener("input", () => {
    persistAuthProgress();
    updateButtons();
  });
  emailInput.addEventListener("input", () => {
    if (mode === "login") refreshLoginImageOptions();
    persistAuthProgress();
    updateButtons();
  });
  authForm.addEventListener("submit", submitAuth);
  analyzeButton.addEventListener("click", runRegistrationAnalysis);
  document
    .getElementById("clear-points")
    .addEventListener("click", hideRequestFeedback);
  analysisMethodInputs.forEach((input) => {
    input.addEventListener("change", () => {
      invalidateAnalysis();
      persistAuthProgress();
      updateButtons();
    });
  });
  document.addEventListener("points-changed", () => {
    invalidateAnalysis();
    persistAuthProgress();
  });
  document.addEventListener("image-selection-started", () => {
    invalidateAnalysis();
    persistAuthProgress();
  });
  document.addEventListener("image-loaded", () => {
    invalidateAnalysis();
    persistAuthProgress();
  });
  authView.addEventListener("click", (event) => {
    const card = event.target.closest(".pattern-card[data-pattern]");
    if (card) openPatternModal(card.dataset.pattern);
  });
  patternModalClose.addEventListener("click", closePatternModal);
  patternModal
    .querySelector(".pattern-modal-backdrop")
    .addEventListener("click", closePatternModal);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && patternModal.classList.contains("is-open"))
      closePatternModal();
  });
  function updateVisualPoint(number, x, y) {
    visualPointPositions[number] = { x, y };
    const element = document.querySelector(
      `.visual-point[data-point="${number}"]`,
    );
    element.style.left = `${x}%`;
    element.style.top = `${y}%`;
    const path = Object.values(visualPointPositions)
      .map(
        (point, index) =>
          `${index ? "L" : "M"} ${(point.x / 100) * 500} ${(point.y / 100) * 500}`,
      )
      .join(" ");
    interactivePath.setAttribute("d", path);
  }
  let draggingPoint = null;
  draggablePoints.forEach((point) => {
    point.addEventListener("pointerdown", (event) => {
      draggingPoint = point;
      point.classList.add("is-dragging");
      point.setPointerCapture(event.pointerId);
      event.preventDefault();
    });
    point.addEventListener("pointermove", (event) => {
      if (draggingPoint !== point) return;
      const rect = visualCanvas.getBoundingClientRect();
      updateVisualPoint(
        Number(point.dataset.point),
        Math.max(
          7,
          Math.min(93, ((event.clientX - rect.left) / rect.width) * 100),
        ),
        Math.max(
          8,
          Math.min(92, ((event.clientY - rect.top) / rect.height) * 100),
        ),
      );
    });
    const stopDragging = () => {
      point.classList.remove("is-dragging");
      draggingPoint = null;
    };
    point.addEventListener("pointerup", stopDragging);
    point.addEventListener("pointercancel", stopDragging);
  });
  Object.entries(visualPointPositions).forEach(([number, position]) =>
    updateVisualPoint(Number(number), position.x, position.y),
  );
  setMode("register");
  return restoreAuthProgress;
}

function resetAuth() {
  const form = document.getElementById("auth-form");
  form.reset();
  document.getElementById("clear-points").click();
  document.getElementById("register-tab").click();
  document.getElementById("request-feedback").hidden = true;
}

function initializeAuth({ onAuthenticated }) {
  const AUTH_PROGRESS_KEY = "passpoints_auth_progress";
  const authView = document.getElementById("auth-view");
  const authForm = document.getElementById("auth-form");
  const usernameInput = document.getElementById("username");
  const emailInput = document.getElementById("email");
  const toleranceControl = document.getElementById("tolerance-control");
  const toleranceRadiusInput = document.getElementById("tolerance-radius");
  const toleranceValue = document.getElementById("tolerance-value");
  const usernameField = document.getElementById("username-field");
  const registerTab = document.getElementById("register-tab");
  const loginTab = document.getElementById("login-tab");
  const weakPatterns = document.getElementById("weak-patterns");
  const analyzeButton = document.getElementById("analyze-button");
  const analyzeLabel = document.getElementById("analyze-label");
  const analyzeSpinner = document.getElementById("analyze-spinner");
  const changePasswordButton = document.getElementById("change-password");
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
  const confirmationModal = document.getElementById(
    "confirmation-feedback-modal",
  );
  const confirmationModalClose = document.getElementById(
    "confirmation-feedback-close",
  );
  const passwordStageStatus = document.getElementById("password-stage-status");
  const restartPasswordButton = document.getElementById(
    "restart-password-button",
  );
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
  let registrationId = null;
  let consecutiveSuccesses = 0;
  let registrationCancellation = null;

  function updateUIForStep() {
    const title = document.querySelector('[data-i18n="createSequence"]');
    const count = document.getElementById("point-count");
    changePasswordButton.hidden = !registrationId;
    const isRepeatingPassword = mode === "register" && Boolean(registrationId);
    toleranceControl.hidden = mode !== "register";
    toleranceRadiusInput.disabled = Boolean(registrationId) || pending;
    document.dispatchEvent(
      new CustomEvent("authentication-mode-changed", {
        detail: { mode, repeating: isRepeatingPassword },
      }),
    );

    analysisMethodSelector.hidden = mode !== "register" || isRepeatingPassword;
    analyzeButton.hidden = mode !== "register" || isRepeatingPassword;

    if (isRepeatingPassword) {
      analysisFeedback.hidden = true;
    }

    // El análisis solo se muestra antes de iniciar las repeticiones.
    const repeatingPassword = Boolean(registrationId);

    analysisMethodSelector.hidden = mode !== "register" || repeatingPassword;

    analyzeButton.hidden = mode !== "register" || repeatingPassword;

    analysisFeedback.hidden =
      mode !== "register" || repeatingPassword || !analysisResult;
    if (!registrationId) {
      title.textContent =
        window.PasspointsCurrentLanguage === "es"
          ? "Crea tu secuencia"
          : "Create your sequence";
      selectionHint.textContent = t("selectionHint");
    } else {
      const repetition = Math.max(1, consecutiveSuccesses);
      title.textContent =
        window.PasspointsCurrentLanguage === "es"
          ? `Confirma tu secuencia (${repetition}/3)`
          : `Confirm your sequence (${repetition}/3)`;
      selectionHint.textContent =
        window.PasspointsCurrentLanguage === "es"
          ? "Repite los mismos cinco puntos. Un error reinicia la racha."
          : "Repeat the same five points. A mistake resets the streak.";
    }
    count.textContent = "0/5";
    document.dispatchEvent(new CustomEvent("reset-points"));
  }
  function resetRegistrationProgress() {
    const previousRegistrationId = registrationId;
    registrationId = null;
    consecutiveSuccesses = 0;
    usernameInput.readOnly = false;
    emailInput.readOnly = false;
    updateUIForStep();
    if (previousRegistrationId) {
      registrationCancellation = cancelRegistration(previousRegistrationId)
        .catch((error) => {
          console.error("Could not cancel the pending registration:", error);
          showRequestError(
            error,
            window.PasspointsCurrentLanguage === "es"
              ? "No se pudo reiniciar el registro. Inténtalo de nuevo."
              : "The registration could not be reset. Please try again.",
          );
        })
        .finally(() => {
          registrationCancellation = null;
          updateButtons();
        });
      updateButtons();
    }
  }

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
      version: 3,
      mode,
      username: usernameInput.value,
      email: emailInput.value,
      imageId: getImageData().id,
      imageOptionIds: getImageOptionIds(),
      points: getSelectedPointFractions(),
      toleranceRadius: Number(toleranceRadiusInput.value),
      methods: selectedAnalysisMethods(),
      analysisResult,
      registrationId,
      consecutiveSuccesses,
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
    if (!progress || ![1, 2, 3].includes(progress.version)) {
      sessionStorage.removeItem(AUTH_PROGRESS_KEY);
      return;
    }

    restoringProgress = true;
    try {
      usernameInput.value =
        typeof progress.username === "string" ? progress.username : "";
      emailInput.value =
        typeof progress.email === "string" ? progress.email : "";
      if (
        Number.isInteger(progress.toleranceRadius) &&
        progress.toleranceRadius >= 5 &&
        progress.toleranceRadius <= 30
      ) {
        toleranceRadiusInput.value = String(progress.toleranceRadius);
      }
      updateToleranceLabel();
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
        restoredMode === "register" &&
        selectedImage &&
        typeof progress.registrationId === "string" &&
        Number.isInteger(progress.consecutiveSuccesses) &&
        progress.consecutiveSuccesses >= 0 &&
        progress.consecutiveSuccesses < 3
      ) {
        registrationId = progress.registrationId;
        consecutiveSuccesses = progress.consecutiveSuccesses;
        usernameInput.readOnly = true;
        emailInput.readOnly = true;
        updateUIForStep();
        if (Array.isArray(progress.points)) {
          setSelectedPointFractions(progress.points);
        }
      } else if (
        typeof progress.registrationId === "string" &&
        !selectedImage
      ) {
        cancelRegistration(progress.registrationId).catch((error) => {
          console.error("Could not cancel the restored registration:", error);
        });
      }

      if (
        progress.analysisResult &&
        typeof progress.analysisResult.security?.is_weak === "boolean"
      ) {
        analysisResult = progress.analysisResult;
        analysisKey = selectionKey();
        analysisFeedback.hidden =
          mode !== "register" || Boolean(registrationId);
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
      toleranceRadius: Number(toleranceRadiusInput.value),
    });
  }
  function selectedAnalysisMethods() {
    return analysisMethodInputs
      .filter((input) => input.checked)
      .map((input) => input.value);
  }
  function updateButtons() {
    const image = getImageData();
    const selectedMethods = selectedAnalysisMethods();
    const spacingReady =
      mode !== "register" ||
      typeof window.hasValidPointSpacing !== "function" ||
      window.hasValidPointSpacing();
    const ready = Boolean(image.id && hasFiveSelectedPoints() && spacingReady);
    const loginReady = Boolean(
      emailInput.validity.valid && emailInput.value.trim().length >= 5 && ready,
    );
    const methodsReady = selectedMethods.length > 0;
    registerTab.disabled = pending;
    loginTab.disabled = pending;
    analyzeButton.disabled =
      pending ||
      mode !== "register" ||
      Boolean(registrationId) ||
      !ready ||
      !methodsReady;
    submitButton.disabled =
      pending ||
      !ready ||
      (mode === "login" && (!loginImagesReady || !loginReady)) ||
      registrationCancellation !== null;
    submitLabel.textContent =
      mode !== "register"
        ? t("signIn")
        : pending
          ? t("creatingAccount")
          : registrationId
            ? t("repeatPassword")
            : t("savePassword");
  }
  function setMode(nextMode) {
    if (pending) return;
    const modeChanged = mode !== nextMode;
    if (modeChanged && mode === "register" && registrationId) {
      resetRegistrationProgress();
    }
    mode = nextMode;
    const registering = mode === "register";
    toleranceControl.hidden = !registering;
    document.dispatchEvent(
      new CustomEvent("authentication-mode-changed", {
        detail: { mode, repeating: Boolean(registrationId) },
      }),
    );
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
    weakPatterns.hidden = !registering;
    analysisMethodSelector.hidden = !registering || Boolean(registrationId);
    analyzeButton.hidden = !registering || Boolean(registrationId);
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
        const response = await getLoginImageOptions(
          email,
          getImageCatalogIds(),
        );
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
    toleranceRadiusInput.disabled = value || Boolean(registrationId);
    setPointSelectionLocked(value);
    setImageSelectionLocked(value);
    analyzeSpinner.hidden = !(value && action === "analysis");
    submitSpinner.hidden = !(value && action === "submit");
    analyzeLabel.textContent =
      value && action === "analysis"
        ? t("analyzingSelection")
        : t("analyzeSelection");
    submitLabel.textContent =
      value && action === "submit" && mode === "login"
        ? t("authenticating")
        : mode === "login"
          ? t("signIn")
          : value && action === "submit"
            ? t("creatingAccount")
            : registrationId
              ? t("repeatPassword")
              : t("savePassword");
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
    else if (
      mode === "register" &&
      error.status === 422 &&
      String(error.message).includes("repeated consistently")
    )
      requestFeedback.textContent = isSpanish
        ? "La contraseña debe repetirse de forma consistente. Inténtalo de nuevo."
        : "The password must be repeated consistently. Please try again.";
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
          ? "Selección aceptada por el análisis. Ya puedes guardar la contraseña."
          : "Selection accepted by the analysis. You can now save your password.";
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
          "Patrón angular":
            "La disposición presenta una estructura demasiado regular.",
          "Patrón regular":
            "Los puntos forman una estructura demasiado regular.",
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
    if (pending || submitButton.disabled) return;

    if (mode === "register" && !registrationId) {
      const isSpanish = window.PasspointsCurrentLanguage === "es";
      const missingFields = [];
      const username = usernameInput.value.trim();
      const email = emailInput.value.trim();
      const emailPattern =
        /^[A-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)*\.[A-Z]{2,63}$/i;
      if (!username)
        missingFields.push(isSpanish ? "nombre de usuario" : "username");
      else if (!/^[a-z0-9_.-]{3,100}$/i.test(username))
        missingFields.push(
          isSpanish ? "nombre de usuario válido" : "a valid username",
        );
      if (!email)
        missingFields.push(isSpanish ? "correo electrónico" : "email");
      else if (!emailPattern.test(email) || email.length > 254)
        missingFields.push(
          isSpanish ? "correo electrónico válido" : "a valid email",
        );
      if (!getImageData().id)
        missingFields.push(isSpanish ? "imagen" : "image");
      if (!hasFiveSelectedPoints())
        missingFields.push(
          isSpanish
            ? "contraseña gráfica de cinco puntos"
            : "five-point graphical password",
        );
      if (missingFields.length) {
        requestFeedback.hidden = false;
        requestFeedback.textContent = isSpanish
          ? `Completa o corrige estos campos: ${missingFields.join(", ")}.`
          : `Complete or correct these fields: ${missingFields.join(", ")}.`;
        return;
      }
    }

    const points = getSelectedPoints();
    if (points.length !== 5) return;

    hideRequestFeedback();
    setPending(true, "submit");
    try {
      const image = getImageData();

      let result;
      if (mode === "register") {
        if (!registrationId) {
          const progress = await registerAccount(
            usernameInput.value.trim(),
            emailInput.value.trim(),
            image,
            points,
            Number(toleranceRadiusInput.value),
          );
          registrationId = progress.registration_id;
          consecutiveSuccesses = progress.consecutive_successes;
          usernameInput.readOnly = true;
          emailInput.readOnly = true;
          updateUIForStep();
          persistAuthProgress();
          showConfirmationModal(true, consecutiveSuccesses);
          return;
        }

        result = await registerRepetition(registrationId, points);
        consecutiveSuccesses = result.consecutive_successes;
        if (!result.completed) {
          updateUIForStep();
          persistAuthProgress();
          showConfirmationModal(result.attempt_correct, consecutiveSuccesses);
          return;
        }
      } else {
        result = await authenticate(emailInput.value.trim(), image, points);
      }

      sessionStorage.setItem("passpoints_access_token", result.access_token);
      sessionStorage.removeItem(AUTH_PROGRESS_KEY);
      registrationId = null;
      consecutiveSuccesses = 0;
      usernameInput.readOnly = false;
      emailInput.readOnly = false;
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
    const data =
      patternInformation[pattern]?.[window.PasspointsCurrentLanguage || "es"];
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

  function showConfirmationModal(attemptCorrect, successes) {
    const title = document.getElementById("confirmation-feedback-title");
    const desc = document.getElementById("confirmation-feedback-description");
    const btn = document.getElementById("confirmation-feedback-close");

    const remaining = attemptCorrect ? 3 - successes : 3;

    title.textContent = t(
      attemptCorrect
        ? "passwordConfirmationTitle"
        : "passwordConfirmationWrongTitle",
    );

    if (!attemptCorrect) {
      desc.textContent = t("passwordConfirmationWrongHint", { n: remaining });
    } else if (remaining === 1) {
      desc.textContent = t("passwordConfirmationLast");
    } else {
      desc.textContent = t("passwordConfirmationHint", { n: remaining });
    }
    btn.textContent = t("passwordConfirmationButton");

    confirmationModal.classList.add("is-open");
    confirmationModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    confirmationModalClose.focus();
  }
  function closeConfirmationModal() {
    confirmationModal.classList.remove("is-open");
    confirmationModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }
  confirmationModalClose.addEventListener("click", closeConfirmationModal);
  confirmationModal
    .querySelector(".confirmation-modal-backdrop")
    .addEventListener("click", closeConfirmationModal);
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
      updateUIForStep(false);
    } else {
      document.getElementById("view-title").textContent =
        t("authViewTitleLogin");
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
  toleranceRadiusInput.addEventListener("input", () => {
    updateToleranceLabel();
    document.dispatchEvent(new CustomEvent("tolerance-radius-changed"));
    if (mode === "register" && !registrationId) invalidateAnalysis();
    persistAuthProgress();
  });
  function updateToleranceLabel() {
    toleranceValue.textContent = `${toleranceRadiusInput.value} px`;
  }
  authForm.addEventListener("submit", submitAuth);
  analyzeButton.addEventListener("click", runRegistrationAnalysis);
  document
    .getElementById("clear-points")
    .addEventListener("click", hideRequestFeedback);
  changePasswordButton.addEventListener("click", () => {
    hideRequestFeedback();
    resetRegistrationProgress();
  });
  analysisMethodInputs.forEach((input) => {
    input.addEventListener("change", () => {
      invalidateAnalysis();
      persistAuthProgress();
      updateButtons();
    });
  });
  document.addEventListener("points-changed", () => {
    if (mode === "register" && registrationId) {
      if (hasFiveSelectedPoints()) hideRequestFeedback();
      persistAuthProgress();
      updateButtons();
      return;
    }
    invalidateAnalysis();
    persistAuthProgress();
  });
  document.addEventListener("image-selection-started", () => {
    if (mode === "register" && registrationId) {
      resetRegistrationProgress();
    }
    invalidateAnalysis();
    persistAuthProgress();
  });
  document.addEventListener(
    "cancel-registration-progress",
    resetRegistrationProgress,
  );
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
    if (
      event.key === "Escape" &&
      confirmationModal.classList.contains("is-open")
    )
      closeConfirmationModal();
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
  updateToleranceLabel();
  return restoreAuthProgress;
}

function resetAuth() {
  document.dispatchEvent(new CustomEvent("cancel-registration-progress"));
  const form = document.getElementById("auth-form");
  form.reset();
  document.getElementById("clear-points").click();
  document.getElementById("register-tab").click();
  document.getElementById("request-feedback").hidden = true;
}

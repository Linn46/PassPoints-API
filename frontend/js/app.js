const LANGUAGE_STORAGE_KEY = "passpoints-language";

window.PasspointsTranslations = {
  es: {
    headerSubtitle: "Autenticación gráfica",
    footerSubtitle: "Proyecto de investigación en seguridad gráfica",
    authViewTitle: "Una contraseña que se dibuja.",
    authViewTitleLogin: "Vuelve a tu imagen.",
    authIntro: "Utiliza una imagen y una secuencia de cinco puntos que solo tú conozcas.",
    registerTab: "Crear cuenta",
    loginTab: "Iniciar sesión",
    userAccess: "Acceso",
    usernameLabel: "Nombre de usuario",
    usernamePlaceholder: "Tu nombre",
    emailLabel: "Correo electrónico",
    emailPlaceholder: "nombre@ejemplo.com",
    chooseImage: "Elige tu imagen",
    chooseImageHint: "Selecciona una escena que puedas recordar.",
    imageStatus: "Sin seleccionar",
    createSequence: "Crea tu secuencia",
    sequencePrompt: "Selecciona exactamente cinco puntos.",
    selectionHint: "Primero selecciona una imagen y después marca cinco lugares en el orden que prefieras.",
    pickImageStage: "Selecciona una imagen",
    imageStageHint: "Aquí aparecerá tu escena",
    resetPoints: "Reiniciar",
    analysisMethods: "Métodos de análisis",
    analysisMethodsHint: "Selecciona uno o varios métodos para evaluar tu contraseña.",
    delaunayMethodLabel: "Delaunay",
    distanceHullMethodLabel: "Distancia media + convex hull",
    analyzeSelection: "Analizar selección",
    analyzingSelection: "Analizando",
    createAccount: "Crear mi cuenta",
    creatingAccount: "Creando cuenta",
    signIn: "Iniciar sesión",
    authenticating: "Autenticando",
    weakPatternModalLabel: "PATRÓN DÉBIL",
    weakPatternModalTip: "Distribuye los puntos por diferentes zonas de la imagen.",
    patternModalClose: "Cerrar explicación",
    patternModalTipLabel: "Consejo",
    panelInfoAriaLabel: "Información sobre Passpoints",
    pointFeedbackWaiting: "Aún no hay puntos seleccionados.",
    pointFeedbackAccepted: "Selección aceptada por el análisis. Ya puedes crear tu cuenta.",
    securitySection: "SEGURIDAD",
    securityHeading: "Una contraseña más difícil de predecir",
    securityIntro: "El análisis comprueba si tus cinco puntos forman patrones demasiado fáciles de anticipar.",
    patternGrouped: "Agrupado",
    patternGroupDescription: "Puntos demasiado concentrados.",
    patternLine: "Line / Diag",
    patternLineDescription: "Puntos alineados en línea o diagonal.",
    patternRegular: "Regular",
    patternRegularDescription: "Puntos separados de forma uniforme.",
    patternAngular: "Angular",
    patternAngularDescription: "Una estructura geométrica ordenada.",
    patternDescription: "Ver explicación →",
    visualBadge: "SEGURIDAD GRÁFICA",
    visualSummary: "5 puntos",
    visualSequence: "1 secuencia",
    homeSpace: "ESPACIO PERSONAL",
    homeTitle: "Tu espacio de seguridad gráfica.",
    homeIntro: "Explora información, recursos y novedades sobre autenticación gráfica.",
    passpointLabel: "TU PASSPOINT",
    credentialProtected: "Contraseña protegida",
    sequenceLabel: "SECUENCIA DE CINCO PUNTOS",
    securityDetails: "Revisar información de seguridad",
    knowPasspoints: "CONOCE PASSPOINTS",
    securityRemember: "Seguridad que puedes recordar",
    continueExploring: "PARA SEGUIR EXPLORANDO",
    resourcesTitle: "Recursos",
    researchLabel: "Investigación",
    researchDescription: "Principios y contexto de autenticación gráfica",
    videosLabel: "Videos",
    videosDescription: "Material audiovisual sobre seguridad digital",
    readingLabel: "Lecturas",
    readingDescription: "Conceptos para entender el análisis de patrones",
    resourcesNote: "Recursos informativos del proyecto Passpoints.",
    accountSecurity: "SEGURIDAD DE TU CUENTA",
    graphicalAccess: "Acceso gráfico activo",
    sessionAuthenticated: "Tu sesión está autenticada",
    graphicalAuth: "Autenticación gráfica",
    validatedMessage: "Tu imagen y la secuencia de puntos se validaron correctamente.",
    didYouKnow: "¿SABÍAS QUE...?",
    pointOrder: "El orden de los puntos es tan importante como su posición.",
    pointsInSequence: "puntos en secuencia",
    theProject: "EL PROYECTO",
    projectDescription: "Proyecto de investigación sobre autenticación gráfica y evaluación de patrones.",
    myAccount: "Mi cuenta",
    accountMenu: "Mi cuenta",
    profile: "Mi perfil",
    security: "Seguridad",
    appearance: "Apariencia",
    about: "Acerca de Passpoints",
    logout: "Cerrar sesión",
    viewProfile: "Mi perfil",
    viewSecurity: "Seguridad",
    viewAbout: "Acerca de Passpoints",
    languageSwitch: "Cambiar idioma",
    themeLight: "Claro",
    themeDark: "Oscuro",
    themeToggleLight: "Cambiar a modo claro",
    themeToggleDark: "Cambiar a modo oscuro",
    profileNameLabel: "Nombre",
    profileEmailLabel: "Correo electrónico",
    profileCopy: "Tu cuenta utiliza autenticación gráfica con una imagen y cinco puntos en un orden específico.",
    securityCopy: "La selección utilizada se conserva solo durante esta sesión en la aplicación.",
    aboutCopy: "Passpoints es un proyecto de investigación sobre autenticación gráfica y análisis de patrones de selección.",
    visualPassword: "Tu contraseña",
    visualSequenceTitle: "Una secuencia visual",
    rememberPath: "Recuerda el camino, no la contraseña.",
    sequenceProtected: "Secuencia protegida",
    howItWorks: "¿Cómo funciona?",
    howItWorksText: "Elige una imagen, selecciona cinco puntos y utiliza la misma secuencia cada vez que quieras acceder.",
    visualFeature: "Visual",
    personalFeature: "Personal",
    analyticalFeature: "Analizada",
    easyToRemember: "Fácil de recordar",
    ownSequence: "Tu propia secuencia",
    detectPatterns: "Detectamos patrones",
    passpointsHint: "Passpoints, home",
    brandTitle: "Passpoints, home",
    sectionTitle: "Autenticación",
    homeSection: "Home",
    footerBrand: "PASSPOINTS",
    accountSummary: "Mi cuenta",
    noSelection: "Sin seleccionar",
    notSelected: "Sin seleccionar",
    accountThemeLabelLight: "Claro",
    accountThemeLabelDark: "Oscuro",
  },
  en: {
    headerSubtitle: "Secure graphical authentication",
    footerSubtitle: "Research project on graphical security",
    authViewTitle: "A password you draw.",
    authViewTitleLogin: "Back to your image.",
    authIntro: "Use an image and a sequence of five points that only you know.",
    registerTab: "Create account",
    loginTab: "Sign in",
    userAccess: "Access",
    usernameLabel: "Username",
    usernamePlaceholder: "Your name",
    emailLabel: "Email",
    emailPlaceholder: "name@example.com",
    chooseImage: "Choose your image",
    chooseImageHint: "Select a scene you can remember.",
    imageStatus: "Not selected",
    createSequence: "Create your sequence",
    sequencePrompt: "Select exactly five points.",
    selectionHint: "First select an image and then mark five places in the order you prefer.",
    pickImageStage: "Select an image",
    imageStageHint: "Your scene will appear here",
    resetPoints: "Reset",
    analysisMethods: "Analysis methods",
    analysisMethodsHint: "Select one or more methods to evaluate your password.",
    delaunayMethodLabel: "Delaunay",
    distanceHullMethodLabel: "Mean distance + convex hull",
    analyzeSelection: "Analyze selection",
    analyzingSelection: "Analyzing",
    createAccount: "Create my account",
    creatingAccount: "Creating account",
    signIn: "Sign in",
    authenticating: "Authenticating",
    weakPatternModalLabel: "WEAK PATTERN",
    weakPatternModalTip: "Spread the points across different areas of the image.",
    patternModalClose: "Close explanation",
    patternModalTipLabel: "Tip",
    panelInfoAriaLabel: "Information about Passpoints",
    pointFeedbackWaiting: "No points selected yet.",
    pointFeedbackAccepted: "Selection accepted by the analysis. You can now create your account.",
    securitySection: "SECURITY",
    securityHeading: "A password that is harder to predict",
    securityIntro: "The analysis checks whether your five points form patterns that are too easy to anticipate.",
    patternGrouped: "Grouped",
    patternGroupDescription: "Points clustered too closely.",
    patternLine: "Line / Diag",
    patternLineDescription: "Points aligned in a line or diagonal.",
    patternRegular: "Regular",
    patternRegularDescription: "Points spaced too evenly.",
    patternAngular: "Angular",
    patternAngularDescription: "A highly ordered geometric structure.",
    patternDescription: "See explanation →",
    visualBadge: "GRAPHICAL SECURITY",
    visualSummary: "5 points",
    visualSequence: "1 sequence",
    homeSpace: "PERSONAL SPACE",
    homeTitle: "Your graphical security space.",
    homeIntro: "Explore information, resources, and updates about graphical authentication.",
    passpointLabel: "YOUR PASSPOINT",
    credentialProtected: "Protected password",
    sequenceLabel: "SEQUENCE OF FIVE POINTS",
    securityDetails: "Review security information",
    knowPasspoints: "DISCOVER PASSPOINTS",
    securityRemember: "Security you can remember",
    continueExploring: "KEEP EXPLORING",
    resourcesTitle: "Resources",
    researchLabel: "Research",
    researchDescription: "Principles and context of graphical authentication",
    videosLabel: "Videos",
    videosDescription: "Audio-visual material on digital security",
    readingLabel: "Readings",
    readingDescription: "Concepts to understand pattern analysis",
    resourcesNote: "Informative resources from the Passpoints project.",
    accountSecurity: "YOUR ACCOUNT SECURITY",
    graphicalAccess: "Active graphical access",
    sessionAuthenticated: "Your session is authenticated",
    graphicalAuth: "Graphical authentication",
    validatedMessage: "Your image and point sequence were validated successfully.",
    didYouKnow: "DID YOU KNOW...?",
    pointOrder: "The order of the points matters as much as their position.",
    pointsInSequence: "points in sequence",
    theProject: "THE PROJECT",
    projectDescription: "Research project on graphical authentication and pattern evaluation.",
    myAccount: "My account",
    accountMenu: "My account",
    profile: "My profile",
    security: "Security",
    appearance: "Appearance",
    about: "About Passpoints",
    logout: "Log out",
    viewProfile: "My profile",
    viewSecurity: "Security",
    viewAbout: "About Passpoints",
    languageSwitch: "Change language",
    themeLight: "Light",
    themeDark: "Dark",
    themeToggleLight: "Switch to light mode",
    themeToggleDark: "Switch to dark mode",
    profileNameLabel: "Name",
    profileEmailLabel: "Email",
    profileCopy: "Your account uses graphical authentication with one image and five points in a specific order.",
    securityCopy: "The selected pattern is only kept during this session in the app.",
    aboutCopy: "Passpoints is a research project on graphical authentication and selection pattern analysis.",
    visualPassword: "Your password",
    visualSequenceTitle: "A visual sequence",
    rememberPath: "Remember the path, not the password.",
    sequenceProtected: "Protected sequence",
    howItWorks: "How it works",
    howItWorksText: "Choose an image, select five points, and use the same sequence every time you access the app.",
    visualFeature: "Visual",
    personalFeature: "Personal",
    analyticalFeature: "Analyzed",
    easyToRemember: "Easy to remember",
    ownSequence: "Your own sequence",
    detectPatterns: "We detect patterns",
    passpointsHint: "Passpoints, home",
    brandTitle: "Passpoints, home",
    sectionTitle: "Authentication",
    homeSection: "Home",
    footerBrand: "PASSPOINTS",
    accountSummary: "My account",
    noSelection: "No selection",
    notSelected: "Not selected",
    accountThemeLabelLight: "Light",
    accountThemeLabelDark: "Dark",
  },
};

window.PasspointsCurrentLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY) || "es";

function t(key) {
  const language = window.PasspointsCurrentLanguage || "es";
  return window.PasspointsTranslations?.[language]?.[key] || key;
}

function applyLanguageStrings() {
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (key && t(key) !== key) {
      element.textContent = t(key);
    }
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    const key = element.dataset.i18nPlaceholder;
    if (key && t(key) !== key) {
      element.placeholder = t(key);
    }
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    const key = element.dataset.i18nAriaLabel;
    if (key && t(key) !== key) {
      element.setAttribute("aria-label", t(key));
    }
  });
  const languageToggle = document.getElementById("language-toggle");
  if (languageToggle) {
    languageToggle.textContent = window.PasspointsCurrentLanguage === "es" ? "EN" : "ES";
    languageToggle.setAttribute(
      "aria-label",
      window.PasspointsCurrentLanguage === "es"
        ? "Switch language to English"
        : "Cambiar idioma a español",
    );
    languageToggle.title =
      window.PasspointsCurrentLanguage === "es" ? "English" : "Español";
  }
}

function setLanguage(language) {
  const nextLanguage = language === "en" ? "en" : "es";
  window.PasspointsCurrentLanguage = nextLanguage;
  localStorage.setItem(LANGUAGE_STORAGE_KEY, nextLanguage);
  document.documentElement.lang = nextLanguage;
  applyLanguageStrings();
  if (typeof window.refreshLanguageUI === "function") {
    window.refreshLanguageUI();
  }
}

window.refreshLanguageUI = function refreshLanguageUI() {
  if (typeof window.renderHome === "function") {
    const current = window.currentUserState || null;
    if (current) window.renderHome(current);
  }
};

let currentUser = null;

function showView(viewName) {
  const authView = document.getElementById("auth-view");
  const homeView = document.getElementById("home-view");
  const authenticated = viewName === "home";
  authView.hidden = authenticated;
  homeView.hidden = !authenticated;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadView(viewName) {
  const target = document.getElementById(`${viewName}-view`);
  const response = await fetch(`views/${viewName}.html`);
  if (!response.ok) throw new Error(`No se pudo cargar la vista ${viewName}.`);
  target.innerHTML = await response.text();
  applyLanguageStrings();
}

function handleAuthenticated(userState) {
  currentUser = userState;
  window.currentUserState = userState;
  renderHome(currentUser);
  updateAccountUser(currentUser.user);
  showView("home");
}

function logout() {
  sessionStorage.removeItem("passpoints_access_token");
  currentUser = null;
  window.currentUserState = null;
  closeAccountMenu();
  resetAuth();
  showView("auth");
}

async function initializeApp() {
  const languageToggle = document.getElementById("language-toggle");
  if (languageToggle) {
    languageToggle.addEventListener("click", () => {
      setLanguage(window.PasspointsCurrentLanguage === "es" ? "en" : "es");
      if (typeof window.refreshLanguageUI === "function") window.refreshLanguageUI();
    });
  }

  setLanguage(window.PasspointsCurrentLanguage);

  await Promise.all([loadView("auth"), loadView("home")]);
  const accountMount = document.getElementById("account-mount");
  const accountResponse = await fetch("views/account.html");
  if (!accountResponse.ok)
    throw new Error("No se pudo cargar la vista account.");
  accountMount.innerHTML = await accountResponse.text();

  initializeImageSelector();
  initializePointSelector();
  initializeAuth({ onAuthenticated: handleAuthenticated });
  initializeHome();
  initializeAccount({ onLogout: logout });
  applyLanguageStrings();
  showView("auth");
}

document.addEventListener("DOMContentLoaded", initializeApp, { once: true });

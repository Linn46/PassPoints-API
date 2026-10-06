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
}

function handleAuthenticated(userState) {
  currentUser = userState;
  renderHome(currentUser);
  updateAccountUser(currentUser.user);
  showView("home");
}

function logout() {
  sessionStorage.removeItem("passpoints_access_token");
  currentUser = null;
  closeAccountMenu();
  resetAuth();
  showView("auth");
}

async function initializeApp() {
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
  showView("auth");
}

document.addEventListener("DOMContentLoaded", initializeApp, { once: true });
>>>>>>> 029dc1f (feat: translate frontend copy to english)
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadView(viewName) {
  const target = document.getElementById(`${viewName}-view`);
  const response = await fetch(`views/${viewName}.html`);
  if (!response.ok) throw new Error(`No se pudo cargar la vista ${viewName}.`);
  target.innerHTML = await response.text();
}

function handleAuthenticated(userState) {
  currentUser = userState;
  renderHome(currentUser);
  updateAccountUser(currentUser.user);
  showView("home");
}

function logout() {
  sessionStorage.removeItem("passpoints_access_token");
  currentUser = null;
  closeAccountMenu();
  resetAuth();
  showView("auth");
}

<<<<<<< HEAD
async function initializeApp() {
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
  showView("auth");
}

document.addEventListener("DOMContentLoaded", initializeApp, { once: true });
=======
function setPending(value, action) {
  pending = value;
  setPointSelectionLocked(value);
  setImageSelectionLocked(value);
  analyzeSpinner.hidden = !(value && action === "analysis");
  submitSpinner.hidden = !(value && action === "submit");
  analyzeLabel.textContent =
    value && action === "analysis" ? "Analyzing" : "Analyze selection";
  submitLabel.textContent =
    value && action === "submit"
      ? mode === "register"
        ? "Creating account"
        : "Authenticating"
      : mode === "register"
        ? "Create my account"
        : "Sign in";
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
      "The service could not be reached. Please try again.";
  } else if (mode === "login" && error.status === 401) {
    requestFeedback.textContent =
      "Authentication failed. Check the image and selected points.";
  } else if (mode === "register" && error.status === 409) {
    requestFeedback.textContent =
      "That username or email is already associated with an account.";
  } else if (error.status === 503) {
    requestFeedback.textContent =
      "The authentication service is not configured. Restart the API with DATABASE_URL and AUTH_TOKEN_SECRET defined.";
  } else if (
    mode === "register" &&
    error.status === 422 &&
    /weak|déb|pattern/i.test(String(error.message))
  ) {
    requestFeedback.textContent =
      "This selection shows a weak pattern. Try other points.";
  } else {
    requestFeedback.textContent = fallback;
  }
}

function hideRequestFeedback() {
  requestFeedback.hidden = true;
  requestFeedback.textContent = "";
}

setMode("register");
>>>>>>> 029dc1f (feat: translate frontend copy to english)

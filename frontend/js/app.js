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

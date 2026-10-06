function initializeHome() {
  document
    .getElementById("security-details-button")
    .addEventListener("click", () => {
      document
        .querySelector(".account-security")
        .scrollIntoView({ behavior: "smooth", block: "center" });
    });
}

function renderHome(state) {
  document.getElementById("home-image-name").textContent = state.image.name;
  document.getElementById("home-image").src = state.image.src;
  const pointsLayer = document.getElementById("home-image-points");
  const sequence = document.getElementById("home-sequence");
  pointsLayer.replaceChildren();
  sequence.replaceChildren();
  state.fractions.forEach((point, index) => {
    const marker = document.createElement("span");
    marker.className = "home-point-marker";
    marker.textContent = String(index + 1);
    marker.style.left = `${point.x * 100}%`;
    marker.style.top = `${point.y * 100}%`;
    pointsLayer.appendChild(marker);
    const item = document.createElement("span");
    item.className = "sequence-point";
    item.textContent = String(index + 1);
    sequence.appendChild(item);
  });
  const userName = state.user.username;
  document.getElementById("credential-description").textContent =
    state.registered
      ? `Cuenta creada para ${userName}. El análisis aceptó la selección gráfica.`
      : `Hola, ${userName}. Tu imagen y secuencia se verificaron correctamente.`;
}

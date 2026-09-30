const pointsLayer = document.getElementById("points-layer");
const pointCount = document.getElementById("point-count");
const clearPointsButton = document.getElementById("clear-points");
const selectedImageElement = document.getElementById("selected-image");
const pointFeedback = document.getElementById("point-feedback");

const selectedPoints = [];
const MAX_POINTS = 5;
let pointSelectionLocked = false;

document.addEventListener("image-loaded", resetPoints);

selectedImageElement.addEventListener("click", (event) => {
  if (
    pointSelectionLocked ||
    selectedPoints.length >= MAX_POINTS ||
    !getImageData().id
  )
    return;

  const imageRect = selectedImageElement.getBoundingClientRect();
  const relativeX = Math.max(
    0,
    Math.min(1, (event.clientX - imageRect.left) / imageRect.width),
  );
  const relativeY = Math.max(
    0,
    Math.min(1, (event.clientY - imageRect.top) / imageRect.height),
  );
  const imageData = getImageData();
  selectedPoints.push({
    x: relativeX * imageData.width,
    y: relativeY * imageData.height,
    relativeX,
    relativeY,
  });
  renderPoints();
  document.dispatchEvent(new CustomEvent("points-changed"));
});

function resetPoints() {
  selectedPoints.length = 0;
  renderPoints();
  document.dispatchEvent(new CustomEvent("points-changed"));
}

function renderPoints() {
  pointsLayer.replaceChildren();
  selectedPoints.forEach((point, index) => {
    const marker = document.createElement("span");
    marker.className = "point-marker";
    marker.textContent = String(index + 1);
    marker.style.left = `${point.relativeX * 100}%`;
    marker.style.top = `${point.relativeY * 100}%`;
    pointsLayer.appendChild(marker);
  });

  const count = selectedPoints.length;
  pointCount.textContent = `${count}/5`;
  clearPointsButton.disabled = pointSelectionLocked || count === 0;
  pointFeedback.textContent =
    count === 5
      ? "Secuencia completa. Puedes analizarla."
      : count === 0
        ? "Aún no hay puntos seleccionados."
        : `Selecciona ${5 - count} punto${count === 4 ? "" : "s"} más.`;
}

clearPointsButton.addEventListener("click", resetPoints);

function getSelectedPoints() {
  return selectedPoints.map(({ x, y }) => ({ x, y }));
}

function getSelectedPointFractions() {
  return selectedPoints.map(({ relativeX, relativeY }) => ({
    x: relativeX,
    y: relativeY,
  }));
}

function hasFiveSelectedPoints() {
  return selectedPoints.length === MAX_POINTS;
}

function setPointSelectionLocked(locked) {
  pointSelectionLocked = locked;
  clearPointsButton.disabled = locked || selectedPoints.length === 0;
}

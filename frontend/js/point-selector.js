const pointsLayer = document.getElementById("points-layer");
const pointCount = document.getElementById("point-count");
const clearPointsButton = document.getElementById("clear-points");
const analyzeButton = document.getElementById("analyze-button");
const selectedImageElement = document.getElementById("selected-image");

const selectedPoints = [];

const MAX_POINTS = 5;

document.addEventListener("image-loaded", () => {
  selectedPoints.length = 0;
  pointsLayer.innerHTML = "";
  updatePointCounter();
});

selectedImageElement.addEventListener("click", (event) => {
  if (selectedPoints.length >= MAX_POINTS) {
    return;
  }

  const imageRect = selectedImageElement.getBoundingClientRect();
  const areaRect = document
    .getElementById("image-area")
    .getBoundingClientRect();

  const visualX = event.clientX - imageRect.left;
  const visualY = event.clientY - imageRect.top;

  const imageData = getImageData();

  const scaleX = imageData.width / imageRect.width;
  const scaleY = imageData.height / imageRect.height;

  const originalX = visualX * scaleX;
  const originalY = visualY * scaleY;

  const point = {
    x: originalX,
    y: originalY,
  };

  selectedPoints.push(point);

  const markerX = imageRect.left - areaRect.left + visualX;
  const markerY = imageRect.top - areaRect.top + visualY;

  createPointMarker(markerX, markerY, selectedPoints.length);

  updatePointCounter();
});

function createPointMarker(x, y, number) {
  const marker = document.createElement("div");

  marker.className = "point-marker";

  marker.textContent = `P${number}`;

  marker.style.left = `${x}px`;
  marker.style.top = `${y}px`;

  pointsLayer.appendChild(marker);
}

function updatePointCounter() {
  const count = selectedPoints.length;

  pointCount.textContent = `${count} / ${MAX_POINTS}`;

  clearPointsButton.disabled = count === 0;

  analyzeButton.disabled = count !== MAX_POINTS;
}

clearPointsButton.addEventListener("click", () => {
  selectedPoints.length = 0;

  pointsLayer.innerHTML = "";

  updatePointCounter();
});

function getSelectedPoints() {
  return selectedPoints.map((point) => ({
    x: point.x,
    y: point.y,
  }));
}

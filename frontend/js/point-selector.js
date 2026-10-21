const selectedPoints = [];
const MAX_POINTS = 5;
let pointSelectionLocked = false;

function initializePointSelector() {
  const pointsLayer = document.getElementById("points-layer");
  const pointCount = document.getElementById("point-count");
  const clearPointsButton = document.getElementById("clear-points");
  const undoPointButton = document.getElementById("undo-point");
  const selectedImageElement = document.getElementById("selected-image");
  const pointFeedback = document.getElementById("point-feedback");

  function resetPoints() {
    selectedPoints.length = 0;
    renderPoints();
    document.dispatchEvent(new CustomEvent("points-changed"));
  }

  function undoLastPoint() {
    if (pointSelectionLocked || selectedPoints.length === 0) return;
    selectedPoints.pop();
    renderPoints();
    document.dispatchEvent(new CustomEvent("points-changed"));
  }

  function renderPoints() {
    pointsLayer.replaceChildren();
    selectedPoints.forEach((point, index) => {
      const marker = document.createElement("button");
      marker.type = "button";
      marker.className = "point-marker";
      marker.textContent = String(index + 1);
      marker.style.left = `${point.relativeX * 100}%`;
      marker.style.top = `${point.relativeY * 100}%`;
      marker.setAttribute(
        "aria-label",
        `Move point ${index + 1} by dragging or using the arrow keys`,
      );
      marker.addEventListener("pointerdown", (event) => {
        if (pointSelectionLocked) return;
        event.preventDefault();
        marker.setPointerCapture(event.pointerId);
      });
      marker.addEventListener("pointermove", (event) => {
        if (
          pointSelectionLocked ||
          !marker.hasPointerCapture(event.pointerId)
        )
          return;
        const imageRect = selectedImageElement.getBoundingClientRect();
        movePoint(
          index,
          (event.clientX - imageRect.left) / imageRect.width,
          (event.clientY - imageRect.top) / imageRect.height,
          false,
        );
      });
      marker.addEventListener("pointerup", (event) => {
        if (!marker.hasPointerCapture(event.pointerId)) return;
        marker.releasePointerCapture(event.pointerId);
        document.dispatchEvent(new CustomEvent("points-changed"));
      });
      marker.addEventListener("pointercancel", (event) => {
        if (marker.hasPointerCapture(event.pointerId))
          marker.releasePointerCapture(event.pointerId);
        document.dispatchEvent(new CustomEvent("points-changed"));
      });
      marker.addEventListener("keydown", (event) => {
        const offsets = {
          ArrowLeft: [-0.01, 0],
          ArrowRight: [0.01, 0],
          ArrowUp: [0, -0.01],
          ArrowDown: [0, 0.01],
        };
        const offset = offsets[event.key];
        if (!offset || pointSelectionLocked) return;
        event.preventDefault();
        movePoint(
          index,
          point.relativeX + offset[0],
          point.relativeY + offset[1],
        );
      });
      pointsLayer.appendChild(marker);
    });

    const count = selectedPoints.length;
    pointCount.textContent = `${count}/5`;
    clearPointsButton.disabled = pointSelectionLocked || count === 0;
    undoPointButton.disabled = pointSelectionLocked || count === 0;
    pointFeedback.textContent =
      count === 5
        ? "Sequence complete. You can analyze it."
        : count === 0
          ? "No points selected yet."
          : `Select ${5 - count} more point${count === 4 ? "" : "s"}.`;
  }

  function getSelectedPoints() {
    return selectedPoints.map(({ x, y }) => ({ x, y }));
  }

  function getSelectedPointFractions() {
    return selectedPoints.map(({ relativeX, relativeY }) => ({
      x: relativeX,
      y: relativeY,
    }));
  }

  function setSelectedPointFractions(points) {
    if (
      !Array.isArray(points) ||
      points.length > MAX_POINTS ||
      points.some(
        ({ x, y } = {}) =>
          !Number.isFinite(x) ||
          !Number.isFinite(y) ||
          x < 0 ||
          x > 1 ||
          y < 0 ||
          y > 1,
      )
    )
      throw new Error("Saved Passpoints coordinates are invalid.");

    const image = getImageData();
    if (!image.id && points.length) return false;
    const restored = points.map(({ x, y }) => ({
      x: x * image.width,
      y: y * image.height,
      relativeX: x,
      relativeY: y,
    }));
    if (
      new Set(restored.map(({ x, y }) => `${x}:${y}`)).size !== restored.length
    )
      throw new Error("Saved Passpoints coordinates must be unique.");

    selectedPoints.splice(0, selectedPoints.length, ...restored);
    renderPoints();
    document.dispatchEvent(new CustomEvent("points-changed"));
    return true;
  }

  function hasFiveSelectedPoints() {
    return selectedPoints.length === MAX_POINTS;
  }

  function setPointSelectionLocked(locked) {
    pointSelectionLocked = locked;
    clearPointsButton.disabled = locked || selectedPoints.length === 0;
    undoPointButton.disabled = locked || selectedPoints.length === 0;
  }

  document.addEventListener("image-selection-started", resetPoints);
  function getGridCell(x, y, width, height) {
    const GRID_DIVISIONS = 5;
    return [
      Math.min(GRID_DIVISIONS, Math.floor((x / width) * GRID_DIVISIONS + 0.5)),
      Math.min(GRID_DIVISIONS, Math.floor((y / height) * GRID_DIVISIONS + 0.5))
    ];
  }

  function movePoint(index, relativeX, relativeY, dispatchChange = true) {
    const imageData = getImageData();
    const point = selectedPoints[index];
    const nextX = Math.max(0, Math.min(1, relativeX));
    const nextY = Math.max(0, Math.min(1, relativeY));
    const nextCell = getGridCell(
      nextX * imageData.width,
      nextY * imageData.height,
      imageData.width,
      imageData.height,
    );
    const overlapsAnotherPoint = selectedPoints.some(
      (otherPoint, otherIndex) => {
        if (otherIndex === index) return false;
        const otherCell = getGridCell(
          otherPoint.x,
          otherPoint.y,
          imageData.width,
          imageData.height,
        );
        return otherCell[0] === nextCell[0] && otherCell[1] === nextCell[1];
      },
    );
    if (overlapsAnotherPoint) {
      pointFeedback.textContent = t("pointsTooClose");
      return false;
    }

    point.x = nextX * imageData.width;
    point.y = nextY * imageData.height;
    point.relativeX = nextX;
    point.relativeY = nextY;
    const marker = pointsLayer.children[index];
    marker.style.left = `${nextX * 100}%`;
    marker.style.top = `${nextY * 100}%`;
    if (dispatchChange) document.dispatchEvent(new CustomEvent("points-changed"));
    return true;
  }

  document.addEventListener("image-loaded", resetPoints);
  document.addEventListener("reset-points", resetPoints);
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
    const point = {
      x: relativeX * imageData.width,
      y: relativeY * imageData.height,
      relativeX,
      relativeY,
    };
    
    // Validación de celda distinta (Passpoints rule)
    const newCell = getGridCell(point.x, point.y, imageData.width, imageData.height);
    if (selectedPoints.some(p => {
        const pCell = getGridCell(p.x, p.y, imageData.width, imageData.height);
        return pCell[0] === newCell[0] && pCell[1] === newCell[1];
    })) {
        pointFeedback.textContent = t("pointsTooClose");
        return;
    }

    if (
      selectedPoints.some(
        (selectedPoint) =>
          selectedPoint.x === point.x && selectedPoint.y === point.y,
      )
    ) {
      pointFeedback.textContent =
        window.PasspointsCurrentLanguage === "es"
          ? "Ese punto ya está seleccionado. Elige una ubicación diferente."
          : "That point is already selected. Choose a different location.";
      return;
    }

    selectedPoints.push(point);
    renderPoints();
    document.dispatchEvent(new CustomEvent("points-changed"));
  });
  clearPointsButton.addEventListener("click", resetPoints);
  undoPointButton.addEventListener("click", undoLastPoint);
  Object.assign(window, {
    getSelectedPoints,
    getSelectedPointFractions,
    setSelectedPointFractions,
    hasFiveSelectedPoints,
    setPointSelectionLocked,
  });
  renderPoints();
}

const selectedPoints = [];
const MAX_POINTS = 5;
let pointSelectionLocked = false;
let authenticationMode = "register";
let repeatingPassword = false;

function initializePointSelector() {
  const pointsLayer = document.getElementById("points-layer");
  const pointCount = document.getElementById("point-count");
  const clearPointsButton = document.getElementById("clear-points");
  const undoPointButton = document.getElementById("undo-point");
  const selectedImageElement = document.getElementById("selected-image");
  const pointFeedback = document.getElementById("point-feedback");
  function isTooClose(point, otherPoint) {
    if (authenticationMode !== "register" || repeatingPassword) return false;
    return Math.hypot(point.x - otherPoint.x, point.y - otherPoint.y) <= 20;
  }

  function hasValidPointSpacing() {
    for (let index = 0; index < selectedPoints.length; index += 1) {
      for (
        let otherIndex = index + 1;
        otherIndex < selectedPoints.length;
        otherIndex += 1
      ) {
        if (
          isTooClose(selectedPoints[index], selectedPoints[otherIndex]) ||
          (selectedPoints[index].x === selectedPoints[otherIndex].x &&
            selectedPoints[index].y === selectedPoints[otherIndex].y)
        ) {
          return false;
        }
      }
    }
    return true;
  }

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
  function movePoint(index, relativeX, relativeY, dispatchChange = true) {
    const imageData = getImageData();
    const point = selectedPoints[index];
    const nextX = Math.max(0, Math.min(1, relativeX));
    const nextY = Math.max(0, Math.min(1, relativeY));
    const nextPoint = { x: nextX * imageData.width, y: nextY * imageData.height };
    if (
      selectedPoints.some(
        (otherPoint, otherIndex) =>
          otherIndex !== index &&
          (isTooClose(nextPoint, otherPoint) ||
            (nextPoint.x === otherPoint.x && nextPoint.y === otherPoint.y)),
      )
    ) {
      pointFeedback.textContent = t("pointsTooClose");
      return false;
    }

    point.x = nextPoint.x;
    point.y = nextPoint.y;
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
  document.addEventListener("authentication-mode-changed", (event) => {
    authenticationMode = event.detail?.mode ?? "register";
    repeatingPassword = Boolean(event.detail?.repeating);
  });
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
    if (
      selectedPoints.some(
        (selectedPoint) =>
          isTooClose(point, selectedPoint) ||
          (selectedPoint.x === point.x && selectedPoint.y === point.y),
      )
    ) {
      pointFeedback.textContent = t("pointsTooClose");
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
    hasValidPointSpacing,
    setPointSelectionLocked,
  });
  renderPoints();
}

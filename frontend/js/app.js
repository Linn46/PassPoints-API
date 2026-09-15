const analysisButton = document.getElementById("analyze-button");
const resultsSection = document.getElementById("results");
const errorMessage = document.getElementById("error-message");

analysisButton.addEventListener("click", async () => {
  const points = getSelectedPoints();

  if (points.length !== 5) {
    showError("Debes seleccionar exactamente 5 puntos.");
    return;
  }

  hideError();

  analysisButton.disabled = true;
  analysisButton.textContent = "Analizando...";

  try {
    const result = await analyzePoints(points);

    displayResults(result);

    resultsSection.hidden = false;

    resultsSection.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  } catch (error) {
    showError(`No se pudo completar el análisis: ${error.message}`);
  } finally {
    analysisButton.disabled = false;
    analysisButton.textContent = "Analizar contraseña";
  }
});

function displayResults(result) {
  console.log("Resultado recibido de la API:", result);

  const perimeterRejected = Boolean(result.perimeter_test?.reject_null);
  const angleRejected = Boolean(result.angle_test?.reject_null);

  setResultValue("triangle-count", result.triangles?.length);

  setResultValue("average-perimeter", result.average_perimeter);

  setResultValue("average-angle", result.average_max_angle);

  setResultValue("perimeter-statistic", result.perimeter_test?.statistic);

  setResultValue("perimeter-critical", result.perimeter_test?.critical_value);

  setResultValue("perimeter-alpha", result.perimeter_test?.alpha);

  setResultValue(
    "perimeter-decision",
    perimeterRejected ? "Rechazar H0" : "No rechazar H0",
  );

  setResultValue("angle-statistic", result.angle_test?.statistic);

  setResultValue("angle-critical", result.angle_test?.critical_value);

  setResultValue("angle-alpha", result.angle_test?.alpha);

  setResultValue(
    "angle-decision",
    angleRejected ? "Rechazar H0" : "No rechazar H0",
  );

  renderTriangulation(result);
  explainResult(result.security, perimeterRejected, angleRejected);
}

function renderTriangulation(result) {
  const container = document.getElementById("result-image-container");
  const sourceImage = document.getElementById("selected-image");

  if (!container || !sourceImage || !result.triangles) {
    return;
  }

  container.replaceChildren();

  const wrapper = document.createElement("div");
  wrapper.className = "result-visual-wrapper";

  const image = document.createElement("img");
  image.src = sourceImage.src;
  image.alt = "Imagen con la triangulación de los puntos seleccionados";
  const imageData = getImageData();
  const analysisWidth = ANALYSIS_IMAGE_SIZE.width;
  const analysisHeight = ANALYSIS_IMAGE_SIZE.height;

  const overlay = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  overlay.setAttribute("viewBox", `0 0 ${imageData.width} ${imageData.height}`);
  overlay.setAttribute("preserveAspectRatio", "none");
  overlay.classList.add("result-triangulation");

  result.triangles.forEach((triangle) => {
    const polygon = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "polygon",
    );
    polygon.setAttribute(
      "points",
      triangle.vertices
        .map(
          (point) =>
            `${(point.x * imageData.width) / analysisWidth},${(point.y * imageData.height) / analysisHeight}`,
        )
        .join(" "),
    );
    overlay.appendChild(polygon);
  });

  (result.points || []).forEach((point, index) => {
    const marker = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "circle",
    );
    marker.setAttribute("cx", (point.x * imageData.width) / analysisWidth);
    marker.setAttribute("cy", (point.y * imageData.height) / analysisHeight);
    marker.setAttribute("r", "18");
    marker.classList.add("result-point");
    overlay.appendChild(marker);

    const label = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "text",
    );
    label.setAttribute("x", (point.x * imageData.width) / analysisWidth);
    label.setAttribute("y", (point.y * imageData.height) / analysisHeight + 6);
    label.textContent = `P${index + 1}`;
    label.classList.add("result-point-label");
    overlay.appendChild(label);
  });

  wrapper.append(image, overlay);
  container.appendChild(wrapper);
}

function explainResult(security, perimeterRejected, angleRejected) {
  const banner = document.getElementById("result-banner");
  const status = document.getElementById("result-status");
  const securityLevel = document.getElementById("security-level");
  const explanation = document.getElementById("result-explanation");
  const patterns = document.getElementById("security-patterns");
  const summary = document.getElementById("result-summary");
  const detailedExplanation = document.getElementById("detailed-explanation");
  const icon = document.getElementById("result-icon");

  if (!security) {
    return;
  }

  const detectedPatterns = security.patterns || [];
  const hasPattern = security.is_weak;

  banner.classList.toggle("warning", hasPattern);
  banner.classList.toggle("positive", !hasPattern);
  status.textContent = security.title;
  securityLevel.textContent = `Nivel de seguridad: ${security.level ?? "No disponible"}`;
  icon.textContent = hasPattern ? "!" : "✓";
  explanation.textContent = security.explanation;
  patterns.replaceChildren();

  if (detectedPatterns.length === 0) {
    const item = document.createElement("li");
    item.textContent = "Sin patrón específico";
    patterns.appendChild(item);
  } else {
    detectedPatterns.forEach((pattern) => {
      const item = document.createElement("li");
      item.textContent = pattern;
      patterns.appendChild(item);
    });
  }

  summary.textContent = `${security.explanation} Revisa la triangulación para observar la forma que crean tus puntos.`;
  detailedExplanation.textContent = `${security.explanation} El test de perímetros ${perimeterRejected ? "ha detectado" : "no ha detectado"} una regularidad en el tamaño de las figuras y el test de ángulos ${angleRejected ? "ha detectado" : "no ha detectado"} una regularidad en sus formas. Para una contraseña más resistente, evita repetir alineaciones, simetrías o agrupaciones parecidas.`;
}

function setResultValue(elementId, value) {
  const element = document.getElementById(elementId);

  if (!element) {
    return;
  }

  if (value === undefined || value === null) {
    element.textContent = "—";
    return;
  }

  if (typeof value === "number") {
    element.textContent = Number.isInteger(value) ? value : value.toFixed(4);

    return;
  }

  element.textContent = value;
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function hideError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}

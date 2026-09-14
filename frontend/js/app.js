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
  explainResult(perimeterRejected, angleRejected);
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
            `${(point.x * imageData.width) / 1920},${(point.y * imageData.height) / 1080}`,
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
    marker.setAttribute("cx", (point.x * imageData.width) / 1920);
    marker.setAttribute("cy", (point.y * imageData.height) / 1080);
    marker.setAttribute("r", "18");
    marker.classList.add("result-point");
    overlay.appendChild(marker);

    const label = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "text",
    );
    label.setAttribute("x", (point.x * imageData.width) / 1920);
    label.setAttribute("y", (point.y * imageData.height) / 1080 + 6);
    label.textContent = `P${index + 1}`;
    label.classList.add("result-point-label");
    overlay.appendChild(label);
  });

  wrapper.append(image, overlay);
  container.appendChild(wrapper);
}

function explainResult(perimeterRejected, angleRejected) {
  const banner = document.getElementById("result-banner");
  const status = document.getElementById("result-status");
  const explanation = document.getElementById("result-explanation");
  const summary = document.getElementById("result-summary");
  const detailedExplanation = document.getElementById("detailed-explanation");
  const icon = document.getElementById("result-icon");

  const rejectedTests = Number(perimeterRejected) + Number(angleRejected);
  let title;
  let text;

  if (rejectedTests === 0) {
    title = "No se detectan patrones evidentes";
    text =
      "La distribución de tus puntos no coincide claramente con los patrones analizados.";
  } else if (rejectedTests === 2) {
    title = "Se detectan patrones geométricos";
    text =
      "Los dos análisis encontraron una distribución que puede ser predecible.";
  } else {
    title = "Se detecta un patrón parcial";
    text =
      "Uno de los dos análisis encontró una distribución que merece atención.";
  }

  banner.classList.toggle("warning", rejectedTests > 0);
  banner.classList.toggle("positive", rejectedTests === 0);
  status.textContent = title;
  icon.textContent = rejectedTests === 0 ? "✓" : "!";
  explanation.textContent = text;
  summary.textContent = `${text} Revisa la triangulación para entender la forma que crean tus puntos.`;
  detailedExplanation.textContent = `${text} El test de perímetros ${perimeterRejected ? "detectó" : "no detectó"} una regularidad en el tamaño de las figuras y el test de ángulos ${angleRejected ? "detectó" : "no detectó"} una regularidad en sus formas. Para una contraseña más resistente, evita colocar puntos alineados, simétricos o demasiado agrupados.`;
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

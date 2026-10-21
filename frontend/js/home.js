function initializeHome() {
  document
    .getElementById("security-details-button")
    .addEventListener("click", () => {
      document
        .querySelector(".account-security")
        .scrollIntoView({ behavior: "smooth", block: "center" });
    });
}

const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

function svgElement(name, attributes = {}) {
  const element = document.createElementNS(SVG_NAMESPACE, name);
  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, String(value));
  });
  return element;
}

function renderRepetitionChart(history, isSpanish) {
  const chart = document.getElementById("repetition-chart");
  const title = isSpanish
    ? "Intentos y racha consecutiva"
    : "Attempts and consecutive streak";
  const description = isSpanish
    ? "Cada punto muestra la racha consecutiva después de un intento. Los puntos verdes son aciertos y los rojos son fallos. La línea superior marca la meta de tres."
    : "Each point shows the consecutive streak after an attempt. Green points are correct and red points are failures. The top line marks the goal of three.";
  chart.replaceChildren();
  chart.append(
    svgElement("title", { id: "repetition-chart-title" }),
    svgElement("desc", { id: "repetition-chart-description" }),
  );
  chart.querySelector("#repetition-chart-title").textContent = title;
  chart.querySelector("#repetition-chart-description").textContent =
    description;

  const attempts = history.attempts;
  const width = Math.max(640, 112 + Math.max(attempts.length - 1, 0) * 54);
  const top = 28;
  const bottom = 205;
  const left = 54;
  const right = width - 24;
  const xPosition = (index) =>
    attempts.length < 2
      ? left
      : left + (index / (attempts.length - 1)) * (right - left);
  const yPosition = (streak) => bottom - (streak / 3) * (bottom - top);

  chart.setAttribute("viewBox", `0 0 ${width} 260`);
  [0, 1, 2, 3].forEach((streak) => {
    const y = yPosition(streak);
    chart.appendChild(
      svgElement("line", {
        x1: left,
        x2: right,
        y1: y,
        y2: y,
        class: streak === 3 ? "chart-goal-line" : "chart-grid-line",
      }),
    );
    const label = svgElement("text", {
      x: left - 18,
      y: y + 4,
      class: "chart-axis-label",
      "text-anchor": "end",
    });
    label.textContent = String(streak);
    chart.appendChild(label);
  });

  chart.append(
    svgElement("line", {
      x1: left,
      x2: left,
      y1: top,
      y2: bottom,
      class: "chart-axis-line",
    }),
    svgElement("line", {
      x1: left,
      x2: right,
      y1: bottom,
      y2: bottom,
      class: "chart-axis-line",
    }),
  );

  if (attempts.length > 1) {
    const path = svgElement("polyline", {
      points: attempts
        .map(
          (attempt, index) =>
            `${xPosition(index)},${yPosition(attempt.consecutive_successes)}`,
        )
        .join(" "),
      class: "chart-streak-line",
    });
    chart.appendChild(path);
  }

  const labelStep = Math.max(1, Math.ceil(attempts.length / 8));
  attempts.forEach((attempt, index) => {
    const x = xPosition(index);
    const y = yPosition(attempt.consecutive_successes);
    const point = svgElement("circle", {
      cx: x,
      cy: y,
      r: 6,
      class: attempt.is_correct ? "chart-point-correct" : "chart-point-failure",
    });
    const tooltip = svgElement("title");
    tooltip.textContent = isSpanish
      ? `Intento ${attempt.attempt_number}: ${attempt.is_correct ? "acierto" : "fallo"}, racha ${attempt.consecutive_successes}`
      : `Attempt ${attempt.attempt_number}: ${attempt.is_correct ? "correct" : "failure"}, streak ${attempt.consecutive_successes}`;
    point.appendChild(tooltip);
    chart.appendChild(point);
    if (index % labelStep === 0 || index === attempts.length - 1) {
      const label = svgElement("text", {
        x,
        y: bottom + 20,
        class: "chart-axis-label",
        "text-anchor": "middle",
      });
      label.textContent = String(attempt.attempt_number);
      chart.appendChild(label);
    }
  });

  const xTitle = svgElement("text", {
    x: (left + right) / 2,
    y: 250,
    class: "chart-axis-title",
    "text-anchor": "middle",
  });
  xTitle.textContent = isSpanish ? "Intento" : "Attempt";
  chart.appendChild(xTitle);
  const yTitle = svgElement("text", {
    x: 16,
    y: (top + bottom) / 2,
    class: "chart-axis-title",
    "text-anchor": "middle",
    transform: `rotate(-90 16 ${(top + bottom) / 2})`,
  });
  yTitle.textContent = isSpanish ? "Racha" : "Streak";
  chart.appendChild(yTitle);
}

window.renderHome = function renderHome(state) {
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
  const isSpanish = (window.PasspointsCurrentLanguage || "es") === "es";
  document.getElementById("credential-description").textContent =
    state.registered
      ? isSpanish
        ? `Cuenta creada para ${userName}.`
        : `Account created for ${userName}.`
      : isSpanish
        ? `Hola, ${userName}. Tu imagen y secuencia se verificaron correctamente.`
        : `Hello, ${userName}. Your image and sequence were verified successfully.`;

  const status = document.getElementById("repetition-history-status");
  const results = document.getElementById("repetition-results");
  const history = state.repetitionHistory;
  if (!history) {
    status.hidden = false;
    status.textContent = window.PasspointsCurrentLanguage === "es"
      ? "Cargando historial de repeticiones…"
      : "Loading repetition history…";
    results.hidden = true;
    return;
  }
  if (!history.has_history) {
    status.hidden = false;
    status.textContent = window.PasspointsCurrentLanguage === "es"
      ? "No hay historial detallado para este usuario. Los intentos anteriores a este registro no se conservaron."
      : "There is no detailed history for this user. Attempts from before this registration were not retained.";
    results.hidden = true;
    return;
  }

  status.hidden = true;
  results.hidden = false;
  const goalUnavailable =
    window.PasspointsCurrentLanguage === "es" ? "No alcanzada" : "Not reached";
  document.getElementById("repetition-total").textContent = String(
    history.total_attempts,
  );
  document.getElementById("repetition-failures").textContent = String(
    history.failures,
  );
  document.getElementById("repetition-goal").textContent =
    history.attempts_to_goal === null
      ? goalUnavailable
      : String(history.attempts_to_goal);
  renderRepetitionChart(history, window.PasspointsCurrentLanguage === "es");

  const conclusion = document.getElementById("repetition-conclusion");
  const failureText =
    history.failures === 1
      ? isSpanish
        ? "1 fallo"
        : "1 failure"
      : isSpanish
        ? `${history.failures} fallos`
        : `${history.failures} failures`;
  conclusion.textContent =
    history.attempts_to_goal === null
      ? window.PasspointsCurrentLanguage === "es"
        ? "El historial disponible no muestra cuándo se alcanzó la meta. Estos datos describen únicamente la repetición durante el registro y no miden la seguridad general de tu contraseña."
        : "The available history does not show when the goal was reached. These data describe repetition during registration only and do not measure your password's overall security."
      : window.PasspointsCurrentLanguage === "es"
        ? `Alcanzaste tres aciertos consecutivos en ${history.attempts_to_goal} intentos y tuviste ${failureText}. Esto describe únicamente la repetición durante el registro; no es una medida general de la seguridad de tu contraseña.`
        : `You reached three consecutive correct attempts in ${history.attempts_to_goal} attempts, with ${failureText}. This describes repetition during registration only; it is not a general measure of your password's security.`;
};

window.showRepetitionHistoryError = function showRepetitionHistoryError() {
  const status = document.getElementById("repetition-history-status");
  status.hidden = false;
  status.textContent =
    window.PasspointsCurrentLanguage === "es"
      ? "No se pudo cargar el historial de repeticiones."
      : "The repetition history could not be loaded.";
  document.getElementById("repetition-results").hidden = true;
};

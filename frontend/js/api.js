const API_ORIGIN = "http://127.0.0.1:8001";
const ANALYSIS_URL = `${API_ORIGIN}/api/v1/analysis`;

class ApiError extends Error {
  constructor(status, detail) {
    super(detail);
    this.status = status;
  }
}

async function requestJson(url, payload, method = "POST", headers = {}) {
  let response;
  try {
    response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json", ...headers },
      ...(payload === undefined ? {} : { body: JSON.stringify(payload) }),
    });
  } catch (error) {
    console.error("Passpoints API connection error:", error);
    throw new ApiError(0, "connection");
  }

  let data = {};
  if (response.status !== 204) {
    try {
      data = await response.json();
    } catch (error) {
      console.error("Passpoints API returned a non-JSON response:", error);
    }
  }
  if (!response.ok) {
    console.error("Passpoints API request failed:", response.status, data);
    
    // LOG DETALLADO PARA DEPURACIÓN
    console.log("Detalles del error recibido:", data);

    const detail = Array.isArray(data.errors)
      ? data.errors
          .map(({ field, message }) => [field, message].filter(Boolean).join(": "))
          .join("; ")
      : Array.isArray(data.detail)
        ? data.detail.map((error) => `${error.loc[1]}: ${error.msg}`).join("; ") // Mejoramos el detalle de Pydantic
        : data.message ?? data.detail ?? data.error ?? "request_failed";
    throw new ApiError(response.status, detail);
  }
  return data;
}

function authPayload(image, points) {
  return {
    image_id: image.id,
    image_width: image.width,
    image_height: image.height,
    points,
  };
}

async function analyzeSelection(image, points, methods = ["delaunay_statistical"]) {
  const selectedMethods = methods && methods.length > 0 ? methods : ["delaunay_statistical"];
  return requestJson(ANALYSIS_URL, {
    image_width: image.width,
    image_height: image.height,
    alpha: 0.05,
    points,
    methods: selectedMethods,
  });
}

async function registerAccount(username, email, image, points, toleranceRadius) {
  return requestJson(`${API_ORIGIN}/auth/register`, {
    username,
    email,
    ...authPayload(image, points),
    tolerance_radius: toleranceRadius,
  });
}

async function registerRepetition(registrationId, points) {
  return requestJson(
    `${API_ORIGIN}/auth/register/${encodeURIComponent(registrationId)}/repetitions`,
    { points },
  );
}

async function cancelRegistration(registrationId) {
  return requestJson(
    `${API_ORIGIN}/auth/register/${encodeURIComponent(registrationId)}`,
    undefined,
    "DELETE",
  );
}

async function authenticate(email, image, points) {
  return requestJson(`${API_ORIGIN}/auth/login`, {
    email,
    ...authPayload(image, points),
  });
}

async function getLoginImageOptions(email, imageIds) {
  return requestJson(`${API_ORIGIN}/auth/login-images`, {
    email,
    image_ids: imageIds,
  });
}

async function getRepetitionHistory(accessToken) {
  return requestJson(
    `${API_ORIGIN}/auth/repetition-history`,
    undefined,
    "GET",
    { Authorization: `Bearer ${accessToken}` },
  );
}

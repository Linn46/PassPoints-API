const API_ORIGIN = "http://127.0.0.1:8001";
const ANALYSIS_URL = `${API_ORIGIN}/api/v1/analysis`;

class ApiError extends Error {
  constructor(status, detail) {
    super(detail);
    this.status = status;
  }
}

async function requestJson(url, payload) {
  let response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    console.error("Passpoints API connection error:", error);
    throw new ApiError(0, "connection");
  }

  let data = {};
  try {
    data = await response.json();
  } catch (error) {
    console.error("Passpoints API returned a non-JSON response:", error);
  }
  if (!response.ok) {
    console.error("Passpoints API request failed:", response.status, data);
    throw new ApiError(response.status, data.detail ?? "request_failed");
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

async function registerAccount(username, email, image, points) {
  return requestJson(`${API_ORIGIN}/auth/register`, {
    username,
    email,
    ...authPayload(image, points),
  });
}

async function authenticate(email, image, points) {
  return requestJson(`${API_ORIGIN}/auth/login`, {
    email,
    ...authPayload(image, points),
  });
}

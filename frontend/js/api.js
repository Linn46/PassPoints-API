const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

const DEFAULT_ALPHA = 0.05;
const ANALYSIS_IMAGE_SIZE = {
  width: 1920,
  height: 1080,
};

async function analyzePoints(points) {
  const imageData = getImageData();

  if (imageData.width === 0 || imageData.height === 0) {
    throw new Error("Debes seleccionar una imagen antes de analizar.");
  }

  const normalizedPoints = points.map((point) => ({
    x: (point.x * ANALYSIS_IMAGE_SIZE.width) / imageData.width,
    y: (point.y * ANALYSIS_IMAGE_SIZE.height) / imageData.height,
  }));

  const response = await fetch(`${API_BASE_URL}/analysis`, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      image_width: ANALYSIS_IMAGE_SIZE.width,
      image_height: ANALYSIS_IMAGE_SIZE.height,
      alpha: DEFAULT_ALPHA,
      points: normalizedPoints,
    }),
  });

  if (!response.ok) {
    let errorMessage = "No se pudo realizar el análisis.";

    try {
      const errorData = await response.json();

      if (errorData.detail) {
        errorMessage = Array.isArray(errorData.detail)
          ? errorData.detail.map((error) => error.msg).join(", ")
          : errorData.detail;
      }
    } catch {
      // Se mantiene el mensaje genérico.
    }

    throw new Error(errorMessage);
  }

  return await response.json();
}

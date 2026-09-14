const imageInput = document.getElementById("image-input");
const selectedImage = document.getElementById("selected-image");
const imageWrapper = document.getElementById("image-wrapper");
const imageArea = document.getElementById("image-area");
const emptyState = document.getElementById("empty-state");
const imageStatus = document.getElementById("image-status");

let imageData = {
  width: 0,
  height: 0,
};

let currentImageUrl = null;

imageInput.addEventListener("change", (event) => {
  const file = event.target.files[0];

  if (!file) {
    return;
  }

  if (!file.type.startsWith("image/")) {
    imageStatus.textContent = "El archivo seleccionado no es una imagen.";
    return;
  }

  const imageUrl = URL.createObjectURL(file);

  if (currentImageUrl) {
    URL.revokeObjectURL(currentImageUrl);
  }

  currentImageUrl = imageUrl;

  selectedImage.src = imageUrl;

  selectedImage.onload = () => {
    imageData.width = selectedImage.naturalWidth;
    imageData.height = selectedImage.naturalHeight;

    imageWrapper.hidden = false;
    emptyState.hidden = true;

    imageArea.classList.remove("empty");

    imageStatus.textContent = `${imageData.width} × ${imageData.height}px`;

    selectedImage.onload = null;

    document.dispatchEvent(
      new CustomEvent("image-loaded", {
        detail: {
          width: imageData.width,
          height: imageData.height,
        },
      }),
    );
  };
});

function getImageData() {
  return {
    width: imageData.width,
    height: imageData.height,
  };
}

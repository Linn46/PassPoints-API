const PASSPOINT_IMAGES = [
  {
    id: "coast-sunset",
    name: "Costa al atardecer",
    src: "assets/images/coast.svg",
    tone: "sand",
  },
  {
    id: "botanical-garden",
    name: "Jardín botánico",
    src: "assets/images/botanical.svg",
    tone: "leaf",
  },
  {
    id: "terracotta-house",
    name: "Casa de terracota",
    src: "assets/images/architecture.svg",
    tone: "clay",
  },
  {
    id: "desert-palms",
    name: "Palmeras del desierto",
    src: "assets/images/desert.svg",
    tone: "sun",
  },
  {
    id: "island-shore",
    name: "Orilla de la isla",
    src: "assets/images/coastline.svg",
    tone: "sea",
  },
];

const PASSPOINT_IMAGE_SIZE = { width: 1920, height: 1080 };

let selectedImageData = null;
let imageSelectionLocked = false;

function initializeImageSelector() {
  const imageOptions = document.getElementById("image-options");
  const selectedImage = document.getElementById("selected-image");
  const imageFrame = document.getElementById("image-frame");
  const imageStage = document.getElementById("image-stage");
  const stageEmpty = document.getElementById("stage-empty");
  const imageStatus = document.getElementById("image-status");

  function renderImageOptions() {
    PASSPOINT_IMAGES.forEach((image) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "image-option";
      button.dataset.imageId = image.id;
      button.setAttribute("aria-pressed", "false");
      button.setAttribute("aria-label", `Elegir ${image.name}`);
      button.disabled = imageSelectionLocked;

      const thumbnail = document.createElement("img");
      thumbnail.src = image.src;
      thumbnail.alt = "";
      thumbnail.loading = "lazy";

      const label = document.createElement("span");
      label.textContent = image.name;
      button.append(thumbnail, label);
      button.addEventListener("click", () => selectImage(image));
      imageOptions.appendChild(button);
    });
  }

  function selectImage(image) {
    if (imageSelectionLocked) return;
    selectedImageData = image;
    imageOptions.querySelectorAll(".image-option").forEach((button) => {
      const isSelected = button.dataset.imageId === image.id;
      button.classList.toggle("is-selected", isSelected);
      button.setAttribute("aria-pressed", String(isSelected));
    });

    selectedImage.onload = () => {
      imageFrame.hidden = false;
      stageEmpty.hidden = true;
      imageStage.classList.remove("is-empty");
      imageStatus.textContent = image.name;
      document.dispatchEvent(
        new CustomEvent("image-loaded", { detail: getImageData() }),
      );
    };
    selectedImage.src = image.src;
  }

  function setImageSelectionLocked(locked) {
    imageSelectionLocked = locked;
    imageOptions.querySelectorAll(".image-option").forEach((button) => {
      button.disabled = locked;
    });
  }

  function getImageData() {
    return {
      id: selectedImageData?.id ?? null,
      name: selectedImageData?.name ?? "",
      src: selectedImageData?.src ?? "",
      width: selectedImageData ? PASSPOINT_IMAGE_SIZE.width : 0,
      height: selectedImageData ? PASSPOINT_IMAGE_SIZE.height : 0,
    };
  }

  Object.assign(window, { getImageData, setImageSelectionLocked, selectImage });
  renderImageOptions();
}

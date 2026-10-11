const PASSPOINT_IMAGES = [
  {
    id: "coast-sunset",
    name: "Coast at sunset",
    src: "assets/images/coast.svg",
    tone: "sand",
  },
  {
    id: "botanical-garden",
    name: "Botanical garden",
    src: "assets/images/botanical.svg",
    tone: "leaf",
  },
  {
    id: "terracotta-house",
    name: "Terracotta house",
    src: "assets/images/architecture.svg",
    tone: "clay",
  },
  {
    id: "desert-palms",
    name: "Desert palms",
    src: "assets/images/desert.svg",
    tone: "sun",
  },
  {
    id: "island-shore",
    name: "Island shore",
    src: "assets/images/coastline.svg",
    tone: "sea",
  },
  {
    id: "mountain-lake",
    name: "Mountain lake",
    src: "assets/images/mountain-lake.svg",
    tone: "sea",
  },
  {
    id: "forest-trail",
    name: "Forest trail",
    src: "assets/images/forest-trail.svg",
    tone: "leaf",
  },
  {
    id: "city-night",
    name: "City at night",
    src: "assets/images/city-night.svg",
    tone: "blue",
  },
  {
    id: "coral-reef",
    name: "Coral reef",
    src: "assets/images/coral-reef.svg",
    tone: "sea",
  },
  {
    id: "snow-cabin",
    name: "Snow cabin",
    src: "assets/images/snow-cabin.svg",
    tone: "sand",
  },
  {
    id: "autumn-park",
    name: "Autumn park",
    src: "assets/images/autumn-park.svg",
    tone: "clay",
  },
  {
    id: "lavender-field",
    name: "Lavender field",
    src: "assets/images/lavender-field.svg",
    tone: "leaf",
  },
  {
    id: "waterfall",
    name: "Waterfall",
    src: "assets/images/waterfall.svg",
    tone: "sea",
  },
  {
    id: "lighthouse",
    name: "Lighthouse",
    src: "assets/images/lighthouse.svg",
    tone: "sand",
  },
  {
    id: "red-canyon",
    name: "Red canyon",
    src: "assets/images/red-canyon.svg",
    tone: "clay",
  },
  {
    id: "night-sky",
    name: "Night sky",
    src: "assets/images/night-sky.svg",
    tone: "blue",
  },
  {
    id: "vineyard",
    name: "Vineyard",
    src: "assets/images/vineyard.svg",
    tone: "leaf",
  },
  {
    id: "bamboo-grove",
    name: "Bamboo grove",
    src: "assets/images/bamboo-grove.svg",
    tone: "leaf",
  },
  {
    id: "harbor",
    name: "Harbor",
    src: "assets/images/harbor.svg",
    tone: "sea",
  },
  {
    id: "meadow",
    name: "Wildflower meadow",
    src: "assets/images/meadow.svg",
    tone: "leaf",
  },
  {
    id: "city-canal",
    name: "City canal",
    src: "assets/images/city-canal.svg",
    tone: "blue",
  },
];

const PASSPOINT_IMAGE_SIZE = { width: 1920, height: 1080 };

let selectedImageData = null;
let imageSelectionLocked = false;
let currentImageOptions = [];

function selectRandomImages(images, count, random = Math.random) {
  const uniqueImages = [];
  const seenIds = new Set();
  for (const image of images) {
    if (!image || typeof image.id !== "string" || !image.id || seenIds.has(image.id))
      continue;
    seenIds.add(image.id);
    uniqueImages.push(image);
  }
  if (!Number.isInteger(count) || count < 0 || uniqueImages.length < count)
    throw new RangeError(`Cannot choose ${count} images from a catalog of ${uniqueImages.length}.`);

  for (let index = uniqueImages.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(random() * (index + 1));
    [uniqueImages[index], uniqueImages[swapIndex]] = [
      uniqueImages[swapIndex],
      uniqueImages[index],
    ];
  }
  return uniqueImages.slice(0, count);
}

function initializeImageSelector() {
  const imageOptions = document.getElementById("image-options");
  const selectedImage = document.getElementById("selected-image");
  const imageFrame = document.getElementById("image-frame");
  const imageStage = document.getElementById("image-stage");
  const stageEmpty = document.getElementById("stage-empty");
  const imageStatus = document.getElementById("image-status");

  function renderImageOptions() {
    imageOptions.replaceChildren();
    currentImageOptions.forEach((image) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "image-option";
      button.dataset.imageId = image.id;
      button.setAttribute("aria-pressed", "false");
      button.setAttribute("aria-label", `Choose ${image.name}`);
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
    if (
      imageSelectionLocked ||
      !currentImageOptions.some((option) => option.id === image.id)
    )
      return;
    selectedImageData = image;
    imageOptions.querySelectorAll(".image-option").forEach((button) => {
      const isSelected = button.dataset.imageId === image.id;
      button.classList.toggle("is-selected", isSelected);
      button.setAttribute("aria-pressed", String(isSelected));
    });

    selectedImage.onload = () => {
      if (selectedImageData?.id !== image.id) return;
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

  function clearSelection() {
    selectedImageData = null;
    imageFrame.hidden = true;
    stageEmpty.hidden = false;
    imageStage.classList.add("is-empty");
    imageStatus.textContent =
      window.PasspointsCurrentLanguage === "en" ? "Not selected" : "Sin seleccionar";
    document.dispatchEvent(new CustomEvent("image-loaded", { detail: null }));
  }

  function setImageSelectionMode(mode) {
    imageOptions.dataset.mode = mode;
    currentImageOptions =
      mode === "register" ? selectRandomImages(PASSPOINT_IMAGES, 5) : [];
    renderImageOptions();
    clearSelection();
  }

  function setLoginImageOptions(imageIds) {
    if (!Array.isArray(imageIds) || imageIds.length !== 3 || new Set(imageIds).size !== 3)
      throw new Error("Login requires exactly three different image options.");
    const imagesById = new Map(PASSPOINT_IMAGES.map((image) => [image.id, image]));
    const images = imageIds.map((id) => imagesById.get(id));
    if (images.some((image) => !image))
      throw new Error("Login options contain an image missing from the catalog.");
    currentImageOptions = images;
    imageOptions.dataset.mode = "login";
    renderImageOptions();
    clearSelection();
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

  Object.assign(window, {
    getImageData,
    getImageCatalogIds: () => PASSPOINT_IMAGES.map((image) => image.id),
    setImageSelectionLocked,
    setImageSelectionMode,
    setLoginImageOptions,
    selectImage,
  });
  setImageSelectionMode("register");
}

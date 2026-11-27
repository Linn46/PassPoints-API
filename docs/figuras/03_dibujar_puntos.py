from pathlib import Path
import json
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BACKGROUND = ROOT / "docs" / "figuras" / "figura_02_fondo.png"
OUTPUT = ROOT / "docs" / "figuras" / "puntos_dibujados.png"

if len(sys.argv) != 2:
    print("Uso: python docs/figuras/03_dibujar_puntos.py puntos.json")
    sys.exit(1)

points_file = (ROOT / sys.argv[1]).resolve()

if not BACKGROUND.is_file():
    raise FileNotFoundError("Primero debes ejecutar 02_extraer_fondo.py")

if not points_file.is_file():
    raise FileNotFoundError(f"No existe el archivo de puntos: {points_file}")

with points_file.open("r", encoding="utf-8") as file:
    data = json.load(file)

points = data["points"]

if len(points) != 5:
    raise ValueError("Se requieren exactamente cinco puntos.")

coordinates = [(float(point["x"]), float(point["y"])) for point in points]

image = Image.open(BACKGROUND).convert("RGB")
for x, y in coordinates:
    if not 0 <= x < image.width or not 0 <= y < image.height:
        raise ValueError(
            f"El punto ({x}, {y}) está fuera del fondo "
            f"de {image.width}x{image.height} píxeles."
        )

draw = ImageDraw.Draw(image)

try:
    font = ImageFont.truetype("DejaVuSans.ttf", 20)
except OSError:
    font = ImageFont.load_default()

radius = max(7, image.width // 150)

for index, (x, y) in enumerate(coordinates, start=1):
    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill="red",
        outline="white",
        width=2,
    )
    draw.text((x + radius + 4, y - radius), f"P{index}", fill="white", font=font)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
image.save(OUTPUT)
print(f"Figura creada: {OUTPUT}")

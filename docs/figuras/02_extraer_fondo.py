from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "figuras" / "fondo_extraido.png"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

if len(sys.argv) < 2:
    print("Uso:")
    print("python docs/figuras/02_extraer_fondo.py ruta/de/la/imagen")
    sys.exit(1)

source = (ROOT / sys.argv[1]).resolve()

if not source.is_file():
    raise FileNotFoundError(f"No existe la imagen: {source}")

if source.suffix.lower() not in EXTENSIONS:
    raise ValueError("El archivo indicado no es una imagen compatible.")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with Image.open(source) as image:
    image.convert("RGB").save(OUTPUT, quality=95)

print(f"Imagen original: {source}")
print(f"Copia creada: {OUTPUT}")

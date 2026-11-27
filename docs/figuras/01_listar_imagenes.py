from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".svg"}
EXCLUDED = {
    ".git",
    "__pycache__",
    ".kilo",
    "node_modules",
    ".venv",
    "venv",
    "site-packages",
}

print("\nIMÁGENES ENCONTRADAS EN EL PROYECTO\n")

found = []

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    if any(part in EXCLUDED for part in path.parts):
        continue

    if path.suffix.lower() in EXTENSIONS:
        found.append(path)

for index, path in enumerate(sorted(found), start=1):
    print(f"{index:03d}. {path.relative_to(ROOT)}")

print(f"\nTotal: {len(found)} imágenes")

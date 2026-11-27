import matplotlib.pyplot as plt

WIDTH = 1000
HEIGHT = 700
points = [
    (120, 180),
    (350, 230),
    (560, 140),
    (760, 300),
    (860, 520),
]

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.set_xlim(0, WIDTH)
ax.set_ylim(0, HEIGHT)
ax.set_aspect("equal")

# Borde que representa la imagen
ax.plot(
    [0, WIDTH, WIDTH, 0, 0],
    [0, 0, HEIGHT, HEIGHT, 0],
    color="black",
    linewidth=1.2,
)

# Dibujar puntos
for i, (x, y) in enumerate(points, start=1):
    ax.scatter(x, y, s=100, zorder=3, color="tab:blue")
    ax.annotate(
        f"P{i} ({x}, {y})",
        (x, y),
        xytext=(8, -15),
        textcoords="offset points",
        fontsize=9,
    )

# Ejes y etiquetas
ax.set_xlabel("Coordenada X (píxeles)")
ax.set_ylabel("Coordenada Y (píxeles)")
ax.set_title("Sistema de coordenadas y selección de puntos PassPoints")

ax.grid(True, linestyle="--", alpha=0.4)

# Indicar el origen
ax.annotate(
    "Origen (0, 0)",
    xy=(0, 0),
    xytext=(30, 30),
    textcoords="offset points",
    arrowprops={"arrowstyle": "->"},
)

plt.tight_layout()
plt.savefig(
    "docs/figuras/figura_01_coordenadas.png",
    dpi=300,
    bbox_inches="tight",
)
plt.savefig(
    "docs/figuras/figura_01_coordenadas.svg",
    bbox_inches="tight",
)

plt.show()

import json
import importlib.util
from math import hypot
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.point import Point
from app.domain.triangle import Triangle
from app.geometry.delaunay.triangulator import triangulate
from app.geometry.distance.matrix import distance_matrix
from app.geometry.triangle.angles import triangle_angles_degrees
from app.geometry.triangle.perimeter import average_delaunay_perimeter

_hull_spec = importlib.util.spec_from_file_location(
    "passpoints_convex_hull",
    ROOT
    / "app"
    / "application"
    / "analysis"
    / "methods"
    / "mean_distance_convex_hull"
    / "convex_hull.py",
)
if _hull_spec is None or _hull_spec.loader is None:
    raise ImportError("No se pudo cargar la función de envolvente del backend.")
_hull_module = importlib.util.module_from_spec(_hull_spec)
_hull_spec.loader.exec_module(_hull_module)
convex_hull = _hull_module.convex_hull

FIGURES = ROOT / "docs" / "figuras"
BACKGROUND = FIGURES / "figura_02_fondo.png"
ANALYSIS = FIGURES / "seleccion_capitulo_2_analisis.json"
WIDTH = 1920
HEIGHT = 1080

COLORS = {
    "teal": (0, 174, 170, 230),
    "yellow": (255, 219, 92, 245),
    "orange": (255, 111, 77, 245),
    "white": (255, 255, 255, 255),
    "dark": (17, 35, 40, 235),
    "point": (255, 237, 96, 255),
}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    filename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(filename, size)


def create_canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    if not BACKGROUND.is_file():
        raise FileNotFoundError(f"No existe el fondo preparado: {BACKGROUND}")

    image = Image.open(BACKGROUND).convert("RGBA")
    if image.size != (WIDTH, HEIGHT):
        raise ValueError(
            f"El fondo debe medir {WIDTH}x{HEIGHT}, no {image.width}x{image.height}."
        )

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((40, 35, 1115, 154), radius=22, fill=COLORS["dark"])
    draw.text((70, 53), "PASSPOINTS  /  FIGURA METODOLÓGICA", font=load_font(21, True), fill=COLORS["yellow"])
    draw.text((70, 84), title, font=load_font(38, True), fill=COLORS["white"])
    draw.text((70, 130), subtitle, font=load_font(20), fill=COLORS["white"])
    draw.rounded_rectangle(
        (40, HEIGHT - 66, 790, HEIGHT - 24),
        radius=14,
        fill=COLORS["dark"],
    )
    draw.text(
        (58, HEIGHT - 58),
        "Secuencia ilustrativa; no representa resultados experimentales.",
        font=load_font(17),
        fill=COLORS["white"],
    )
    return image, draw


def draw_points(draw: ImageDraw.ImageDraw, points: list[Point]) -> None:
    for index, point in enumerate(points, start=1):
        x, y = point.x, point.y
        draw.ellipse(
            (x - 16, y - 16, x + 16, y + 16),
            fill=COLORS["point"],
            outline=COLORS["white"],
            width=5,
        )
        label_x = x + 22 if x < WIDTH - 140 else x - 82
        label_y = y - 38 if y > 115 else y + 24
        draw.rounded_rectangle(
            (label_x - 8, label_y - 4, label_x + 57, label_y + 34),
            radius=9,
            fill=COLORS["dark"],
        )
        draw.text(
            (label_x, label_y),
            f"P{index}",
            font=load_font(23, True),
            fill=COLORS["white"],
        )


def save(image: Image.Image, filename: str) -> None:
    image.convert("RGB").save(FIGURES / filename, quality=95)


def load_analysis(path: Path) -> tuple[dict, list[Point], list[Triangle]]:
    with path.open(encoding="utf-8") as file:
        response = json.load(file)

    points = [
        Point(float(point["x"]), float(point["y"]))
        for point in response["points"]
    ]
    triangles = [
        Triangle(
            tuple(
                Point(float(point["x"]), float(point["y"]))
                for point in item["vertices"]
            )
        )
        for item in response["triangles"]
    ]
    if len(points) != 5:
        raise ValueError(f"{path.name} debe contener exactamente cinco puntos.")

    point_set = set(points)
    if any(vertex not in point_set for triangle in triangles for vertex in triangle.vertices):
        raise ValueError(f"{path.name} contiene triángulos con vértices no seleccionados.")

    return response, points, triangles


def verify_analysis(response: dict, triangles: list[Triangle], path: Path) -> None:
    points = [Point(float(point["x"]), float(point["y"])) for point in response["points"]]
    api_triangle_sets = {frozenset(triangle.vertices) for triangle in triangles}
    backend_triangle_sets = {
        frozenset(triangle.vertices) for triangle in triangulate(points).triangles
    }
    if api_triangle_sets != backend_triangle_sets:
        raise ValueError(f"La triangulación no coincide con el backend en {path.name}.")

    average_max_angle = sum(
        max(triangle_angles_degrees(triangle)) for triangle in triangles
    ) / len(triangles)
    if abs(average_max_angle - response["average_max_angle"]) > 1e-8:
        raise ValueError(
            f"Los ángulos calculados no coinciden con {path.name}: "
            f"{average_max_angle} != {response['average_max_angle']}."
        )

    average_perimeter = average_delaunay_perimeter(tuple(triangles))
    if abs(average_perimeter - response["average_perimeter"]) > 1e-8:
        raise ValueError(
            f"Los perímetros calculados no coinciden con {path.name}: "
            f"{average_perimeter} != {response['average_perimeter']}."
        )


def create_coordinate_figure(points: list[Point]) -> None:
    image = Image.open(BACKGROUND).convert("RGBA")
    grid = Image.new("RGBA", image.size, (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid)

    x_ticks = [0, 480, 960, 1440, WIDTH]
    y_ticks = [0, 270, 540, 810, HEIGHT]
    for x in x_ticks:
        grid_draw.line((x, 0, x, HEIGHT), fill=(255, 255, 255, 135), width=3)
    for y in y_ticks:
        grid_draw.line((0, y, WIDTH, y), fill=(255, 255, 255, 135), width=3)
    image = Image.alpha_composite(image, grid)
    draw = ImageDraw.Draw(image, "RGBA")

    draw.rounded_rectangle((40, 35, 1150, 158), radius=22, fill=COLORS["dark"])
    draw.text((70, 50), "PASSPOINTS  /  REFERENCIA ESPACIAL", font=load_font(21, True), fill=COLORS["yellow"])
    draw.text((70, 79), "Sistema de coordenadas de la imagen", font=load_font(37, True), fill=COLORS["white"])
    draw.text((70, 125), "1920 x 1080 píxeles · origen arriba a la izquierda", font=load_font(20), fill=COLORS["white"])

    for x in x_ticks:
        label = f"{x}"
        label_x = min(max(x - 34, 8), WIDTH - 90)
        draw.rounded_rectangle(
            (label_x, 169, label_x + 78, 205),
            radius=8,
            fill=COLORS["dark"],
        )
        draw.text((label_x + 8, 174), label, font=load_font(19, True), fill=COLORS["white"])

    for y in y_ticks:
        label_y = min(max(y - 18, 8), HEIGHT - 40)
        draw.rounded_rectangle((10, label_y, 82, label_y + 36), radius=8, fill=COLORS["dark"])
        draw.text((20, label_y + 5), f"{y}", font=load_font(18, True), fill=COLORS["white"])

    for index, point in enumerate(points, start=1):
        x, y = point.x, point.y
        draw.ellipse(
            (x - 15, y - 15, x + 15, y + 15),
            fill=COLORS["point"],
            outline=COLORS["white"],
            width=5,
        )
        label = f"P{index} ({x:.0f}, {y:.0f})"
        label_x = x + 22 if x < WIDTH - 260 else x - 210
        label_y = y - 39 if y > 235 else y + 23
        box = draw.textbbox((0, 0), label, font=load_font(19, True))
        label_width = box[2] - box[0]
        draw.rounded_rectangle(
            (label_x - 8, label_y - 4, label_x + label_width + 10, label_y + 34),
            radius=8,
            fill=COLORS["dark"],
        )
        draw.text((label_x, label_y), label, font=load_font(19, True), fill=COLORS["white"])

    draw.rounded_rectangle(
        (840, HEIGHT - 68, 1880, HEIGHT - 20),
        radius=14,
        fill=COLORS["dark"],
    )
    draw.text(
        (858, HEIGHT - 57),
        "X crece a la derecha · Y hacia abajo · origen (0, 0).",
        font=load_font(20),
        fill=COLORS["white"],
    )
    save(image, "figura_08_sistema_coordenadas.png")


def main() -> None:
    if not ANALYSIS.is_file():
        raise FileNotFoundError(f"No existe la respuesta de análisis: {ANALYSIS}")

    response, points, triangles = load_analysis(ANALYSIS)
    verify_analysis(response, triangles, ANALYSIS)

    image, draw = create_canvas(
        "Triangulación de Delaunay",
        "Malla de triángulos devuelta por el endpoint de análisis.",
    )
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for index, triangle in enumerate(triangles, start=1):
        vertices = [(point.x, point.y) for point in triangle.vertices]
        overlay_draw.polygon(vertices, fill=(0, 174, 170, 72))
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image, "RGBA")
    for index, triangle in enumerate(triangles, start=1):
        vertices = [(point.x, point.y) for point in triangle.vertices]
        draw.line(vertices + [vertices[0]], fill=COLORS["teal"], width=8, joint="curve")
        center = (
            sum(point[0] for point in vertices) / 3,
            sum(point[1] for point in vertices) / 3,
        )
        draw.ellipse(
            (center[0] - 25, center[1] - 25, center[0] + 25, center[1] + 25),
            fill=COLORS["dark"],
        )
        draw.text(
            (center[0] - 19, center[1] - 17),
            f"T{index}",
            font=load_font(20, True),
            fill=COLORS["white"],
        )
    draw_points(draw, points)
    save(image, "figura_04_delaunay.png")

    image, draw = create_canvas(
        "Ángulos interiores de los triángulos",
        "Valores calculados con la función geométrica del backend (grados).",
    )
    angle_label_counts: dict[tuple[float, float], int] = {}
    for triangle in triangles:
        vertices = [(point.x, point.y) for point in triangle.vertices]
        draw.line(vertices + [vertices[0]], fill=COLORS["yellow"], width=7, joint="curve")
        angles = triangle_angles_degrees(triangle)
        for vertex_index, vertex in enumerate(triangle.vertices):
            first = triangle.vertices[(vertex_index + 1) % 3]
            second = triangle.vertices[(vertex_index + 2) % 3]
            first_length = hypot(first.x - vertex.x, first.y - vertex.y)
            second_length = hypot(second.x - vertex.x, second.y - vertex.y)
            direction_x = (first.x - vertex.x) / first_length + (second.x - vertex.x) / second_length
            direction_y = (first.y - vertex.y) / first_length + (second.y - vertex.y) / second_length
            direction_length = hypot(direction_x, direction_y) or 1
            vertex_key = (vertex.x, vertex.y)
            label_radius = 84 + 78 * angle_label_counts.get(vertex_key, 0)
            angle_label_counts[vertex_key] = angle_label_counts.get(vertex_key, 0) + 1
            label_x = vertex.x + direction_x / direction_length * label_radius
            label_y = vertex.y + direction_y / direction_length * label_radius
            text = f"{angles[vertex_index]:.1f}°"
            box = draw.textbbox((0, 0), text, font=load_font(22, True))
            label_width = box[2] - box[0]
            label_height = box[3] - box[1]
            draw.rounded_rectangle(
                (
                    label_x - label_width / 2 - 9,
                    label_y - label_height / 2 - 7,
                    label_x + label_width / 2 + 9,
                    label_y + label_height / 2 + 7,
                ),
                radius=9,
                fill=COLORS["dark"],
            )
            draw.text(
                (label_x - label_width / 2, label_y - label_height / 2 - 3),
                text,
                font=load_font(22, True),
                fill=COLORS["white"],
            )
    draw_points(draw, points)
    save(image, "figura_05_angulos.png")

    hull = convex_hull([(point.x, point.y) for point in points])
    image, draw = create_canvas(
        "Envolvente convexa",
        "Polígono mínimo que contiene la selección de cinco puntos.",
    )
    if len(hull) >= 3:
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).polygon(hull, fill=(255, 111, 77, 75))
        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image, "RGBA")
        draw.line(hull + [hull[0]], fill=COLORS["orange"], width=9, joint="curve")
    draw_points(draw, points)
    save(image, "figura_06_envolvente_convexa.png")

    matrix = distance_matrix(points)
    image, draw = create_canvas(
        "Distancias euclidianas entre puntos",
        "Se muestran los diez pares no ordenados; unidades en píxeles.",
    )
    for first_index in range(len(points)):
        for second_index in range(first_index + 1, len(points)):
            first = points[first_index]
            second = points[second_index]
            draw.line(
                (first.x, first.y, second.x, second.y),
                fill=(0, 174, 170, 150),
                width=4,
            )
    draw_points(draw, points)

    panel = (1390, 205, 1870, 844)
    draw.rounded_rectangle(panel, radius=24, fill=COLORS["dark"])
    draw.text((1430, 232), "Pares y distancias", font=load_font(27, True), fill=COLORS["yellow"])
    row_y = 292
    for first_index in range(len(points)):
        for second_index in range(first_index + 1, len(points)):
            pair = f"P{first_index + 1} - P{second_index + 1}"
            value = matrix[first_index][second_index]
            draw.text((1430, row_y), pair, font=load_font(21, True), fill=COLORS["white"])
            draw.text(
                (1665, row_y),
                f"{value:,.1f} px",
                font=load_font(21),
                fill=COLORS["white"],
            )
            row_y += 49
    save(image, "figura_07_distancias.png")

    _, coordinate_points, _ = load_analysis(
        FIGURES / "seleccion_regular_analisis.json"
    )
    create_coordinate_figure(coordinate_points)

    expected_pattern_ids = {
        "seleccion_agrupada_analisis.json": "clustered",
        "seleccion_lineal_analisis.json": "linear",
        "seleccion_regular_analisis.json": "regular",
    }
    for filename, expected_pattern_id in expected_pattern_ids.items():
        pattern_response, _, pattern_triangles = load_analysis(FIGURES / filename)
        verify_analysis(pattern_response, pattern_triangles, FIGURES / filename)
        detected_ids = {
            detail["pattern_id"]
            for detail in pattern_response["security"]["pattern_details"]
        }
        if expected_pattern_id not in detected_ids:
            raise ValueError(
                f"El backend no confirmó {expected_pattern_id} en {filename}."
            )

    print("Figuras creadas: 04–08; respuestas y geometrías verificadas.")
    print(f"Ángulo máximo medio informado por API: {response.get('average_max_angle')}")


if __name__ == "__main__":
    main()

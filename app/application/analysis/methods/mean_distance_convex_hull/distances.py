from __future__ import annotations

from math import hypot


def mean_distance(points: list[tuple[float, float]]) -> float:
    if len(points) < 2:
        return 0.0

    distances: list[float] = []
    for index, point in enumerate(points):
        for other in points[index + 1 :]:
            distances.append(hypot(point[0] - other[0], point[1] - other[1]))

    if not distances:
        return 0.0
    return sum(distances) / len(distances)


def mean_distance_rectangle(image_width: float, image_height: float) -> float:
    if image_width <= 0 or image_height <= 0:
        return 0.0
    rectangle_area = image_width * image_height
    return rectangle_area / max(image_width, image_height)

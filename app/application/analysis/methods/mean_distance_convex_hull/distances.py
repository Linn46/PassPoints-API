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

from __future__ import annotations

from math import hypot


def _cross(o: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if len(points) <= 1:
        return list(points)

    ordered = sorted(set(points))
    if len(ordered) <= 1:
        return ordered

    lower: list[tuple[float, float]] = []
    for point in ordered:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper: list[tuple[float, float]] = []
    for point in reversed(ordered):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    hull = lower[:-1] + upper[:-1]
    return hull


def hull_perimeter(points: list[tuple[float, float]]) -> float:
    hull = convex_hull(points)
    if len(hull) < 2:
        return 0.0

    total = 0.0
    for index in range(len(hull)):
        current = hull[index]
        next_point = hull[(index + 1) % len(hull)]
        total += hypot(current[0] - next_point[0], current[1] - next_point[1])
    return total


def hull_area(points: list[tuple[float, float]]) -> float:
    hull = convex_hull(points)
    if len(hull) < 3:
        return 0.0

    total = 0.0
    for index in range(len(hull)):
        current = hull[index]
        next_point = hull[(index + 1) % len(hull)]
        total += current[0] * next_point[1] - current[1] * next_point[0]
    return abs(total) / 2.0

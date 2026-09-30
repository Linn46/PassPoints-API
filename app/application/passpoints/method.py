import json
import math
from collections.abc import Sequence

from app.application.auth.credential_security import hash_secret, verify_secret

GRID_DIVISIONS = 5
PREVIOUS_GRID_DIVISIONS = (10, 20)

class Passpoints:
    @classmethod
    def create_credential(
        cls,
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
    ) -> str:
        return hash_secret(
            cls._representation(image_id, image_width, image_height, points)
        )

    @classmethod
    def verify_credential(
        cls,
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
        verifier: str,
    ) -> bool:
        try:
            current = cls._representation(
                image_id, image_width, image_height, points,
                version=3,
                grid_divisions=GRID_DIVISIONS,
            )
            if verify_secret(current, verifier):
                return True

            for version, grid_divisions in zip(
                (2, 1), PREVIOUS_GRID_DIVISIONS
            ):
                previous = cls._representation(
                    image_id,
                    image_width,
                    image_height,
                    points,
                    version=version,
                    grid_divisions=grid_divisions,
                )
                if verify_secret(previous, verifier):
                    return True
        except ValueError:
            return False
        return False

    @staticmethod
    def _representation(
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
        *,
        version: int = 3,
        grid_divisions: int = GRID_DIVISIONS,
    ) -> str:
        if not image_id.strip() or image_width <= 0 or image_height <= 0:
            raise ValueError("Image identity and dimensions are required.")
        if len(points) != 5:
            raise ValueError("A Passpoints credential requires five points.")

        cells = []
        for x, y in points:
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("Point coordinates must be finite.")
            if not 0 <= x <= image_width or not 0 <= y <= image_height:
                raise ValueError("Point coordinates must be inside the image.")
            cells.append(
                (
                    min(grid_divisions, math.floor(x / image_width * grid_divisions + 0.5)),
                    min(grid_divisions, math.floor(y / image_height * grid_divisions + 0.5)),
                )
            )
        if len(set(cells)) != 5:
            raise ValueError("Every point must occupy a distinct tolerance cell.")

        deltas = [
            [x2 - x1, y2 - y1]
            for (x1, y1), (x2, y2) in zip(cells, cells[1:])
        ]
        return json.dumps(
            {
                "version": version,
                "image_id": image_id.strip(),
                "grid_divisions": grid_divisions,
                "start": list(cells[0]),
                "deltas": deltas,
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
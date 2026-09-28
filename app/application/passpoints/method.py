import json
import math
from collections.abc import Sequence

from app.application.auth.credential_security import hash_secret, verify_secret


GRID_DIVISIONS = 20


class Passpoints:
    @classmethod
    def create_credential(
        cls,
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
    ) -> str:
        representation = cls._canonical_representation(
            image_id, image_width, image_height, points
        )
        return hash_secret(representation)

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
            representation = cls._canonical_representation(
                image_id, image_width, image_height, points
            )
        except ValueError:
            return False
        return verify_secret(representation, verifier)

    @staticmethod
    def _canonical_representation(
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
    ) -> str:
        if not image_id.strip():
            raise ValueError("image_id must not be blank.")
        if image_width <= 0 or image_height <= 0:
            raise ValueError("Image dimensions must be positive.")
        if len(points) != 5:
            raise ValueError("A Passpoints credential requires five points.")

        cells: list[tuple[int, int]] = []
        for x, y in points:
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("Point coordinates must be finite.")
            if not 0 <= x <= image_width or not 0 <= y <= image_height:
                raise ValueError("Point coordinates must be inside the image.")
            relative_x = x / image_width
            relative_y = y / image_height
            cells.append(
                (
                    min(GRID_DIVISIONS, math.floor(relative_x * GRID_DIVISIONS + 0.5)),
                    min(GRID_DIVISIONS, math.floor(relative_y * GRID_DIVISIONS + 0.5)),
                )
            )

        if len(set(cells)) != 5:
            raise ValueError("Each selected point must map to a distinct grid cell.")

        deltas = [
            [current[0] - previous[0], current[1] - previous[1]]
            for previous, current in zip(cells, cells[1:])
        ]
        canonical = {
            "version": 1,
            "image_id": image_id.strip(),
            "grid_divisions": GRID_DIVISIONS,
            "start": list(cells[0]),
            "deltas": deltas,
        }
        return json.dumps(
            canonical,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
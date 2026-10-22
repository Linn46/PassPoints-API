import base64
import hashlib
import json
import math
from collections.abc import Sequence

from cryptography.fernet import Fernet, InvalidToken

from app.application.auth.credential_security import hash_secret, verify_secret

MIN_TOLERANCE_RADIUS = 5
MAX_TOLERANCE_RADIUS = 30
DEFAULT_TOLERANCE_RADIUS = 10
_ENCRYPTION_KEY_CONTEXT = b"Passpoints coordinate encryption v1\0"


class Passpoints:
    @classmethod
    def create_credential(
        cls,
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
        tolerance_radius: int = DEFAULT_TOLERANCE_RADIUS,
    ) -> str:
        cls._validate_points(
            image_id, image_width, image_height, points, tolerance_radius
        )
        return hash_secret(
            cls._canonical_representation(
                image_id,
                image_width,
                image_height,
                points,
                tolerance_radius,
            )
        )

    @classmethod
    def encrypt_points(
        cls,
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
        encryption_secret: str,
        tolerance_radius: int = DEFAULT_TOLERANCE_RADIUS,
    ) -> str:
        cls._validate_points(
            image_id, image_width, image_height, points, tolerance_radius
        )
        payload = json.dumps(
            {
                "image_id": image_id.strip(),
                "image_width": image_width,
                "image_height": image_height,
                "tolerance_radius": tolerance_radius,
                "points": [[float(x), float(y)] for x, y in points],
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        return cls._fernet(encryption_secret).encrypt(payload.encode()).decode()

    @classmethod
    def verify_credential(
        cls,
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
        verifier: str,
        encrypted_points: str | None,
        tolerance_radius: int,
        encryption_secret: str,
    ) -> bool:
        if encrypted_points is None:
            return False
        try:
            cls._validate_points(image_id, image_width, image_height, points)
            payload = cls._fernet(encryption_secret).decrypt(
                encrypted_points.encode()
            )
            saved = json.loads(payload)
            if (
                saved["image_id"] != image_id.strip()
                or saved["image_width"] != image_width
                or saved["image_height"] != image_height
                or saved["tolerance_radius"] != tolerance_radius
            ):
                return False
            reference_points = [
                (float(point[0]), float(point[1])) for point in saved["points"]
            ]
            reference_representation = cls._canonical_representation(
                image_id,
                image_width,
                image_height,
                reference_points,
                tolerance_radius,
            )
            if not verify_secret(reference_representation, verifier):
                return False
            cls._validate_points(
                image_id,
                image_width,
                image_height,
                reference_points,
                tolerance_radius,
            )
            return all(
                math.hypot(current_x - saved_x, current_y - saved_y)
                <= tolerance_radius
                for (current_x, current_y), (saved_x, saved_y) in zip(
                    points, reference_points
                )
            )
        except (
            IndexError,
            KeyError,
            TypeError,
            ValueError,
            InvalidToken,
            UnicodeDecodeError,
        ):
            return False

    @staticmethod
    def _fernet(encryption_secret: str) -> Fernet:
        secret = encryption_secret.encode("utf-8")
        if len(secret) < 32:
            raise ValueError("AUTH_TOKEN_SECRET must contain at least 32 bytes.")
        key = base64.urlsafe_b64encode(
            hashlib.sha256(_ENCRYPTION_KEY_CONTEXT + secret).digest()
        )
        return Fernet(key)

    @staticmethod
    def _canonical_representation(
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
        tolerance_radius: int,
    ) -> str:
        return json.dumps(
            {
                "version": 4,
                "image_id": image_id.strip(),
                "image_width": image_width,
                "image_height": image_height,
                "tolerance_radius": tolerance_radius,
                "points": [[float(x), float(y)] for x, y in points],
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def _validate_points(
        cls,
        image_id: str,
        image_width: int,
        image_height: int,
        points: Sequence[tuple[float, float]],
        tolerance_radius: int | None = None,
    ) -> None:
        if not image_id.strip() or image_width <= 0 or image_height <= 0:
            raise ValueError("Image identity and dimensions are required.")
        if len(points) != 5:
            raise ValueError("A Passpoints credential requires five points.")
        if tolerance_radius is not None and not (
            MIN_TOLERANCE_RADIUS <= tolerance_radius <= MAX_TOLERANCE_RADIUS
        ):
            raise ValueError("Tolerance radius must be between 5 and 30 pixels.")

        for x, y in points:
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("Point coordinates must be finite.")
            if not 0 <= x <= image_width or not 0 <= y <= image_height:
                raise ValueError("Point coordinates must be inside the image.")

        if tolerance_radius is not None:
            minimum_distance = 2 * tolerance_radius
            for index, (x, y) in enumerate(points):
                if any(
                    math.hypot(x - other_x, y - other_y) <= minimum_distance
                    for other_x, other_y in points[index + 1 :]
                ):
                    raise ValueError("Passpoints must not be too close together.")

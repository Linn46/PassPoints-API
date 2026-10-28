import json

import pytest

from app.application.passpoints.method import Passpoints


IMAGE = "botanical-garden"
WIDTH = 1920
HEIGHT = 1080
TOLERANCE = 10
SECRET = "test-encryption-secret-32-bytes!"
POINTS = [
    (432, 162),
    (654, 367),
    (1422, 799),
    (1038, 583),
    (462, 907),
]


def create_saved_credential(points=POINTS, tolerance=TOLERANCE):
    verifier = Passpoints.create_credential(
        IMAGE, WIDTH, HEIGHT, points, tolerance
    )
    encrypted_points = Passpoints.encrypt_points(
        IMAGE, WIDTH, HEIGHT, points, SECRET, tolerance
    )
    return verifier, encrypted_points


def verify(points, verifier, encrypted_points, tolerance=TOLERANCE, image=IMAGE):
    return Passpoints.verify_credential(
        image,
        WIDTH,
        HEIGHT,
        points,
        verifier,
        encrypted_points,
        tolerance,
        SECRET,
    )


def test_credential_stores_an_argon2_verifier_and_encrypted_coordinates() -> None:
    verifier, encrypted_points = create_saved_credential()

    assert verifier.startswith("$argon2id$")
    assert encrypted_points != json.dumps(POINTS)
    assert all(str(coordinate) not in encrypted_points for point in POINTS for coordinate in point)


def test_same_and_nearby_ordered_points_verify_inside_euclidean_tolerance() -> None:
    verifier, encrypted_points = create_saved_credential()
    moved = [(x + 6, y + 7) for x, y in POINTS]

    assert verify(POINTS, verifier, encrypted_points)
    assert verify(moved, verifier, encrypted_points)


def test_point_outside_tolerance_does_not_verify() -> None:
    verifier, encrypted_points = create_saved_credential()
    moved = [(x + 11, y) for x, y in POINTS]

    assert not verify(moved, verifier, encrypted_points)


def test_tolerance_radius_is_selected_and_persisted_in_verifier_flow() -> None:
    verifier, encrypted_points = create_saved_credential(tolerance=20)
    moved = [(x + 19, y) for x, y in POINTS]

    assert verify(moved, verifier, encrypted_points, tolerance=20)
    assert not verify(moved, verifier, encrypted_points, tolerance=10)


def test_order_and_image_binding_are_preserved() -> None:
    verifier, encrypted_points = create_saved_credential()

    assert not verify(list(reversed(POINTS)), verifier, encrypted_points)
    assert not verify(POINTS, verifier, encrypted_points, image="different-image")


def test_tampered_or_missing_encrypted_coordinates_fail_closed() -> None:
    verifier, encrypted_points = create_saved_credential()

    assert not verify(POINTS, verifier, encrypted_points[:-2] + "xx")
    assert not verify(POINTS, verifier, None)


@pytest.mark.parametrize("radius", [4, 31])
def test_tolerance_radius_must_be_between_five_and_thirty(radius: int) -> None:
    with pytest.raises(ValueError, match="between 5 and 30"):
        Passpoints.create_credential(IMAGE, WIDTH, HEIGHT, POINTS, radius)


def test_points_with_overlapping_tolerance_regions_are_rejected() -> None:
    too_close = [(100, 100), (119, 100), *POINTS[2:]]

    with pytest.raises(ValueError, match="too close"):
        Passpoints.create_credential(IMAGE, WIDTH, HEIGHT, too_close, 10)


def test_adaptive_tolerance_uses_deviation_margin_and_spacing_cap() -> None:
    assert Passpoints.estimate_tolerance_radius(8.2, POINTS) == 11
    close_points = [(100, 100), (130, 100), *POINTS[2:]]
    assert Passpoints.estimate_tolerance_radius(25, close_points) == 14
    assert Passpoints.estimate_tolerance_radius(0, POINTS) == 5

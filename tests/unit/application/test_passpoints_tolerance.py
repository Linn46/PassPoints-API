import pytest

from app.application.passpoints.method import Passpoints


IMAGE = "botanical-garden"
WIDTH = 1920
HEIGHT = 1080
POINTS = [
    (432, 162),
    (654, 367),
    (1422, 799),
    (1038, 583),
    (462, 907),
]


def test_nearby_selection_crossing_old_cell_boundary_is_accepted() -> None:
    verifier = Passpoints.create_credential(IMAGE, WIDTH, HEIGHT, POINTS)
    moved = [(x + 100, y) for x, y in POINTS]

    assert Passpoints.verify_credential(IMAGE, WIDTH, HEIGHT, moved, verifier)


def test_selection_outside_tolerance_region_is_rejected() -> None:
    verifier = Passpoints.create_credential(IMAGE, WIDTH, HEIGHT, POINTS)
    moved = [(x + 250, y) for x, y in POINTS]

    assert not Passpoints.verify_credential(IMAGE, WIDTH, HEIGHT, moved, verifier)


def test_tolerance_preserves_point_order_and_image_binding() -> None:
    verifier = Passpoints.create_credential(IMAGE, WIDTH, HEIGHT, POINTS)
    moved = [(x + 10, y - 10) for x, y in POINTS]

    assert not Passpoints.verify_credential(
        IMAGE, WIDTH, HEIGHT, list(reversed(moved)), verifier
    )
    assert not Passpoints.verify_credential(
        "different-image", WIDTH, HEIGHT, moved, verifier
    )


@pytest.mark.parametrize("version, grid_divisions", [(2, 10), (1, 20)])
def test_previous_grid_credentials_remain_verifiable(
    version: int, grid_divisions: int
) -> None:
    legacy_representation = Passpoints._representation(
        IMAGE, WIDTH, HEIGHT, POINTS, version=version, grid_divisions=grid_divisions
    )
    from app.application.auth.credential_security import hash_secret

    verifier = hash_secret(legacy_representation)

    assert Passpoints.verify_credential(IMAGE, WIDTH, HEIGHT, POINTS, verifier)
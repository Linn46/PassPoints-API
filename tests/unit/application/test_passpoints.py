import json

from app.application.passpoints.method import Passpoints


POINTS = [
    (214, 173),
    (843, 921),
    (1472, 284),
    (1165, 735),
    (521, 492),
]


def test_create_credential_accepts_five_ordered_points() -> None:
    verifier = Passpoints.create_credential("image-001", 1920, 1080, POINTS)

    assert verifier.startswith("$argon2id$")


def test_canonical_representation_is_deterministic() -> None:
    first = Passpoints._canonical_representation(
        "image-001", 1920, 1080, POINTS
    )
    second = Passpoints._canonical_representation(
        "image-001", 1920, 1080, POINTS
    )

    assert first == second


def test_canonical_representation_encodes_ordered_dx_and_dy() -> None:
    representation = json.loads(
        Passpoints._canonical_representation("image-001", 1920, 1080, POINTS)
    )

    assert representation["start"] == [2, 3]
    assert representation["deltas"] == [[7, 14], [6, -12], [-3, 9], [-7, -5]]
    assert representation["grid_divisions"] == 20


def test_normalization_is_relative_to_image_dimensions() -> None:
    scaled_points = [(x * 2, y * 2) for x, y in POINTS]

    first = Passpoints._canonical_representation(
        "image-001", 1920, 1080, POINTS
    )
    scaled = Passpoints._canonical_representation(
        "image-001", 3840, 2160, scaled_points
    )

    assert first == scaled


def test_discretization_accepts_small_selection_tolerance() -> None:
    slightly_moved = [(x + 2, y + 2) for x, y in POINTS]
    verifier = Passpoints.create_credential("image-001", 1920, 1080, POINTS)

    assert Passpoints.verify_credential(
        "image-001", 1920, 1080, slightly_moved, verifier
    )


def test_same_passpoints_selection_verifies() -> None:
    verifier = Passpoints.create_credential("image-001", 1920, 1080, POINTS)

    assert Passpoints.verify_credential("image-001", 1920, 1080, POINTS, verifier)


def test_different_passpoints_selection_does_not_verify() -> None:
    verifier = Passpoints.create_credential("image-001", 1920, 1080, POINTS)
    changed = [(250, 200), *POINTS[1:]]

    assert not Passpoints.verify_credential(
        "image-001", 1920, 1080, changed, verifier
    )


def test_credential_is_bound_to_image_identity() -> None:
    verifier = Passpoints.create_credential("image-001", 1920, 1080, POINTS)

    assert not Passpoints.verify_credential("image-002", 1920, 1080, POINTS, verifier)


def test_verifier_does_not_reveal_original_points() -> None:
    verifier = Passpoints.create_credential("image-001", 1920, 1080, POINTS)

    assert verifier.startswith("$argon2id$")
    assert all(str(coordinate) not in verifier for point in POINTS for coordinate in point)
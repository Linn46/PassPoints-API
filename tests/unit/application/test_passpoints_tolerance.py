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
SECRET = "test-encryption-secret-32-bytes!"


def test_moved_points_within_tolerance_verify_against_saved_coordinates() -> None:
    verifier = Passpoints.create_credential(IMAGE, WIDTH, HEIGHT, POINTS, 10)
    encrypted = Passpoints.encrypt_points(
        IMAGE, WIDTH, HEIGHT, POINTS, SECRET, 10
    )
    moved = [(x + 6, y + 7) for x, y in POINTS]

    assert Passpoints.verify_credential(
        IMAGE, WIDTH, HEIGHT, moved, verifier, encrypted, 10, SECRET
    )


def test_selection_outside_tolerance_region_is_rejected() -> None:
    verifier = Passpoints.create_credential(IMAGE, WIDTH, HEIGHT, POINTS, 5)
    encrypted = Passpoints.encrypt_points(
        IMAGE, WIDTH, HEIGHT, POINTS, SECRET, 5
    )
    moved = [(x + 6, y) for x, y in POINTS]

    assert not Passpoints.verify_credential(
        IMAGE, WIDTH, HEIGHT, moved, verifier, encrypted, 5, SECRET
    )

from random import Random

import pytest

from app.application.auth.image_selection import (
    InsufficientImageCatalogError,
    RegisteredImageUnavailableError,
    select_login_images,
)


IMAGE_IDS = ["image-1", "image-2", "image-3", "image-4", "image-5"]


def test_login_options_have_three_distinct_images_and_keep_registered_image() -> None:
    options = select_login_images(IMAGE_IDS, "image-3", Random(7))

    assert len(options) == 3
    assert len(set(options)) == 3
    assert "image-3" in options


def test_registered_image_appears_in_each_random_position() -> None:
    positions = {
        select_login_images(IMAGE_IDS, "image-3", Random(seed)).index("image-3")
        for seed in range(30)
    }

    assert positions == {0, 1, 2}


def test_unknown_account_gets_three_random_distinct_images() -> None:
    options = select_login_images(IMAGE_IDS, rng=Random(7))

    assert len(options) == 3
    assert len(set(options)) == 3
    assert set(options) <= set(IMAGE_IDS)


def test_duplicate_catalog_ids_never_create_duplicate_choices() -> None:
    options = select_login_images(
        ["image-1", "image-1", "image-2", "image-3", "image-4"],
        "image-1",
        Random(7),
    )

    assert len(options) == 3
    assert len(set(options)) == 3


def test_catalog_with_fewer_than_three_unique_images_fails_explicitly() -> None:
    with pytest.raises(InsufficientImageCatalogError):
        select_login_images(["image-1", "image-1", "image-2"])


def test_missing_registered_image_is_not_replaced_by_a_distractor() -> None:
    with pytest.raises(RegisteredImageUnavailableError):
        select_login_images(IMAGE_IDS, "retired-image", Random(7))

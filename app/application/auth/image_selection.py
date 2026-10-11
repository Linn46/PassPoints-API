from random import Random, SystemRandom


class InsufficientImageCatalogError(ValueError):
    pass


class RegisteredImageUnavailableError(ValueError):
    pass


def select_login_images(
    catalog_image_ids: list[str],
    registered_image_id: str | None = None,
    rng: Random | None = None,
) -> list[str]:
    unique_image_ids = list(dict.fromkeys(catalog_image_ids))
    if len(unique_image_ids) < 3:
        raise InsufficientImageCatalogError(
            "At least three different images are required."
        )

    chooser = rng or SystemRandom()
    if registered_image_id is None:
        return chooser.sample(unique_image_ids, 3)
    if registered_image_id not in unique_image_ids:
        raise RegisteredImageUnavailableError(
            "The registered image is not in the current image catalog."
        )

    distractors = chooser.sample(
        [image_id for image_id in unique_image_ids if image_id != registered_image_id],
        2,
    )
    options = [*distractors, registered_image_id]
    chooser.shuffle(options)
    return options

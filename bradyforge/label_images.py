"""Helpers for listing available label-type images for Tab 1.

This module only discovers filenames of label images stored in a directory
(e.g. ``config.LABEL_IMAGES_PATH``). Reading or base64-encoding image bytes
for the API layer is deferred to a future cycle.
"""

import os

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}


def list_label_images(images_dir):
    """Return a sorted list of image filenames found directly in ``images_dir``.

    Only files (not subdirectories) directly inside ``images_dir`` are
    considered, and only those whose extension matches ``IMAGE_EXTENSIONS``
    (case-insensitively). If ``images_dir`` does not exist or cannot be
    read (e.g. a permissions error), an empty list is returned instead of
    raising.
    """
    try:
        entries = os.listdir(images_dir)
    except OSError:
        return []

    images = []
    for entry in entries:
        full_path = os.path.join(images_dir, entry)
        if not os.path.isfile(full_path):
            continue
        _, extension = os.path.splitext(entry)
        if extension.lower() in IMAGE_EXTENSIONS:
            images.append(entry)

    return sorted(images)

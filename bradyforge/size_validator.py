"""Validation for uploaded file sizes.

`validate_upload_size` confirms only that a file's size, in bytes, does
not exceed the configured maximum upload size. It does not check file
type, content, or structure — those are separate concerns handled
elsewhere.
"""

import os

from bradyforge.config import MAX_UPLOAD_SIZE_BYTES


class FileTooLargeError(Exception):
    """Raised when a file's size exceeds the allowed maximum."""


def validate_upload_size(path, max_bytes=None):
    """Confirm that the file at `path` is at or under `max_bytes`.

    `max_bytes` defaults to `bradyforge.config.MAX_UPLOAD_SIZE_BYTES` when
    not explicitly passed. Returns True if the file's size is less than or
    equal to `max_bytes` (a file exactly at the limit passes). Raises
    `FileTooLargeError`, naming the file's actual size and the limit, if
    the file's size exceeds `max_bytes`.
    """
    if max_bytes is None:
        max_bytes = MAX_UPLOAD_SIZE_BYTES

    size = os.path.getsize(path)

    if size > max_bytes:
        raise FileTooLargeError(
            f"File is too large: {path} is {size} bytes, "
            f"which exceeds the maximum allowed size of {max_bytes} bytes"
        )

    return True

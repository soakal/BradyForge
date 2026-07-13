"""Helpers for resolving upload filenames without overwriting existing files.

Tab 2's upload flow keeps the original filename whenever possible, and only
appends a timestamp when a file with the same name already exists in the
destination directory.
"""

import os
from datetime import datetime

TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


def resolve_upload_filename(directory, filename, now=None):
    """Return a filename safe to use for an upload in ``directory``.

    If no file named ``filename`` exists in ``directory``, ``filename`` is
    returned unchanged. Otherwise, a timestamp is inserted before the file
    extension (e.g. ``report.v2.xlsx`` -> ``report.v2_20260713_140501.xlsx``)
    so the new file does not collide with the existing one.

    ``now`` may be supplied (typically a ``datetime`` instance) to make the
    timestamp deterministic in tests; it defaults to ``datetime.now()``.
    """
    destination = os.path.join(directory, filename)
    if not os.path.exists(destination):
        return filename

    if now is None:
        now = datetime.now()

    name, extension = os.path.splitext(filename)
    timestamp = now.strftime(TIMESTAMP_FORMAT)
    return f"{name}_{timestamp}{extension}"

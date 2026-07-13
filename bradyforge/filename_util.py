"""Helpers for resolving upload filenames without overwriting existing files.

Tab 2's upload flow keeps the original filename whenever possible, and only
appends a timestamp when a file with the same name already exists in the
destination directory.
"""

import os
from datetime import datetime

TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Characters Windows forbids in filenames (path separators are handled
# separately by taking the basename).
_INVALID_FILENAME_CHARS = set('<>:"|?*')


def resolve_upload_filename(directory, filename, now=None):
    """Return a filename safe to use for an upload in ``directory``.

    If no file named ``filename`` exists in ``directory``, ``filename`` is
    returned unchanged. Otherwise, a timestamp is inserted before the file
    extension (e.g. ``report.v2.xlsx`` -> ``report.v2_20260713_140501.xlsx``)
    so the new file does not collide with the existing one. If the
    timestamped name *also* already exists (two submissions of the same
    filename within the same second), a numeric suffix is appended
    (``report_20260713_140501_2.xlsx``, ``_3``, ...) until a free name is
    found.

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
    candidate = f"{name}_{timestamp}{extension}"
    counter = 2
    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{name}_{timestamp}_{counter}{extension}"
        counter += 1
    return candidate


def sanitize_filename(filename):
    """Reduce a caller-supplied filename to a safe basename, or ``None``.

    Filenames arriving over the JS bridge are untrusted input: a crafted
    or accidental value could contain path separators (``..\\evil.xlsx``),
    characters Windows forbids (``:"<>|?*`` or control characters), or be
    empty/whitespace. This strips any directory components (both ``/`` and
    ``\\`` are treated as separators regardless of platform), trims
    surrounding whitespace and trailing dots/spaces (which Windows drops
    silently), and returns the cleaned basename — or ``None`` if nothing
    usable remains or forbidden characters are present.
    """
    if not isinstance(filename, str):
        return None

    basename = filename.replace("\\", "/").rsplit("/", 1)[-1]
    basename = basename.strip().rstrip(". ")

    if not basename or basename in (".", ".."):
        return None
    if any(ch in _INVALID_FILENAME_CHARS or ord(ch) < 32 for ch in basename):
        return None
    return basename

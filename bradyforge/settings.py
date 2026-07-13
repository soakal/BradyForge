"""Persistence for user-editable BradyForge settings.

Settings are stored as a small JSON file with exactly three known keys:
`uploads_path`, `label_images_path`, and `fallback_email`. This module is
UI-independent — it knows nothing about PyWebView or where the settings
file should live on disk. Callers must pass an explicit `path`; deciding
where that file lives (e.g. a per-user config directory) is not part of
this module.
"""

import json
import os

from bradyforge import config

_KNOWN_KEYS = ("uploads_path", "label_images_path", "fallback_email")


def default_settings():
    """Return the default settings dict.

    `uploads_path` and `label_images_path` default to the confirmed
    values in `bradyforge/config.py` (read dynamically, so runtime
    overrides of the config module take effect). `fallback_email` has no
    confirmed default, so it defaults to an empty string.
    """
    return {
        "uploads_path": config.UPLOADS_PATH,
        "label_images_path": config.LABEL_IMAGES_PATH,
        "fallback_email": "",
    }


def load_settings(path):
    """Load settings from the JSON file at `path`.

    If `path` does not exist, or exists but cannot be parsed as valid
    JSON, `default_settings()` is returned. Otherwise, the parsed data is
    merged over `default_settings()`: only the three known keys are kept,
    any missing known keys fall back to their defaults, and any unknown
    keys in the file are ignored.

    Values are also sanity-checked: a stored value only overrides its
    default if it is a non-empty (non-whitespace) string. This means a
    user who saves an empty uploads/label-images path gets the confirmed
    default back rather than an unusable empty path.
    """
    defaults = default_settings()

    if not os.path.exists(path):
        return defaults

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return defaults

    if not isinstance(data, dict):
        return defaults

    merged = dict(defaults)
    for key in _KNOWN_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            merged[key] = value
    return merged


def save_settings(data, path):
    """Save `data` as JSON to `path`, creating parent directories if needed.

    Only the three known keys are written; unknown keys in `data` are
    dropped, non-string values are ignored, and string values are
    stripped of surrounding whitespace. The write is atomic (write to a
    temp file, then `os.replace`) so a crash mid-write can never leave a
    truncated/corrupt settings file behind.
    """
    filtered = {}
    for key in _KNOWN_KEYS:
        value = data.get(key) if isinstance(data, dict) else None
        if isinstance(value, str):
            filtered[key] = value.strip()

    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(filtered, f)
    os.replace(temp_path, path)

"""JS-bridge API surface for BradyForge.

The `Api` class defined here is the object that will eventually be
handed to `webview.create_window(..., js_api=api_instance)` (or exposed
via `window.expose()`) so the JS front end can call plain Python
methods. This module intentionally never imports `webview`: `Api` is
plain Python and every method must be directly unit-testable as a
normal method call, without a live webview.
"""

import os
import shutil
from pathlib import Path

from bradyforge.filename_util import resolve_upload_filename
from bradyforge.settings import load_settings, save_settings
from bradyforge.size_validator import FileTooLargeError, validate_upload_size
from bradyforge.xlsx_validator import InvalidXlsxError, validate_xlsx_file

# Default per-user location for the settings file. Never touched at
# import time or in `Api.__init__` — only read/written lazily when
# `get_settings`/`save_settings` are actually called.
DEFAULT_SETTINGS_PATH = Path.home() / ".bradyforge" / "settings.json"


class Api:
    """Backend API exposed to the JS front end via PyWebView.

    Methods are added incrementally, module by module, as each backend
    module is built out. This starts with settings-related methods only.
    """

    def __init__(self, settings_path=None):
        self.settings_path = (
            settings_path if settings_path is not None else DEFAULT_SETTINGS_PATH
        )

    def get_settings(self):
        """Return the current settings dict, loaded from disk."""
        return load_settings(self.settings_path)

    def save_settings(self, data):
        """Persist `data` as the new settings, then return the canonical result.

        Delegates to `bradyforge.settings.save_settings`, then re-reads
        via `get_settings()` so callers receive the merged/persisted
        dict rather than a raw echo of their input.
        """
        save_settings(data, self.settings_path)
        return self.get_settings()

    def accept_upload(self, source_path, destination_dir):
        """Validate and copy an uploaded workbook into `destination_dir`.

        Runs `source_path` through `validate_xlsx_file` (genuine, non-corrupted
        .xlsx) and `validate_upload_size` (within the configured size limit).
        On success, resolves a collision-safe destination filename via
        `resolve_upload_filename`, copies the file with `shutil.copy2`, and
        returns `{"ok": True, "saved_path": ..., "filename": ...}`.

        Expected validation failures (`InvalidXlsxError`, `FileTooLargeError`)
        are caught and returned as `{"ok": False, "error": <message>}` rather
        than propagated, since the future JS bridge can't catch raised Python
        exceptions. Any other unexpected exception propagates normally.
        """
        try:
            validate_xlsx_file(source_path)
            validate_upload_size(source_path)
        except (InvalidXlsxError, FileTooLargeError) as exc:
            return {"ok": False, "error": str(exc)}

        filename = resolve_upload_filename(
            destination_dir, os.path.basename(source_path)
        )
        saved_path = os.path.join(destination_dir, filename)
        shutil.copy2(source_path, saved_path)

        return {"ok": True, "saved_path": str(saved_path), "filename": filename}

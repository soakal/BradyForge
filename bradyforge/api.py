"""JS-bridge API surface for BradyForge.

The `Api` class defined here is the object that will eventually be
handed to `webview.create_window(..., js_api=api_instance)` (or exposed
via `window.expose()`) so the JS front end can call plain Python
methods. This module intentionally never imports `webview`: `Api` is
plain Python and every method must be directly unit-testable as a
normal method call, without a live webview.
"""

import base64
import io
import os
import shutil
import tempfile
from pathlib import Path

from bradyforge import config
from bradyforge.fallback_saver import save_local_and_zip
from bradyforge.filename_util import resolve_upload_filename
from bradyforge.generic_writer import write_generic_workbook
from bradyforge.settings import load_settings, save_settings
from bradyforge.size_validator import FileTooLargeError, validate_upload_size
from bradyforge.xlsx_validator import InvalidXlsxError, validate_xlsx_file

# Default per-user location for the settings file. Never touched at
# import time or in `Api.__init__` — only read/written lazily when
# `get_settings`/`save_settings` are actually called.
DEFAULT_SETTINGS_PATH = Path.home() / ".bradyforge" / "settings.json"

# Default per-user location for locally-saved fallback uploads. Never
# touched at import time or in `Api.__init__` — only created/written
# lazily when `accept_upload` actually needs to fall back to it.
DEFAULT_FALLBACK_DIR = Path.home() / ".bradyforge" / "fallback"


class Api:
    """Backend API exposed to the JS front end via PyWebView.

    Methods are added incrementally, module by module, as each backend
    module is built out. This starts with settings-related methods only.
    """

    def __init__(self, settings_path=None, fallback_dir=None):
        self.settings_path = (
            settings_path if settings_path is not None else DEFAULT_SETTINGS_PATH
        )
        self.fallback_dir = (
            fallback_dir if fallback_dir is not None else DEFAULT_FALLBACK_DIR
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

    def accept_upload(self, source_path, destination_dir=None):
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

        If `destination_dir` turns out to be unreachable (e.g. an offline
        network share), the collision-resolve + copy attempt raises
        `OSError`/`PermissionError`. That is caught here and treated as a
        fallback case: the source file's bytes are saved locally and zipped
        via `bradyforge.fallback_saver.save_local_and_zip` (into
        `self.fallback_dir`), and the result reflects the fallback with
        `{"ok": True, "fallback": True, "local_path": ..., "zip_path": ...,
        "message": ...}`.

        `destination_dir` is optional; when omitted (or `None`), it defaults
        to `bradyforge.config.UPLOADS_PATH`, so callers don't need to know or
        pass the real uploads location.
        """
        destination_dir = (
            destination_dir if destination_dir is not None else config.UPLOADS_PATH
        )

        try:
            validate_xlsx_file(source_path)
            validate_upload_size(source_path)
        except (InvalidXlsxError, FileTooLargeError) as exc:
            return {"ok": False, "error": str(exc)}

        try:
            filename = resolve_upload_filename(
                destination_dir, os.path.basename(source_path)
            )
            saved_path = os.path.join(destination_dir, filename)
            shutil.copy2(source_path, saved_path)
        except (OSError, PermissionError):
            filename = os.path.basename(source_path)
            source_bytes = Path(source_path).read_bytes()
            fallback_result = save_local_and_zip(
                source_bytes, filename, self.fallback_dir
            )
            return {
                "ok": True,
                "fallback": True,
                "local_path": fallback_result.local_path,
                "zip_path": fallback_result.zip_path,
                "message": fallback_result.message,
            }

        return {"ok": True, "saved_path": str(saved_path), "filename": filename}

    def accept_upload_bytes(self, filename, base64_content, destination_dir=None):
        """Base64-transport variant of `accept_upload` for the JS bridge.

        JS reads the uploaded `File` via `FileReader.readAsDataURL()` (or
        similar) and sends the resulting base64 string across the bridge,
        since raw binary payloads aren't a natural fit for the JS-to-Python
        call boundary. This method decodes `base64_content` (stripping a
        leading `"data:...;base64,"` prefix if present), writes the decoded
        bytes to a temp file named exactly `filename` (so `accept_upload`'s
        internal `os.path.basename(source_path)` resolves to the original
        name), then fully delegates to `accept_upload` for validation,
        collision-safe copying, and fallback handling. The temp directory is
        always removed afterward, regardless of whether `accept_upload`
        succeeds, returns an error, or raises.

        `destination_dir` is optional; when omitted (or `None`), it is passed
        through unchanged to `accept_upload`, which resolves the default
        (`bradyforge.config.UPLOADS_PATH`) itself.
        """
        if "," in base64_content:
            _, _, base64_content = base64_content.partition(",")
        raw_bytes = base64.b64decode(base64_content)

        temp_dir = tempfile.mkdtemp()
        try:
            temp_path = os.path.join(temp_dir, filename)
            with open(temp_path, "wb") as f:
                f.write(raw_bytes)
            return self.accept_upload(temp_path, destination_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def submit_generic_labels(self, rows, filename, destination_dir=None):
        """Write generic label `rows` to a new workbook in `destination_dir`.

        Mirrors `accept_upload`'s pattern: resolves a collision-safe
        destination filename via `resolve_upload_filename`, then writes the
        workbook via `write_generic_workbook`, returning
        `{"ok": True, "saved_path": ..., "filename": ...}`.

        An empty `rows` list is treated as an expected failure and returned
        as `{"ok": False, "error": <message>}` rather than raised, since the
        future JS bridge can't catch raised Python exceptions. Any other
        unexpected exception propagates normally.

        If `destination_dir` turns out to be unreachable (e.g. an offline
        network share), the collision-resolve + write attempt raises
        `OSError`/`PermissionError`. That is caught here and treated as a
        fallback case, mirroring `accept_upload`: the generated workbook's
        bytes are saved locally and zipped via
        `bradyforge.fallback_saver.save_local_and_zip` (into
        `self.fallback_dir`), and the result reflects the fallback with
        `{"ok": True, "fallback": True, "local_path": ..., "zip_path": ...,
        "message": ...}`.

        `destination_dir` is optional; when omitted (or `None`), it defaults
        to `bradyforge.config.UPLOADS_PATH`, so callers don't need to know or
        pass the real uploads location.
        """
        destination_dir = (
            destination_dir if destination_dir is not None else config.UPLOADS_PATH
        )

        if not rows:
            return {"ok": False, "error": "No label rows provided."}

        buffer = io.BytesIO()
        write_generic_workbook(rows, buffer)
        source_bytes = buffer.getvalue()

        try:
            resolved_filename = resolve_upload_filename(destination_dir, filename)
            saved_path = os.path.join(destination_dir, resolved_filename)
            with open(saved_path, "wb") as f:
                f.write(source_bytes)
        except (OSError, PermissionError):
            fallback_result = save_local_and_zip(
                source_bytes, filename, self.fallback_dir
            )
            return {
                "ok": True,
                "fallback": True,
                "local_path": fallback_result.local_path,
                "zip_path": fallback_result.zip_path,
                "message": fallback_result.message,
            }

        return {
            "ok": True,
            "saved_path": str(saved_path),
            "filename": resolved_filename,
        }

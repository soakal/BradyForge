"""JS-bridge API surface for BradyForge.

The `Api` class defined here is the object that will eventually be
handed to `webview.create_window(..., js_api=api_instance)` (or exposed
via `window.expose()`) so the JS front end can call plain Python
methods. This module intentionally never imports `webview`: `Api` is
plain Python and every method must be directly unit-testable as a
normal method call, without a live webview.
"""

import base64
import binascii
import io
import os
import shutil
import tempfile
from pathlib import Path

from bradyforge.fallback_saver import save_local_and_zip
from bradyforge.filename_util import resolve_upload_filename, sanitize_filename
from bradyforge.generic_writer import write_generic_workbook
from bradyforge.label_images import list_label_images
from bradyforge.settings import load_settings, save_settings
from bradyforge.size_validator import FileTooLargeError, validate_upload_size
from bradyforge.xlsx_validator import InvalidXlsxError, validate_xlsx_file

# Extension -> MIME type map used by `Api.get_label_images` to build data
# URLs. Kept in sync with `bradyforge.label_images.IMAGE_EXTENSIONS`.
_LABEL_IMAGE_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
}

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
        dict rather than a raw echo of their input. If `data` is not a
        dict (malformed input from the JS bridge), nothing is written and
        the current settings are returned unchanged.
        """
        if isinstance(data, dict):
            save_settings(data, self.settings_path)
        return self.get_settings()

    def _uploads_dir(self):
        """Resolve the effective uploads directory from saved settings.

        `load_settings` already falls back to the confirmed
        `bradyforge.config` defaults for missing/empty values, so this
        always returns a usable path string. This is what makes the
        Settings screen's "Uploads Folder Path" actually take effect.
        """
        return load_settings(self.settings_path)["uploads_path"]

    def _label_images_dir(self):
        """Resolve the effective label-images directory from saved settings."""
        return load_settings(self.settings_path)["label_images_path"]

    def _save_bytes_to_destination(self, destination_dir, filename, source_bytes):
        """Write `source_bytes` into `destination_dir` without overwriting.

        Resolves a collision-safe name via `resolve_upload_filename`, then
        opens the destination with exclusive-create (`"xb"`) so that even
        if another user on another machine wins a race for the same
        resolved name between the existence check and the write, this
        write fails with `FileExistsError` instead of silently clobbering
        their file — in which case the name is re-resolved and retried a
        few times. Returns `(resolved_filename, saved_path)`. Any genuine
        unreachability error (`OSError`/`PermissionError`) propagates for
        the caller's fallback handling.
        """
        last_error = None
        for _ in range(5):
            resolved = resolve_upload_filename(destination_dir, filename)
            saved_path = os.path.join(destination_dir, resolved)
            try:
                with open(saved_path, "xb") as f:
                    f.write(source_bytes)
                return resolved, saved_path
            except FileExistsError as exc:
                last_error = exc
        raise last_error

    def accept_upload(self, source_path, destination_dir=None):
        """Validate and copy an uploaded workbook into `destination_dir`.

        Runs `source_path` through `validate_xlsx_file` (genuine, non-corrupted
        .xlsx) and `validate_upload_size` (within the configured size limit).
        On success, resolves a collision-safe destination filename and
        writes the file's bytes with an exclusive-create open (see
        `_save_bytes_to_destination`), returning
        `{"ok": True, "saved_path": ..., "filename": ...}`.

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
        to the saved settings' `uploads_path` (which itself falls back to
        `bradyforge.config.UPLOADS_PATH`), so callers don't need to know or
        pass the real uploads location and edits made on the Settings
        screen take effect immediately.
        """
        if destination_dir is None:
            destination_dir = self._uploads_dir()

        try:
            validate_xlsx_file(source_path)
            validate_upload_size(source_path)
        except (InvalidXlsxError, FileTooLargeError) as exc:
            return {"ok": False, "error": str(exc)}

        source_bytes = Path(source_path).read_bytes()
        original_filename = os.path.basename(source_path)

        try:
            filename, saved_path = self._save_bytes_to_destination(
                destination_dir, original_filename, source_bytes
            )
        except (OSError, PermissionError):
            fallback_result = save_local_and_zip(
                source_bytes, original_filename, self.fallback_dir
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

        `filename` and `base64_content` are untrusted JS-bridge input:
        the filename is reduced to a safe basename via `sanitize_filename`
        (rejecting path traversal, forbidden Windows characters, and
        empty names), and a base64 payload that cannot be decoded is
        reported as `{"ok": False, "error": ...}` rather than raised.

        `destination_dir` is optional; when omitted (or `None`), it is passed
        through unchanged to `accept_upload`, which resolves the default
        (saved settings `uploads_path`, falling back to
        `bradyforge.config.UPLOADS_PATH`) itself.
        """
        safe_filename = sanitize_filename(filename)
        if safe_filename is None:
            return {
                "ok": False,
                "error": "Invalid filename: it must be a plain name without "
                'path separators or the characters < > : " | ? *.',
            }

        if not isinstance(base64_content, str):
            return {"ok": False, "error": "Invalid file content."}
        if "," in base64_content:
            _, _, base64_content = base64_content.partition(",")
        try:
            raw_bytes = base64.b64decode(base64_content)
        except (binascii.Error, ValueError):
            return {
                "ok": False,
                "error": "The uploaded file content could not be decoded.",
            }

        temp_dir = tempfile.mkdtemp()
        try:
            temp_path = os.path.join(temp_dir, safe_filename)
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

        `rows` and `filename` are untrusted JS-bridge input: the filename
        is reduced to a safe basename via `sanitize_filename` (rejecting
        path traversal, forbidden Windows characters, and empty names),
        and structurally malformed rows are reported as
        `{"ok": False, "error": ...}` rather than raised.

        `destination_dir` is optional; when omitted (or `None`), it defaults
        to the saved settings' `uploads_path` (which itself falls back to
        `bradyforge.config.UPLOADS_PATH`), so callers don't need to know or
        pass the real uploads location and edits made on the Settings
        screen take effect immediately.
        """
        if destination_dir is None:
            destination_dir = self._uploads_dir()

        if not rows:
            return {"ok": False, "error": "No label rows provided."}

        safe_filename = sanitize_filename(filename)
        if safe_filename is None:
            return {
                "ok": False,
                "error": "Invalid filename: it must be a plain name without "
                'path separators or the characters < > : " | ? *.',
            }

        buffer = io.BytesIO()
        try:
            write_generic_workbook(rows, buffer)
        except (KeyError, TypeError, AttributeError):
            return {
                "ok": False,
                "error": "Malformed label rows: each row must provide "
                "line1, line2, line3, and qty.",
            }
        source_bytes = buffer.getvalue()

        try:
            resolved_filename, saved_path = self._save_bytes_to_destination(
                destination_dir, safe_filename, source_bytes
            )
        except (OSError, PermissionError):
            fallback_result = save_local_and_zip(
                source_bytes, safe_filename, self.fallback_dir
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

    def get_label_images(self, images_dir=None):
        """Return renderable label images found in `images_dir`.

        Delegates filename discovery to
        `bradyforge.label_images.list_label_images`, then reads and
        base64-encodes each file's bytes into a `data:` URL suitable for
        direct use as an `<img>` `src` in the JS front end. Returns a list
        of `{"filename": ..., "data_url": ...}` dicts, in the same
        (sorted) order `list_label_images` returned.

        If an individual file can't be read (e.g. it disappears or
        becomes unreadable between listing and reading), it is silently
        skipped rather than aborting the whole listing.

        `images_dir` is optional; when omitted (or `None`), it defaults to
        the saved settings' `label_images_path` (which itself falls back
        to `bradyforge.config.LABEL_IMAGES_PATH`), so callers don't need
        to know or pass the real label-images location and edits made on
        the Settings screen take effect immediately.
        """
        if images_dir is None:
            images_dir = self._label_images_dir()

        results = []
        for filename in list_label_images(images_dir):
            full_path = os.path.join(images_dir, filename)
            _, extension = os.path.splitext(filename)
            mime = _LABEL_IMAGE_MIME_TYPES.get(
                extension.lower(), "application/octet-stream"
            )
            try:
                with open(full_path, "rb") as f:
                    raw_bytes = f.read()
            except OSError:
                continue
            encoded = base64.b64encode(raw_bytes).decode("ascii")
            data_url = f"data:{mime};base64,{encoded}"
            results.append({"filename": filename, "data_url": data_url})

        return results

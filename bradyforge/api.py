"""JS-bridge API surface for BradyForge.

The `Api` class defined here is the object that will eventually be
handed to `webview.create_window(..., js_api=api_instance)` (or exposed
via `window.expose()`) so the JS front end can call plain Python
methods. This module intentionally never imports `webview`: `Api` is
plain Python and every method must be directly unit-testable as a
normal method call, without a live webview.
"""

from pathlib import Path

from bradyforge.settings import load_settings, save_settings

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

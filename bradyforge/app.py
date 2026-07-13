"""PyWebView entry point for BradyForge.

This module wires together the desktop window and the static HTML/CSS
front end under ``bradyforge/webui/``. ``webview`` is imported lazily
inside ``create_window()`` (not at module import time) so this module —
and the rest of the app/test suite — can be imported in environments
where the ``pywebview`` package is not installed (e.g. this dev/CI
environment, where it is only listed in requirements.txt for eventual
packaging).

This module does not start the webview event loop; that is left to
``run()`` / the ``__main__`` block below (used by the PyInstaller-built
executable), which calls ``create_window()`` then ``webview.start()``.
"""

import sys
from pathlib import Path

from bradyforge.api import Api


def _resolve_webui_dir():
    """Return the directory containing the static webui assets.

    When running as a PyInstaller-frozen executable, the webui assets
    are bundled into ``sys._MEIPASS`` (the temp extraction dir
    PyInstaller sets at runtime) under a ``webui`` folder. Otherwise
    (normal dev/test execution), resolve the path relative to this
    package directory, as before.
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "webui"
    return Path(__file__).resolve().parent / "webui"


# Path to the static HTML shell loaded by the webview window.
HTML_PATH = _resolve_webui_dir() / "index.html"


def create_window():
    """Construct (but do not start) the PyWebView window.

    Imports ``webview`` lazily so importing this module never requires
    ``pywebview`` to be installed. Returns the created window object;
    callers are responsible for calling ``webview.start()`` themselves.
    """
    import webview

    api = Api()
    return webview.create_window("BradyForge", url=str(HTML_PATH), js_api=api)


def run():
    """Create the window and start the webview event loop.

    This is the entry point used by the PyInstaller-built executable
    (see ``BradyForge.spec``). It is never exercised by the test suite,
    since no display/webview is available in this environment.
    """
    import webview

    create_window()
    webview.start()


if __name__ == "__main__":
    run()

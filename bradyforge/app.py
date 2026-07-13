"""PyWebView entry point for BradyForge.

This module wires together the desktop window and the static HTML/CSS
front end under ``bradyforge/webui/``. ``webview`` is imported lazily
inside ``create_window()`` (not at module import time) so this module —
and the rest of the app/test suite — can be imported in environments
where the ``pywebview`` package is not installed (e.g. this dev/CI
environment, where it is only listed in requirements.txt for eventual
packaging).

This module does not start the webview event loop; that is left to a
future entry point (e.g. a ``__main__`` block or PyInstaller launcher)
once the UI has more than a static shell.
"""

from pathlib import Path

# Path to the static HTML shell loaded by the webview window.
HTML_PATH = Path(__file__).resolve().parent / "webui" / "index.html"


def create_window():
    """Construct (but do not start) the PyWebView window.

    Imports ``webview`` lazily so importing this module never requires
    ``pywebview`` to be installed. Returns the created window object;
    callers are responsible for calling ``webview.start()`` themselves.
    """
    import webview

    return webview.create_window("BradyForge", url=str(HTML_PATH))

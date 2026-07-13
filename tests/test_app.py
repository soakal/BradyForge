import sys

import bradyforge.app as app


def test_import_does_not_require_webview():
    # Importing bradyforge.app must succeed even though pywebview is not
    # installed in this environment; webview must only be imported lazily
    # inside create_window(), never at module import time.
    assert "webview" not in sys.modules


def test_html_path_exists():
    assert app.HTML_PATH.is_file()


def test_html_contains_expected_tab_ids():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    assert 'id="tab-generic"' in content
    assert 'id="tab-upload"' in content

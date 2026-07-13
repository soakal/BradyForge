import re
import sys
from unittest.mock import MagicMock

import bradyforge.app as app
from bradyforge.api import Api


def test_import_does_not_require_webview():
    # Importing bradyforge.app must succeed even though pywebview is not
    # installed in this environment; webview must only be imported lazily
    # inside create_window(), never at module import time.
    assert "webview" not in sys.modules


def test_create_window_passes_api_as_js_api(monkeypatch):
    sentinel = object()
    fake_webview = MagicMock()
    fake_webview.create_window.return_value = sentinel
    monkeypatch.setitem(sys.modules, "webview", fake_webview)

    result = app.create_window()

    fake_webview.create_window.assert_called_once()
    _, kwargs = fake_webview.create_window.call_args
    assert kwargs["url"] == str(app.HTML_PATH)
    assert isinstance(kwargs["js_api"], Api)
    assert result is sentinel


def test_html_path_exists():
    assert app.HTML_PATH.is_file()


def test_html_contains_expected_tab_ids():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    assert 'id="tab-generic"' in content
    assert 'id="tab-upload"' in content
    assert 'id="tab-settings"' in content


def _extract_panel(content, panel_id):
    """Return the inner HTML of a `<div id="{panel_id}" ...>...</div>` block.

    Simple depth-aware scan good enough for this static, hand-authored
    markup (no nested `<div>` parsing library required).
    """
    marker = re.search(r'<div id="%s"[^>]*>' % re.escape(panel_id), content)
    assert marker, f"panel {panel_id!r} not found"
    start = marker.end()
    depth = 1
    pos = start
    for m in re.finditer(r"<div[^>]*>|</div>", content[start:]):
        if m.group(0).startswith("</div"):
            depth -= 1
        else:
            depth += 1
        if depth == 0:
            pos = start + m.start()
            break
    return content[start:pos]


def test_generic_panel_contains_expected_field_ids():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_generic = _extract_panel(content, "panel-generic")
    panel_upload = _extract_panel(content, "panel-upload")

    expected_ids = [
        "name",
        "department",
        "line1",
        "line2",
        "line3",
        "quantity",
        "label-picker",
        "save-generic-btn",
    ]
    for field_id in expected_ids:
        needle = f'id="{field_id}"'
        assert needle in panel_generic, f"{needle} missing from #panel-generic"
        assert needle not in panel_upload, f"{needle} unexpectedly found in #panel-upload"


def test_generic_panel_required_fields():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_generic = _extract_panel(content, "panel-generic")
    name_tag = re.search(r'<input[^>]*id="name"[^>]*>', panel_generic)
    department_tag = re.search(r'<input[^>]*id="department"[^>]*>', panel_generic)
    assert name_tag and "required" in name_tag.group(0)
    assert department_tag and "required" in department_tag.group(0)


def test_generic_panel_quantity_is_number_input():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_generic = _extract_panel(content, "panel-generic")
    quantity_tag = re.search(r'<input[^>]*id="quantity"[^>]*>', panel_generic)
    assert quantity_tag and 'type="number"' in quantity_tag.group(0)


def test_generic_panel_has_no_script_tags():
    # This cycle only adds static markup — JS wiring is a future step.
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_generic = _extract_panel(content, "panel-generic")
    assert "<script" not in panel_generic


def test_upload_panel_contains_expected_field_ids():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_generic = _extract_panel(content, "panel-generic")
    panel_upload = _extract_panel(content, "panel-upload")

    expected_ids = [
        "upload-dropzone",
        "file-input",
        "upload-name",
        "upload-department",
        "save-upload-btn",
    ]
    for field_id in expected_ids:
        needle = f'id="{field_id}"'
        assert needle in panel_upload, f"{needle} missing from #panel-upload"
        assert needle not in panel_generic, f"{needle} unexpectedly found in #panel-generic"


def test_upload_panel_required_fields():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_upload = _extract_panel(content, "panel-upload")
    name_tag = re.search(r'<input[^>]*id="upload-name"[^>]*>', panel_upload)
    department_tag = re.search(r'<input[^>]*id="upload-department"[^>]*>', panel_upload)
    assert name_tag and "required" in name_tag.group(0)
    assert department_tag and "required" in department_tag.group(0)


def test_upload_panel_file_input_accepts_xlsx():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_upload = _extract_panel(content, "panel-upload")
    file_input_tag = re.search(r'<input[^>]*id="file-input"[^>]*>', panel_upload)
    assert file_input_tag and 'type="file"' in file_input_tag.group(0)
    assert file_input_tag and 'accept=".xlsx"' in file_input_tag.group(0)


def test_upload_panel_has_no_script_tags():
    # This cycle only adds static markup — JS wiring is a future step.
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_upload = _extract_panel(content, "panel-upload")
    assert "<script" not in panel_upload


def test_index_html_has_exactly_one_external_app_js_script_tag():
    # Tab-switching JS is wired in via a single external <script src="app.js">
    # tag; no inline <script>...</script> blocks with embedded JS.
    content = app.HTML_PATH.read_text(encoding="utf-8")
    script_blocks = re.findall(r"<script\b([^>]*)>(.*?)</script>", content, re.DOTALL)
    assert len(script_blocks) == 1, f"expected exactly one <script> tag, found {script_blocks!r}"
    attrs, inline_js = script_blocks[0]
    assert 'src="app.js"' in attrs
    assert inline_js.strip() == "", "app.js content must live in the external file, not inline"


def test_app_js_script_tag_appears_after_all_panels():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    script_pos = content.index('<script src="app.js"')
    for panel_id in ("panel-generic", "panel-upload", "panel-settings"):
        panel_content = _extract_panel(content, panel_id)
        panel_end = content.index(panel_content) + len(panel_content)
        assert script_pos > panel_end, f"script tag must appear after #{panel_id}"


def test_settings_panel_contains_expected_field_ids():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_generic = _extract_panel(content, "panel-generic")
    panel_upload = _extract_panel(content, "panel-upload")
    panel_settings = _extract_panel(content, "panel-settings")

    expected_ids = [
        "uploads-path",
        "label-images-path",
        "fallback-email",
        "save-settings-btn",
    ]
    for field_id in expected_ids:
        needle = f'id="{field_id}"'
        assert needle in panel_settings, f"{needle} missing from #panel-settings"
        assert needle not in panel_generic, f"{needle} unexpectedly found in #panel-generic"
        assert needle not in panel_upload, f"{needle} unexpectedly found in #panel-upload"


def test_settings_panel_fallback_email_is_email_input():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_settings = _extract_panel(content, "panel-settings")
    fallback_email_tag = re.search(r'<input[^>]*id="fallback-email"[^>]*>', panel_settings)
    assert fallback_email_tag and 'type="email"' in fallback_email_tag.group(0)


def test_settings_panel_has_no_script_tags():
    # This cycle only adds static markup — JS wiring is a future step.
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_settings = _extract_panel(content, "panel-settings")
    assert "<script" not in panel_settings


APP_JS_PATH = app.HTML_PATH.parent / "app.js"


def test_app_js_exists():
    assert APP_JS_PATH.is_file()


def test_app_js_references_all_tab_and_panel_ids():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    for tab_id in ("tab-generic", "tab-upload", "tab-settings"):
        assert tab_id in content, f"{tab_id!r} missing from app.js"
    for panel_id in ("panel-generic", "panel-upload", "panel-settings"):
        assert panel_id in content, f"{panel_id!r} missing from app.js"


def test_app_js_has_no_pywebview_api_calls():
    # Wiring window.pywebview.api is out of scope for this cycle.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    assert "window.pywebview" not in content
    assert ".api." not in content


def test_app_js_has_balanced_braces():
    # Not a full JS parser — just a quick sanity heuristic against
    # obvious syntax errors.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    assert content.count("{") == content.count("}")
    assert content.count("(") == content.count(")")

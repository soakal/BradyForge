import re
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


def test_index_html_has_no_script_tags_anywhere():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    assert "<script" not in content

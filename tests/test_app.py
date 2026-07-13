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


def test_app_js_calls_settings_api_methods():
    # Settings load/save is wired to window.pywebview.api this cycle.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    assert "window.pywebview.api.get_settings" in content
    assert "window.pywebview.api.save_settings" in content


def test_app_js_references_settings_dict_keys():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    for key in ("uploads_path", "label_images_path", "fallback_email"):
        assert key in content, f"{key!r} missing from app.js"


def test_app_js_references_settings_dom_ids():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    for field_id in (
        "uploads-path",
        "label-images-path",
        "fallback-email",
        "save-settings-btn",
    ):
        assert field_id in content, f"{field_id!r} missing from app.js"


def test_settings_panel_has_status_element():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_settings = _extract_panel(content, "panel-settings")
    assert 'id="settings-status"' in panel_settings


def test_app_js_has_balanced_braces():
    # Not a full JS parser — just a quick sanity heuristic against
    # obvious syntax errors.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    assert content.count("{") == content.count("}")
    assert content.count("(") == content.count(")")


def test_upload_panel_has_status_element():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_upload = _extract_panel(content, "panel-upload")
    assert 'id="upload-status"' in panel_upload


def test_app_js_references_upload_dom_ids():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    for field_id in (
        "upload-dropzone",
        "file-input",
        "upload-name",
        "upload-department",
        "save-upload-btn",
        "upload-status",
    ):
        assert field_id in content, f"{field_id!r} missing from app.js"


def test_app_js_wires_dropzone_click_and_drag_events():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    assert '"drop"' in content
    assert '"dragover"' in content
    assert '"dragleave"' in content
    assert '"change"' in content


def test_app_js_checks_xlsx_extension_case_insensitively():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    assert re.search(r"\.xlsx", content, re.IGNORECASE)
    # The extension check itself must be case-insensitive (e.g. a regex
    # with the /i flag, or an equivalent .toLowerCase() comparison).
    assert re.search(r"xlsx\$/i", content) or "toLowerCase" in content


def test_app_js_enforces_25mb_size_limit():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    assert "26214400" in content or "25 * 1024 * 1024" in content


def _extract_upload_wiring_section(content):
    """Return the app.js slice that wires up the Upload panel.

    Bounded by the "Upload panel" comment marker (start of this cycle's
    additions) and the `loadSettings` function definition (start of the
    pre-existing Settings wiring), so we can assert this cycle's new code
    doesn't sneak in an Api call without being thrown off by the
    already-legitimate `window.pywebview.api.*` calls used by Settings.
    """
    start = content.index("// Upload panel — client-side")
    end = content.index("function loadSettings")
    assert end > start
    return content[start:end]


def test_app_js_upload_wiring_calls_accept_upload_bytes():
    # The Upload panel's Save button now calls the backend via
    # accept_upload_bytes, reading the selected file as a data URL and
    # branching on the result's ok/fallback flags.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    upload_section = _extract_upload_wiring_section(content)
    assert "accept_upload_bytes(" in upload_section
    assert "readAsDataURL(" in upload_section
    assert "FileReader" in upload_section
    assert ".ok" in upload_section
    assert ".fallback" in upload_section
    assert "pywebview" in upload_section


def test_app_js_upload_placeholder_message_removed():
    # The old "connecting to backend in a future step" placeholder must be
    # gone now that the upload actually calls the backend.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    assert "connecting to backend in a future step" not in content


def test_generic_panel_has_status_element():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    panel_generic = _extract_panel(content, "panel-generic")
    assert 'id="generic-status"' in panel_generic


def _extract_generic_wiring_section(content):
    """Return the app.js slice that wires up the Generic Form panel.

    Bounded by the "Generic Form panel" comment marker (start of this
    cycle's additions) and the "Upload panel" comment marker (start of
    the pre-existing Upload wiring), so assertions on `.ok`/`.fallback`
    branching land on the Generic Form's own handler rather than the
    Upload panel's already-legitimate `window.pywebview.api.*` calls.
    """
    start = content.index("// Generic Form panel")
    end = content.index("// Upload panel — client-side")
    assert end > start
    return content[start:end]


def test_app_js_generic_wiring_calls_submit_generic_labels():
    # The Generic Form panel's Save button calls the backend via
    # submit_generic_labels, prompting for a filename and branching on
    # the result's ok/fallback flags.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    generic_section = _extract_generic_wiring_section(content)
    assert "submit_generic_labels(" in generic_section
    assert "window.prompt(" in generic_section
    assert ".ok" in generic_section
    assert ".fallback" in generic_section
    assert "pywebview" in generic_section


def test_app_js_generic_wiring_references_field_ids():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    generic_section = _extract_generic_wiring_section(content)
    for field_id in ("name", "department", "line1", "line2", "line3", "quantity"):
        assert field_id in generic_section, f"{field_id!r} missing from generic wiring section"


def test_app_js_generic_wiring_auto_appends_xlsx_extension():
    # If the user's typed filename doesn't already end in .xlsx, the
    # Save flow must append it automatically before calling the backend.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    generic_section = _extract_generic_wiring_section(content)
    assert re.search(r"\\\.xlsx\$", generic_section, re.IGNORECASE)
    assert '+= ".xlsx"' in generic_section or '+ ".xlsx"' in generic_section


def _extract_label_picker_wiring_section(content):
    """Return the app.js slice that wires up the live label-image picker.

    Bounded by the "Label picker" comment marker (start of this cycle's
    additions) and the `loadSettings` function definition (start of the
    pre-existing Settings wiring), mirroring the boundary convention used
    by `_extract_upload_wiring_section`.
    """
    start = content.index("// Label picker")
    end = content.index("function loadSettings")
    assert end > start
    return content[start:end]


def test_app_js_label_picker_calls_get_label_images():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    label_picker_section = _extract_label_picker_wiring_section(content)
    assert "get_label_images(" in label_picker_section
    assert "label-picker" in label_picker_section
    assert "pywebview" in label_picker_section


def test_app_js_label_picker_has_selection_toggle():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    label_picker_section = _extract_label_picker_wiring_section(content)
    assert "is-selected" in label_picker_section


def test_app_js_label_picker_has_no_images_fallback_message():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    label_picker_section = _extract_label_picker_wiring_section(content)
    assert "No label images found." in label_picker_section


def test_app_js_label_picker_has_error_fallback_message():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    label_picker_section = _extract_label_picker_wiring_section(content)
    assert "Could not load label images." in label_picker_section


def test_resolve_webui_dir_uses_meipass_when_frozen(monkeypatch, tmp_path):
    # When running as a PyInstaller-frozen executable, the webui assets
    # must be resolved from sys._MEIPASS (the temp extraction dir
    # PyInstaller sets at runtime), not the source tree.
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    result = app._resolve_webui_dir()

    assert result == tmp_path / "webui"


def test_resolve_webui_dir_uses_package_dir_when_not_frozen():
    # Existing (non-frozen) behavior must be unchanged: resolved relative
    # to the bradyforge package directory.
    assert app._resolve_webui_dir() == app.HTML_PATH.parent
    assert not getattr(sys, "frozen", False)


def test_app_js_calls_load_label_images_alongside_load_settings():
    # loadLabelImages() must be invoked in the same page-load
    # initialization context as loadSettings() (i.e. inside the
    # DOMContentLoaded listener, near its final loadSettings() call).
    content = APP_JS_PATH.read_text(encoding="utf-8")
    tail = content[content.rindex("function loadSettings") :]
    assert "loadLabelImages();" in tail
    assert "loadSettings();" in tail


def test_app_js_retries_api_dependent_features_on_pywebviewready():
    # window.pywebview.api is injected asynchronously by pywebview and
    # may not exist yet at DOMContentLoaded; loadLabelImages()/
    # loadSettings() must also be wired to fire on pywebview's own
    # "ready" event so they aren't silently skipped if the api becomes
    # available after DOMContentLoaded already ran.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    tail = content[content.rindex("function loadSettings") :]
    assert "pywebviewready" in tail
    assert "addEventListener" in tail


STYLES_CSS_PATH = app.HTML_PATH.parent / "styles.css"


def test_app_js_init_guard_prevents_double_initialization():
    # If the api is already present at DOMContentLoaded AND the
    # pywebviewready event fires afterward, the api-dependent init must
    # only run once (a second run would clobber in-progress Settings
    # edits and drop the label-tile selection).
    content = APP_JS_PATH.read_text(encoding="utf-8")
    tail = content[content.rindex("function loadSettings") :]
    assert "apiFeaturesInitialized" in tail


def test_app_js_prevents_document_level_drop_navigation():
    # Dropping a file outside the dropzone must not navigate the webview
    # away from the app (the browser default for file drops).
    content = APP_JS_PATH.read_text(encoding="utf-8")
    head = content[: content.index("// Generic Form panel")]
    assert '"drop"' in head
    assert '"dragover"' in head
    assert "preventDefault" in head


def test_app_js_validates_quantity_as_whole_number():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    generic_section = _extract_generic_wiring_section(content)
    assert "Quantity must be a whole number." in generic_section


def test_app_js_upload_captures_file_before_async_read():
    # The file reference must be captured into a local before the
    # asynchronous FileReader/upload starts, so changing the selection
    # mid-upload can't swap the filename or null the reference.
    content = APP_JS_PATH.read_text(encoding="utf-8")
    upload_section = _extract_upload_wiring_section(content)
    assert "fileToUpload = selectedUploadFile" in upload_section
    assert "readAsDataURL(fileToUpload)" in upload_section


def test_app_js_disables_buttons_while_submission_in_flight():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    generic_section = _extract_generic_wiring_section(content)
    upload_section = _extract_upload_wiring_section(content)
    assert "saveGenericBtn.disabled = true" in generic_section
    assert "saveUploadBtn.disabled = true" in upload_section


def test_html_dropzone_is_keyboard_accessible():
    content = app.HTML_PATH.read_text(encoding="utf-8")
    dropzone_tag = re.search(r'<div[^>]*id="upload-dropzone"[^>]*>', content)
    assert dropzone_tag
    assert 'tabindex="0"' in dropzone_tag.group(0)
    assert 'role="button"' in dropzone_tag.group(0)
    # And app.js must open the file picker on keyboard activation.
    js = APP_JS_PATH.read_text(encoding="utf-8")
    assert '"keydown"' in js


def test_app_js_label_tiles_are_buttons():
    content = APP_JS_PATH.read_text(encoding="utf-8")
    label_picker_section = _extract_label_picker_wiring_section(content)
    assert 'createElement("button")' in label_picker_section
    assert "aria-pressed" in label_picker_section


def test_styles_css_defines_error_status_styling():
    # app.js toggles the `is-error` class on the status areas; the CSS
    # must actually style it so error messages are distinguishable.
    css = STYLES_CSS_PATH.read_text(encoding="utf-8")
    assert ".is-error" in css
    assert "--color-error" in css

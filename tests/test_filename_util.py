from datetime import datetime

from bradyforge.filename_util import resolve_upload_filename

FIXED_NOW = datetime(2026, 7, 13, 14, 5, 1)


def test_returns_original_filename_when_no_collision(tmp_path):
    result = resolve_upload_filename(str(tmp_path), "report.xlsx", now=FIXED_NOW)

    assert result == "report.xlsx"


def test_appends_timestamp_before_extension_on_collision(tmp_path):
    filename = "report.xlsx"
    (tmp_path / filename).write_text("existing upload")

    result = resolve_upload_filename(str(tmp_path), filename, now=FIXED_NOW)

    assert result == "report_20260713_140501.xlsx"
    assert not (tmp_path / result).exists()


def test_multi_dot_filename_splits_extension_correctly_on_collision(tmp_path):
    filename = "report.v2.xlsx"
    (tmp_path / filename).write_text("existing upload")

    result = resolve_upload_filename(str(tmp_path), filename, now=FIXED_NOW)

    assert result == "report.v2_20260713_140501.xlsx"
    assert not (tmp_path / result).exists()


def test_same_second_double_collision_appends_counter(tmp_path):
    # Two submissions of the same filename within the same second: the
    # timestamped name already exists, so a numeric suffix must be added
    # rather than silently reusing (and overwriting) the same name.
    filename = "report.xlsx"
    (tmp_path / filename).write_text("existing upload")
    (tmp_path / "report_20260713_140501.xlsx").write_text("first same-second upload")

    result = resolve_upload_filename(str(tmp_path), filename, now=FIXED_NOW)

    assert result == "report_20260713_140501_2.xlsx"
    assert not (tmp_path / result).exists()


def test_same_second_triple_collision_increments_counter(tmp_path):
    filename = "report.xlsx"
    (tmp_path / filename).write_text("existing upload")
    (tmp_path / "report_20260713_140501.xlsx").write_text("second")
    (tmp_path / "report_20260713_140501_2.xlsx").write_text("third")

    result = resolve_upload_filename(str(tmp_path), filename, now=FIXED_NOW)

    assert result == "report_20260713_140501_3.xlsx"
    assert not (tmp_path / result).exists()


def test_sanitize_filename_keeps_plain_names():
    from bradyforge.filename_util import sanitize_filename

    assert sanitize_filename("report.xlsx") == "report.xlsx"
    assert sanitize_filename("  report.xlsx  ") == "report.xlsx"
    assert sanitize_filename("étiquette 標籤.xlsx") == "étiquette 標籤.xlsx"


def test_sanitize_filename_strips_directory_components():
    from bradyforge.filename_util import sanitize_filename

    assert sanitize_filename(r"..\..\evil.xlsx") == "evil.xlsx"
    assert sanitize_filename("../../evil.xlsx") == "evil.xlsx"
    assert sanitize_filename(r"C:\Users\x\evil.xlsx") == "evil.xlsx"
    assert sanitize_filename("/tmp/evil.xlsx") == "evil.xlsx"


def test_sanitize_filename_rejects_unusable_names():
    from bradyforge.filename_util import sanitize_filename

    assert sanitize_filename("") is None
    assert sanitize_filename("   ") is None
    assert sanitize_filename(".") is None
    assert sanitize_filename("..") is None
    assert sanitize_filename("...") is None
    assert sanitize_filename(None) is None
    assert sanitize_filename(42) is None
    assert sanitize_filename('bad:"name?.xlsx') is None
    assert sanitize_filename("bad<name>.xlsx") is None
    assert sanitize_filename("bad|name.xlsx") is None
    assert sanitize_filename("bad\x00name.xlsx") is None


def test_sanitize_filename_trims_trailing_dots_and_spaces():
    from bradyforge.filename_util import sanitize_filename

    assert sanitize_filename("report.xlsx. ") == "report.xlsx"

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

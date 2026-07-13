from pathlib import Path

import pytest

from bradyforge.xlsx_validator import InvalidXlsxError, validate_xlsx_file

SAMPLE_MULTI_TAB_PATH = (
    Path(__file__).resolve().parent.parent
    / "samples"
    / "Sample Completed Multi-Tab File.xlsx"
)


def test_genuine_sample_file_is_valid():
    assert validate_xlsx_file(SAMPLE_MULTI_TAB_PATH) is True


def test_nonexistent_path_raises(tmp_path):
    missing_path = tmp_path / "does-not-exist.xlsx"

    with pytest.raises(InvalidXlsxError):
        validate_xlsx_file(missing_path)


def test_non_xlsx_text_file_raises(tmp_path):
    fake_path = tmp_path / "not-really-xlsx.xlsx"
    fake_path.write_text("this is plain text, not a zip/xlsx file")

    with pytest.raises(InvalidXlsxError):
        validate_xlsx_file(fake_path)


def test_truncated_xlsx_bytes_raise(tmp_path):
    truncated_path = tmp_path / "truncated.xlsx"
    with open(SAMPLE_MULTI_TAB_PATH, "rb") as source:
        original_bytes = source.read()
    truncated_path.write_bytes(original_bytes[: len(original_bytes) // 2])

    with pytest.raises(InvalidXlsxError):
        validate_xlsx_file(truncated_path)

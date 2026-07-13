import zipfile

from bradyforge.fallback_saver import FallbackSaveResult, save_local_and_zip


def test_saves_local_file_with_correct_content(tmp_path):
    content = b"workbook bytes go here"

    result = save_local_and_zip(content, "report.xlsx", tmp_path)

    assert result.local_path == str(tmp_path / "report.xlsx")
    with open(result.local_path, "rb") as f:
        assert f.read() == content


def test_creates_valid_zip_containing_matching_content(tmp_path):
    content = b"another workbook's bytes"

    result = save_local_and_zip(content, "data.xlsx", tmp_path)

    assert result.zip_path == str(tmp_path / "data.zip")
    with zipfile.ZipFile(result.zip_path) as zf:
        assert zf.namelist() == ["data.xlsx"]
        assert zf.read("data.xlsx") == content


def test_message_explains_unreachable_share_and_next_steps(tmp_path):
    result = save_local_and_zip(b"content", "sheet.xlsx", tmp_path)

    message_lower = result.message.lower()
    assert "unreachable" in message_lower
    assert "place" in message_lower and "share" in message_lower
    assert "email" in message_lower and "fallback contact" in message_lower


def test_returns_fallback_save_result_instance(tmp_path):
    result = save_local_and_zip(b"content", "sheet.xlsx", tmp_path)

    assert isinstance(result, FallbackSaveResult)


def test_creates_fallback_dir_if_missing(tmp_path):
    missing_dir = tmp_path / "does_not_exist_yet"

    result = save_local_and_zip(b"content", "sheet.xlsx", missing_dir)

    assert missing_dir.exists()
    assert missing_dir.is_dir()
    with open(result.local_path, "rb") as f:
        assert f.read() == b"content"

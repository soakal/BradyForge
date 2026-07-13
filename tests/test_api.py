from pathlib import Path

from bradyforge.api import Api
from bradyforge.settings import default_settings

SAMPLE_MULTI_TAB_PATH = (
    Path(__file__).resolve().parent.parent
    / "samples"
    / "Sample Completed Multi-Tab File.xlsx"
)


def test_get_settings_on_fresh_instance_returns_defaults(tmp_path):
    api = Api(settings_path=tmp_path / "settings.json")

    assert api.get_settings() == default_settings()


def test_save_settings_then_get_settings_round_trips(tmp_path):
    api = Api(settings_path=tmp_path / "settings.json")
    data = {
        "uploads_path": r"\\some-server\share\uploads",
        "label_images_path": r"\\some-server\share\images",
        "fallback_email": "someone@example.com",
    }

    api.save_settings(data)

    assert api.get_settings() == data


def test_save_settings_returns_canonical_persisted_dict(tmp_path):
    api = Api(settings_path=tmp_path / "settings.json")
    data = {
        "uploads_path": r"\\some-server\share\uploads",
        "label_images_path": r"\\some-server\share\images",
        "fallback_email": "someone@example.com",
        "extra_unknown_key": "ignored",
    }

    result = api.save_settings(data)

    assert result == api.get_settings()
    assert "extra_unknown_key" not in result


def test_accept_upload_valid_xlsx_copies_file(tmp_path):
    source_path = tmp_path / "source" / "report.xlsx"
    source_path.parent.mkdir()
    source_path.write_bytes(SAMPLE_MULTI_TAB_PATH.read_bytes())
    destination_dir = tmp_path / "destination"
    destination_dir.mkdir()

    api = Api()
    result = api.accept_upload(str(source_path), str(destination_dir))

    assert result["ok"] is True
    saved_path = Path(result["saved_path"])
    assert result["filename"] == "report.xlsx"
    assert saved_path == destination_dir / "report.xlsx"
    assert saved_path.exists()
    assert saved_path.read_bytes() == source_path.read_bytes()


def test_accept_upload_corrupted_file_returns_error_without_raising(tmp_path):
    source_path = tmp_path / "source" / "not-really.xlsx"
    source_path.parent.mkdir()
    source_path.write_text("this is plain text, not a zip/xlsx file")
    destination_dir = tmp_path / "destination"
    destination_dir.mkdir()

    api = Api()
    result = api.accept_upload(str(source_path), str(destination_dir))

    assert result["ok"] is False
    assert "error" in result
    assert list(destination_dir.iterdir()) == []


def test_accept_upload_oversized_file_returns_error_without_raising(
    tmp_path, monkeypatch
):
    monkeypatch.setattr("bradyforge.size_validator.MAX_UPLOAD_SIZE_BYTES", 1000)
    source_path = tmp_path / "source" / "report.xlsx"
    source_path.parent.mkdir()
    source_path.write_bytes(SAMPLE_MULTI_TAB_PATH.read_bytes())
    destination_dir = tmp_path / "destination"
    destination_dir.mkdir()

    api = Api()
    result = api.accept_upload(str(source_path), str(destination_dir))

    assert result["ok"] is False
    assert "error" in result
    assert list(destination_dir.iterdir()) == []


def test_accept_upload_filename_collision_gets_timestamp_suffix(tmp_path):
    source_path = tmp_path / "source" / "report.xlsx"
    source_path.parent.mkdir()
    source_path.write_bytes(SAMPLE_MULTI_TAB_PATH.read_bytes())
    destination_dir = tmp_path / "destination"
    destination_dir.mkdir()
    existing_path = destination_dir / "report.xlsx"
    existing_path.write_text("existing upload")

    api = Api()
    result = api.accept_upload(str(source_path), str(destination_dir))

    assert result["ok"] is True
    assert result["filename"] != "report.xlsx"
    assert result["filename"].startswith("report_")
    assert result["filename"].endswith(".xlsx")
    saved_path = Path(result["saved_path"])
    assert saved_path.exists()
    # The pre-existing file must not have been overwritten.
    assert existing_path.read_text() == "existing upload"

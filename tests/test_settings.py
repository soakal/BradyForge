import json

from bradyforge.config import LABEL_IMAGES_PATH, UPLOADS_PATH
from bradyforge.settings import default_settings, load_settings, save_settings


def test_default_settings_uses_config_defaults():
    defaults = default_settings()

    assert defaults["uploads_path"] == UPLOADS_PATH
    assert defaults["label_images_path"] == LABEL_IMAGES_PATH
    assert defaults["fallback_email"] == ""


def test_load_settings_on_nonexistent_path_returns_defaults(tmp_path):
    missing_path = tmp_path / "does_not_exist.json"

    assert load_settings(str(missing_path)) == default_settings()


def test_save_then_load_round_trips(tmp_path):
    settings_path = tmp_path / "settings.json"
    data = {
        "uploads_path": r"\\some-server\share\uploads",
        "label_images_path": r"\\some-server\share\images",
        "fallback_email": "someone@example.com",
    }

    save_settings(data, str(settings_path))
    loaded = load_settings(str(settings_path))

    assert loaded == data


def test_load_settings_on_corrupt_json_returns_defaults(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text("{not valid json", encoding="utf-8")

    assert load_settings(str(settings_path)) == default_settings()


def test_load_settings_merges_partial_and_ignores_unknown_keys(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        json.dumps({"fallback_email": "known@example.com", "extra_unknown_key": "ignored"}),
        encoding="utf-8",
    )

    loaded = load_settings(str(settings_path))

    assert loaded == {
        "uploads_path": UPLOADS_PATH,
        "label_images_path": LABEL_IMAGES_PATH,
        "fallback_email": "known@example.com",
    }
    assert "extra_unknown_key" not in loaded


def test_save_settings_creates_parent_directories(tmp_path):
    settings_path = tmp_path / "nested" / "dir" / "settings.json"

    save_settings(default_settings(), str(settings_path))

    assert settings_path.exists()


def test_load_settings_ignores_empty_and_non_string_values(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "uploads_path": "   ",
                "label_images_path": 123,
                "fallback_email": "kept@example.com",
            }
        ),
        encoding="utf-8",
    )

    loaded = load_settings(str(settings_path))

    assert loaded["uploads_path"] == UPLOADS_PATH
    assert loaded["label_images_path"] == LABEL_IMAGES_PATH
    assert loaded["fallback_email"] == "kept@example.com"


def test_save_settings_strips_whitespace_and_drops_non_strings(tmp_path):
    settings_path = tmp_path / "settings.json"
    save_settings(
        {
            "uploads_path": "  \\\\server\\share\\uploads  ",
            "label_images_path": None,
            "fallback_email": "a@b.com",
        },
        str(settings_path),
    )

    stored = json.loads(settings_path.read_text(encoding="utf-8"))
    assert stored["uploads_path"] == "\\\\server\\share\\uploads"
    assert "label_images_path" not in stored
    assert stored["fallback_email"] == "a@b.com"


def test_save_settings_leaves_no_temp_file_behind(tmp_path):
    settings_path = tmp_path / "settings.json"
    save_settings(default_settings(), str(settings_path))

    assert sorted(p.name for p in tmp_path.iterdir()) == ["settings.json"]

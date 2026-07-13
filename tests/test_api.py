from bradyforge.api import Api
from bradyforge.settings import default_settings


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

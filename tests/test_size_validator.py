import pytest

from bradyforge.config import MAX_UPLOAD_SIZE_BYTES
from bradyforge.size_validator import FileTooLargeError, validate_upload_size


def _write_file_of_size(path, size_bytes):
    path.write_bytes(b"\x00" * size_bytes)
    return path


def test_file_under_limit_passes(tmp_path):
    small_path = _write_file_of_size(tmp_path / "small.bin", 10)

    assert validate_upload_size(small_path) is True


def test_file_exactly_at_limit_passes(tmp_path):
    at_limit_path = _write_file_of_size(tmp_path / "at-limit.bin", 100)

    assert validate_upload_size(at_limit_path, max_bytes=100) is True


def test_file_over_limit_raises(tmp_path):
    over_limit_path = _write_file_of_size(tmp_path / "over-limit.bin", 101)

    with pytest.raises(FileTooLargeError):
        validate_upload_size(over_limit_path, max_bytes=100)


def test_custom_max_bytes_overrides_config_default(tmp_path):
    custom_path = _write_file_of_size(tmp_path / "custom.bin", 50)

    # Passes with a generous custom limit, independent of the config default.
    assert validate_upload_size(custom_path, max_bytes=1000) is True

    # Fails with a strict custom limit smaller than the config default.
    with pytest.raises(FileTooLargeError):
        validate_upload_size(custom_path, max_bytes=10)

    assert MAX_UPLOAD_SIZE_BYTES > 50

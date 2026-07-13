from bradyforge.label_images import list_label_images


def test_returns_sorted_image_filenames_and_ignores_non_images(tmp_path):
    (tmp_path / "widget.png").write_text("png data")
    (tmp_path / "banner.JPG").write_text("jpg data")
    (tmp_path / "a_first.jpeg").write_text("jpeg data")
    (tmp_path / "notes.txt").write_text("not an image")
    (tmp_path / "report.xlsx").write_text("not an image")

    result = list_label_images(str(tmp_path))

    assert result == ["a_first.jpeg", "banner.JPG", "widget.png"]


def test_does_not_recurse_into_subdirectories(tmp_path):
    (tmp_path / "top.png").write_text("png data")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "nested.png").write_text("png data")

    result = list_label_images(str(tmp_path))

    assert result == ["top.png"]


def test_empty_directory_returns_empty_list(tmp_path):
    result = list_label_images(str(tmp_path))

    assert result == []


def test_nonexistent_directory_returns_empty_list_without_raising(tmp_path):
    missing_dir = tmp_path / "does_not_exist"

    result = list_label_images(str(missing_dir))

    assert result == []

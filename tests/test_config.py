from bradyforge import config


def test_uploads_path_default():
    assert config.UPLOADS_PATH == r"\\vrsi-dc4\SharedDocs\Brady Labeler\BradyForge"


def test_label_images_path_default():
    assert config.LABEL_IMAGES_PATH == (
        r"\\vrsi-dc4\SharedDocs\Brady Labeler\BradyForge\ImageFiles"
    )


def test_max_upload_size_bytes_default():
    assert config.MAX_UPLOAD_SIZE_BYTES == 25 * 1024 * 1024

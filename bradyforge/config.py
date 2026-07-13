"""Default configuration values for BradyForge.

These are the confirmed defaults from Section 0 of BradyForge-SPEC.md
(see CONFIRMED-INPUTS.md). The two network paths below (`UPLOADS_PATH`
and `LABEL_IMAGES_PATH`) are overridable at runtime via the in-app
Settings screen, whose values are persisted by `bradyforge/settings.py`;
`MAX_UPLOAD_SIZE_BYTES` is a fixed default, not currently
settings-configurable.
"""

# UNC path where uploaded Excel workbooks are stored.
UPLOADS_PATH = r"\\vrsi-dc4\SharedDocs\Brady Labeler\BradyForge"

# UNC path where label-type images are stored.
LABEL_IMAGES_PATH = r"\\vrsi-dc4\SharedDocs\Brady Labeler\BradyForge\ImageFiles"

# Maximum allowed size, in bytes, for an uploaded file (25MB).
MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024

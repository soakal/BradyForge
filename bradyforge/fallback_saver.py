"""Local fallback save-and-zip for when the uploads share is unreachable.

`save_local_and_zip` handles only the local-save-and-zip mechanics: given
file content and a target filename, it writes the content to a local
fallback directory, zips the resulting file, and returns a result carrying
both paths plus a user-facing message. It does not perform any network or
UNC-path reachability checks itself — callers are expected to have already
determined that the uploads share write failed before reaching here.
"""

import os
import zipfile
from dataclasses import dataclass

from bradyforge.filename_util import resolve_upload_filename


@dataclass
class FallbackSaveResult:
    """Outcome of a local fallback save-and-zip operation."""

    local_path: str
    zip_path: str
    message: str


def save_local_and_zip(source_bytes, filename, fallback_dir):
    """Save `source_bytes` locally as `filename` and zip it.

    `fallback_dir` is the local directory to write into (created if it does
    not already exist). The file is written as `fallback_dir/filename`, and
    a zip archive containing that single file is created alongside it as
    `fallback_dir/<name>.zip` (using the filename's stem).

    If a file named `filename` already exists in `fallback_dir` (e.g. a
    previous fallback save of the same workbook), a collision-safe name is
    resolved via `resolve_upload_filename` so the earlier fallback copy is
    never overwritten; the zip name follows the resolved filename's stem.

    Returns a `FallbackSaveResult` with the local file path, the zip path,
    and a human-readable message explaining that the uploads share was
    unreachable, that the file was saved locally instead, and that the user
    should place the file on the share later or email the zip to the
    configured fallback contact.
    """
    os.makedirs(fallback_dir, exist_ok=True)

    filename = resolve_upload_filename(fallback_dir, filename)
    local_path = os.path.join(fallback_dir, filename)
    with open(local_path, "wb") as f:
        f.write(source_bytes)

    stem, _extension = os.path.splitext(filename)
    zip_path = os.path.join(fallback_dir, f"{stem}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(local_path, arcname=filename)

    message = (
        "The uploads share is unreachable, so this file was saved locally "
        f"instead at {local_path} and zipped to {zip_path}. "
        "Please place the file on the share later once it is reachable, "
        "or email the zip to the configured fallback contact."
    )

    return FallbackSaveResult(local_path=local_path, zip_path=zip_path, message=message)

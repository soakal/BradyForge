"""Validation for uploaded .xlsx workbooks.

`validate_xlsx_file` confirms only that a path exists and points to a
genuine, openable .xlsx file. It does not check file size, tab count,
sheet names, or content structure — those are separate concerns handled
elsewhere.
"""

import os

import openpyxl


class InvalidXlsxError(Exception):
    """Raised when a path does not point to a genuine, openable .xlsx file."""


def validate_xlsx_file(path):
    """Confirm that `path` exists and is a genuine, non-corrupted .xlsx file.

    Returns True if the file exists and openpyxl can successfully open it
    as a workbook. Raises `InvalidXlsxError` if the file does not exist,
    is not a valid .xlsx/zip file, or openpyxl otherwise fails to open it.
    """
    if not os.path.isfile(path):
        raise InvalidXlsxError(f"File does not exist: {path}")

    try:
        workbook = openpyxl.load_workbook(path, read_only=True)
    except Exception as exc:
        raise InvalidXlsxError(
            f"File is not a valid .xlsx workbook: {path} ({exc})"
        ) from exc

    workbook.close()
    return True

"""Writer for the generic label workbook format.

Produces .xlsx files matching the header row of
`samples/Generic Label template.xlsx` (verified via openpyxl):

    Line 1 | Line2 | Line3 | qty

Note the inconsistent spacing is intentional and matches the real
template verbatim — "Line 1" has a space, "Line2"/"Line3" do not.
"""

import openpyxl

HEADER = ("Line 1", "Line2", "Line3", "qty")


def write_generic_workbook(rows, dest_path):
    """Write `rows` to a new .xlsx file at `dest_path`.

    `rows` is a list of dicts, each with keys `line1`, `line2`, `line3`,
    `qty`. The output file has the header row `HEADER` followed by one
    row per dict, in the same order as `rows`.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(HEADER)
    for row in rows:
        sheet.append((row["line1"], row["line2"], row["line3"], row["qty"]))
    workbook.save(dest_path)

# BradyForge — Confirmed Section 0 Inputs

Answers to `BradyForge-SPEC.md` Section 0, confirmed by Brian on 2026-07-13.

1. **Uploads folder (UNC):** `\\vrsi-dc4\SharedDocs\Brady Labeler\BradyForge`
2. **Label-types images folder (UNC):** `\\vrsi-dc4\SharedDocs\Brady Labeler\BradyForge\ImageFiles`
3. **Application folder (where BradyForge.exe will live):** `\\vrsi-dc4\SharedDocs\Brady Labeler\BradyForge\Application`
4. **Generic template sample:** `samples/Generic Label template.xlsx` — single sheet (`Sheet1`), header row only: `Line 1 | Line2 | Line3 | qty`. Each subsequent row is one label to print.
5. **Existing completed Excel file sample:** `samples/Sample Completed Multi-Tab File.xlsx` — real production job workbook (GM Orion ZJ040), 19 tabs (`Cell Info`, `Device Cables`, `Artifact Labels`, `Stand labels`, `FORMULA`, `LOOKUP`, etc.), heavy with formulas/lookups. Per spec, Tab 2 validation only needs to confirm the upload is a genuine, non-corrupted `.xlsx` — tab count/structure is irrelevant.
6. **Max upload file size:** 25MB (spec's proposed default, confirmed).

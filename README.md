# BradyForge

BradyForge is a standalone Windows desktop application — built with Python and
[PyWebView](https://pywebview.flowrl.com/) wrapping an HTML/CSS/JS front end —
that lets anyone on the VRSI corporate network submit label print jobs. Users
either fill out a **generic label form** (Line 1 / Line 2 / Line 3 / Quantity,
per label type) or **upload an already-completed Excel workbook**. Submissions
are written directly to a shared network folder for import into the Brady
label maker workflow. There is no server component: the app runs locally on
each user's machine and writes straight to the network share.

See `BradyForge-SPEC.md` for the full project specification and
`CONFIRMED-INPUTS.md` for the confirmed operational inputs referenced below.

## Confirmed operational parameters

These values are confirmed (see `CONFIRMED-INPUTS.md`) and live as defaults in
`bradyforge/config.py`, editable later via the in-app settings screen:

- **Uploads folder (UNC):** `\\vrsi-dc4\SharedDocs\Brady Labeler\BradyForge`
- **Label-types images folder (UNC):** `\\vrsi-dc4\SharedDocs\Brady Labeler\BradyForge\ImageFiles`
- **Max upload file size:** 25MB

## Project structure / module map

```
bradyforge/
    config.py           Confirmed default UNC paths and the max upload size constant.
    settings.py         Load/save user-editable settings (uploads path, label images
                         path, fallback email) as a small JSON file; UI-independent.
    generic_writer.py   Writes generic-form label rows to a .xlsx workbook matching
                         the sample generic template's header row (Line 1 | Line2 |
                         Line3 | qty).
    xlsx_validator.py   Confirms an uploaded path is a genuine, openable .xlsx file
                         (existence + openpyxl load); no size or structure checks.
    size_validator.py   Confirms an uploaded file's size is at or under the
                         configured max upload size.
    filename_util.py    Resolves a collision-safe upload filename, appending a
                         timestamp only if a same-named file already exists.
    fallback_saver.py   Saves file bytes locally and zips them when the uploads
                         share is unreachable, returning a user-facing message.
    label_images.py     Lists label-type image filenames found in a directory
                         (for the Tab 1 label picker), filtered by extension.
    api.py              The `Api` class — the JS-bridge surface handed to
                         PyWebView's `js_api`. Plain Python, no `webview` import,
                         so every method is directly unit-testable. Wires together
                         settings, upload validation/copy, generic-workbook
                         writing, fallback saving, and label-image listing.
    app.py               PyWebView entry point: builds (but does not start) the
                         desktop window, pointing it at webui/index.html and
                         handing it an Api instance as js_api. Imports webview
                         lazily so the module (and test suite) import cleanly
                         without pywebview installed.
    webui/
        index.html       Static three-tab shell (Generic Form / Existing File
                         Upload / Settings) with all form fields and DOM ids.
        styles.css        Visual styling — a navy + amber palette deliberately
                         distinct from default "AI tool" gradients.
        app.js           Tab switching plus Api-bridge wiring for Settings,
                         Generic Form save, Upload panel (drag-and-drop, client-
                         side validation, upload), and the live label-image picker.
```

## Getting started / development setup

Install dependencies:

```
pip install -r requirements.txt
```

Run the test suite:

```
python -m pytest -q
```

As of this writing, this runs **126 tests**, all passing.

**Testability design:** the test suite is deliberately runnable without a
display, without `pywebview` installed, and without launching the packaged
executable (it was originally developed in a display-less sandbox):

- `bradyforge/app.py` imports `webview` lazily (only inside `create_window()`),
  so the module — and the whole test suite — can be imported and exercised
  without `pywebview` installed or a display available.
- `bradyforge/api.py`'s `Api` class never imports `webview` either; every
  method is plain Python and directly unit-testable as a normal method call.
- Front-end behavior (`webui/index.html`, `webui/app.js`) is verified with
  static-pattern checks in `tests/test_app.py` — reading the HTML/JS source
  as text and asserting on the presence of expected DOM ids, attributes,
  Api-bridge calls, and wiring, rather than rendering the page in a browser.
- The Python backend is otherwise covered with normal `pytest` unit tests
  (one test module per `bradyforge/` module, e.g. `tests/test_api.py`,
  `tests/test_generic_writer.py`, etc.).

## Out of scope

Per `BradyForge-SPEC.md`, the following are explicitly **not** part of this
project:

- No user login / authentication — open to anyone on the corporate network.
- No submission history logging on user machines.
- No Hermes or other home-network integration (network isolation).
- No public code-signing certificate — packaging uses a self-signed
  certificate only.
- No hosted server or web deployment — this is a standalone `.exe` only.

## Packaging

Packaged build output (the `.exe` produced by PyInstaller, plus any
accompanying build artifacts such as a self-signed certificate) is documented
in `release/README.md`. The PyInstaller build configuration now lives at the
repo root:

- `BradyForge.spec` — the PyInstaller spec file, bundling
  `bradyforge/webui/index.html`, `styles.css`, and `app.js` into the frozen
  app and producing a single-file, windowed executable at
  `dist/BradyForge.exe`.
- `BUILD.md` — step-by-step instructions for running the PyInstaller build
  and, optionally, code-signing the resulting `.exe` with a self-signed
  certificate.

**Status:** the PyInstaller build and self-signed code-signing steps have
been executed on a real Windows machine; the signed executable is staged at
`release/BradyForge.exe` (build output itself is gitignored — only
`release/README.md` is tracked). The exe does not rebuild itself: after any
source change under `bradyforge/`, re-run the build and re-sign per
`BUILD.md` before shipping.

## Documentation

- A plain-language **user manual** for non-technical staff filling out the
  form is available in `USER-MANUAL.md`.
- A proprietary **LICENSE** for VRSI (internal use only, not open source) is
  available in `LICENSE`.

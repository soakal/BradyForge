# release/

This folder holds the **packaged output** of the BradyForge build — specifically the
standalone `.exe` produced by PyInstaller, along with any accompanying build artifacts
the packaging process generates alongside it (for example, a self-signed code-signing
certificate file used to sign the executable).

## What is tracked here

Only documentation and (in a future step) build configuration/scripts belong in version
control under this folder. This `README.md` is tracked. The actual build output —
the `.exe` and any other generated binaries — is **not** committed to git; it is
excluded via `.gitignore` and should be produced locally (or in CI) by running the
build.

## Where the build configuration lives

The PyInstaller build configuration (a `.spec` file or a build script) does not exist
yet. When it is added, it will live at the repo root or in a `packaging/`-style
location — not inside this `release/` folder, which is reserved for build output only.

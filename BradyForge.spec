# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for BradyForge.
#
# NOTE: This spec is authored as configuration only. It has NOT been
# executed or verified by an actual PyInstaller build in this
# development environment (PyInstaller is not installed here, and there
# is no Windows GUI available to smoke-test the resulting exe). It
# should be validated by running `pyinstaller BradyForge.spec` on a
# real Windows machine with the project's dependencies installed. See
# BUILD.md for the full build (and code-signing) procedure.

block_cipher = None

a = Analysis(
    ["bradyforge/app.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("bradyforge/webui/index.html", "webui"),
        ("bradyforge/webui/styles.css", "webui"),
        ("bradyforge/webui/app.js", "webui"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="BradyForge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

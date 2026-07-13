# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for BradyForge.
#
# This spec has been executed on a real Windows machine: running
# `pyinstaller BradyForge.spec` produces a single-file, windowed
# executable at dist/BradyForge.exe, which is then signed with the
# self-signed certificate and staged in release/. See BUILD.md for the
# full build (and code-signing) procedure. Remember to rebuild after
# source changes — the exe in release/ does not update itself.

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

# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for LostDock.
#
#   uv pip install pyinstaller
#   pyinstaller lostdock.spec
#
# Outputs dist/lostdock (and dist/lostdock.app on macOS).
# For a single-file build, pass --onefile on the CLI instead.

import os
import sys
import tomllib

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Read the project version from pyproject.toml so binaries carry the release tag.
with open(os.path.join(os.path.dirname(os.path.abspath(SPEC)), "pyproject.toml"), "rb") as _f:
    _pyproject = tomllib.load(_f)
version = _pyproject["project"]["version"]

datas = []
# Bundle the example plugins directory so plugins ship inside the binary.
plugins_dir = os.path.join(os.path.dirname(os.path.abspath(SPEC)), "plugins")
if os.path.isdir(plugins_dir):
    datas += [
        (os.path.join(plugins_dir, f), "lostdock/plugins")
        for f in os.listdir(plugins_dir)
        if f.endswith(".py")
    ]

a = Analysis(
    ["src/lostdock/main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "lostdock.core",
        "lostdock.core.models",
        "lostdock.core.compiler",
        "lostdock.core.operators",
        "lostdock.core.ratelimit",
        "lostdock.core.proxy",
        "lostdock.adapters",
        "lostdock.adapters.base",
        "lostdock.adapters.google",
        "lostdock.adapters.duckduckgo",
        "lostdock.adapters.bing",
        "lostdock.services",
        "lostdock.services.repository",
        "lostdock.services.executor",
        "lostdock.services.filter",
        "lostdock.services.crawler",
        "lostdock.services.scheduler",
        "lostdock.services.exporter",
        "lostdock.services.plugins",
        "lostdock.ui",
        "lostdock.ui.main_window",
        "lostdock.ui.dork_builder",
        "lostdock.ui.results_view",
        "lostdock.ui.settings",
        "lostdock.ui.worker",
        "bs4",
        "requests",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "test", "pytest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="lostdock",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="lostdock",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="LostDock.app",
        icon=None,
        bundle_identifier="dev.lostdock.app",
        info_plist={
            "CFBundleShortVersionString": version,
            "NSHighResolutionCapable": True,
        },
    )

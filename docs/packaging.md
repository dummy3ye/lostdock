# Packaging

LostDock ships as native binaries per platform via PyInstaller, plus a self-contained
Windows installer/updater. The project includes everything needed in the repo:
`lostdock.spec`, the installer source, and an Arch Linux `PKGBUILD`.

## The spec file

`lostdock.spec` drives the main build. It:

- reads the version from `pyproject.toml` so binaries carry the release tag;
- bundles the `plugins/` directory into the binary as `lostdock/plugins`;
- collects Playwright's data files and hidden imports (the Chromium node driver must ship
  alongside the app);
- lists all `lostdock` submodules as hidden imports so the frozen app resolves them;
- excludes `tkinter`, `test`, and `pytest` from the bundle.

Build it with:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec
```

Output is `dist/lostdock` (a directory) and, on macOS, `dist/LostDock.app`. For a
single-file build, pass `--onefile` on the CLI instead.

## Windows

- **App binary** — `dist/lostdock.exe` from the spec build.
- **Installer** — a separate single-file executable built from
  `src/installer/windows/main.py`:

  ```bash
  pyinstaller --onefile --windowed --name lostdock-installer src/installer/windows/main.py
  ```

  The installer is **stdlib-only** (small, dependency-free) and manages the app without
  admin rights:
  - double-click → GUI wizard
  - `install` → install, or update if already present
  - `update` → fetch the latest release from GitHub and replace files
  - `uninstall` → remove the app, Start Menu shortcut, and registry entry

  Install layout (per-user, no admin): `%LOCALAPPDATA%\LostDock\LostDock.exe` plus a
  Start Menu shortcut and an `HKCU` uninstall entry.

- **Signing** — CI generates a self-signed certificate (OpenSSL) and signs the installer
  with `osslsigncode`. Self-signed means SmartScreen will warn on first run; an EV
  certificate can be swapped in for commercial distribution.

## macOS

- Run `pyinstaller lostdock.spec` → produces `dist/LostDock.app`.
- Sign and notarize before distributing: `codesign` the bundle (the spec exposes
  `codesign_identity`/`entitlements_file` for passing an identity), then submit for
  notarization and staple.

## Linux

- `dist/lostdock` binary from the spec build.
- The CI uploads it as a tar archive; the binary's exec bit is set in the release asset.
- For distribution you can wrap it in an AppImage or Flatpak.
- **Arch Linux** — a `PKGBUILD` lives in `packaging/aur/`. It builds from source and
  installs the app plus the desktop entry (`assets/lostdock.desktop`).

## CI

Two GitHub Actions workflows:

- **ci** — on push to `master` and on PRs: installs Qt system deps, runs `ruff check`,
  `ruff format --check`, and `pytest`.
- **build** — on tags (`v*`) and manual dispatch: builds the Linux and Windows binaries
  via the spec, builds and signs the Windows installer, and publishes a GitHub Release
  with auto-generated notes (see [Development: releasing](development.md#releasing)).

Linux runner installs Qt runtime deps (`libegl1`, `libgl1`, `libxkbcommon0`,
`libdbus-1-3`) and `python -m playwright install chromium` before building, so the frozen
app can render headless pages.

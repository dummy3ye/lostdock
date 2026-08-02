"""LostDock Windows installer, updater and uninstaller.

A single one-file executable (PyInstaller --onefile --windowed) that manages
the application without admin rights. Double-clicking it opens a small Tkinter
wizard; the CLI subcommands stay available for silent/unattended use:

    lostdock-installer.exe          open the GUI wizard (Windows)
    lostdock-installer.exe install  install (or update if already present)
    lostdock-installer.exe update   fetch the latest release and replace files
    lostdock-installer.exe uninstall remove app, shortcut and registry entry

Everything is stdlib-only so the binary stays tiny and dependency-free.

Install layout (per-user, no admin required):
    %LOCALAPPDATA%\\LostDock\\LostDock.exe     the app
    %LOCALAPPDATA%\\LostDock\\lostdock-windows-<ver>.zip
    %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\LostDock.lnk
    HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\LostDock
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.request
import zipfile
from collections.abc import Callable

try:  # Windows-only; imported lazily on other platforms.
    import ctypes
    import ctypes.wintypes
    import winreg
except ImportError:  # pragma: no cover - non-Windows dev/test env
    ctypes = None  # type: ignore[assignment]
    winreg = None  # type: ignore[assignment]

REPO = "dummy3ye/lostdock"
API_LATEST = f"https://api.github.com/repos/{REPO}/releases/latest"
ASSET_PREFIX = "lostdock-windows-"

INSTALL_DIR_ENV = "LOSTDOCK_INSTALL_DIR"
START_MENU = r"Microsoft\Windows\Start Menu\Programs"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\LostDock"
SHORTCUT_NAME = "LostDock.lnk"

Report = Callable[[str], None]


class MessageType:
    INFO = 0x40
    WARNING = 0x30
    ERROR = 0x10
    YESNO = 0x04


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def install_dir() -> str:
    if INSTALL_DIR_ENV in os.environ:
        return os.environ[INSTALL_DIR_ENV]
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "LostDock")


def _installed_version() -> str | None:
    """Return the version of the currently installed app, if any."""
    dest = install_dir()
    if not os.path.isdir(dest):
        return None
    for entry in os.listdir(dest):
        if entry.startswith(ASSET_PREFIX) and entry.endswith(".zip"):
            return entry[len(ASSET_PREFIX) : -len(".zip")]
    return None


def _latest_release() -> tuple[str, str]:
    """Return (version, asset_url) for the newest windows zip release."""
    req = urllib.request.Request(API_LATEST, headers={"User-Agent": "lostdock-installer"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        release = json.load(resp)
    version = release["tag_name"].lstrip("v")
    for asset in release.get("assets", []):
        if asset["name"].startswith(ASSET_PREFIX) and asset["name"].endswith(".zip"):
            return version, asset["browser_download_url"]
    raise RuntimeError(f"no windows zip asset found in release v{version}")


def _download(url: str, dest: str, report: Report | None = None) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "lostdock-installer"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as out:
        total = int(resp.headers.get("Content-Length") or 0)
        written = 0
        while chunk := resp.read(1 << 20):
            out.write(chunk)
            written += len(chunk)
            if report is not None and total:
                report(f"Downloading... {written * 100 // total}%")


def _extract_zip(zip_path: str, target: str) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(target)


def _find_exe(directory: str) -> str | None:
    for root, _dirs, files in os.walk(directory):
        for f in files:
            if f.lower() == "lostdock.exe":
                return os.path.join(root, f)
    return None


def _launcher(shortcut: str, exe: str) -> None:
    """Create a Start Menu shortcut via the Windows Script Host."""
    ps = (
        "$ws=New-Object -ComObject WScript.Shell;"
        f"$s=$ws.CreateShortcut('{shortcut}');"
        f"$s.TargetPath='{exe}';"
        f"$s.WorkingDirectory='{os.path.dirname(exe)}';"
        f"$s.Save()"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def _write_uninstall_entry(version: str, uninstall_exe: str) -> None:
    if winreg is None:  # pragma: no cover - non-Windows
        return
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as key:
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "LostDock")
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "LostDock")
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstall_exe}" uninstall')
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir())
        winreg.SetValueEx(
            key, "DisplayIcon", 0, winreg.REG_SZ, os.path.join(install_dir(), "LostDock.exe")
        )
        winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)


def _remove_uninstall_entry() -> None:
    if winreg is None:  # pragma: no cover - non-Windows
        return
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
    except FileNotFoundError:
        pass


def _msgbox(text: str, title: str = "LostDock", kind: int = MessageType.INFO) -> int:
    if not _is_frozen() or ctypes is None:
        print(text)
        return 1
    return ctypes.windll.user32.MessageBoxW(ctypes.wintypes.HWND(0), text, title, kind)


def _notify(report: Report | None, text: str, kind: int = MessageType.INFO) -> None:
    if report is not None:
        report(text)
    else:
        _msgbox(text, kind=kind)


def _deploy(report: Report | None = None) -> str:
    """Download the latest release and stage it in the install dir.

    Returns the installed version string. The app binary is normalized to
    ``LostDock.exe`` regardless of how it is named inside the archive.
    """
    version, url = _latest_release()
    dest = install_dir()
    os.makedirs(dest, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, f"{ASSET_PREFIX}{version}.zip")
        _download(url, zip_path, report=report)
        if report is not None:
            report("Extracting...")
        extract_dir = os.path.join(tmp, "app")
        _extract_zip(zip_path, extract_dir)
        exe = _find_exe(extract_dir)
        if exe is None:
            raise RuntimeError("lostdock.exe not found in the release archive")
        _remove_installed(dest)
        shutil.copytree(extract_dir, dest, dirs_exist_ok=True)
        shutil.copy2(zip_path, os.path.join(dest, os.path.basename(zip_path)))
        final_exe = os.path.join(dest, "LostDock.exe")
        if not os.path.exists(final_exe):
            shutil.copy2(exe, final_exe)
    return version


def _remove_installed(dest: str) -> None:
    if os.path.exists(dest):
        shutil.rmtree(dest, ignore_errors=True)


def install(force_update: bool = False, report: Report | None = None) -> int:
    dest = install_dir()
    if not force_update and os.path.exists(os.path.join(dest, "LostDock.exe")):
        return update(report=report)

    try:
        _notify(report, "Downloading the latest LostDock release...")
        version = _deploy(report)
    except Exception as exc:
        _notify(report, f"Install failed: {exc}", MessageType.ERROR)
        return 1

    _write_uninstall_entry(version, sys.executable if _is_frozen() else os.path.abspath(__file__))
    shortcut_dir = os.path.join(os.environ.get("APPDATA", ""), START_MENU)
    os.makedirs(shortcut_dir, exist_ok=True)
    shortcut = os.path.join(shortcut_dir, SHORTCUT_NAME)
    try:
        _launcher(shortcut, os.path.join(dest, "LostDock.exe"))
    except Exception:
        pass

    _notify(report, f"LostDock v{version} installed.\n\nShortcut created in the Start Menu.")
    return 0


def update(report: Report | None = None) -> int:
    dest = install_dir()
    if not os.path.exists(dest):
        return install(report=report)
    try:
        _notify(report, "Checking for a newer LostDock release...")
        version = _deploy(report)
    except Exception as exc:
        _notify(report, f"Update failed: {exc}", MessageType.ERROR)
        return 1
    _write_uninstall_entry(version, sys.executable if _is_frozen() else os.path.abspath(__file__))
    _notify(report, f"LostDock updated to v{version}.")
    return 0


def _do_uninstall(report: Report | None = None) -> None:
    dest = install_dir()
    _remove_installed(dest)
    shortcut = os.path.join(os.environ.get("APPDATA", ""), START_MENU, SHORTCUT_NAME)
    if os.path.exists(shortcut):
        try:
            os.remove(shortcut)
        except OSError:
            pass
    _remove_uninstall_entry()
    _notify(report, "LostDock has been removed.")


def uninstall(report: Report | None = None) -> int:
    confirm = _msgbox("Remove LostDock and all its files?", "Uninstall LostDock", MessageType.YESNO)
    if confirm != 6:  # IDYES
        return 0
    _do_uninstall(report)
    return 0


# --- GUI wizard ---------------------------------------------------------------------------


class _InstallerApp:
    """Tkinter wizard driving the install/update/uninstall operations."""

    def __init__(self, root, tk, ttk, messagebox) -> None:
        self.root = root
        self.tk = tk
        self.ttk = ttk
        self.messagebox = messagebox
        self._busy = False
        self._build()

    def _build(self) -> None:
        self.root.title("LostDock Installer")
        self.root.resizable(False, False)
        self.root.geometry("460x320")
        frame = self.ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        self.ttk.Label(frame, text="LostDock", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        self.ttk.Label(
            frame, text="Install, update or remove LostDock on this PC.", foreground="#555"
        ).pack(anchor="w", pady=(2, 12))

        self.status = self.ttk.Label(frame, text="Checking for updates...", anchor="w")
        self.status.pack(fill="x")

        self.progress = self.ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=(6, 4))
        self.progress["value"] = 0

        self.log = self.tk.Text(frame, height=6, state="disabled", wrap="word", relief="sunken")
        self.log.pack(fill="both", expand=True, pady=(8, 10))

        buttons = self.ttk.Frame(frame)
        buttons.pack(fill="x")
        self.btn_uninstall = self.ttk.Button(buttons, text="Uninstall", command=self.on_uninstall)
        self.btn_uninstall.pack(side="right")
        self.btn_close = self.ttk.Button(buttons, text="Close", command=self.root.destroy)
        self.btn_close.pack(side="right", padx=(0, 8))
        self.btn_install = self.ttk.Button(
            buttons, text="Install / Update", command=self.on_install
        )
        self.btn_install.pack(side="left")

        self._refresh_status()

    def _report(self, text: str) -> None:
        self.root.after(0, self._append_log, text)

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.btn_install.configure(state=state)
        self.btn_uninstall.configure(state=state)
        if busy:
            self.progress.start()
        else:
            self.progress.stop()

    def _refresh_status(self) -> None:
        installed = _installed_version()
        label = f"Installed: {('v' + installed) if installed else 'not installed'}"
        self.status.configure(text=label)
        self._append_log(f"Latest release: {API_LATEST}")

    def _work(self, fn: Callable[[], int]) -> None:
        if self._busy:
            return
        self._set_busy(True)

        def runner() -> None:
            try:
                result = fn()
            except Exception as exc:  # pragma: no cover - defensive
                result = 1
                self.root.after(0, self._append_log, f"Error: {exc}")
            self.root.after(0, self._done, result)

        threading.Thread(target=runner, daemon=True).start()

    def _done(self, result: int) -> None:
        self._set_busy(False)
        self._append_log("Done." if result == 0 else "Finished with errors.")
        self._refresh_status()

    def on_install(self) -> None:
        self._work(lambda: install(report=self._report))

    def on_uninstall(self) -> None:
        if self._busy:
            return
        if not self.messagebox.askyesno("Uninstall LostDock", "Remove LostDock and all its files?"):
            return
        self._work(lambda: (_do_uninstall(self._report), 0)[1])


def run_gui() -> int:
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ImportError:  # pragma: no cover - non-GUI runtime
        return install()
    try:
        root = tk.Tk()
    except tk.TclError:  # pragma: no cover - headless
        return install()
    _InstallerApp(root, tk, ttk, messagebox)
    root.mainloop()
    return 0


# --- entrypoint ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    cmd = argv[1].lower() if len(argv) > 1 else None
    if cmd in ("gui", "--gui"):
        return run_gui()
    if cmd is None:
        if os.name == "nt":
            return run_gui()
        return install()
    if cmd in ("install", "--install"):
        return install()
    if cmd in ("update", "--update", "upgrade"):
        return update()
    if cmd in ("uninstall", "--uninstall", "remove"):
        return uninstall()
    if cmd in ("--version", "version"):
        print("LostDock installer")
        return 0
    print(f"usage: {os.path.basename(sys.argv[0])} [install|update|uninstall]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

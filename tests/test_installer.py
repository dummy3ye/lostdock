"""Tests for the Windows installer/updater/uninstaller module."""

import importlib.util
import json
import os
import zipfile

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "lostdock_installer",
    os.path.join(os.path.dirname(__file__), "..", "src", "installer", "windows", "main.py"),
)
_installer = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_installer)


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("LOSTDOCK_INSTALL_DIR", str(tmp_path / "app"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))


def _fake_release(
    monkeypatch, version="0.2.1", url="https://example.invalid/lostdock-windows-0.2.1.zip"
):
    monkeypatch.setattr(_installer, "_latest_release", lambda: (version, url, "notes"))


def _fake_download(monkeypatch, tmp_path):
    def fake(url, dest, report=None):
        with zipfile.ZipFile(dest, "w") as zf:
            zf.writestr("lostdock.exe", "MZ")
            zf.writestr("README.md", "hello")
            zf.writestr("_internal/mod.txt", "x")

    monkeypatch.setattr(_installer, "_download", fake)
    monkeypatch.setattr(_installer, "_launcher", lambda *a: None)


def test_latest_release_parses_asset(monkeypatch):
    payload = {
        "tag_name": "v0.2.1",
        "body": "## What's new\n- fix thing",
        "assets": [
            {
                "name": "lostdock-linux-0.2.1.tar.gz",
                "browser_download_url": "https://x/linux.tar.gz",
            },
            {"name": "lostdock-windows-0.2.1.zip", "browser_download_url": "https://x/windows.zip"},
        ],
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps(payload).encode()

    def fake_urlopen(req, timeout=60):
        assert req.get_header("User-agent") == "lostdock-installer"
        return FakeResponse()

    monkeypatch.setattr(_installer.urllib.request, "urlopen", fake_urlopen)
    version, url, notes = _installer._latest_release()
    assert version == "0.2.1"
    assert url == "https://x/windows.zip"
    assert "fix thing" in notes


def test_latest_release_missing_asset(monkeypatch):
    payload = {
        "tag_name": "v0.2.1",
        "assets": [{"name": "not-a-windows-zip", "browser_download_url": "https://x"}],
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps(payload).encode()

    def fake_urlopen(req, timeout=60):
        return FakeResponse()

    monkeypatch.setattr(_installer.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError):
        _installer._latest_release()


def test_installed_version_reads_zip_name(monkeypatch, tmp_path):
    dest = _installer.install_dir()
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, "lostdock-windows-0.2.0.zip"), "w").close()
    assert _installer._installed_version() == "0.2.0"


def test_installed_version_none_when_empty(monkeypatch, tmp_path):
    assert _installer._installed_version() is None


def test_install_downloads_extracts_and_writes_entry(monkeypatch, tmp_path):
    _fake_download(monkeypatch, tmp_path)
    _fake_release(monkeypatch)
    assert _installer.install() == 0
    dest = _installer.install_dir()
    assert os.path.exists(os.path.join(dest, "LostDock.exe"))
    assert os.path.exists(os.path.join(dest, "README.md"))
    assert os.path.exists(os.path.join(dest, "lostdock-windows-0.2.1.zip"))


def test_install_routes_to_update_when_present(monkeypatch, tmp_path):
    _fake_download(monkeypatch, tmp_path)
    _fake_release(monkeypatch)
    dest = _installer.install_dir()
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, "LostDock.exe"), "wb").write(b"MZ")
    assert _installer.install() == 0


def test_install_reports_progress(monkeypatch, tmp_path):
    _fake_download(monkeypatch, tmp_path)
    _fake_release(monkeypatch)
    seen = []
    assert _installer.install(report=seen.append) == 0
    assert any("installed" in line for line in seen)


def test_update_replaces_files(monkeypatch, tmp_path):
    _fake_download(monkeypatch, tmp_path)
    _fake_release(monkeypatch)
    dest = _installer.install_dir()
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "stale.txt"), "w") as f:
        f.write("old")
    assert _installer.update() == 0
    assert not os.path.exists(os.path.join(dest, "stale.txt"))
    assert os.path.exists(os.path.join(dest, "LostDock.exe"))


def test_uninstall_removes_dest(monkeypatch, tmp_path):
    dest = _installer.install_dir()
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, "LostDock.exe"), "wb").write(b"MZ")
    monkeypatch.setattr(_installer, "_msgbox", lambda *a, **k: 6)
    assert _installer.uninstall() == 0
    assert not os.path.exists(dest)


def test_uninstall_declined_keeps_files(monkeypatch, tmp_path):
    dest = _installer.install_dir()
    os.makedirs(dest, exist_ok=True)
    monkeypatch.setattr(_installer, "_msgbox", lambda *a, **k: 7)
    assert _installer.uninstall() == 0
    assert os.path.exists(dest)


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["install"], 0),
        (["update"], 0),
        (["uninstall"], 0),
        (["--version"], 0),
        (["bogus"], 2),
    ],
)
def test_main_dispatch(monkeypatch, tmp_path, args, expected):
    monkeypatch.setattr(_installer, "_deploy", lambda report=None: "0.0.0")
    monkeypatch.setattr(_installer, "_write_uninstall_entry", lambda *a: None)
    monkeypatch.setattr(_installer, "_msgbox", lambda *a, **k: 1)
    assert _installer.main(["installer.exe", *args]) == expected


def test_main_no_args_non_windows_runs_cli(monkeypatch):
    monkeypatch.setattr(_installer, "_deploy", lambda report=None: "0.0.0")
    monkeypatch.setattr(_installer, "_write_uninstall_entry", lambda *a: None)
    assert _installer.main(["installer.exe"]) == 0

"""Google search routed through a real Chrome/Chromium browser via CDP.

The requests-based GoogleEngine is often blocked with 429 / reCAPTCHA from
datacenter IPs. This adapter instead launches the user's own Chrome or
Chromium, drives it over the Chrome DevTools Protocol (WebSocket, stdlib
only), and scrapes the rendered SERP. Using a persistent user-data-dir means
once a CAPTCHA is solved (or the IP is residential) results flow normally.

NOTE: Google's ToS restrict automated access; this is for security research
and is rate-limited by default.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import random
import shutil
import socket
import struct
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlencode, urlparse

from ..core.models import SearchResult
from ..core.ratelimit import RateLimiter, default_limiter
from .base import BlockedError, EngineError, SearchEngine
from .google import _parse_google_serp

log = logging.getLogger(__name__)

_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

DEFAULT_PROFILE = Path.home() / ".lostdock" / "chrome-profile"


def _find_chrome() -> Optional[str]:
    """Locate a Chrome/Chromium binary."""
    env = os.environ.get("LOSTDOCK_CHROME")
    candidates = [
        env,
        "google-chrome-stable",
        "google-chrome",
        "chromium",
        "chromium-browser",
        "chrome",
        # Windows
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if os.path.exists(candidate):
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    return None


def _is_bot_page(html: str) -> bool:
    low = html.lower()
    return (
        "/sorry/" in html
        or "g-recaptcha" in html
        or "unusual traffic" in low
        or "captcha" in low
    )


class _WebSocket:
    """Minimal RFC 6455 client (text frames, masking) for CDP."""

    def __init__(self, host: str, port: int, path: str, timeout: float = 15.0) -> None:
        self.host = host
        self.port = port
        self.path = path
        self.timeout = timeout
        self._sock: Optional[socket.socket] = None

    def connect(self) -> None:
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self._sock.settimeout(self.timeout)
        self._sock.sendall(request.encode())
        response = self._read_headers()
        accept = base64.b64encode(
            hashlib.sha1((key + _WS_GUID).encode()).digest()
        ).decode()
        if f"Sec-WebSocket-Accept: {accept}" not in response:
            raise EngineError("WebSocket handshake failed (bad Sec-WebSocket-Accept)")

    def _read_headers(self) -> str:
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self._sock.recv(4096)
            if not chunk:
                break
            buf += chunk
        return buf.decode(errors="replace")

    def _recv_exact(self, n: int) -> bytes:
        data = b""
        while len(data) < n:
            chunk = self._sock.recv(n - len(data))
            if not chunk:
                raise EngineError("WebSocket connection closed")
            data += chunk
        return data

    def send_text(self, text: str, opcode: int = 0x1) -> None:
        payload = text.encode()
        mask = os.urandom(4)
        header = bytearray()
        header.append(0x80 | opcode)  # FIN + opcode
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", length)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", length)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self._sock.sendall(bytes(header) + masked)

    def recv_text(self, timeout: Optional[float] = None) -> Optional[str]:
        self._sock.settimeout(timeout or self.timeout)
        while True:
            b1, b2 = self._recv_exact(2)
            opcode = b1 & 0x0F
            length = b2 & 0x7F
            masked = bool(b2 & 0x80)
            if length == 126:
                length = struct.unpack(">H", self._recv_exact(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self._recv_exact(8))[0]
            mask = self._recv_exact(4) if masked else b""
            payload = self._recv_exact(length)
            if masked:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            if opcode == 0x9:  # ping -> pong
                self.send_text(payload.decode(errors="replace"), opcode=0xA)
                continue
            if opcode == 0x8:  # close
                return None
            if opcode == 0x1:  # text
                return payload.decode(errors="replace")

    def close(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None


class _CdpSession:
    """Thin request/response wrapper over a DevTools WebSocket."""

    def __init__(self, ws: _WebSocket) -> None:
        self._ws = ws
        self._next_id = 1

    def call(self, method: str, params: Optional[dict] = None) -> dict:
        msg_id = self._next_id
        self._next_id += 1
        self._ws.send_text(
            json.dumps({"id": msg_id, "method": method, "params": params or {}})
        )
        while True:
            text = self._ws.recv_text()
            if text is None:
                raise EngineError("CDP connection closed")
            msg = json.loads(text)
            if msg.get("id") == msg_id:
                if "error" in msg:
                    raise EngineError(f"CDP {method} failed: {msg['error']}")
                return msg.get("result", {})


class ChromeEngine(SearchEngine):
    """Runs Google searches inside a real Chrome/Chromium over CDP."""

    name = "google-chrome"

    def __init__(
        self,
        limiter: Optional[RateLimiter] = None,
        proxies=None,
        browser: Optional[str] = None,
        user_data_dir: Optional[Path] = None,
        port: int = 9222,
        headless: bool = True,
        timeout: float = 15.0,
    ) -> None:
        self.limiter = limiter or default_limiter()
        self.proxies = proxies
        self.browser = browser or _find_chrome()
        self.user_data_dir = Path(user_data_dir or DEFAULT_PROFILE)
        self.port = port
        self.headless = headless
        self.timeout = timeout
        self._proc: Optional[subprocess.Popen] = None
        self._ws: Optional[_WebSocket] = None
        self._session: Optional[_CdpSession] = None

    # ----- lifecycle -----
    def _ensure_browser(self) -> None:
        if self.browser is None or (
            not os.path.exists(self.browser) and shutil.which(self.browser) is None
        ):
            raise EngineError(
                "No Chrome/Chromium found. Install Google Chrome or Chromium, or "
                "set the LOSTDOCK_CHROME env var to the binary path."
            )
        if self._proc is not None and self._proc.poll() is None:
            return
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            self.browser,
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-sync",
            "about:blank",
        ]
        if self.headless:
            cmd.append("--headless=new")
            cmd.append("--disable-gpu")
        try:
            if os.geteuid() == 0:  # noqa: PLC2801 - root needs --no-sandbox
                cmd.append("--no-sandbox")
        except AttributeError:
            pass  # Windows has no geteuid
        self._proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        self._wait_for_cdp()

    def _wait_for_cdp(self) -> None:
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{self.port}/json/version", timeout=1
                ):
                    return
            except Exception:  # noqa: BLE001 - retry until ready
                time.sleep(0.2)
        raise EngineError("Chrome started but the DevTools endpoint never came up")

    def _connect(self) -> _CdpSession:
        self._ensure_browser()
        if self._session is not None:
            return self._session
        with urllib.request.urlopen(
            f"http://127.0.0.1:{self.port}/json/list", timeout=5
        ) as resp:
            targets = json.load(resp)
        page = next((t for t in targets if t.get("type") == "page"), None)
        if page is None:
            req = urllib.request.Request(
                f"http://127.0.0.1:{self.port}/json/new?about:blank", method="PUT"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                page = json.load(resp)
        ws_url = page["webSocketDebuggerUrl"]
        parts = urlparse(ws_url)
        ws = _WebSocket(parts.hostname, parts.port, parts.path, timeout=self.timeout)
        ws.connect()
        self._ws = ws
        session = _CdpSession(ws)
        session.call("Page.enable")
        session.call("Runtime.enable")
        self._session = session
        return session

    def _navigate(self, url: str) -> str:
        session = self._connect()
        session.call("Page.navigate", {"url": url})
        for _ in range(int(self.timeout / 0.3)):
            time.sleep(0.3)
            res = session.call(
                "Runtime.evaluate",
                {"expression": "document.readyState", "returnByValue": True},
            )
            if res.get("result", {}).get("value") == "complete":
                break
        time.sleep(0.5)  # let JS-driven SERP render
        res = session.call(
            "Runtime.evaluate",
            {
                "expression": "document.documentElement.outerHTML",
                "returnByValue": True,
            },
        )
        return res.get("result", {}).get("value", "")

    def close(self) -> None:
        if self._ws is not None:
            self._ws.close()
            self._ws = None
        self._session = None
        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None

    def __del__(self) -> None:  # pragma: no cover - best-effort cleanup
        try:
            self.close()
        except Exception:  # noqa: BLE001
            pass

    # ----- engine interface -----
    def search(
        self,
        query: str,
        pages: int = 1,
        per_page: int = 10,
        stop_at: Optional[int] = None,
    ) -> List[SearchResult]:
        results: List[SearchResult] = []
        try:
            for page in range(pages):
                self.limiter.acquire()
                params = {
                    "q": query,
                    "start": page * per_page,
                    "num": per_page,
                    "hl": "en",
                }
                url = "https://www.google.com/search?" + urlencode(params)
                html = self._navigate(url)
                if _is_bot_page(html):
                    raise BlockedError(
                        "Google served a reCAPTCHA / bot-check in the browser. "
                        "This IP may be flagged (common for datacenter IPs). Run the "
                        f"search once in headed mode or open {self.user_data_dir} in "
                        "a normal Chrome, solve the CAPTCHA, and retry — the profile "
                        "is reused so results will flow afterwards."
                    )
                page_results = _parse_google_serp(
                    html, query, position_offset=len(results)
                )
                results.extend(page_results)
                if stop_at and len(results) >= stop_at:
                    return results[:stop_at]
                if page < pages - 1:
                    time.sleep(random.uniform(1.0, 2.0))
            return results
        finally:
            self.close()

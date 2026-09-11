"""Poly Pen download page. Samsung Sans drop-in TTF is served as Samsungsans.ttf."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 48751
ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
COMPARE = ROOT / "compare.html"
FONT = ROOT / "fonts" / "ttf" / "PolyPen-Regular.ttf"
NANUM = ROOT / "fonts" / "nanum" / "NanumPenScript-Regular.ttf"
SAMSUNG = ROOT / "fonts" / "samsung" / "Samsungsans.ttf"
SAMSUNG_ZIP = ROOT / "downloads" / "PolyPen-SamsungSans.zip"
OFL = ROOT / "OFL.txt"


def _ensure_samsung() -> None:
    if FONT.exists() and (not SAMSUNG.exists() or not SAMSUNG_ZIP.exists()):
        import sys

        sys.path.insert(0, str(ROOT / "sources"))
        from make_samsung import main as make_samsung

        make_samsung()


def _font_bytes() -> int:
    return FONT.stat().st_size if FONT.exists() else 0


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _send(self, status: int, body: bytes, content_type: str, download: str | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if download:
            self.send_header("Content-Disposition", f'attachment; filename="{download}"')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, INDEX.read_bytes(), "text/html; charset=utf-8")
            return
        if path in ("/compare", "/compare.html"):
            self._send(200, COMPARE.read_bytes(), "text/html; charset=utf-8")
            return
        if path == "/fonts/NanumPenScript-Regular.ttf":
            if not NANUM.exists():
                self._send(404, b"missing nanum", "text/plain; charset=utf-8")
                return
            self._send(200, NANUM.read_bytes(), "font/ttf")
            return
        if path in (
            "/fonts/poly-pen.ttf",
            "/fonts/PolyPen-Regular.ttf",
            "/download/poly-pen.ttf",
            "/download/PolyPen-Regular.ttf",
        ):
            if not FONT.exists():
                self._send(404, b"missing font", "text/plain; charset=utf-8")
                return
            data = FONT.read_bytes()
            download = "PolyPen-Regular.ttf" if path.startswith("/download/") else None
            self._send(200, data, "font/ttf", download)
            return
        if path in (
            "/fonts/Samsungsans.ttf",
            "/download/Samsungsans.ttf",
            "/download/SamsungSans.ttf",
        ):
            _ensure_samsung()
            if not SAMSUNG.exists():
                self._send(404, b"missing samsung slot font", "text/plain; charset=utf-8")
                return
            data = SAMSUNG.read_bytes()
            download = "Samsungsans.ttf" if path.startswith("/download/") else None
            self._send(200, data, "font/ttf", download)
            return
        if path == "/download/PolyPen-SamsungSans.zip":
            _ensure_samsung()
            if not SAMSUNG_ZIP.exists():
                self._send(404, b"missing zip", "text/plain; charset=utf-8")
                return
            self._send(200, SAMSUNG_ZIP.read_bytes(), "application/zip", "PolyPen-SamsungSans.zip")
            return
        if path == "/download/OFL.txt":
            self._send(200, OFL.read_bytes(), "text/plain; charset=utf-8", "OFL.txt")
            return
        if path == "/meta":
            _ensure_samsung()
            payload = {
                "family": "Poly Pen",
                "filename": "PolyPen-Regular.ttf",
                "bytes": _font_bytes(),
                "glyphs": 11743,
                "samsung": {
                    "filename": "Samsungsans.ttf",
                    "bytes": SAMSUNG.stat().st_size if SAMSUNG.exists() else 0,
                    "zip": "PolyPen-SamsungSans.zip",
                },
            }
            self._send(200, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")


def main() -> None:
    _ensure_samsung()
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Poly Pen download  http://127.0.0.1:{PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()

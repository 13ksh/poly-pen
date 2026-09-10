"""Poly Pen download page."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 48751
ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
FONT = ROOT / "fonts" / "ttf" / "PolyPen-Regular.ttf"
OFL = ROOT / "OFL.txt"


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
        if path == "/download/OFL.txt":
            self._send(200, OFL.read_bytes(), "text/plain; charset=utf-8", "OFL.txt")
            return
        if path == "/meta":
            payload = {
                "family": "Poly Pen",
                "filename": "PolyPen-Regular.ttf",
                "bytes": _font_bytes(),
                "glyphs": 11743,
            }
            self._send(200, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Poly Pen download  http://127.0.0.1:{PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()

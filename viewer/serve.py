#!/usr/bin/env python3
"""Stateless local server for the run viewer.

Serves the viewer itself at http://127.0.0.1:8000/ and the run logs under
/data/ (default root: the repo's results/ directory). GET /data returns a JSON
listing of every *.jsonl file under the root so the run picker can populate
itself; nothing is cached or stored server-side.

Usage (from anywhere):
  python viewer/serve.py                 # port 8000, logs at ../results
  python viewer/serve.py --port 8080 --logs path/to/logs

Then open http://127.0.0.1:8000/
"""

from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

VIEWER_DIR = Path(__file__).resolve().parent


def find_logs(root: Path) -> list[dict]:
    out = []
    for p in sorted(root.rglob("*.jsonl")):
        st = p.stat()
        out.append({"path": p.relative_to(root).as_posix(),
                    "size": st.st_size, "mtime": int(st.st_mtime)})
    return out


class Handler(BaseHTTPRequestHandler):
    logs_root: Path = VIEWER_DIR.parent / "results"

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        path = self.path.split("?", 1)[0].split("#", 1)[0]

        if path in ("/data", "/data/"):
            body = json.dumps(find_logs(self.logs_root)).encode()
            return self._send(200, body, "application/json")

        if path.startswith("/data/"):
            rel = path[len("/data/"):]
            target = (self.logs_root / rel).resolve()
            if not target.is_relative_to(self.logs_root.resolve()) or not target.is_file():
                return self._send(404, b"not found", "text/plain")
            return self._send(200, target.read_bytes(),
                              "application/jsonl; charset=utf-8")

        if path == "/":
            path = "/index.html"
        target = (VIEWER_DIR / path.lstrip("/")).resolve()
        if not target.is_relative_to(VIEWER_DIR) or not target.is_file():
            return self._send(404, b"not found", "text/plain")
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        return self._send(200, target.read_bytes(), ctype)

    def log_message(self, fmt: str, *args) -> None:  # quiet
        pass


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--logs", type=Path, default=VIEWER_DIR.parent / "results",
                    help="directory served under /data (default: ../results)")
    args = ap.parse_args()

    Handler.logs_root = args.logs.resolve()
    logs = find_logs(Handler.logs_root)
    print(f"serving viewer  : http://127.0.0.1:{args.port}/")
    print(f"serving logs at : /data/  (root: {Handler.logs_root}, {len(logs)} .jsonl files)")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Local preview server (SETUP-INSTRUCTIONS 10.1, "Local preview").

    python tools/serve.py            # build the site, then serve build/site/
    python tools/serve.py --port 8945
    python tools/serve.py --no-build # serve the site built by the last run

Builds the site (tools/build.py, including the site step and its allowlist
audit) and serves build/site/ on localhost with the standard library's
http.server — the README documents this as the way to review rendered
output before a release. It is the local stand-in for the deployed Worker:
the site root at /, the catalogue under /web/, and the 404 page for any
path that is not in the allowlist.

A path that does not resolve serves 404.html with HTTP status 404, the way
wrangler.jsonc's "not_found_handling": "404-page" does in production.
"""

from __future__ import annotations

import argparse
import http.server
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "build" / "site"


class SiteHandler(http.server.SimpleHTTPRequestHandler):
    """Static files from build/site/, with the site's own 404 page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def send_error(self, code, message=None, explain=None):
        page = SITE / "404.html"
        if code == http.HTTPStatus.NOT_FOUND and page.is_file():
            body = page.read_bytes()
            self.send_response(http.HTTPStatus.NOT_FOUND, message)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return
        super().send_error(code, message, explain)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the site and serve build/site/ on localhost "
                    "(SETUP-INSTRUCTIONS 10.1, local preview).")
    parser.add_argument("--port", type=int, default=8000,
                        help="port to listen on (default 8000)")
    parser.add_argument("--no-build", action="store_true",
                        help="serve the site from the last build instead of "
                             "building first")
    args = parser.parse_args(argv)

    if not args.no_build:
        run([sys.executable, str(ROOT / "tools" / "build.py")])
    if not (SITE / "index.html").is_file():
        raise SystemExit(f"{SITE} is not built — run without --no-build")

    with http.server.ThreadingHTTPServer(("", args.port), SiteHandler) as server:
        host, port = server.server_address[:2]
        print(f"serving {SITE} at http://{'localhost' if not host else host}:"
              f"{port}/ — Ctrl-C to stop")
        print(f"landing page: http://localhost:{port}/  ·  "
              f"catalogue: http://localhost:{port}/web/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
        finally:
            server.server_close()
    return 0


def run(cmd: list) -> None:
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(f"command failed ({proc.returncode}): "
                         f"{' '.join(str(c) for c in cmd)}")


if __name__ == "__main__":
    sys.exit(main())

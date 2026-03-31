#!/usr/bin/env python3
"""
Print sorted OpenAPI paths for local FastAPI apps (no HTTP server).

Usage (from repo root or backend/):
  cd backend
  python scripts/openapi_route_inventory.py --app server
  python scripts/openapi_route_inventory.py --app server_new
  python scripts/openapi_route_inventory.py --compare-url https://bayan-backend-4zn3.onrender.com

Requires backend/.env or minimal env (MONGO_URL, JWT_SECRET) for importing server.py.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Ensure imports resolve when cwd is backend/
BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)


def _ensure_min_env() -> None:
    from dotenv import load_dotenv

    load_dotenv(BACKEND / ".env", override=False)
    if not os.environ.get("MONGO_URL"):
        os.environ["MONGO_URL"] = "mongodb://127.0.0.1:27017"
    if not os.environ.get("JWT_SECRET"):
        os.environ["JWT_SECRET"] = "local-openapi-inventory-placeholder-min-32-chars"


def route_tuples_from_schema(schema: dict) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for path, methods in schema.get("paths", {}).items():
        for m in methods:
            if m.upper() in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
                out.add((m.upper(), path))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--app",
        choices=("server", "server_new", "both"),
        default="server",
        help="Which local module:app to introspect",
    )
    ap.add_argument(
        "--compare-url",
        default="",
        help="Base URL of a deployed API (fetches /openapi.json)",
    )
    args = ap.parse_args()

    _ensure_min_env()

    local_sets: dict[str, set[tuple[str, str]]] = {}

    if args.app in ("server", "both"):
        import server as server_mod

        local_sets["server:app"] = route_tuples_from_schema(server_mod.app.openapi())

    if args.app in ("server_new", "both"):
        import server_new as sn

        local_sets["server_new:app"] = route_tuples_from_schema(sn.app.openapi())

    for name, routes in local_sets.items():
        print(f"\n=== LOCAL {name} ({len(routes)} route methods) ===")
        for method, path in sorted(routes):
            print(f"  {method:7} {path}")

    if args.compare_url:
        import json
        import urllib.request

        base = args.compare_url.rstrip("/")
        url = f"{base}/openapi.json"
        print(f"\n=== REMOTE {url} ===")
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                remote = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Failed to fetch: {e}", file=sys.stderr)
            return 1
        remote_set = route_tuples_from_schema(remote)
        print(f"  ({len(remote_set)} route methods)")

        if len(local_sets) == 1:
            local_name, local_routes = next(iter(local_sets.items()))
            only_local = sorted(local_routes - remote_set)
            only_remote = sorted(remote_set - local_routes)

            print(
                f"\n=== SUMMARY: {local_name} has {len(local_routes)} | "
                f"remote has {len(remote_set)} | "
                f"only-local {len(only_local)} | only-remote {len(only_remote)} ==="
            )

            print(f"\n=== ONLY IN {local_name} (not on remote) — {len(only_local)} ===")
            for method, path in only_local:
                print(f"  {method:7} {path}")

            print(f"\n=== ONLY ON REMOTE (not in {local_name}) — {len(only_remote)} ===")
            for method, path in only_remote:
                print(f"  {method:7} {path}")

            if not only_local and not only_remote:
                print("\n(OpenAPI route sets match.)")
            elif only_local and only_remote:
                print(
                    "\n[Note] Both sides have unique routes — different apps or "
                    "different commits. For Render to match this repo, start with: "
                    "uvicorn server:app (see render.yaml / backend/Procfile)."
                )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

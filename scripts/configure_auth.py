"""Save user-supplied SESSDATA using yutto's native authentication file."""
from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path
import sys

from yutto.auth import default_auth_file, load_auth_file, parse_auth_inline, save_auth, validate_profile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auth-file", type=Path, default=default_auth_file())
    parser.add_argument("--profile", default="billi_downloader")
    args = parser.parse_args()
    validate_profile(args.profile)
    path = args.auth_file.expanduser().resolve()
    if path.exists() and load_auth_file(path) is None:
        parser.error("Existing authentication file is invalid; it has not been changed.")
    raw = os.environ.get("BILIBILI_SESSDATA")
    if raw is None:
        if not sys.stdin.isatty():
            parser.error("Use an interactive terminal or supply BILIBILI_SESSDATA in the environment.")
        raw = getpass.getpass("SESSDATA (or Cookie containing SESSDATA): ")
    raw = raw.strip()
    if not raw or any(ord(char) < 32 or ord(char) == 127 for char in raw):
        parser.error("SESSDATA is empty or contains control characters.")
    cookie = parse_auth_inline(raw) if "=" in raw or ";" in raw else None
    if ("=" in raw or ";" in raw) and cookie is None:
        parser.error("Cookie must contain SESSDATA.")
    sessdata = cookie["SESSDATA"] if cookie else raw
    bili_jct = cookie["bili_jct"] if cookie else None
    save_auth(path, args.profile, sessdata, bili_jct)
    print(f"Authentication saved: {path} (profile: {args.profile}).")
    print("Saved locally; login validity has not yet been checked.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError):
        print("Could not save authentication; check the path, profile and file format.", file=sys.stderr)
        raise SystemExit(1)

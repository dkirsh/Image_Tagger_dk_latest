#!/usr/bin/env python3
"""flickr_key_setup.py — tell me exactly what to do with a Flickr API key.

It does the safe thing AND prints your exact next steps:
  1. reads the key from $FLICKR_API_KEY (preferred) or --key
  2. sanity-checks the format and (optionally) validates it against Flickr
  3. stores it in a git-IGNORED .env (chmod 600) so it can never be committed
  4. refuses to write anywhere git would track, and never prints the full key
  5. prints the exact commands to run next

Usage
-----
    export FLICKR_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    python3 flickr_key_setup.py                 # validate + store + instructions
    python3 flickr_key_setup.py --key XXXX       # pass explicitly instead of env
    python3 flickr_key_setup.py --no-test        # skip the network validation call
    python3 flickr_key_setup.py --no-store       # just advise, write nothing
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

FLICKR_REST = "https://api.flickr.com/services/rest/"


def mask(key: str) -> str:
    """Never show a full secret: bd34...e887"""
    key = key.strip()
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}...{key[-4:]}"


def repo_root(start: Path) -> Path:
    try:
        out = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(out.stdout.strip())
    except Exception:
        return start


def is_git_ignored(path: Path, root: Path) -> bool:
    """True if git would ignore `path` (i.e. it is safe to hold a secret)."""
    rc = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "-q", str(path)],
    ).returncode
    return rc == 0  # 0 => ignored


def ensure_gitignore(root: Path) -> list[str]:
    """Make sure secret files can't be committed. Returns patterns added."""
    gi = root / ".gitignore"
    want = [".env", ".env.*", "*.key", "*.secret", "secrets/"]
    have = gi.read_text().splitlines() if gi.exists() else []
    added = [p for p in want if p not in have]
    if added:
        block = "\n# --- secrets: never commit API keys / credentials ---\n" + "\n".join(added) + "\n"
        with gi.open("a") as fh:
            fh.write(block)
    return added


def valid_format(key: str) -> bool:
    # Flickr API keys are 32 hex chars.
    return bool(re.fullmatch(r"[0-9a-fA-F]{32}", key.strip()))


def test_key(key: str, timeout: float = 10.0) -> tuple[bool, str]:
    """Hit flickr.test.echo — a harmless call that proves the key works."""
    params = urllib.parse.urlencode({
        "method": "flickr.test.echo",
        "api_key": key,
        "format": "json",
        "nojsoncallback": "1",
    })
    try:
        with urllib.request.urlopen(f"{FLICKR_REST}?{params}", timeout=timeout) as r:
            data = json.loads(r.read().decode())
    except Exception as e:  # network / DNS / TLS
        return False, f"could not reach Flickr ({e.__class__.__name__}: {e})"
    if data.get("stat") == "ok":
        return True, "key accepted by Flickr (flickr.test.echo => ok)"
    return False, f"Flickr rejected the key: {data.get('message', data)}"


def store_key(env_file: Path, key: str, root: Path) -> None:
    """Write FLICKR_API_KEY into a gitignored .env with 0600 perms."""
    if not is_git_ignored(env_file, root):
        raise SystemExit(
            f"REFUSING to write {env_file} — git does not ignore it, so the key "
            f"could be committed. Run this again after .gitignore covers .env."
        )
    lines = env_file.read_text().splitlines() if env_file.exists() else []
    lines = [ln for ln in lines if not ln.startswith("FLICKR_API_KEY=")]
    lines.append(f"FLICKR_API_KEY={key}")
    env_file.write_text("\n".join(lines) + "\n")
    env_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600


def main() -> int:
    ap = argparse.ArgumentParser(description="Safely set up a Flickr API key.")
    ap.add_argument("--key", help="the API key (else read from $FLICKR_API_KEY)")
    ap.add_argument("--env-file", default=".env", help="where to store it (default: .env)")
    ap.add_argument("--no-test", action="store_true", help="skip the network validation call")
    ap.add_argument("--no-store", action="store_true", help="advise only; write nothing")
    args = ap.parse_args()

    key = (args.key or os.environ.get("FLICKR_API_KEY", "")).strip()
    if not key:
        print("No key given. Pass --key or `export FLICKR_API_KEY=...` first.", file=sys.stderr)
        return 2

    root = repo_root(Path.cwd())
    env_file = (root / args.env_file) if not os.path.isabs(args.env_file) else Path(args.env_file)

    print(f"Key:        {mask(key)}   (never printed in full)")
    print(f"Repo root:  {root}")
    print(f"Env file:   {env_file}")
    print("-" * 60)

    # 1. format
    if valid_format(key):
        print("[ok]   format looks like a Flickr key (32 hex chars)")
    else:
        print("[warn] does NOT look like a 32-char hex Flickr key — double-check it")

    # 2. make secrets un-committable
    added = ensure_gitignore(root)
    if added:
        print(f"[fix]  added to .gitignore so it can't be committed: {', '.join(added)}")
    else:
        print("[ok]   .gitignore already blocks .env / *.key")

    # 3. validate against Flickr
    if args.no_test:
        print("[skip] network validation (--no-test)")
    else:
        ok, msg = test_key(key)
        print(f"[{'ok' if ok else 'FAIL'}]   {msg}")

    # 4. store it
    if args.no_store:
        print("[skip] not storing (--no-store)")
    else:
        store_key(env_file, key, root)
        print(f"[ok]   stored in {env_file} (perms 600, git-ignored)")

    # 5. exact next steps
    print("-" * 60)
    print("NEXT STEPS — exactly what to do with the key:")
    print(f"  1. Load it into your shell for this session:")
    print(f"       set -a; source {env_file}; set +a")
    print(f"     (or keep exporting it manually: export FLICKR_API_KEY=...)")
    print(f"  2. Run the collector — it reads $FLICKR_API_KEY, no key on the CLI:")
    print(f"       python3 <collector>.py -q 'brutalist concrete interior' -b flickr -n 40 \\")
    print(f"         --flickr-license '4,5,7,8,9,10' --emit-stimulus-manifest \\")
    print(f"         --experiment-name goldilocks_interiors_pilot -o collection")
    print(f"  3. Confirm it never lands in git:  git check-ignore {env_file}  (should echo the path)")
    print(f"  4. If this key was ever pasted in a shared/logged channel, ROTATE it at")
    print(f"       https://www.flickr.com/services/apps/  and re-run this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

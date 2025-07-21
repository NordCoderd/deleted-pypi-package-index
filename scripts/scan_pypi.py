#!/usr/bin/env python3
"""Fetch PyPI project list, detect deletions / revivals, update logs in pypi-uploader-directory/."""

from pathlib import Path
from datetime import datetime, timezone
import sys
import requests

URL      = "https://pypi.org/simple/"
HEADERS  = {"Accept": "application/vnd.pypi.simple.v1+json"}
TODAY    = datetime.now(timezone.utc).strftime("%d-%m-%Y")     # DD-MM-YYYY

ROOT     = Path(__file__).resolve().parent.parent
OUT_DIR  = ROOT / "pypi-uploader-directory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LATEST_TXT  = OUT_DIR / "latest-pypi-state.txt"
DELETED_TXT = OUT_DIR / "deleted-pypi-packages.txt"
REVIVED_TXT = OUT_DIR / "revived-pypi-packages.txt"

DELETED_CSV = OUT_DIR / "deleted-pypi-packages.csv"
REVIVED_CSV = OUT_DIR / "revived-pypi-packages.csv"


def fetch_current_projects() -> set[str]:
    r = requests.get(URL, headers=HEADERS, timeout=120)
    r.raise_for_status()
    return {item["name"] for item in r.json()["projects"]}


def load_set(path: Path) -> set[str]:
    return set(path.read_text().splitlines()) if path.exists() else set()


def append_unique(path: Path, items: set[str]) -> None:
    if not items:
        return
    existing = load_set(path)
    new = sorted(items - existing)
    if new:
        path.write_text(path.read_text() + "\n".join(new) + "\n" if path.exists() else "\n".join(new) + "\n")


def prepend_csv(path: Path, rows: list[str]) -> None:
    """Prepend new rows so newest dates stay on top; no deduplication."""
    existing = path.read_text() if path.exists() else ""
    path.write_text("\n".join(rows) + ("\n" if rows else "") + existing)


def main() -> None:
    new_projects = fetch_current_projects()

    # First run: only snapshot
    if not LATEST_TXT.exists():
        LATEST_TXT.write_text("\n".join(sorted(new_projects)) + "\n")
        print(f"Initial snapshot saved: {len(new_projects)} projects")
        return

    old_projects  = load_set(LATEST_TXT)
    prev_deleted  = load_set(DELETED_TXT)

    deleted_now   = old_projects - new_projects
    revived_now   = new_projects & prev_deleted

    # TXT lists (uniqueness preserved)
    append_unique(DELETED_TXT, deleted_now)
    append_unique(REVIVED_TXT, revived_now)

    # CSV logs (no uniqueness, newest first, dot separator)
    prepend_csv(DELETED_CSV, [f"{TODAY},{pkg}" for pkg in sorted(deleted_now)])
    prepend_csv(REVIVED_CSV, [f"{TODAY},{pkg}" for pkg in sorted(revived_now)])

    # Purge revived packages from deleted TXT list
    if revived_now:
        remaining_deleted = prev_deleted - revived_now
        DELETED_TXT.write_text("\n".join(sorted(remaining_deleted)) + ("\n" if remaining_deleted else ""))

    # Overwrite latest snapshot
    LATEST_TXT.write_text("\n".join(sorted(new_projects)) + "\n")

    print(f"Snapshot refreshed: {len(new_projects)} projects")
    print(f"Deleted this run : {len(deleted_now)}")
    print(f"Revived this run : {len(revived_now)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"scan_pypi.py failed: {exc}", file=sys.stderr)
        sys.exit(1)
#!/usr/bin/env python3
"""Fetch PyPI project list, detect deletions and revivals, update files in pypi-uploader-directory/."""

from pathlib import Path
import sys
import requests

URL = "https://pypi.org/simple/"
HEADERS = {"Accept": "application/vnd.pypi.simple.v1+json"}

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "pypi-uploader-directory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LATEST   = OUT_DIR / "latest-pypi-state.txt"
DELETED  = OUT_DIR / "deleted-pypi-packages.txt"
REVIVED  = OUT_DIR / "revived-pypi-packages.txt"


def fetch_current_projects() -> list[str]:
    resp = requests.get(URL, headers=HEADERS, timeout=120)
    resp.raise_for_status()
    projects = {item["name"] for item in resp.json()["projects"]}
    return sorted(projects)


def load_set(path: Path) -> set[str]:
    return set(path.read_text().splitlines()) if path.exists() else set()


def append_unique(path: Path, items: set[str]) -> None:
    if not items:
        return
    existing = load_set(path)
    with path.open("a", encoding="utf-8") as f:
        for pkg in sorted(items - existing):
            f.write(f"{pkg}\n")


def main() -> None:
    new_projects = set(fetch_current_projects())

    if not LATEST.exists():
        LATEST.write_text("\n".join(sorted(new_projects)) + "\n", encoding="utf-8")
        print(f"Initial snapshot saved: {len(new_projects)} projects")
        return

    old_projects   = load_set(LATEST)
    prev_deleted   = load_set(DELETED)

    deleted_now    = old_projects - new_projects
    revived_now    = new_projects & prev_deleted

    append_unique(DELETED, deleted_now)
    append_unique(REVIVED, revived_now)

    if revived_now:
        remaining_deleted = prev_deleted - revived_now
        DELETED.write_text(
            "\n".join(sorted(remaining_deleted)) + ("\n" if remaining_deleted else ""),
            encoding="utf-8",
            )

    LATEST.write_text("\n".join(sorted(new_projects)) + "\n", encoding="utf-8")

    print(f"Snapshot refreshed: {len(new_projects)} projects")
    print(f"Deleted this run : {len(deleted_now)}")
    print(f"Revived this run : {len(revived_now)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"scan_pypi.py failed: {exc}", file=sys.stderr)
        sys.exit(1)

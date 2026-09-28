#!/usr/bin/env python3
"""Generate data/nemesis_packages.txt — the package names nemesis_repo carries.

Run automatically by up.sh. ATT reads this list (functions.load_nemesis_packages) to
tell nemesis_repo packages from chaotic-aur ones: find_package_repo() picks the repo
to blame in "repo not enabled" errors, and desktopr.desktop_needs_nemesis() greys out
desktops that need nemesis_repo. A hand-kept list drifted badly (2 of ~123 kiro-arc /
celestial themes listed), so it is generated again.

Source resolution order:
  1. $NEMESIS_REPO_DIR if set (a directory of built *.pkg.tar.zst files)
  2. ~/EDU/nemesis_repo/x86_64 (local nemesis_repo checkout — the source of truth)
  3. `pacman -Slq nemesis_repo` (the published DB, when nemesis_repo is enabled here)
If none resolve, the existing committed data file is left untouched.
"""

import os
import subprocess
import sys
from os import path

SCRIPT_DIR = path.dirname(path.realpath(__file__))
OUTPUT = path.join(SCRIPT_DIR, "usr/share/archlinux-tweak-tool/data/nemesis_packages.txt")

LOCAL_CANDIDATES = [
    os.environ.get("NEMESIS_REPO_DIR", ""),
    path.expanduser("~/EDU/nemesis_repo/x86_64"),
]


def info(msg):
    print(f"[nemesis-list] {msg}")


def from_repo_dir(repo_dir):
    """Package names from built package files: <name>-<pkgver>-<pkgrel>-<arch>.pkg.tar.zst."""
    names = set()
    for filename in os.listdir(repo_dir):
        if filename.endswith(".pkg.tar.zst"):
            parts = filename[: -len(".pkg.tar.zst")].rsplit("-", 3)
            if len(parts) == 4:
                names.add(parts[0])
    return names


def from_pacman():
    """Package names from the nemesis_repo sync DB; empty when the repo isn't enabled here."""
    try:
        res = subprocess.run(["pacman", "-Slq", "nemesis_repo"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return set()
    return set(res.stdout.split()) if res.returncode == 0 else set()


def main():
    """Resolve a source, write the sorted list, and report what changed."""
    names, source = set(), None
    for candidate in LOCAL_CANDIDATES:
        if candidate and path.isdir(candidate):
            names, source = from_repo_dir(candidate), candidate
            if names:
                break
    if not names:
        names, source = from_pacman(), "pacman -Slq nemesis_repo"
    if not names:
        info("no source found (no local nemesis_repo, repo not enabled) — keeping the committed list")
        return 0

    old = set()
    if path.exists(OUTPUT):
        with open(OUTPUT) as f:
            old = {line.strip() for line in f if line.strip()}
    with open(OUTPUT, "w") as f:
        f.write("\n".join(sorted(names)) + "\n")
    info(f"{len(names)} packages from {source} (+{len(names - old)} / -{len(old - names)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

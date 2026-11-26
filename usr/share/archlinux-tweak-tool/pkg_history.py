# ============================================================
# Author: Erik Dubois
# ============================================================
# Maintenance → History tab — logic. Turns /var/log/pacman.log into a list of
# transactions and finds older package versions still in the pacman cache.

import glob
import os
import re
import subprocess

import functions as fn

PACMAN_LOG = "/var/log/pacman.log"
MAX_TRANSACTIONS = 300

_LINE_RE = re.compile(r"^\[(?P<stamp>[^\]]+)\] \[(?P<src>[A-Z-]+)\] (?P<msg>.*)$")
_ACTION_RE = re.compile(
    r"^(?P<action>installed|upgraded|downgraded|removed|reinstalled) (?P<pkg>\S+) \((?P<vers>[^)]*)\)$"
)


def _pretty_stamp(stamp):
    # 2026-11-26T05:15:08+0100 → 2026-11-26 05:15
    return stamp[:16].replace("T", " ")


def parse_log(lines, limit=MAX_TRANSACTIONS):
    """Return transactions newest first: [{"time", "command", "entries": [{action, pkg, old, new}]}]."""
    transactions = []
    command = ""
    current = None
    for line in lines:
        match = _LINE_RE.match(line.rstrip("\n"))
        if not match:
            continue
        src, msg = match.group("src"), match.group("msg")
        if src == "PACMAN" and msg.startswith("Running '"):
            command = msg[len("Running '"):].rstrip("'")
        elif src == "ALPM" and msg == "transaction started":
            current = {"time": _pretty_stamp(match.group("stamp")), "command": command, "entries": []}
        elif src == "ALPM" and msg in ("transaction completed", "transaction failed"):
            if current and current["entries"]:
                transactions.append(current)
            current = None
        elif src == "ALPM" and current is not None:
            action = _ACTION_RE.match(msg)
            if action:
                vers = action.group("vers").split(" -> ")
                current["entries"].append({
                    "action": action.group("action"),
                    "pkg": action.group("pkg"),
                    "old": vers[0],
                    "new": vers[-1],
                })
    transactions.reverse()
    return transactions[:limit]


def read_history(path=PACMAN_LOG, limit=MAX_TRANSACTIONS):
    """Parse the pacman log; returns [] when it can't be read."""
    try:
        with open(path, encoding="utf-8", errors="replace") as log_file:
            return parse_log(log_file, limit)
    except OSError as error:
        fn.log_warn(f"Could not read {path}: {error}")
        return []


def cache_dirs():
    """Return pacman's CacheDir list (falls back to the default)."""
    try:
        result = subprocess.run(["pacman-conf", "CacheDir"], capture_output=True, text=True, timeout=5)
        dirs = [d.strip() for d in result.stdout.splitlines() if d.strip()]
    except (OSError, subprocess.SubprocessError):
        dirs = []
    return dirs or ["/var/cache/pacman/pkg/"]


def cache_index(dirs=None):
    """Return {"<pkg>-<pkgver>-<pkgrel>": path} for every package file in the pacman cache."""
    index = {}
    for cache in dirs or cache_dirs():
        for path in glob.glob(os.path.join(glob.escape(cache), "*.pkg.tar.*")):
            if path.endswith(".sig"):
                continue
            # <name>-<pkgver>-<pkgrel>-<arch>.pkg.tar.<ext> → drop "-<arch>.pkg.tar.<ext>"
            stem = os.path.basename(path).split(".pkg.tar.")[0]
            index.setdefault(stem.rsplit("-", 1)[0], path)
    return index


def find_cached(pkg, version, index):
    """Return the cached file for <pkg> at <version> (pkgver-pkgrel), or None."""
    return index.get(f"{pkg}-{version}")


def install_file(path):
    """Install one cached package file with pacman -U in a terminal; returns the Popen."""
    fn.log_subsection(f"Installing from cache: {path}")
    return fn.launch_pacman_install_file_in_terminal(path)

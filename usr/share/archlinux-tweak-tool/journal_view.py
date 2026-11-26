# ============================================================
# Author: Erik Dubois
# ============================================================
# Logging → Journal tab — logic. Reads the systemd journal as JSON so the GUI can
# show it as a table (time, level, service, message) instead of raw text.

import datetime
import json
import os
import subprocess

import functions as fn

MAX_ENTRIES = 5000

# journalctl -p takes the lowest priority to include; 0 = emerg … 7 = debug
LEVEL_ERRORS = 3
LEVEL_WARNINGS = 4
LEVEL_EVERYTHING = 6

LEVEL_NAMES = {0: "emergency", 1: "alert", 2: "critical", 3: "error", 4: "warning", 5: "notice", 6: "info", 7: "debug"}

_ENV = {**os.environ, "LC_ALL": "C"}


def _stamp(microseconds):
    return datetime.datetime.fromtimestamp(int(microseconds) / 1_000_000)


def list_boots():
    """Return boots newest first: [{"index": 0, "first": datetime, "last": datetime}, ...]."""
    try:
        result = subprocess.run(["journalctl", "--list-boots", "-o", "json", "--no-pager"],
                                capture_output=True, text=True, env=_ENV, timeout=20)
        boots = json.loads(result.stdout or "[]")
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        fn.log_warn(f"Could not list boots: {error}")
        return [{"index": 0, "first": None, "last": None}]
    out = [{"index": b["index"], "first": _stamp(b["first_entry"]), "last": _stamp(b["last_entry"])} for b in boots]
    out.sort(key=lambda b: b["index"], reverse=True)
    return out or [{"index": 0, "first": None, "last": None}]


def _message(value):
    # MESSAGE is a list of bytes when it is not valid UTF-8
    if isinstance(value, list):
        return bytes(v for v in value if isinstance(v, int) and 0 <= v < 256).decode("utf-8", errors="replace")
    return str(value or "")


def parse_line(line):
    """Turn one journalctl -o json line into an entry dict, or None."""
    try:
        record = json.loads(line)
    except ValueError:
        return None
    try:
        priority = int(record.get("PRIORITY", 6))
    except (TypeError, ValueError):
        priority = 6
    service = record.get("_SYSTEMD_UNIT") or record.get("SYSLOG_IDENTIFIER") or record.get("_COMM") or "kernel"
    stamp = record.get("__REALTIME_TIMESTAMP")
    return {
        "time": _stamp(stamp) if stamp else None,
        "priority": priority,
        "service": str(service),
        "message": _message(record.get("MESSAGE")).strip(),
    }


def read_entries(boot_index=0, max_priority=LEVEL_WARNINGS, limit=MAX_ENTRIES):
    """Return (entries newest first, capped) for one boot, up to max_priority."""
    cmd = ["journalctl", "-b", str(boot_index), "-p", str(max_priority), "-o", "json", "-r", "-n", str(limit),
           "--no-pager"]
    fn.log_info(f"Journal: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=_ENV, timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        fn.log_error(f"journalctl failed: {error}")
        return [], False
    entries = [e for e in (parse_line(line) for line in result.stdout.splitlines()) if e]
    return entries, len(entries) >= limit


def summarize(entries):
    """Return (errors, warnings, services) counted over the entries."""
    errors = sum(1 for e in entries if e["priority"] <= LEVEL_ERRORS)
    warnings = sum(1 for e in entries if e["priority"] == LEVEL_WARNINGS)
    return errors, warnings, len({e["service"] for e in entries})


def as_text(entries):
    """Plain-text lines for the clipboard, oldest first like journalctl."""
    lines = []
    for e in reversed(entries):
        when = e["time"].strftime("%Y-%m-%d %H:%M:%S") if e["time"] else ""
        lines.append(f"{when} {LEVEL_NAMES.get(e['priority'], e['priority'])} {e['service']}: {e['message']}")
    return "\n".join(lines)

# ============================================================
# Author: Erik Dubois
# ============================================================
# Diagnostic report for the "Report a problem" button on every Arch-based system that is
# not Kiro / KiroTux (those use kiro-report). Ported from kiro-report: same sections where
# they apply, same redaction rules. The report text stays English on purpose — it is read
# by the maintainer, not by the user.

import datetime
import os
import platform
import re
import socket
import subprocess

import functions as fn

ISSUES_URL = "https://github.com/kirodubes/archlinux-tweak-tool/issues/new"

DRIVER_PACKAGES = re.compile(
    r"^(xf86-video-|xf86-input-|xorg-server|mesa|lib32-mesa|vulkan-|lib32-vulkan-|libva|lib32-libva|libvdpau|"
    r"nvidia|lib32-nvidia|libdrm|intel-media-driver|intel-gmmlib|onevpl|opencl-)", re.IGNORECASE)

_OCTET = r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])"
# Same order and rules as kiro-report's redact(): MAC and UUID before the broader rules; the IPv4
# rule skips a quad followed by "-" or ".<letter>" so package versions (libva 2.23.0-1) survive;
# the IPv6 rule needs "::" with no alphanumeric neighbour, so PCI addresses and Calamares::Job survive.
_REDACTIONS = (
    (re.compile(r"\x1b\[[0-9;]*m"), ""),
    (re.compile(r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"), "<mac>"),
    (re.compile(r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"), "<uuid>"),
    (re.compile(r"\b[0-9a-f]{32}\b"), "<machine-id>"),
    (re.compile(rf"\b{_OCTET}\.{_OCTET}\.{_OCTET}\.{_OCTET}(?=[^-.0-9]|\.[^0-9A-Za-z]|\.$|$)", re.MULTILINE), "<ip>"),
    (re.compile(r"(?<![0-9A-Za-z:])[0-9A-Fa-f:]*::[0-9A-Fa-f:]*(?![0-9A-Za-z:])"), "<ipv6>"),
)


def redact(text, host, user):
    """Replace IP/MAC/UUID/machine-id, the hostname and the username with placeholders."""
    for pattern, replacement in _REDACTIONS:
        text = pattern.sub(replacement, text)
    if user:
        text = text.replace(f"/home/{user}", "/home/<user>")
    # Stricter boundaries than kiro-report's \b: vanilla Arch's default hostname is "archlinux",
    # and \b would turn "archlinux-tweak-tool" into "<host>-tweak-tool".
    for value, placeholder in ((host, "<host>"), (user, "<user>")):
        if value:
            text = re.sub(rf"(?<![\w.-]){re.escape(value)}(?![\w-])", placeholder, text)
    return text


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _field(name, value):
    return f"  {name + ':':<26} {value}"


def _block(title, body, empty="(none)"):
    lines = [f"── {title} ──"]
    lines.extend(f"    {line}" for line in (body.splitlines() if body else [empty]))
    return "\n".join(lines + [""])


def _tail(text, count):
    return "\n".join(text.splitlines()[-count:])


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def _os_release_name():
    match = re.search(r'^PRETTY_NAME="?([^"\n]*)"?', _read("/etc/os-release"), re.MULTILINE)
    return match.group(1) if match else "unknown"


def _cpu_model():
    match = re.search(r"^model name\s*:\s*(.*)$", _read("/proc/cpuinfo"), re.MULTILINE)
    return match.group(1) if match else platform.machine()


def _memory():
    match = re.search(r"^MemTotal:\s*(\d+)", _read("/proc/meminfo"), re.MULTILINE)
    return f"{int(match.group(1)) / 1048576:.1f} GiB" if match else "unknown"


def _graphics():
    """VGA / 3D / Display devices from lspci -nnk, each with its driver in use."""
    devices, current = [], None
    for line in _run(["lspci", "-nnk"]).splitlines():
        if not line.startswith(("\t", " ")):
            current = line if re.search(r"VGA compatible|3D controller|Display controller", line) else None
            if current:
                devices.append(current)
        elif current and "Kernel driver in use" in line:
            devices.append("  " + line.strip())
    return "\n".join(devices)


def _session():
    env = fn.get_terminal_env()
    desktop = env.get("XDG_CURRENT_DESKTOP") or fn.desktop or "unknown"
    session = env.get("XDG_SESSION_TYPE") or ("wayland" if env.get("WAYLAND_DISPLAY") else "x11")
    return desktop, session


def _repositories():
    sections = re.findall(r"^\s*\[([^\]]+)\]", _read("/etc/pacman.conf"), re.MULTILINE)
    return " ".join(s for s in sections if s != "options")


def _att_session_log():
    log = getattr(fn.LOG_FILE, "name", None)
    return _tail(_read(log), 60) if log else ""


def build():
    """Return the redacted report text."""
    desktop, session = _session()
    explicit = _run(["pacman", "-Qe"])
    drivers = "\n".join(line for line in _run(["pacman", "-Q"]).splitlines() if DRIVER_PACKAGES.match(line))
    failed = " ".join(line.split()[0] for line in _run(
        ["systemctl", "--failed", "--no-legend", "--plain"]).splitlines() if line.split())
    pacman_actions = "\n".join(line for line in _read(fn.pacman_logfile).splitlines()
                               if re.search(r"\[ALPM\] (installed|upgraded|removed)", line))

    parts = [
        "##################################################################",
        "# ArchLinux Tweak Tool (ATT) diagnostic report",
        f"# Generated : {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
        "#",
        "# Sensitive values (IP / MAC / UUID / machine-id / hostname /",
        "# username) have been redacted so this file is safe to paste on",
        "# the public ATT issue tracker. Glance through it anyway.",
        "##################################################################",
        "",
        "── System ──",
        _field("Distro (ATT)", fn.get_distro_label()),
        _field("os-release", _os_release_name()),
        _field("ATT package", _run(["pacman", "-Q", "archlinux-tweak-tool"]) or "not installed (git copy?)"),
        _field("Kernel", platform.release()),
        _field("Boot mode", "UEFI" if os.path.isdir("/sys/firmware/efi") else "BIOS"),
        _field("Root filesystem", _run(["findmnt", "-no", "FSTYPE", "/"]) or "unknown"),
        _field("CPU", _cpu_model()),
        _field("Memory", _memory()),
        _field("Desktop", desktop),
        _field("Session type", session),
        _field("Repositories", _repositories()),
        _field("Failed units", failed or "none"),
        _field("Explicit packages", str(len(explicit.splitlines()))),
        "",
        _block("Graphics devices", _graphics()),
        _block("Graphics / driver packages", drivers),
        _block("Journal errors this boot (priority >= err, last 25)", _tail(_run(
            ["journalctl", "-p", "3", "-b", "--no-pager"]), 25)),
        _block("Kernel errors (dmesg level err+, last 25)", _tail(_run(
            ["dmesg", "--level=err,crit,alert,emerg"]), 25)),
        _block("Recent pacman actions (last 30)", _tail(pacman_actions, 30)),
        _block("ATT log of this session (last 60 lines)", _att_session_log()),
        _block("Explicitly installed packages", explicit),
    ]
    return redact("\n".join(parts), socket.gethostname(), fn.sudo_username)


def save(text):
    """Write the report to the user's home folder, owned by the user; return the path."""
    path = os.path.join(fn.home, f"att-report-{datetime.datetime.now():%Y%m%d-%H%M%S}.log")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    fn.permissions(path)
    fn.log_success(f"Report saved: {path}")
    return path

# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

"""Kiro's AUR check: switch kiro-aur-check on or off as paru's PreBuildCommand."""

import os
import subprocess

import functions as fn

TOOL = "/usr/local/bin/kiro-paru-aur-check"
SCANNER = "/usr/bin/cachyos-pi-scan"
SYSTEM_CONF = "/etc/paru.conf"


def available():
    """True on Kiro / KiroTux when kiro-system-files ships the switch script."""
    return fn.get_distro_label() in ("Kiro", "KiroTux") and os.access(TOOL, os.X_OK)


def scanner_installed():
    """True when cachyos-pi-scan, the scanner kiro-aur-check runs, is installed."""
    return os.access(SCANNER, os.X_OK)


def config_files():
    """The paru.conf files that exist: /etc and the user's own (paru reads the user's one first)."""
    candidates = [SYSTEM_CONF, os.path.join(fn.home, ".config", "paru", "paru.conf")]
    return [path for path in candidates if os.path.isfile(path)]


def status(path):
    """Return on / off / other / no-paru for one paru.conf."""
    try:
        result = subprocess.run([TOOL, "--status", "--file", path], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return "off"
    return result.stdout.strip() or "off"


def effective_state(states):
    """The state paru acts on: the last file in config_files() order wins (the user's own paru.conf)."""
    return states[-1] if states else "no-paru"


def current_state():
    """The state paru acts on for the user ATT runs for."""
    return effective_state([status(path) for path in config_files()])


def set_enabled(enable):
    """Switch the check on or off in every paru.conf; return the files that kept another PreBuildCommand."""
    action = "--enable" if enable else "--disable"
    fn.log_subsection(f"AUR check: {'on' if enable else 'off'}")
    left_alone = []
    for path in config_files():
        result = subprocess.run([TOOL, action, "--file", path], capture_output=True, text=True)
        if result.returncode == 0:
            fn.log_info(f"{path}: AUR check {'on' if enable else 'off'}")
        else:
            fn.log_warn(f"{path}: left alone (another PreBuildCommand is set)")
            left_alone.append(path)
    return left_alone

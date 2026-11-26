# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

"""Kiro's AUR check: switch kiro-aur-check on or off for paru (PreBuildCommand) and yay (init.lua hook)."""

import os
import subprocess

import functions as fn

TOOL = "/usr/local/bin/kiro-paru-aur-check"
YAY_TOOL = "/usr/local/bin/kiro-yay-aur-check"
SCANNER = "/usr/bin/cachyos-pi-scan"
SYSTEM_CONF = "/etc/paru.conf"
YAY = "/usr/bin/yay"


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


def yay_file():
    """The user's yay Lua config; yay has no system-wide one."""
    return os.path.join(fn.home, ".config", "yay", "init.lua")


def yay_managed():
    """True when yay is installed and kiro-system-files ships the yay switch (yay 13+ reads init.lua)."""
    return os.access(YAY, os.X_OK) and os.access(YAY_TOOL, os.X_OK)


def status(path, tool=TOOL):
    """Return the state one config file is in (paru: on / off / other / no-paru, yay: on / off / no-file)."""
    try:
        result = subprocess.run([tool, "--status", "--file", path], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return "off"
    return result.stdout.strip() or "off"


def effective_state(states):
    """The state paru acts on: the last file in config_files() order wins (the user's own paru.conf)."""
    return states[-1] if states else "no-paru"


def combined_state(paru_state, yay_state):
    """One switch for both helpers: on only when every installed helper has the check on."""
    if paru_state == "other":
        return "other"
    states = [] if paru_state == "no-paru" else [paru_state]
    if yay_state is not None:
        states.append("on" if yay_state == "on" else "off")
    if not states:
        return "no-helper"
    return "on" if all(state == "on" for state in states) else "off"


def current_state():
    """The state of the check for the user ATT runs for, across paru and yay."""
    paru_state = effective_state([status(path) for path in config_files()])
    yay_state = status(yay_file(), YAY_TOOL) if yay_managed() else None
    return combined_state(paru_state, yay_state)


def set_enabled(enable):
    """Switch the check on or off for paru and yay; return the files that kept another PreBuildCommand."""
    action = "--enable" if enable else "--disable"
    word = "on" if enable else "off"
    fn.log_subsection(f"AUR check: {word}")
    left_alone = []
    for path in config_files():
        result = subprocess.run([TOOL, action, "--file", path], capture_output=True, text=True)
        if result.returncode == 0:
            fn.log_info(f"{path}: AUR check {word}")
        else:
            fn.log_warn(f"{path}: left alone (another PreBuildCommand is set)")
            left_alone.append(path)
    if yay_managed():
        path = yay_file()
        result = subprocess.run([YAY_TOOL, action, "--file", path], capture_output=True, text=True)
        if result.returncode == 0:
            fn.log_info(f"{path}: AUR check {word}")
        else:
            fn.log_warn(f"{path}: could not be changed: {result.stderr.strip()}")
    return left_alone

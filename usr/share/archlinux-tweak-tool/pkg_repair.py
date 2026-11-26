# ============================================================
# Author: Erik Dubois
# ============================================================
# Maintenance → Repair tab — logic. Finds package files that are missing or
# changed (pacman -Qkk) and reinstalls only the packages that own them.

import fnmatch
import glob
import os
import re
import subprocess

import functions as fn

# Packages whose files change at runtime by design, so -Qkk always flags them.
QK_IGNORE = ("ohmychadwm-git", "bind", "cups", "nfs-utils")

# Package files changed on purpose: branding, a generated cache, and a helper whose
# install script makes it setgid utmp (flagged on every system).
IGNORE_PATHS = ("/usr/lib/os-release", "/usr/lib/vlc/plugins/plugins.dat", "/usr/lib/utempter/utempter")

# Settings and state: services rewrite these all the time and pacman's backup list
# misses many of them, so a reinstall is never the fix there. /boot belongs to the
# bootloader and mkinitcpio: Kiro's systemd-boot installs drop *-ucode.img on purpose
# (the microcode hook embeds it in the initramfs).
IGNORE_PREFIXES = ("/etc/", "/var/", "/boot/")

DAMAGED_REASONS = ("No such file or directory", "SHA256 checksum mismatch", "Size mismatch")
PERMISSION_REASONS = ("Permissions mismatch", "UID mismatch", "GID mismatch", "Symlink path mismatch")

HOOK_DIRS = ("/usr/share/libalpm/hooks", "/etc/pacman.d/hooks")

# warning: <pkg>: <path> (<reason>)   — "backup file:" lines never match this
_WARNING_RE = re.compile(r"^warning: (?P<pkg>[^:\s]+): (?P<path>/.*) \((?P<reason>[^()]+)\)$")


def _edits_its_targets(hook_path):
    # Stock and local hooks (systemd, icon caches, bootloader updates …) only react to their
    # targets. Kiro/EDU hooks rewrite them — e.g. hiding an upstream session, converting icons.
    return os.path.basename(hook_path).startswith(("kiro-", "edu-"))


def hook_targets(hook_dirs=HOOK_DIRS):
    """Return (path_patterns, packages) that file-editing pacman hooks rewrite after install."""
    patterns, packages = [], set()
    for hook_dir in hook_dirs:
        for hook_path in glob.glob(os.path.join(hook_dir, "*.hook")):
            if not _edits_its_targets(hook_path):
                continue
            hook_type = None
            try:
                with open(hook_path, encoding="utf-8", errors="replace") as hook_file:
                    for raw in hook_file:
                        key, _sep, value = raw.partition("=")
                        key, value = key.strip(), value.strip()
                        if key == "Type":
                            hook_type = value
                        elif key == "Target" and value and not value.startswith("!"):
                            if hook_type == "Package":
                                packages.add(value)
                            else:
                                patterns.append("/" + value.lstrip("/"))
            except OSError:
                continue
    return patterns, packages


def parse_qkk(output, hook_patterns=(), hook_packages=frozenset()):
    """Return {pkg: {"damaged": [paths], "permissions": [paths]}} from pacman -Qkk output."""
    problems = {}
    for line in output.splitlines():
        match = _WARNING_RE.match(line.strip())
        if not match:
            continue
        pkg, path, reason = match.group("pkg"), match.group("path"), match.group("reason")
        if pkg in QK_IGNORE or pkg in hook_packages:
            continue
        if path in IGNORE_PATHS or path.startswith(IGNORE_PREFIXES):
            continue
        if any(fnmatch.fnmatch(path, pattern) for pattern in hook_patterns):
            continue
        if reason in PERMISSION_REASONS and os.path.isdir(path):
            # directories are shared by many packages, whose metadata often disagree
            continue
        if reason in DAMAGED_REASONS:
            kind = "damaged"
        elif reason in PERMISSION_REASONS:
            kind = "permissions"
        else:
            continue
        entry = problems.setdefault(pkg, {"damaged": [], "permissions": []})
        if path not in entry[kind]:
            entry[kind].append(path)
    return problems


def foreign_packages():
    """Return the set of installed packages that are in no sync repo (AUR / local builds)."""
    result = subprocess.run(["pacman", "-Qmq"], capture_output=True, text=True)
    return set(result.stdout.split())


def scan():
    """Run pacman -Qkk and return (problems, foreign_set); slow — call from a thread."""
    fn.log_subsection("Scanning installed packages with pacman -Qkk")
    # pacman translates its warnings; the parser needs the English ones (a Dutch picard flagged nothing)
    result = subprocess.run(["pacman", "-Qkk"], capture_output=True, text=True, env={**os.environ, "LC_ALL": "C"})
    patterns, packages = hook_targets()
    problems = parse_qkk(result.stderr, patterns, packages)
    fn.log_info(f"Repair scan: {len(problems)} package(s) with damaged or missing files")
    return problems, foreign_packages()


def reinstall(packages):
    """Reinstall the given repo packages in a terminal; returns the Popen."""
    fn.log_subsection(f"Reinstalling: {' '.join(packages)}")
    return fn.launch_pacman_reinstall_in_terminal(" ".join(packages))

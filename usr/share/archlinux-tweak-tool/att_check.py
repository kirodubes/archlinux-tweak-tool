# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
#
# att-check engine — read-only, per-page compatibility preflight.
#
# Walks every page ATT would show (page list + visibility guards read from
# gui.py by AST, so a new page can never be silently skipped), resolves the
# packages each page can install against the enabled repos, and runs the tool
# and path probes each page needs. Never changes the system: no pacman -Sy,
# no sudo, no writes except the optional Markdown report.
"""Per-page compatibility preflight for ArchLinux Tweak Tool."""

import argparse
import ast
import datetime
import importlib
import os
import platform
import re
import shutil
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")

import functions as fn  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACMAN_CONF = os.environ.get("ATT_CHECK_PACMAN_CONF", "/etc/pacman.conf")

# Install entry points and the index of the argument holding the package name(s).
_INSTALL_CALLS = {
    "launch_pacman_install_in_terminal": (0, "repo"),
    "install_package": (1, "repo"),
    "launch_aur_install_in_terminal": (1, "aur"),
}

# The Kiro naming prefixes back up data/nemesis_packages.txt for ATT installs whose copy
# predates the generated list (it was hand-kept and badly incomplete until 2026-09-28).
_NEMESIS_PREFIXES = ("kiro-", "celestial-", "surfn-", "neo-candy-", "edu-")

PASS, WARN, FAIL, HIDDEN, NA, UNCHECKED = "PASS", "WARN", "FAIL", "HIDDEN", "N/A", "UNCHECKED"
_ESP_DIRS = ("/boot/efi", "/efi", "/boot")


# ── system facts ────────────────────────────────────────────────────


def _run(cmd, timeout=30):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return res.returncode, res.stdout
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def _which(binary):
    return shutil.which(binary) is not None


def _os_release(key):
    try:
        for line in open("/etc/os-release"):
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return ""


def _enabled_repos():
    repos = []
    try:
        for line in open(PACMAN_CONF):
            s = line.strip()
            if s.startswith("[") and s.endswith("]") and s != "[options]":
                repos.append(s[1:-1])
    except OSError:
        pass
    return repos


def _root_fstype():
    _, out = _run(["findmnt", "-no", "FSTYPE", "/"])
    return out.strip() or "unknown"


def _init_system():
    # sd_booted() semantics; /proc/1/comm lies inside PID namespaces (containers, sandboxes).
    return "systemd" if os.path.isdir("/run/systemd/system") else "non-systemd"


def _graphical_login():
    """Return (type, desktop) of the user's x11/wayland logind session, e.g. when run over SSH."""
    _, out = _run(["loginctl", "list-sessions", "--no-legend"])
    for sid in (line.split()[0] for line in out.splitlines() if line.strip()):
        _, props = _run(["loginctl", "show-session", sid, "-p", "Name", "-p", "Type", "-p", "Desktop"])
        info = dict(line.split("=", 1) for line in props.splitlines() if "=" in line)
        if info.get("Name") == fn.sudo_username and info.get("Type") in ("x11", "wayland"):
            return info["Type"], info.get("Desktop", "")
    return "", ""


def _session():
    env = os.environ.get("XDG_SESSION_TYPE", "")
    if env in ("x11", "wayland"):
        return env
    return _graphical_login()[0] or env or "none"


def _desktop():
    # /etc/att/current_desktop is what ATT's own detect-desktop resolved last run; running
    # that script here would write to /etc, so fall back to the session variables instead.
    try:
        val = open("/etc/att/current_desktop").read().strip()
        if val:
            return val
    except OSError:
        pass
    for key in ("XDG_CURRENT_DESKTOP", "DESKTOP_SESSION", "XDG_SESSION_DESKTOP"):
        if os.environ.get(key):
            return os.environ[key]
    return _graphical_login()[1] or "none"


def _initramfs_tool():
    if _which("mkinitcpio"):
        return "mkinitcpio"
    if _which("dracut"):
        return "dracut"
    return "none"


def _bootloader():
    # systemd-boot and Limine publish LoaderInfo in efivars, readable without root. Fall back to
    # ATT's own detection, which needs the ESP readable (it often is 0700 on systemd-boot installs).
    try:
        for name in os.listdir("/sys/firmware/efi/efivars"):
            if name.startswith("LoaderInfo-"):
                info = open(os.path.join("/sys/firmware/efi/efivars", name), "rb").read()[4:]
                info = info.decode("utf-16-le", "ignore").rstrip("\x00").lower()
                if info.startswith("systemd-boot"):
                    return "systemd-boot"
                if info.startswith("limine"):
                    return "limine"
    except OSError:
        pass
    return importlib.import_module("plymouth").detect_bootloader()


def _esp_readable():
    return all(os.access(d, os.R_OK | os.X_OK) for d in _ESP_DIRS if os.path.isdir(d))


def collect_facts():
    """Return the system facts shown in the report header."""
    return {
        "distro": fn.distr,
        "label": fn.get_distro_label(),
        "pretty": _os_release("PRETTY_NAME") or fn.distr,
        "kernel": platform.release(),
        "session": _session(),
        "desktop": _desktop(),
        "init": _init_system(),
        "bootloader": _bootloader(),
        "esp_readable": _esp_readable(),
        "initramfs": _initramfs_tool(),
        "root_fs": _root_fstype(),
        "repos": _enabled_repos(),
        "aur_helper": fn.get_aur_helper() or "none",
    }


# ── package index ───────────────────────────────────────────────────


class PackageIndex:
    """Installed / available lookups against the enabled sync DBs (no refresh)."""

    def __init__(self, facts):
        self.facts = facts
        _, out = _run(["pacman", "-Qq"])
        self.installed = set(out.split())
        self.repo_of = {}
        _, out = _run(["pacman", "--config", PACMAN_CONF, "-Sl"])
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                self.repo_of.setdefault(parts[1], parts[0])
        _, out = _run(["pacman", "--config", PACMAN_CONF, "-Sg"])
        self.groups = {line.split()[0] for line in out.splitlines() if line.strip()}
        self.nemesis = fn.load_nemesis_packages()
        self._provides = {}

    def _resolve_provider(self, name):
        if name not in self._provides:
            rc, out = _run(["pacman", "--config", PACMAN_CONF, "-Sp", "--print-format", "%r", name], timeout=15)
            self._provides[name] = out.split()[0] if rc == 0 and out.strip() else None
        return self._provides[name]

    def status(self, name, kind="repo", repo_hint=None):
        """Return (obtainable, text) for one package name."""
        if name in self.installed:
            return True, "installed"
        if kind == "aur":
            helper = self.facts["aur_helper"]
            if helper != "none":
                return True, f"AUR via {helper}"
            return False, "AUR package, no AUR helper installed"
        if name in self.repo_of:
            return True, f"available ({self.repo_of[name]})"
        if name in self.groups:
            return True, "available (group)"
        provider = self._resolve_provider(name)
        if provider:
            return True, f"available via provides ({provider})"
        repos = self.facts["repos"]
        if (name in self.nemesis or name.startswith(_NEMESIS_PREFIXES)) and "nemesis_repo" not in repos:
            return False, "needs nemesis_repo (not enabled)"
        if repo_hint and repo_hint not in repos:
            return False, f"needs {repo_hint} (not enabled)"
        return False, "not found in the enabled repos"


# ── package discovery ───────────────────────────────────────────────


def _const_strings(node):
    """Package names in a constant str / list / tuple node, or None when not constant."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.split()
    if isinstance(node, (ast.List, ast.Tuple)):
        names = []
        for elt in node.elts:
            sub = _const_strings(elt)
            if sub is None:
                return None
            names.extend(sub)
        return names
    return None


def _simple_assignments(scope):
    """Map name -> constant package list for plain `x = "pkg"` / `x = [...]` in one scope."""
    found = {}
    for node in ast.walk(scope):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            names = _const_strings(node.value)
            if names is not None:
                found.setdefault(node.targets[0].id, names)
    return found


def scan_module(module):
    """AST-scan one module: return ({package: kind}, dynamic_reference_count)."""
    path = os.path.join(BASE_DIR, module + ".py")
    try:
        tree = ast.parse(open(path).read())
    except (OSError, SyntaxError):
        return {}, 0
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    scope_consts = {tree: _simple_assignments(tree)}
    packages, dynamic = {}, 0
    # One pass over every call, so calls inside nested callbacks are counted exactly once.
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        spec = _INSTALL_CALLS.get(node.func.attr)
        if spec is None or len(node.args) <= spec[0]:
            continue
        arg = node.args[spec[0]]
        names = _const_strings(arg)
        if names is None and isinstance(arg, ast.Name):
            # Resolve the name from the innermost enclosing function outwards, then the module.
            scope = parents.get(node)
            while names is None and scope is not None:
                if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
                    if scope not in scope_consts:
                        scope_consts[scope] = _simple_assignments(scope)
                    names = scope_consts[scope].get(arg.id)
                scope = parents.get(scope)
        if names is None:
            dynamic += 1
            continue
        for name in names:
            packages.setdefault(name, spec[1])
    return packages, dynamic


_SUBPROCESS_CALLS = {"Popen", "run", "check_output", "call", "check_call", "subprocess_run", "subprocess_call"}
_COMMAND_PREFIXES = {"sudo", "pkexec", "env", "nohup", "setsid", "exec"}
# Install forms only (-S / -Sy / -Syu / -Su); -Sc, -Ss, -Si, -Sl, -Sp are not installs.
_SHELL_INSTALL = re.compile(r"\bpacman[ \t]+-S(?:yy?)?u?[ \t]+([^;&|'\"\n)]+)")
# A program the code first probes for (shutil.which / path.exists) is an optional fallback, not a requirement.
_GUARD_CALLS = {"which", "exists", "isfile"}
# Calls whose string arguments are prose for humans, never commands.
_PROSE_CALLS = re.compile(r"^(log_\w+|debug_print|show_in_app_notification|set_markup|set_text|set_label|"
                          r"set_tooltip_text|set_tooltip_markup|Label|print)$")
_SCRIPT_REF = re.compile(r"data/bin/([A-Za-z0-9_.-]+)")
_PKG_NAME = re.compile(r"^[a-z0-9@._+-]+$")


def _command_from_argv(elts):
    """First real program in a constant argv list, skipping sudo/env-style prefixes and their flags."""
    skip_next = False
    for elt in elts:
        if skip_next:
            skip_next = False
            continue
        if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str)):
            return None
        word = elt.value
        if word in _COMMAND_PREFIXES or word.startswith("-") or "=" in word:
            skip_next = word in ("-u", "--user")
            continue
        return os.path.basename(word)
    return None


def _shell_packages(text):
    names = []
    for match in _SHELL_INSTALL.finditer(text):
        names += [w for w in match.group(1).split() if not w.startswith("-") and _PKG_NAME.match(w)]
    return names


def scan_commands(module):
    """AST-scan one module for shell-string installs, directly run programs and data/bin scripts."""
    path = os.path.join(BASE_DIR, module + ".py")
    try:
        tree = ast.parse(open(path).read())
    except (OSError, SyntaxError):
        return set(), set(), set()
    prose = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                prose.add(id(first.value))
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if _PROSE_CALLS.match(name):
                prose.update(id(sub) for arg in node.args for sub in ast.walk(arg))
    packages, tools, scripts, guarded = set(), set(), set(), set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in _GUARD_CALLS
                and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
            guarded.add(os.path.basename(node.args[0].value))
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in prose:
            packages.update(_shell_packages(node.value))
            scripts.update(_SCRIPT_REF.findall(node.value))
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in _SUBPROCESS_CALLS and node.args):
            continue
        first = node.args[0]
        if isinstance(first, (ast.List, ast.Tuple)):
            tool = _command_from_argv(first.elts)
        elif isinstance(first, ast.Constant) and isinstance(first.value, str):
            tool = _command_from_argv([ast.Constant(w) for w in first.value.split()])
        elif isinstance(first, ast.JoinedStr) and first.values and isinstance(first.values[0], ast.Constant):
            tool = _command_from_argv([ast.Constant(w) for w in str(first.values[0].value).split()])
        else:
            tool = None
        if tool and _PKG_NAME.match(tool) and tool not in ("bash", "sh"):
            tools.add(tool)
    return packages, tools - guarded, scripts


def _script_packages(script):
    try:
        return _shell_packages(open(os.path.join(BASE_DIR, "data", "bin", script)).read())
    except OSError:
        return []


def harvest(obj, out=None, repo=None):
    """Collect {package: repo_hint} from catalog dicts using package/packages/pkgname keys."""
    out = {} if out is None else out
    if isinstance(obj, dict):
        if isinstance(obj.get("repo"), str):
            repo = obj["repo"]
        for key, value in obj.items():
            if key in ("package", "packages", "pkgname"):
                values = value.split() if isinstance(value, str) else value
                for name in values if isinstance(values, (list, tuple)) else []:
                    if isinstance(name, str):
                        out.setdefault(name, repo)
            else:
                harvest(value, out, repo)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            harvest(item, out, repo)
    return out


def _family_packages(module, attr, prefix):
    families = getattr(importlib.import_module(module), attr)
    return {prefix + entry[0]: None for _, members in families for entry in members}


def _desktop_packages():
    desktopr = importlib.import_module("desktopr")
    return {p: None for pkgs in desktopr._get_desktop_packages().values() for p in pkgs}


def _icon_set(key):
    return harvest(importlib.import_module("icons").ICON_SETS[key]["families"])


def _icon_horst():
    icons = importlib.import_module("icons")
    families = [icons.ICON_SETS[set_key]["families"].get(fam, []) for _, set_key, fams in icons.HORST_TABS
                for fam in fams]
    return harvest(families)


def _kernels():
    return {k["pkg"]: ("chaotic-aur" if k.get("requires_chaotic") else None)
            for k in importlib.import_module("kernel").KERNELS}


# ── probes ──────────────────────────────────────────────────────────


def _probe_bin(binary, hard=True):
    return lambda facts: (_which(binary), f"`{binary}` present", hard)


def _probe_path(path, hard=True):
    return lambda facts: (os.path.exists(path), f"{path} exists", hard)


def _probe_systemd(facts):
    return facts["init"] == "systemd" and _which("systemctl"), "systemd is init (systemctl)", True


def _probe_bootloader(facts):
    if facts["bootloader"] == "unknown" and not facts["esp_readable"]:
        return False, "bootloader unknown: the ESP is only readable by root, re-check with ATT itself", False
    return facts["bootloader"] != "unknown", f"bootloader detected ({facts['bootloader']})", True


def _probe_bootloader_tool(facts):
    tool = {"systemd-boot": "bootctl", "grub": "grub-mkconfig", "limine": "limine", "refind": "refind-install"}.get(
        facts["bootloader"]
    )
    if tool is None:
        return False, "bootloader tool (no bootloader detected)", False
    return _which(tool), f"bootloader tool `{tool}` present", True


def _probe_initramfs(facts):
    return facts["initramfs"] != "none", f"initramfs generator ({facts['initramfs']})", True


def _probe_kernel_hook(facts):
    if not (facts["distro"] == "arch" and facts["bootloader"] == "systemd-boot"):
        return True, "kernel-install hook (not needed here)", False
    ok = fn.check_package_installed("pacman-hook-kernel-install")
    return ok, "pacman-hook-kernel-install (arch + systemd-boot guard)", False


def _probe_btrfs(facts):
    if facts["root_fs"] == "btrfs":
        return True, "root filesystem is btrfs", True
    return False, f"not used (root is {facts['root_fs']}); ATT shows this page disabled", True


def _probe_desktop(facts):
    return facts["desktop"] != "none", f"desktop detected ({facts['desktop']})", False


def _probe_session(facts):
    return facts["session"] in ("x11", "wayland"), f"graphical session ({facts['session']})", False


def _probe_wheel(facts):
    _, out = _run(["getent", "group", "wheel"])
    return bool(out.strip()), "`wheel` group exists", False


def _probe_display_manager(facts):
    link = "/etc/systemd/system/display-manager.service"
    ok = os.path.islink(link)
    name = os.path.basename(os.readlink(link)).replace(".service", "") if ok else "none"
    return ok, f"display manager enabled ({name})", False


# ── page map ────────────────────────────────────────────────────────
#
# One entry per stack.add_titled() title in gui.py. `modules` are AST-scanned
# for install calls, `catalog` adds catalog-driven packages, `probes` are the
# tools/paths the page needs. A title in gui.py missing here reports UNMAPPED.

# Developer-only page (shown only with --dev): hidden on every system, so reporting it says nothing about the box.
_SKIPPED_PAGES = {"Dev"}

PAGES = {
    "Accessibility": {
        "modules": ("accessibility", "accessibility_gui"),
        "catalog": lambda: harvest(importlib.import_module("accessibility").ACCESSIBILITY_APPS),
        "probes": (_probe_session,),
    },
    "AI Tools": {"modules": ("ai", "ai_gui")},
    "Arc themes": {
        "modules": ("themes", "themes_gui"),
        "catalog": lambda: _family_packages("themes", "THEME_FAMILIES", "kiro-arc-"),
        "probes": (_probe_path("/etc/environment", hard=False),),
        "choose_one": True,
    },
    "Autostart": {"modules": ("autostart",), "probes": (_probe_path(os.path.join(fn.home, ".config")),)},
    "Backup": {
        "modules": ("backup", "backup_gui"),
        "catalog": lambda: harvest(importlib.import_module("backup").BACKUP_APPS),
        "choose_one": True,
    },
    "Btrfs": {"modules": ("btrfs", "btrfs_gui"), "catalog": lambda: {p: None for p in
              importlib.import_module("btrfs").PACKAGES}, "probes": (_probe_btrfs,)},
    "Celestial themes": {
        "modules": ("celestial", "celestial_gui"),
        "catalog": lambda: _family_packages("celestial", "CELESTIAL_FAMILIES", "celestial-"),
        "probes": (_probe_path("/etc/environment", hard=False),),
        "choose_one": True,
    },
    "Desktop": {
        "modules": ("desktopr", "desktopr_gui"),
        "catalog": _desktop_packages,
        "probes": (_probe_display_manager,),
        "choose_one": True,
    },
    "Desktop - Wayland": {
        "modules": ("wayland", "wayland_gui"),
        "catalog": lambda: harvest(importlib.import_module("wayland").WAYLAND_WMS),
        "choose_one": True,
    },
    "Fastfetch": {"modules": ("fastfetch", "fastfetch_gui")},
    "Icons Horst": {"catalog": _icon_horst, "choose_one": True},
    "Icons Neo Candy": {"catalog": lambda: _icon_set("neocandy"), "choose_one": True},
    "Icons Surfn": {"catalog": lambda: _icon_set("surfn"), "choose_one": True},
    "ISO": {"modules": ("iso", "iso_gui")},
    "Kernels": {
        "modules": ("kernel", "kernel_gui"),
        "catalog": _kernels,
        "probes": (_probe_bootloader, _probe_bootloader_tool, _probe_initramfs, _probe_kernel_hook),
        "choose_one": True,
    },
    "Locale": {"modules": ("locale_settings", "locale_gui"),
               "probes": (_probe_bin("localectl"), _probe_bin("timedatectl"), _probe_bin("locale-gen"))},
    "Logging": {"modules": ("log_callbacks", "logging_gui"), "probes": (_probe_bin("journalctl"),)},
    "Maintenance": {"modules": ("maintenance", "maintenance_gui")},
    "Network": {"modules": ("network_gui",), "probes": (_probe_systemd,)},
    "Office": {
        "modules": ("office", "office_gui"),
        "catalog": lambda: harvest(importlib.import_module("office").OFFICE_APPS),
        "choose_one": True,
    },
    "Packages": {"modules": ("packages", "packages_gui")},
    "Pacman": {"modules": ("pacman", "pacman_gui", "pacman_functions"), "probes": (_probe_path(PACMAN_CONF),)},
    "Plymouth": {"modules": ("plymouth", "plymouth_gui"), "catalog": lambda: {"plymouth": None},
                 "probes": (_probe_initramfs, _probe_bootloader)},
    "Privacy": {"modules": ("privacy", "privacy_gui"), "probes": (_probe_path("/etc/hosts"),)},
    "Performance": {"modules": ("performance", "performance_gui"), "probes": (_probe_systemd,)},
    "Sddm": {"modules": ("sddm", "sddm_gui", "functions_sddm"), "probes": (_probe_bin("sddm", hard=False),)},
    "Services": {"modules": ("services", "services_gui"), "probes": (_probe_systemd,)},
    "Shells": {"modules": ("shell", "shell_gui", "zsh_theme"),
               "probes": (_probe_path("/etc/shells"), _probe_bin("chsh"))},
    "Software": {"modules": ("software", "software_gui"), "choose_one": True},
    "Streamline": {"modules": ("streamline", "streamline_gui"),
                   "probes": (_probe_path(os.path.join(BASE_DIR, "data", "streamline_packages.txt")),)},
    "System": {"modules": ("system", "system_gui")},
    "Themer": {"modules": ("themer", "themer_gui")},
    "User": {"modules": ("user", "user_gui"),
             "probes": (_probe_bin("useradd"), _probe_bin("usermod"), _probe_bin("sudo"), _probe_wheel)},
    "Wallpaper": {"modules": ("wallpaper", "wallpaper_gui"), "probes": (_probe_session, _probe_desktop)},
}


# ── gui.py: page list + guards ──────────────────────────────────────


def _set_constant(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            try:
                return set(ast.literal_eval(node.value))
            except ValueError:
                return set()
    return set()


def read_gui_pages():
    """Return ([(title, guard_source_or_None)], sddm_hidden, iso_hidden) in sidebar order."""
    tree = ast.parse(open(os.path.join(BASE_DIR, "gui.py")).read())
    pages = []

    def visit(node, guard):
        if isinstance(node, ast.If):
            for child in node.body:
                visit(child, ast.unparse(node.test))
            for child in node.orelse:
                visit(child, guard)
            return
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "add_titled"
                and len(node.value.args) == 3 and isinstance(node.value.args[2], ast.Constant)):
            pages.append((node.value.args[2].value, guard))
        for child in ast.iter_child_nodes(node):
            visit(child, guard)

    for node in tree.body:
        visit(node, None)
    return pages, _set_constant(tree, "_SDDM_HIDDEN_DISTROS"), _set_constant(tree, "_ISO_HIDDEN_DISTROS")


# The exact gui.py guard each mirror below was written against (ast.unparse form).
# If gui.py's condition changes, the page reports a guard-drift WARN until this is updated.
_EXPECTED_GUARDS = {
    "ISO": "fn.distr not in _ISO_HIDDEN_DISTROS",
    "Sddm": "fn.distr not in _SDDM_HIDDEN_DISTROS and (not (fn.check_service_enabled('plasma-login') "
            "or fn.check_service_enabled('plasmalogin')))",
    "Streamline": "fn.get_distro_label() == 'Kiro'",
}


def hidden_reason(title, guard, facts, sddm_hidden, iso_hidden):
    """Mirror gui.py's visibility guards; return a reason string when the page is hidden."""
    if guard != _EXPECTED_GUARDS.get(title):
        return f"unrecognised guard in gui.py: {guard}"
    if guard is None:
        return None
    if title == "Sddm":
        if facts["distro"] in sddm_hidden:
            return f"hidden on {facts['distro']} (_SDDM_HIDDEN_DISTROS)"
        if fn.check_service_enabled("plasma-login") or fn.check_service_enabled("plasmalogin"):
            return "plasma-login manager is enabled"
        return None
    if title == "ISO":
        return f"hidden on {facts['distro']} (_ISO_HIDDEN_DISTROS)" if facts["distro"] in iso_hidden else None
    if title == "Streamline":
        return None if facts["label"] == "Kiro" else "Kiro-only page"
    return None


# ── evaluation ──────────────────────────────────────────────────────


def evaluate_page(title, facts, index):
    """Return a result dict for one visible page."""
    spec = PAGES[title]
    packages, dynamic = {}, 0
    for module in spec.get("modules", ()):
        found, dyn = scan_module(module)
        dynamic += dyn
        for name, kind in found.items():
            packages.setdefault(name, (kind, None))
    catalog = spec.get("catalog")
    if catalog:
        for name, repo_hint in catalog().items():
            packages.setdefault(name, ("repo", repo_hint))
    tools, scripts = set(), set()
    for module in spec.get("modules", ()):
        shell_pkgs, mod_tools, mod_scripts = scan_commands(module)
        tools |= mod_tools
        scripts |= mod_scripts
        for name in shell_pkgs:
            packages.setdefault(name, ("repo", None))
    for script in scripts:
        for name in _script_packages(script):
            packages.setdefault(name, ("repo", None))

    pkg_rows = []
    for name in sorted(packages):
        kind, repo_hint = packages[name]
        ok, text = index.status(name, kind, repo_hint)
        pkg_rows.append((name, ok, text))
    probe_rows = [probe(facts) for probe in spec.get("probes", ())]
    # A program the page can install itself is covered by the package rows above.
    for tool in sorted(tools - set(packages)):
        present = _which(tool)
        probe_rows.append((present, f"`{tool}` {'present' if present else 'not installed'} (the page runs it)", False))
    for script in sorted(scripts):
        probe_rows.append((os.path.isfile(os.path.join(BASE_DIR, "data", "bin", script)),
                           f"helper script data/bin/{script} shipped", True))

    obtainable = sum(1 for _, ok, _ in pkg_rows if ok)
    missing = [row for row in pkg_rows if not row[1]]
    hard_fail = [row for row in probe_rows if not row[0] and row[2]]
    soft_fail = [row for row in probe_rows if not row[0] and not row[2]]

    if title == "Btrfs" and hard_fail:
        verdict = NA
    elif hard_fail or (pkg_rows and obtainable == 0):
        verdict = FAIL
    elif missing or soft_fail:
        verdict = WARN
    elif not pkg_rows and not probe_rows:
        verdict = UNCHECKED
    else:
        verdict = PASS
    return {"title": title, "verdict": verdict, "packages": pkg_rows, "probes": probe_rows,
            "obtainable": obtainable, "dynamic": dynamic}


def run_checks():
    """Return (facts, [page results]) for every page in gui.py."""
    facts = collect_facts()
    index = PackageIndex(facts)
    gui_pages, sddm_hidden, iso_hidden = read_gui_pages()
    results = []
    gui_pages = [(t, g) for t, g in gui_pages if t not in _SKIPPED_PAGES]
    for title, guard in gui_pages:
        if title not in PAGES:
            results.append({"title": title, "verdict": FAIL, "packages": [], "dynamic": 0, "obtainable": 0,
                            "probes": [(False, "UNMAPPED: add this page to att_check.PAGES", True)]})
            continue
        reason = hidden_reason(title, guard, facts, sddm_hidden, iso_hidden)
        if reason:
            verdict = WARN if reason.startswith("unrecognised") else HIDDEN
            results.append({"title": title, "verdict": verdict, "reason": reason, "packages": [], "probes": [],
                            "dynamic": 0, "obtainable": 0})
            continue
        results.append(evaluate_page(title, facts, index))
    known = {t for t, _ in gui_pages}
    for title in sorted(set(PAGES) - known):
        results.append({"title": title, "verdict": WARN, "packages": [], "dynamic": 0, "obtainable": 0,
                        "probes": [(False, "STALE: in att_check.PAGES but no longer in gui.py", False)]})
    return facts, results


# ── output ──────────────────────────────────────────────────────────


def _colors(enabled):
    codes = {PASS: "32", WARN: "33", FAIL: "31", HIDDEN: "36", NA: "36", UNCHECKED: "2", "dim": "2", "bold": "1"}
    if not enabled:
        return {k: ("", "") for k in codes}
    return {k: (f"\033[{v}m", "\033[0m") for k, v in codes.items()}


def _na_note(result):
    return next((label for ok, label, _ in result["probes"] if not ok), "not used on this system")


def summary(results):
    """Return [(verdict, text)] per verdict present; every verdict but PASS names its pages."""
    parts = []
    # N/A pages (e.g. Btrfs on the default ext4) are expected, not a result, so they stay out of the summary.
    for verdict in (PASS, WARN, FAIL, UNCHECKED, HIDDEN):
        titles = [r["title"] for r in results if r["verdict"] == verdict]
        if titles:
            names = "" if verdict == PASS else f" ({', '.join(titles)})"
            parts.append((verdict, f"{verdict} {len(titles)}{names}"))
    return parts


def _problem_lines(result, verbose):
    lines = []
    if "reason" in result:
        lines.append(("dim", result["reason"]))
    if result["verdict"] == UNCHECKED:
        lines.append(("dim", "nothing statically checkable on this page (no install calls or probes)"))
    for ok, label, hard in result["probes"]:
        if verbose or not ok:
            tag = PASS if ok else (NA if result["verdict"] == NA else FAIL if hard else WARN)
            lines.append((tag, label))
    for name, ok, text in result["packages"]:
        if verbose or not ok:
            lines.append((PASS if ok else WARN, f"{name}: {text}"))
    return lines


def print_terminal(facts, results, verbose, use_color):
    """Print the per-page blocks and the summary table."""
    c = _colors(use_color)
    bold, dim = c["bold"], c["dim"]
    print(f"{bold[0]}ATT compatibility check — static preflight{bold[1]}")
    print(f"{dim[0]}Checks prerequisites only (packages obtainable, tools and files present). "
          f"Nothing on this system was changed. UNCHECKED = page has nothing statically checkable.{dim[1]}\n")
    for key in ("pretty", "distro", "label", "kernel", "session", "desktop", "init", "bootloader", "initramfs",
                "root_fs", "aur_helper"):
        print(f"  {key:<11} {facts[key]}")
    print(f"  {'repos':<11} {', '.join(facts['repos']) or 'none'}\n")

    for r in results:
        if r["verdict"] == NA:
            print(f"{dim[0]}{' ' * 11} {r['title']}  {_na_note(r)}{dim[1]}")
            continue
        col = c[r["verdict"]]
        total = len(r["packages"])
        pkg_note = f"  {r['obtainable']}/{total} packages obtainable" if total else ""
        dyn_note = f", {r['dynamic']} installs decided at runtime, not checked" if r["dynamic"] else ""
        print(f"{col[0]}[{r['verdict']:^9}]{col[1]} {bold[0]}{r['title']}{bold[1]}{dim[0]}{pkg_note}{dyn_note}{dim[1]}")
        for tag, text in _problem_lines(r, verbose):
            tc = c[tag]
            print(f"             {tc[0]}{text}{tc[1]}")

    print(f"\n{bold[0]}Summary{bold[1]}")
    for verdict, text in summary(results):
        print(f"  {c[verdict][0]}{text}{c[verdict][1]}")


def write_markdown(facts, results, verbose):
    """Write att-check-<distro>-<date>.md in the current directory; return its path."""
    date = datetime.date.today().strftime("%Y.%m.%d")
    path = os.path.join(os.getcwd(), f"att-check-{facts['distro']}-{date}.md")
    out = [f"# ATT compatibility check — {facts['pretty']} ({date})", "",
           "_Static preflight: prerequisites only, nothing was changed on the system. "
           "UNCHECKED = the page has nothing statically checkable._", "",
           "| Fact | Value |", "|---|---|"]
    for key in ("distro", "label", "kernel", "session", "desktop", "init", "bootloader", "initramfs", "root_fs",
                "aur_helper"):
        out.append(f"| {key} | {facts[key]} |")
    out.append(f"| repos | {', '.join(facts['repos']) or 'none'} |")
    out += ["", "## Summary", ""] + [f"- {text}" for _, text in summary(results)]
    out += ["", "## Overview", "", "| Page | Verdict | Packages obtainable | Notes |", "|---|---|---|---|"]
    for r in results:
        if r["verdict"] == NA:
            note = _na_note(r).replace("not used (", "", 1).replace(")", "", 1)
            out.append(f"| {r['title']} | not used | - | {note} |")
            continue
        total = len(r["packages"])
        pkgs = f"{r['obtainable']}/{total}" if total else "-"
        problems = [text for tag, text in _problem_lines(r, False) if tag != PASS and r["verdict"] != UNCHECKED]
        notes = "; ".join(problems[:3]) + (f" (+{len(problems) - 3} more)" if len(problems) > 3 else "")
        out.append(f"| {r['title']} | {r['verdict']} | {pkgs} | {notes.replace('|', '/')} |")
    out += ["", "## Details", ""]
    for r in results:
        lines = _problem_lines(r, verbose)
        if not lines or r["verdict"] == NA:
            continue
        out += [f"### {r['title']} — {r['verdict']}", ""]
        out += [f"- {tag}: {text}" for tag, text in lines]
        out.append("")
    with open(path, "w") as f:
        f.write("\n".join(out))
    return path


def main():
    """Entry point for the att-check CLI."""
    parser = argparse.ArgumentParser(prog="att-check", description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="list every package and probe, not only problems")
    parser.add_argument("--no-report", action="store_true", help="do not write the Markdown report file")
    parser.add_argument("--no-color", action="store_true", help="disable colored output")
    args = parser.parse_args()

    if os.geteuid() == 0:
        fn.log_error("att-check: run as your normal user, not root.")
        return 1
    if not _which("pacman"):
        fn.log_error("att-check: pacman not found, this is not an Arch-based system.")
        return 1

    facts, results = run_checks()
    use_color = sys.stdout.isatty() and not args.no_color and "NO_COLOR" not in os.environ
    print_terminal(facts, results, args.verbose, use_color)
    if not args.no_report:
        try:
            fn.log_info(f"Report written to {write_markdown(facts, results, args.verbose)}")
        except OSError as e:
            fn.log_error(f"Could not write the report: {e}")
    return 1 if any(r["verdict"] == FAIL for r in results) else 0

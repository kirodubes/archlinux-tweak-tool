# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
# pylint:disable=C0103,C0116,C0411,C0413,I1101,R1705,W0621,W0611,W0622
#
# TABLE OF CONTENTS
# =================
# 1. Constants & Paths
# 2. General Utilities
# 3. UI Utilities
# 4. App Control
# 5. Package Management
# 6. Terminal Launch
# 7. Threading & Queue
# 8. Services (systemd)
# 9. Network & Samba
# 10. Shell
# 11. Privacy
# 12. Fastfetch
# 13. Logging/Pacman Log

import gi

gi.require_version("Gtk", "4.0")

from os import unlink, execl, mkdir, makedirs, listdir, getpid, stat  # noqa: F401
from os import path, getlogin, system, readlink  # noqa: F401
from distro import id
import os
from gi.repository import GLib, Gtk, Gdk, GdkPixbuf
import sys
import threading
import shutil
import struct
import psutil
import datetime
import subprocess
import logging
import re
import time
import pwd
import json
from queue import Queue  # noqa: F401

# Debug flag - set by archlinux-tweak-tool when --debug flag is used
DEBUG = False

# Dev flag - set by archlinux-tweak-tool when --dev flag is used
DEV = False

LOG_FILE = None

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# =====================================================
# Color support detection
# =====================================================


def _has_color_support():
    """Check if terminal supports colors"""
    try:
        if not sys.stdout.isatty():
            return False
        result = subprocess.run(["tput", "colors"], capture_output=True, text=True, timeout=1)
        return result.returncode == 0 and int(result.stdout.strip()) >= 8
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return False


COLORS_ENABLED = _has_color_support()

# Color codes
if COLORS_ENABLED:
    RED = "\033[31m"
    GREEN = "\033[32m"
    GREEN_BOLD = "\033[1;32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
else:
    RED = ""
    GREEN = ""
    GREEN_BOLD = ""
    YELLOW = ""
    BLUE = ""
    PURPLE = ""
    CYAN = ""
    RESET = ""


def set_debug(value):
    """Set the global DEBUG flag"""
    global DEBUG
    DEBUG = value


def set_dev(value):
    global DEV
    DEV = value


def _write_log(text):
    if LOG_FILE:
        LOG_FILE.write(_ANSI_RE.sub("", text) + "\n")
        LOG_FILE.flush()


def init_session_log():
    global LOG_FILE
    stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    os.makedirs(att_sessions_dir, exist_ok=True)
    try:
        log_path = os.path.join(att_sessions_dir, f"log_session_{stamp}.log")
        LOG_FILE = open(log_path, "w", buffering=1)
        permissions(log_path)
        log_info(f"Session log: {log_path}")
    except Exception as e:
        log_warn(f"Could not open session log: {e}")


def debug_print(message):
    if DEBUG:
        print(f"{CYAN}[DEBUG]{RESET} {message}")
        _write_log(f"[DEBUG] {message}")


# =====================================================
# Logging functions with color support
# =====================================================
def log_section(message):
    print(f"\n{GREEN_BOLD}[SECTION] {message}{RESET}")
    _write_log(f"\n[SECTION] {message}")


def log_subsection(message):
    print(f"{CYAN}[SUB] {message}{RESET}")
    _write_log(f"[SUB] {message}")


def log_info(message):
    print(f"{BLUE}[INFO] {message}{RESET}")
    _write_log(f"[INFO] {message}")


def log_item(message):
    print(f"{BLUE}[INFO]{RESET} {message}")
    _write_log(f"[INFO] {message}")


def log_info_concise(message):
    print(message)
    _write_log(message)


def log_success(message):
    print(f"{GREEN}[OK] {message}{RESET}")
    _write_log(f"[OK] {message}")


def log_warn(message):
    print(f"{YELLOW}[WARN] {message}{RESET}")
    _write_log(f"[WARN] {message}")


def log_tip(message):
    print(f"{YELLOW}[TIP] {message}{RESET}")
    _write_log(f"[TIP] {message}")


def log_error(message, lineno=None, cmd=None):
    print()
    sep = "=" * 75
    print(f"{RED}{sep}{RESET}")
    print(f"{RED}⚠️ ERROR DETECTED{RESET}")
    if lineno:
        print(f"{YELLOW}✳️  Line: {lineno}{RESET}")
    if cmd:
        print(f"{YELLOW}📌  Command: '{cmd}'{RESET}")
    print(message)
    print(f"{RED}{sep}{RESET}")
    print()
    parts = [sep, "ERROR DETECTED"]
    if lineno:
        parts.append(f"Line: {lineno}")
    if cmd:
        parts.append(f"Command: '{cmd}'")
    parts.append(str(message))
    parts.append(sep)
    _write_log("\n" + "\n".join(parts) + "\n")


def info(message):
    """Simple info message (no separators)"""
    print(f"{BLUE}ℹ️  {message}{RESET}")


def success(message):
    """Simple success message (no separators)"""
    print(f"{GREEN}✓ {message}{RESET}")


def warn(message):
    """Simple warning message (no separators)"""
    print(f"{YELLOW}⚠️  {message}{RESET}")


def error(message):
    """Simple error message (no separators)"""
    print(f"{RED}✗ {message}{RESET}")


# =====================================================
# =====================================================
# =====================================================
#                      SECTION 1: CONSTANTS & PATHS
# =====================================================
# =====================================================
# =====================================================

distr = id()

_pkexec_uid = os.environ.get("PKEXEC_UID")
sudo_username = pwd.getpwuid(int(_pkexec_uid)).pw_name if _pkexec_uid else getlogin()
home = "/home/" + str(sudo_username)

gpg_conf = "/etc/pacman.d/gnupg/gpg.conf"
gpg_conf_local = home + "/.gnupg/gpg.conf"

gpg_conf_original = "/usr/share/archlinux-tweak-tool/data/gpg.conf"
gpg_conf_local_original = "/usr/share/archlinux-tweak-tool/data/gpg.conf"

# login managers

# sddm
sddm_default_d1 = "/etc/sddm.conf"
sddm_default_d1_bak = "/etc/sddm.conf-bak"
sddm_default_d2 = "/etc/sddm.conf.d/kde_settings.conf"
sddm_default_d2_bak = "/etc/kde_settings.conf-bak"
sddm_default_d2_dir = "/etc/sddm.conf.d/"
sddm_default_d2_dir_bak = "/etc/sddm.conf.d-bak"
sddm_default_d1_kiro = "/usr/share/archlinux-tweak-tool/data/sddm/sddm.conf"
sddm_default_d2_kiro = "/usr/share/archlinux-tweak-tool/data/sddm.conf.d/kde_settings.conf"
display_manager_service = "/etc/systemd/system/display-manager.service"
icons_default = "/usr/share/icons/default/index.theme"

samba_config = "/etc/samba/smb.conf"

mirrorlist = "/etc/pacman.d/mirrorlist"
pacman = "/etc/pacman.conf"
pacman_att = "/usr/share/archlinux-tweak-tool/data/pacman/pacman.conf"
blank_pacman_att = "/usr/share/archlinux-tweak-tool/data/pacman/blank/pacman.conf"

gtk3_settings = home + "/.config/gtk-3.0/settings.ini"
gtk2_settings = home + "/.gtkrc-2.0"
xfce_config = home + "/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml"
xfce4_terminal_config = home + "/.config/xfce4/terminal/terminalrc"
alacritty_config = home + "/.config/alacritty/alacritty.toml"
alacritty_config_dir = home + "/.config/alacritty"
fastfetch_config = home + "/.config/fastfetch/config.jsonc"
fastfetch_kiro = "/usr/share/archlinux-tweak-tool/data/fastfetch/config.jsonc"
zshrc_kiro = "/usr/share/archlinux-tweak-tool/data/.zshrc"
bashrc_kiro = "/usr/share/archlinux-tweak-tool/data/.bashrc"
fish_config_kiro = "/usr/share/archlinux-tweak-tool/data/fish/config.fish"
kiro_fish_payload_src = "/usr/share/archlinux-tweak-tool/data/fish/usr/share/kiro/fish"
kiro_fish_payload_dst = "/usr/share/kiro/fish"
nsswitch_config = "/etc/nsswitch.conf"
nanorc = "/etc/nanorc"
nanorc_bak = "/etc/nanorc-bak"
nanorc_att = "/usr/share/archlinux-tweak-tool/data/nano/nanorc"


def is_att_nanorc_applied():
    import filecmp

    if not path.isfile(nanorc) or not path.isfile(nanorc_att):
        return False
    try:
        return filecmp.cmp(nanorc, nanorc_att, shallow=False)
    except Exception:
        return False


nanorc_img_default = "/usr/share/archlinux-tweak-tool/images/nanorc.jpg"
nanorc_img_att = "/usr/share/archlinux-tweak-tool/images/nanorc-att.jpg"
att_settings = home + "/.config/archlinux-tweak-tool/att_settings.json"
bd = ".att_backups"
config = home + "/.config/archlinux-tweak-tool/settings.ini"
config_dir = home + "/.config/archlinux-tweak-tool/"
polybar = home + "/.config/polybar/"
desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")


def resolve_desktop():
    global desktop
    script = os.path.join(os.path.dirname(__file__), "data", "bin", "detect-desktop")
    try:
        subprocess.run(["bash", script], check=False, timeout=5)
    except Exception:
        pass
    try:
        with open("/etc/att/current_desktop") as f:
            val = f.read().strip()
        if val:
            desktop = val
    except OSError:
        pass
    log_info(f"Desktop: {desktop or '(unknown)'}")


autostart = home + "/.config/autostart/"
pulse_default = "/etc/pulse/default.pa"
bash_config = home + "/.bashrc"
zsh_config = home + "/.zshrc"
fish_config = home + "/.config/fish/config.fish"


def get_config_file():
    shell = get_shell()
    if shell == "bash":
        return bash_config
    elif shell == "zsh":
        return zsh_config
    else:
        return fish_config


account_list = ["Standard", "Administrator"]
i3wm_config = home + "/.config/i3/config"
awesome_config = home + "/.config/awesome/rc.lua"
qtile_config = home + "/.config/qtile/config.py"
qtile_config_theme = home + "/.config/qtile/themes/"
leftwm_config = home + "/.config/leftwm/config.ron"
leftwm_config_theme = home + "/.config/leftwm/themes/"
leftwm_config_theme_current = home + "/.config/leftwm/themes/current"

nemesis_repo = "[nemesis_repo]\n\
Include = /etc/pacman.d/kiro-mirrorlist"

chaotic_aur_repo = "[chaotic-aur]\n\
Include = /etc/pacman.d/chaotic-mirrorlist"

cachyos_repo = "[cachyos]\n\
Include = /etc/pacman.d/cachyos-mirrorlist"

arch_testing_repo = "[core-testing]\n\
Include = /etc/pacman.d/mirrorlist"

arch_core_repo = "[core]\n\
Include = /etc/pacman.d/mirrorlist"

arch_extra_repo = "[extra]\n\
Include = /etc/pacman.d/mirrorlist"

arch_extra_testing_repo = "[extra-testing]\n\
Include = /etc/pacman.d/mirrorlist"

arch_multilib_testing_repo = "[multilib-testing]\n\
Include = /etc/pacman.d/mirrorlist"

arch_multilib_repo = "[multilib]\n\
Include = /etc/pacman.d/mirrorlist"

leftwm_themes_list = [
    "arise",
    "candy",
    "db",
    "db-color-dev",
    "db-comic",
    "db-labels",
    "db-nemesis",
    "db-scifi",
    "docky",
    "doublebar",
    "eden",
    "forest",
    "grayblocks",
    "greyblocks",
    "halo",
    "kittycafe-dm",
    "kittycafe-sm",
    "material",
    "matrix",
    "mesh",
    "parker",
    "pi",
    "sb-horror",
    "shades",
    "smooth",
    "space",
    "starwars",
]

# pacman log file
pacman_logfile = "/var/log/pacman.log"

# pacman cache directory
pacman_cache_dir = "/var/cache/pacman/pkg/"

# pacman lock file
pacman_lockfile = "/var/lib/pacman/db.lck"

# ATT log directory — resolved after home is set (line 227)
att_log_dir = home + "/.config/archlinux-tweak-tool/desktop_history/"
att_packages_dir = home + "/.config/archlinux-tweak-tool/packages/"
att_sessions_dir = home + "/.config/archlinux-tweak-tool/logging_sessions/"
att_streamline_dir = home + "/.config/archlinux-tweak-tool/streamline/"

# logging setup
logger = logging.getLogger("logger")
# create console handler and set level to debug
ch = logging.StreamHandler()

logger.setLevel(logging.INFO)
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter("%(asctime)s:%(levelname)s > %(message)s", "%Y-%m-%d %H:%M:%S")
# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


# =====================================================
# =====================================================
# =====================================================
#              SECTION 2: GENERAL UTILITIES
# =====================================================
# =====================================================
# =====================================================


def get_combo_text(combo):
    """Get selected text from a Gtk.DropDown with Gtk.StringList model."""
    item = combo.get_selected_item()
    return item.get_string() if item is not None else None


def get_lines(files):
    try:
        if path.isfile(files):
            with open(files, "r", encoding="utf-8") as f:
                lines = f.readlines()
                f.close()
            return lines
    except Exception as error:
        debug_print(error)


def get_position(lists, value):
    data = [string for string in lists if value in string]
    if len(data) != 0:
        position = lists.index(data[0])
        return position
    return 0


def get_positions(lists, value):
    data = [string for string in lists if value in string]
    position = []
    for d in data:
        position.append(lists.index(d))
    return position


def _get_variable(lists, value):
    data = [string for string in lists if value in string]

    if len(data) >= 1:
        data1 = [string for string in data if "#" in string]

        for i in data1:
            if i[:4].find("#") != -1:
                data.remove(i)
    if data:
        data_clean = [data[0].strip("\n").replace(" ", "")][0].split("=")
    return data_clean


def check_value(list, value):
    data = [string for string in list if value in string]
    if len(data) >= 1:
        data1 = [string for string in data if "#" in string]
        for i in data1:
            if i[:4].find("#") != -1:
                data.remove(i)
    return data


def check_backups(now):
    if not path.exists(home + "/" + bd + "/Backup-" + now.strftime("%Y-%m-%d %H")):
        makedirs(home + "/" + bd + "/Backup-" + now.strftime("%Y-%m-%d %H"), 0o777)
        permissions(home + "/" + bd + "/Backup-" + now.strftime("%Y-%m-%d %H"))


def check_if_process_is_running(processName):
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=["pid", "name", "create_time"])
            if processName == pinfo["name"]:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def check_pid_is_running(pid: int) -> bool:
    return psutil.pid_exists(pid)


def copytree(self, src, dst, symlinks=False, ignore=None):  # noqa
    if not path.exists(dst):
        makedirs(dst)
    for item in listdir(src):
        s = path.join(src, item)
        d = path.join(dst, item)
        if path.exists(d):
            try:
                shutil.rmtree(d)
            except Exception as error:
                debug_print(error)
                unlink(d)
        if path.isdir(s):
            try:
                shutil.copytree(s, d, symlinks, ignore)
            except Exception as error:
                debug_print(error)
                debug_print("ERROR2")
                self.ecode = 1
        else:
            try:
                shutil.copy2(s, d)
            except:  # noqa
                debug_print("ERROR3")
                self.ecode = 1


def check_sddm_value(list, value):
    data = [string for string in list if value in string]
    return data


def file_check(file):
    if path.isfile(file):
        return True

    return False


def path_check(path):
    if os.path.isdir(path):
        return True

    return False


def is_empty_directory(path):
    if os.path.exists(path) and not os.path.isfile(path):
        if not os.listdir(path):
            return True
        else:
            return False


def check_content(value, file):
    try:
        with open(file, "r", encoding="utf-8") as myfile:
            lines = myfile.readlines()
            myfile.close()

        for line in lines:
            if value in line:
                if value in line:
                    return True
                else:
                    return False
        return False
    except Exception:
        return False


def check_package_installed(package):  # noqa
    if package in _pkg_cache:
        return _pkg_cache[package]
    try:
        subprocess.check_output("pacman -Qi " + package, shell=True, stderr=subprocess.PIPE)
        _pkg_cache[package] = True
    except subprocess.CalledProcessError:
        _pkg_cache[package] = False
    return _pkg_cache[package]


def check_packages_installed(packages):
    """Return a dict {pkg: bool} for all packages in one pacman -Q call."""
    pkg_set = set(packages)
    result = {p: False for p in pkg_set}
    try:
        out = subprocess.check_output(["pacman", "-Q"], text=True, stderr=subprocess.DEVNULL)
        installed = {line.split()[0] for line in out.splitlines() if line.strip()}
        for pkg in pkg_set:
            result[pkg] = pkg in installed
    except Exception:
        pass
    return result


def check_service(service):  # noqa
    try:
        command = "systemctl is-active " + service + ".service"
        output = subprocess.run(
            command.split(" "),
            check=True,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        status = output.stdout.decode().strip()
        if status == "active":
            return True
        else:
            return False
    except Exception:
        return False


def check_firewall_service(service):  # noqa
    try:
        result = subprocess.run(
            ["firewall-cmd", "--query-service", service],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode().strip() == "yes"
    except Exception:
        return False


def firewall_status_markup():
    """Build the live firewall status line (firewalld + mDNS/Samba allow rules)."""
    fw_active = check_service("firewalld")
    fw = "<b>enabled</b>" if fw_active else "disabled"
    if fw_active:
        mdns = "<b>allowed</b>" if check_firewall_service("mdns") else "blocked"
        samba = "<b>allowed</b>" if check_firewall_service("samba") else "blocked"
    else:
        mdns = samba = "—"
    return f"Firewall: {fw}    Network discovery: {mdns}    Samba file sharing: {samba}"


_UNIT_SUFFIXES = (".service", ".timer", ".socket", ".target", ".path", ".mount", ".slice", ".scope")


def check_service_enabled(service):  # noqa
    if service in _svc_cache:
        return _svc_cache[service]
    # Append .service only when no explicit unit type was given, so callers can
    # pass timers/sockets (e.g. "fstrim.timer") without them turning into an
    # invalid "*.timer.service" lookup that always reports disabled.
    unit = service if service.endswith(_UNIT_SUFFIXES) else service + ".service"
    try:
        result = subprocess.run(
            ["systemctl", "is-enabled", unit],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _svc_cache[service] = result.stdout.decode().strip() == "enabled"
    except Exception:
        _svc_cache[service] = False
    return _svc_cache[service]


def _is_kernel_install_bls():
    try:
        return "initrd=\\" in open("/proc/cmdline").read()
    except OSError:
        return False


def get_initramfs_rebuild_cmd():
    """Return the shell command to rebuild all initramfs images."""
    # Garuda's /usr/bin/dracut-rebuild wraps its GRUB+BLS layout correctly;
    # plain `dracut --regenerate-all --force` fails there because kernel-install
    # paths expect /boot/efi/<machine-id>/<kernel>/ directories Garuda doesn't create.
    if os.path.exists("/usr/bin/dracut-rebuild"):
        return "dracut-rebuild"
    if os.path.exists("/usr/bin/dracut"):
        return "dracut --regenerate-all --force"
    # CachyOS+limine: /etc/mkinitcpio.d/ is empty by design; limine-mkinitcpio
    # pipes "rebuild" into limine-mkinitcpio-install which regenerates per-kernel.
    if os.path.exists("/usr/bin/limine-mkinitcpio"):
        return "limine-mkinitcpio"
    if _is_kernel_install_bls():
        # On kernel-install BLS systems the initramfs lives on the ESP at
        # <machine-id>/<kver>/initrd — not in /boot/initramfs-*.img.
        # mkinitcpio -P writes to /boot only and does NOT update the ESP copy,
        # so the startup splash would stay stale. kernel-install add handles
        # both regeneration and ESP sync (including microcode concatenation).
        return (
            "for _kd in /usr/lib/modules/*/;"
            " do [ -d \"$_kd\" ] || continue;"
            " _kv=$(basename \"$_kd\");"
            " [ -f \"${_kd}vmlinuz\" ] || continue;"
            " kernel-install add \"$_kv\" \"${_kd}vmlinuz\";"
            " done"
        )
    return "mkinitcpio -P"


def check_socket(socket):  # noqa
    try:
        command = "systemctl is-active " + socket + ".socket"
        output = subprocess.run(
            command.split(" "),
            check=True,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        status = output.stdout.decode().strip()
        if status == "active":
            return True
        else:
            return False
    except Exception:
        return False


def list_users(filename):  # noqa
    try:
        data = []
        with open(filename, "r", encoding="utf-8") as f:
            for line in f.readlines():
                if "1001" in line.split(":")[2]:
                    data.append(line.split(":")[0])
                if "1002" in line.split(":")[2]:
                    data.append(line.split(":")[0])
                if "1003" in line.split(":")[2]:
                    data.append(line.split(":")[0])
                if "1004" in line.split(":")[2]:
                    data.append(line.split(":")[0])
                if "1005" in line.split(":")[2]:
                    data.append(line.split(":")[0])
            data.sort()
            return data
    except Exception as error:
        debug_print(error)


def check_group(group):
    try:
        groups = subprocess.run(
            ["sh", "-c", "id " + sudo_username],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for x in groups.stdout.decode().split(" "):
            if group in x:
                return True
            else:
                return False
    except Exception as error:
        debug_print(error)


def check_systemd_boot():
    if path_check("/boot/loader") is True and file_check("/boot/loader/loader.conf") is True:
        return True
    else:
        return False


def permissions(dst):
    try:
        groups = subprocess.run(
            ["sh", "-c", "id " + sudo_username],
            check=True,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        group = None
        for x in groups.stdout.decode().split(" "):
            if "gid" in x.lower():  # match gid and GID
                try:
                    g = x.split("(")[1]
                    group = g.replace(")", "").strip()
                    break
                except IndexError:
                    raise ValueError("Unexpected format in 'id' command output.")

        # Ensure the group is retrieved
        if not group:
            raise ValueError(f"Could not determine group for user {sudo_username}.")

        subprocess.call(["chown", "-R", sudo_username + ":" + group, dst], shell=False)
    except Exception as error:
        debug_print(error)


def findgroup():
    try:
        groups = subprocess.run(
            ["sh", "-c", "id " + sudo_username],
            check=True,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        group = None
        for x in groups.stdout.decode().split(" "):
            if "gid" in x.lower():  # match gid and GID
                try:
                    g = x.split("(")[1]
                    group = g.replace(")", "").strip()
                    break
                except IndexError:
                    raise ValueError("Unexpected format in 'id' command output.")

        # Ensure the group is retrieved
        if not group:
            raise ValueError(f"Could not determine group for user {sudo_username}.")
        debug_print("[INFO] : Group = " + group)

    except Exception as error:
        debug_print(error)


# =====================================================
# =====================================================
# =====================================================
#              SECTION 3: UI UTILITIES
# =====================================================
# =====================================================
# =====================================================


def rgb_to_hex(rgb):
    if "rgb" in rgb:
        rgb = rgb.replace("rgb(", "").replace(")", "")
        vals = rgb.split(",")
        return "#{0:02x}{1:02x}{2:02x}".format(clamp(int(vals[0])), clamp(int(vals[1])), clamp(int(vals[2])))
    return rgb


def clamp(x):
    return max(0, min(x, 255))


def copy_func(src, dst, isdir=False):
    if isdir:
        subprocess.run(["cp", "-Rp", src, dst], check=True, shell=False)
    else:
        subprocess.run(["cp", "-p", src, dst], check=True, shell=False)


# exceptions
if distr == "manjaro" and check_content("biglinux", "/etc/os-release"):
    distr = "biglinux"


def _omarchy_marker_set():
    try:
        with open(att_settings, "r", encoding="utf-8") as f:
            return json.load(f).get("omarchy_plymouth_customized", False)
    except (OSError, json.JSONDecodeError):
        return False


if distr == "arch" and (check_content("omarchy", "/etc/plymouth/plymouthd.conf") or _omarchy_marker_set()):
    distr = "omarchy"


def get_distro_label():
    try:
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            content = f.read()
        if "IMAGE_ID=kiro" in content:
            return "Kiro"
        if "IMAGE_ID=Helwan-Linux-Dev-LTS" in content:
            return "Helwan"
        if "ID=cachyos" in content:
            return "CachyOS"
        if 'NAME="Nyarch Linux"' in content:
            return "Nyarch Linux"
        if 'NAME="Garuda Linux"' in content:
            return "Garuda Linux"
        if "ID=prismlinux" in content:
            return "PrismLinux"
        if "ID=biglinux" in content:
            return "BigLinux"
        if "ID=endeavouros" in content:
            return "EndeavourOS"
        if "ID=manjaro" in content:
            return "Manjaro"
        if "ID=xerolinux" in content:
            return "Xerolinux"
        if "ID=rebornos" in content:
            return "RebornOS"
        if "ID=archcraft" in content:
            return "Archcraft"
        if "ID=artix" in content:
            return "Artix"
        if "ID=archman" in content:
            return "ArchMan"
        # Ryoku ships a plain ID=arch os-release — its ryogami shell is the tell
        if path.exists("/usr/bin/ryogami"):
            return "Ryoku"

        if "ID=arch" in content:
            return "Arch"
    except Exception:
        pass
    return distr


def messagebox(self, title, message):
    md2 = Gtk.MessageDialog(
        transient_for=self,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        text=title,
    )
    md2.props.secondary_text = message
    md2.props.secondary_use_markup = True
    loop = GLib.MainLoop()

    def on_response(d, response_id):
        loop.quit()
        d.destroy()

    md2.connect("response", on_response)
    md2.show()
    loop.run()


def confirm_dialog(self, title, message):
    """Show confirmation dialog, return True if user clicked 'Yes'"""
    response_value = [False]
    md = Gtk.MessageDialog(
        transient_for=self,
        message_type=Gtk.MessageType.WARNING,
        buttons=Gtk.ButtonsType.YES_NO,
        text=title,
    )
    md.props.secondary_text = message
    md.props.secondary_use_markup = True
    loop = GLib.MainLoop()

    def on_response(d, response_id):
        response_value[0] = response_id == Gtk.ResponseType.YES
        loop.quit()
        d.destroy()

    md.connect("response", on_response)
    md.show()
    loop.run()
    return response_value[0]


def show_in_app_notification(self, message):
    if self.timeout_id is not None:
        GLib.source_remove(self.timeout_id)
        self.timeout_id = None

    self.notification_label.set_markup('<span foreground="white">' + message + "</span>")
    self.notification_revealer.set_reveal_child(True)
    self.timeout_id = GLib.timeout_add(3000, timeOut, self)


def timeOut(self):
    close_in_app_notification(self)


def close_in_app_notification(self):
    self.notification_revealer.set_reveal_child(False)
    GLib.source_remove(self.timeout_id)
    self.timeout_id = None


# =====================================================
# =====================================================
# =====================================================
#              SECTION 4: APP CONTROL
# =====================================================
# =====================================================
# =====================================================


def restart_program():
    if path.exists("/tmp/att.lock"):
        unlink("/tmp/att.lock")
        python = sys.executable
        execl(python, python, *sys.argv)


# =====================================================
# =====================================================
# =====================================================
#              SECTION 5: PACKAGE MANAGEMENT
# =====================================================
# =====================================================
# =====================================================


def check_nemesis_repo_active():
    nemesis = "[nemesis_repo]"
    for line in get_pacman_conf_lines():
        if nemesis in line:
            if "#" + nemesis in line:
                return False
            else:
                return True
    return False


def check_chaotic_aur_active():
    chaotic = "[chaotic-aur]"
    for line in get_pacman_conf_lines():
        if chaotic in line:
            if "#" + chaotic in line:
                return False
            else:
                return True
    return False


def check_cachyos_repo_active():
    for line in get_pacman_conf_lines():
        stripped = line.strip()
        if stripped.startswith("[cachyos") and stripped.endswith("]") and not stripped.startswith("#"):
            return True
    return False


_nemesis_packages_cache = None

_streamline_categories_cache = None

_pacman_conf_cache = None

_pkg_cache: dict = {}

_svc_cache: dict = {}


def get_pacman_conf_lines():
    global _pacman_conf_cache
    if _pacman_conf_cache is None:
        with open(pacman, "r", encoding="utf-8") as f:
            _pacman_conf_cache = f.readlines()
    return _pacman_conf_cache


def invalidate_pacman_conf_cache():
    global _pacman_conf_cache
    _pacman_conf_cache = None


def invalidate_pkg_cache():
    _pkg_cache.clear()
    _svc_cache.clear()


def load_nemesis_packages():
    """Load the list of nemesis_repo packages from file"""
    global _nemesis_packages_cache
    if _nemesis_packages_cache is not None:
        return _nemesis_packages_cache

    nemesis_file = "/usr/share/archlinux-tweak-tool/data/nemesis_packages.txt"
    _nemesis_packages_cache = set()

    try:
        if path.exists(nemesis_file):
            with open(nemesis_file, "r") as f:
                _nemesis_packages_cache = set(line.strip() for line in f if line.strip())
            debug_print(f"[INFO] Loaded {len(_nemesis_packages_cache)} nemesis packages from {nemesis_file}")
        else:
            debug_print(f"[INFO] nemesis_packages.txt not found at {nemesis_file}")
    except Exception as e:
        debug_print(f"[ERROR] Failed to load nemesis packages: {e}")

    return _nemesis_packages_cache


def load_streamline_categories():
    """Load the Streamline category->packages map from the generated data file.

    Returns an ordered dict {category: [pkg, ...]} parsed from
    data/streamline_packages.txt (TIER 3 of the Kiro ISO list). Missing file
    yields an empty map so the page degrades gracefully on non-Kiro systems.
    """
    global _streamline_categories_cache
    if _streamline_categories_cache is not None:
        return _streamline_categories_cache

    streamline_file = "/usr/share/archlinux-tweak-tool/data/streamline_packages.txt"
    categories: dict = {}
    current = None
    try:
        if path.exists(streamline_file):
            with open(streamline_file, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("###"):
                        current = stripped.lstrip("#").strip()
                        categories[current] = []
                    elif stripped and not stripped.startswith("#") and current is not None:
                        categories[current].append(stripped)
            debug_print(f"[INFO] Loaded {len(categories)} streamline categories from {streamline_file}")
        else:
            debug_print(f"[INFO] streamline_packages.txt not found at {streamline_file}")
    except Exception as e:
        debug_print(f"[ERROR] Failed to load streamline categories: {e}")

    _streamline_categories_cache = categories
    return _streamline_categories_cache


def find_package_repo(package_name):
    """Determine which repo a package belongs to (nemesis_repo or chaotic-aur)"""
    debug_print(f"[INFO] find_package_repo() called for: {package_name}")

    nemesis_packages = load_nemesis_packages()
    if package_name in nemesis_packages:
        debug_print(f"[INFO] Found {package_name} in nemesis_repo")
        return "nemesis_repo"

    debug_print(f"[INFO] Package {package_name} not in nemesis_repo, assuming chaotic-aur")
    return "chaotic-aur"


def check_missing_repo_error(self, error_msg, package):
    """Check if installation error is due to missing repo and show appropriate error"""
    debug_print("\n[INFO] check_missing_repo_error() called")
    debug_print(f"[INFO] Package: {package}")
    debug_print(f"[INFO] Error message length: {len(error_msg)}")
    debug_print(f"[INFO] Error message (first 200 chars): {error_msg[:200]}")

    if "target not found" not in error_msg.lower():
        debug_print("[INFO] 'target not found' not in error message, returning False")
        return False

    debug_print(f"[INFO] 'target not found' detected, querying repo for {package}")
    repo = find_package_repo(package)

    if repo:
        notification = f"Package not found. Please enable {repo} in pacman.conf"
    else:
        notification = "Package not found. Please enable nemesis_repo or chaotic-aur in pacman.conf"

    debug_print(f"[INFO] Showing notification: {notification}")
    GLib.idle_add(show_in_app_notification, self, notification)
    return True


def install_package(self, package):
    try:
        # Map package names to their binary names (some packages have different binary names)
        binary_map = {
            "fastfetch-git": "fastfetch",
            "yay-git": "yay",
            "paru-git": "paru",
            "ripgrep": "rg",
        }
        binary_name = binary_map.get(package, package)
        binary_path = f"/usr/bin/{binary_name}"

        if path.exists(binary_path):
            debug_print(f"{package} already installed")
            GLib.idle_add(show_in_app_notification, self, f"{package} already installed")
            return

        log_subsection(f"Installing {package}...")
        process = launch_pacman_install_in_terminal(package)
        GLib.idle_add(show_in_app_notification, self, f"{package} installation started")
        wait_install_and_update(process, binary_path, None, None, self, f"{package} installed", package)
    except Exception as error:
        log_error(f"Error installing {package}: {error}")
        GLib.idle_add(show_in_app_notification, self, f"Error installing {package}: {error}")


def get_terminal_env():
    env = os.environ.copy()
    try:
        uid = pwd.getpwnam(sudo_username).pw_uid
        xdg_runtime = f"/run/user/{uid}"
        env["XDG_RUNTIME_DIR"] = xdg_runtime
        env["HOME"] = home

        session_keys = {
            b"DISPLAY",
            b"WAYLAND_DISPLAY",
            b"DBUS_SESSION_BUS_ADDRESS",
            b"XDG_SESSION_TYPE",
            b"XDG_CURRENT_DESKTOP",
            b"XAUTHORITY",
        }
        for pid in os.listdir("/proc"):
            env_file = f"/proc/{pid}/environ"
            if not os.path.isfile(env_file):
                continue
            try:
                with open(env_file, "rb") as f:
                    entries = dict(e.split(b"=", 1) for e in f.read().split(b"\x00") if b"=" in e)
                if entries.get(b"LOGNAME", b"").decode() != sudo_username:
                    continue
                # Only trust a real graphical-session process. Many user-owned
                # processes (systemd --user, sshd, the pkexec chain) share LOGNAME
                # but have no DISPLAY/WAYLAND_DISPLAY/XAUTHORITY; matching one of
                # those first (it varies by /proc order — common on Plasma, rare on
                # tiling WMs) left the env without the display vars, so a browser
                # launched as the user had no display to draw on and silently no-opped.
                if not (entries.get(b"DISPLAY") or entries.get(b"WAYLAND_DISPLAY")):
                    continue
                for k in session_keys:
                    val = entries.get(k, b"").decode()
                    if val:
                        env[k.decode()] = val
                break
            except (PermissionError, OSError, ValueError):
                continue
    except Exception:
        pass
    return env


def is_wayland_session():
    try:
        for pid in os.listdir("/proc"):
            env_file = f"/proc/{pid}/environ"
            if not os.path.isfile(env_file):
                continue
            try:
                with open(env_file, "rb") as f:
                    entries = dict(e.split(b"=", 1) for e in f.read().split(b"\x00") if b"=" in e)
                if entries.get(b"LOGNAME", b"").decode() != sudo_username:
                    continue
                session_type = entries.get(b"XDG_SESSION_TYPE", b"").decode().lower()
                wayland_display = entries.get(b"WAYLAND_DISPLAY", b"").decode()
                return session_type == "wayland" or bool(wayland_display)
            except (PermissionError, OSError, ValueError):
                continue
    except Exception:
        pass
    return False


def user_session_env_assignments():
    """Return inline `VAR=val` args that carry the real user's session env through sudo.

    Passed as arguments to `sudo` they survive its env sanitizing (unlike Popen env=).
    Covers both X11 and Wayland — `DISPLAY=:0` was hardcoded before and broke on Wayland.
    XDG_CURRENT_DESKTOP is essential: without it xdg-open falls back to its generic
    opener (which reads mimeapps.list / a hardcoded browser list and tends to open
    Firefox) instead of the desktop-native opener (kde-open/gio) that honours the
    user's real default browser.
    XAUTHORITY is essential on X11 desktops (e.g. Plasma via SDDM) where the X cookie
    lives at a non-default path: without it the browser can't authenticate to the X
    server and silently opens nothing. Tiling WMs using ~/.Xauthority don't need it.
    """
    env = get_terminal_env()
    assignments = [
        f"HOME={env['HOME']}",
        f"XDG_RUNTIME_DIR={env['XDG_RUNTIME_DIR']}",
    ]
    for key in ("DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY", "DBUS_SESSION_BUS_ADDRESS", "XDG_CURRENT_DESKTOP"):
        val = env.get(key)
        if val:
            assignments.append(f"{key}={val}")
    return assignments


def get_default_browser_desktop():
    """Return the user's default browser .desktop id (e.g. 'brave-browser.desktop'), or ''.

    Queried as the real user so it reads their config, not root's.
    """
    for query in (
        ["xdg-settings", "get", "default-web-browser"],
        ["xdg-mime", "query", "default", "x-scheme-handler/https"],
    ):
        try:
            result = subprocess.run(
                ["sudo", "-u", sudo_username, "-H", *user_session_env_assignments(), *query],
                capture_output=True,
                text=True,
                timeout=5,
            )
            value = result.stdout.strip().split(";")[0].strip()
            if value.endswith(".desktop"):
                return value
        except Exception as error:
            log_error(f"Error querying default browser ({query[0]}): {error}")
    return ""


def _desktop_exec_binary(desktop_id):
    """Resolve a .desktop id to an executable (absolute path when possible), or ''."""
    search_dirs = [
        home + "/.local/share/applications",
        "/usr/local/share/applications",
        "/usr/share/applications",
    ]
    for d in search_dirs:
        desktop_path = os.path.join(d, desktop_id)
        if not os.path.isfile(desktop_path):
            continue
        try:
            with open(desktop_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Exec="):
                        # Drop field codes (%u %U %f ...) and keep the program itself.
                        tokens = [t for t in line[len("Exec="):].strip().split() if not t.startswith("%")]
                        if tokens:
                            prog = tokens[0]
                            return prog if os.path.isabs(prog) else (shutil.which(prog) or prog)
        except OSError:
            continue
    return ""


def get_default_browser_binary():
    """Best-effort executable for the user's default browser, else first installed browser."""
    desktop_id = get_default_browser_desktop()
    if desktop_id:
        binary = _desktop_exec_binary(desktop_id)
        if binary:
            return binary
    installed = get_installed_browsers()
    if installed:
        return installed[0][1]
    return ""


def open_url_as_user(url):
    """Open a URL in the real user's default browser; correct on X11 and Wayland.

    ATT runs as root, so the browser is launched as the real user. xdg-open is
    unreliable across that privilege drop — on KDE it hands off to kde-open, whose
    KIO/portal activation fails when spawned from a root process, so nothing opens.
    Launching the resolved browser executable directly is reliable (it's the same
    mechanism the right-click "Open with ..." menu uses), so we do that and only
    fall back to xdg-open if no browser could be resolved.
    """
    log_info(f"Opening URL: {url}")
    binary = get_default_browser_binary()
    if binary:
        open_url_with_browser(url, binary)
        return
    try:
        subprocess.Popen(
            ["sudo", "-u", sudo_username, "-H", *user_session_env_assignments(), "xdg-open", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as error:
        log_error(f"Error opening {url}: {error}")


# Priority order for finding an installed GUI text editor to open local docs.
# mousepad first (Kiro's default XFCE editor), then common DE editors,
# then VSCode / Sublime as power-user fallbacks.
_DOC_EDITORS = (
    "mousepad", "gedit", "gnome-text-editor", "kate", "kwrite",
    "geany", "featherpad", "xed", "pluma", "leafpad", "code", "subl",
)


def _find_doc_editor():
    """Return the first installed editor from the priority list, or None."""
    for ed in _DOC_EDITORS:
        if shutil.which(ed):
            return ed
    return None


def open_doc_in_editor(path):
    """Open a local doc in a detected GUI editor, as the real user (not root).

    ATT runs as root; launching a browser as root is rejected by Firefox and
    similar (XAUTHORITY owned by the session user). Editors don't have that
    self-protection, but we still drop privileges via `sudo -u` so the editor
    inherits the user's session env.
    """
    doc = os.path.basename(path)
    if not os.path.exists(path):
        # Repo-tree fallback when running ATT from source (uninstalled).
        repo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "share", "doc", "archlinux-tweak-tool", doc,
        )
        if os.path.exists(repo_path):
            path = repo_path
        else:
            log_warn(f"{doc} not found at {path} — package may need reinstall")
            return
    editor = _find_doc_editor()
    if editor is None:
        log_warn(
            f"No GUI text editor found (tried: {', '.join(_DOC_EDITORS)}). "
            f"Read it manually: {path}"
        )
        return
    log_info(f"Opening {doc} in {editor}")
    subprocess.Popen(["sudo", "-u", sudo_username, editor, path])


def install_local_package(self, package):
    if not os.path.exists(package):
        log_error(f"Package file not found: {package}")
        GLib.idle_add(show_in_app_notification, self, f"File not found: {package}")
        return
    log_subsection(f"Installing local package: {package}...")
    script = f"sudo pacman -U {package} --noconfirm; read -p 'Press Enter to close...'"
    process = subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    def wait_and_notify():
        process.wait()
        GLib.idle_add(show_in_app_notification, self, f"{os.path.basename(package)} installed")

    threading.Thread(target=wait_and_notify, daemon=True).start()
    GLib.idle_add(show_in_app_notification, self, "Installation started...")


def clear_skel_directory(path="/etc/skel"):
    # Ensure the provided path is indeed /etc/skel or a user-defined path
    if not os.path.exists(path):
        debug_print(f"The directory {path} does not exist.")
        return

    # Iterate over all the items in the directory
    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        # Check if the item is a file or a directory and remove it
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Remove the file or symlink
                debug_print(f"Removed file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove the directory and its content
                debug_print(f"Removed directory: {item_path}")
        except Exception as e:
            debug_print(f"Failed to remove {item_path}. Reason: {e}")


def remove_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return f"File '{file_path}' has been removed successfully."
        except OSError as e:
            return f"Error: {e.strerror}"
    else:
        return f"File '{file_path}' does not exist."


def remove_package(self, package):
    if not check_package_installed(package):
        log_warn(f"{package} is already removed")
        GLib.idle_add(show_in_app_notification, self, f"{package} is already removed")
        return
    log_subsection(f"Removing {package}...")
    try:
        process = launch_pacman_remove_in_terminal(package)
        GLib.idle_add(show_in_app_notification, self, f"{package} removal started")
        wait_and_notify(process, self, f"{package} removed")
    except Exception as error:
        log_error(f"Error removing {package}: {error}")
        GLib.idle_add(show_in_app_notification, self, f"Error removing {package}: {error}")


def update_repos(self):
    try:
        command = "pacman -Sy"
        subprocess.call(
            command.split(" "),
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception as error:
        debug_print(error)


# =====================================================
# =====================================================
# =====================================================
#              SECTION 6: TERMINAL LAUNCH
# =====================================================
# =====================================================
# =====================================================


def get_aur_helper():
    for helper in ["yay", "paru", "trizen", "pikaur"]:
        if path.exists("/usr/bin/" + helper):
            return helper
    return None


def ensure_nodejs_installed():
    import time

    npm_paths = ["/usr/bin/npm", "/usr/local/bin/npm"]
    for npm_path in npm_paths:
        if path.exists(npm_path):
            return True

    debug_print("[INFO] Node.js not found, installing...")
    install_proc = subprocess.run(
        ["pacman", "-S", "--noconfirm", "--needed", "nodejs", "npm"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    debug_print(f"[DEBUG] pacman stdout: {install_proc.stdout}")
    debug_print(f"[DEBUG] pacman stderr: {install_proc.stderr}")
    debug_print(f"[DEBUG] pacman returncode: {install_proc.returncode}")

    time.sleep(2)

    for npm_path in npm_paths:
        if path.exists(npm_path):
            debug_print("[INFO] Node.js installed successfully")
            return True

    debug_print("[ERROR] Node.js/npm installation failed - npm not found in common paths")
    return False


def ensure_git_installed():

    if shutil.which("git"):
        return True

    debug_print("[INFO] Git not found, installing...")
    install_proc = subprocess.run(
        ["pacman", "-S", "--noconfirm", "--needed", "git"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    debug_print(f"[DEBUG] pacman stdout: {install_proc.stdout}")
    debug_print(f"[DEBUG] pacman stderr: {install_proc.stderr}")
    debug_print(f"[DEBUG] pacman returncode: {install_proc.returncode}")

    if install_proc.returncode != 0:
        debug_print(f"[ERROR] Failed to install Git: {install_proc.stderr}")
        return False

    time.sleep(1)

    if shutil.which("git"):
        debug_print("[INFO] Git installed successfully")
        return True
    else:
        debug_print("[ERROR] Git installed but not found in PATH")
        return False


def remove_debug_from_makepkg_conf():
    makepkg_conf = "/etc/makepkg.conf"
    try:
        debug_print(f"[INFO] Starting removal of debug from {makepkg_conf}")

        if not path.exists(makepkg_conf):
            debug_print(f"[ERROR] {makepkg_conf} not found")
            return False

        debug_print(f"[DEBUG] Reading {makepkg_conf}...")
        with open(makepkg_conf, "r") as f:
            lines = f.readlines()

        debug_print(f"[DEBUG] Total lines read: {len(lines)}")

        modified = False
        already_fixed = False
        for i, line in enumerate(lines):
            if line.startswith("OPTIONS="):
                debug_print(f"[DEBUG] Found OPTIONS line at line {i + 1}")
                debug_print(f"[DEBUG] Original line: {line.strip()}")

                if " debug " in line or line.endswith("debug)\n"):
                    lines[i] = line.replace(" debug ", " !debug ")
                    lines[i] = lines[i].replace("debug)", "!debug)")
                    modified = True
                    debug_print(f"[DEBUG] Modified line: {lines[i].strip()}")
                    debug_print("[INFO] Successfully replaced debug with !debug")
                elif " !debug " in line or line.endswith("!debug)\n"):
                    debug_print("[DEBUG] debug is already disabled (!debug)")
                    already_fixed = True
                else:
                    debug_print("[DEBUG] debug not found in OPTIONS line")
                break

        if modified:
            debug_print(f"[DEBUG] Writing changes back to {makepkg_conf}...")
            with open(makepkg_conf, "w") as f:
                f.writelines(lines)
            debug_print("[INFO] Successfully removed debug from /etc/makepkg.conf")
            return True
        elif already_fixed:
            debug_print(f"[INFO] Debug is already disabled (!debug) in {makepkg_conf}")
            return 2
        else:
            debug_print("[WARNING] debug not found in OPTIONS line, no changes made")
            return False

    except PermissionError:
        debug_print(f"[ERROR] Permission denied: need root access to edit {makepkg_conf}")
        return False
    except Exception as e:
        debug_print(f"[ERROR] Failed to modify {makepkg_conf}: {e}")
        return False


def check_debug_status():
    makepkg_conf = "/etc/makepkg.conf"
    try:
        with open(makepkg_conf, "r") as f:
            for line in f:
                if line.startswith("OPTIONS="):
                    if "!debug" in line:
                        return True
                    if "debug" in line:
                        return False
    except Exception:
        pass
    return None


def launch_pacman_install_in_terminal(packages):
    import tempfile

    if not shutil.which("alacritty"):
        log_info("alacritty not found, installing...")
        install_proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"], capture_output=True, text=True
        )
        if install_proc.returncode != 0:
            log_error(f"Failed to install alacritty: {install_proc.stderr}")
            return None

    temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".log")
    temp_path = temp_file.name
    temp_file.close()

    script = f"""
FAILED=()
for pkg in {packages}; do
    echo ""
    echo "━━━ $pkg ━━━"
    pacman -S --noconfirm --needed "$pkg" 2>&1 | tee -a {temp_path}
    if [ ${{PIPESTATUS[0]}} -eq 0 ]; then
        echo "✓ $pkg done"
    else
        echo "✗ $pkg failed (conflict or not found — skipping)"
        FAILED+=("$pkg")
    fi
done

echo ''
if [ ${{#FAILED[@]}} -eq 0 ]; then
    echo '✓ All packages installed successfully'
else
    echo "✗ Skipped (conflict or not found): ${{FAILED[*]}}"
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
    process = subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.temp_file = temp_path
    return process


def launch_pacman_remove_in_terminal(packages):
    import tempfile

    if not shutil.which("alacritty"):
        log_info("alacritty not found, installing...")
        install_proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"], capture_output=True, text=True
        )
        if install_proc.returncode != 0:
            log_error(f"Failed to install alacritty: {install_proc.stderr}")
            return None

    temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".log")
    temp_path = temp_file.name
    temp_file.close()

    script = f"""
set -o pipefail
pacman -R --noconfirm {packages} 2>&1 | tee {temp_path}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Removal successful'
else
    echo '✗ Removal failed'
    if grep -q 'target not found' {temp_path}; then
        echo ''
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        echo 'REASON: Package might be removed already'
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        echo 'SOLUTION:'
        echo '. Check if package is installed: pacman -Q {packages}'
        echo '. Try manual removal: pacman -R {packages}'
        echo '. For dependencies: pacman -Rdd {packages}'
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    elif grep -qE 'error:|failed' {temp_path}; then
        echo ''
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        echo 'REASON: Package might be removed already'
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        echo 'SOLUTION:'
        echo '. Check if package is installed: pacman -Q {packages}'
        echo '. Try manual removal: pacman -R {packages}'
        echo '. For dependencies: pacman -Rdd {packages}'
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    fi
fi

echo ''
echo '=== Operation Finished ==='
echo 'You can close this window'
read -p 'Press Enter to close...'
"""
    process = subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.temp_file = temp_path
    return process


def get_root_filesystem_type():
    """Return the filesystem type of the root mount (empty string if unknown)."""
    try:
        with open("/proc/mounts", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == "/":
                    return parts[2]
    except Exception as error:
        debug_print(error)
    return ""


def launch_btrfs_setup_in_terminal():
    """Install + configure the Kiro btrfs snapshot stack visibly in Alacritty.

    Mirrors the Garuda stack (snapper + snap-pac + btrfs-assistant +
    btrfsmaintenance) with Kiro's policy: snap-pac + cleanup, NO timeline. Every
    step is echoed so the user watches what gets installed and run (no black
    boxes). Idempotent — safe to re-run.
    """
    if not shutil.which("alacritty"):
        log_info("alacritty not found, installing...")
        install_proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"], capture_output=True, text=True
        )
        if install_proc.returncode != 0:
            log_error(f"Failed to install alacritty: {install_proc.stderr}")
            return None

    script = r"""
set -o pipefail

echo '━━━ 1/5  Installing snapshot tools ━━━'
pacman -S --noconfirm --needed snapper snap-pac btrfs-assistant btrfsmaintenance

echo ''
echo '━━━ 2/5  Creating snapper root config ━━━'
# Kiro pre-stages @snapshots mounted at /.snapshots (Calamares). snapper
# create-config insists on creating that subvolume itself and aborts because it
# already exists. Detach our subvolume, let snapper build the config, then delete
# snapper's subvolume and remount ours as the snapshot store.
if [ -f /etc/snapper/configs/root ]; then
    echo 'root config already exists — skipping create-config'
elif mountpoint -q /.snapshots; then
    echo '/.snapshots is pre-staged — detaching it so snapper can create its config'
    if umount /.snapshots && rmdir /.snapshots; then
        snapper -c root create-config /
        btrfs subvolume delete /.snapshots
        mkdir -p /.snapshots
        mount /.snapshots && chmod 750 /.snapshots
        echo 'snapper root config created; @snapshots remounted as the store'
    else
        mountpoint -q /.snapshots || mount /.snapshots 2>/dev/null
        echo 'ERROR: could not detach /.snapshots — left untouched, no config created'
    fi
else
    snapper -c root create-config /
fi

echo ''
echo '━━━ 3/5  Applying snapshot policy (no hourly timeline) ━━━'
snapper -c root set-config TIMELINE_CREATE=no
echo 'TIMELINE_CREATE=no  — snapshots happen on pacman actions via snap-pac'

echo ''
echo '━━━ 4/5  Enabling timers ━━━'
systemctl enable --now snapper-cleanup.timer
# snapper create-config silently enables snapper-timeline.timer; our policy is
# no hourly timeline (TIMELINE_CREATE=no already blocks the snapshots), so disable it.
systemctl disable --now snapper-timeline.timer 2>/dev/null || true
echo 'snapper-timeline.timer disabled (policy: no hourly timeline)'
if systemctl list-unit-files btrfsmaintenance-refresh.path >/dev/null 2>&1; then
    systemctl enable --now btrfsmaintenance-refresh.path
    # The .path unit only refreshes on a config change; run the service once so the
    # scrub/balance timers are installed immediately from the current conf defaults.
    systemctl start btrfsmaintenance-refresh.service
    echo 'btrfsmaintenance enabled — timers installed from /etc/conf.d/btrfsmaintenance:'
    systemctl list-timers 'btrfs-*' --no-pager || true
else
    echo 'btrfsmaintenance-refresh.path not found — review btrfsmaintenance units manually'
fi

echo ''
echo '━━━ 5/5  Baseline snapshot ━━━'
if snapper -c root list | grep -qE 'ATT baseline|Kiro baseline'; then
    echo 'Baseline snapshot already exists — skipping'
else
    snapper -c root create --description 'ATT baseline'
fi
snapper -c root list

echo ''
echo 'snap-pac now creates a pre/post snapshot pair on every pacman action.'
echo 'Note: this setup does not add a boot-menu snapshot picker. Rollback is from'
echo 'the running system or the live ISO (snapper rollback). If you installed with'
echo 'GRUB you can add a picker yourself with grub-btrfs; systemd-boot has none.'

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
    process = subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return process


def launch_btrfs_teardown_in_terminal():
    """Remove the Kiro btrfs snapshot stack visibly in Alacritty — safe & reversible.

    Disables the snapshot timers, removes the snapper 'root' config file, and removes
    the four packages with a plain `pacman -R` (no dependency cascade). It performs NO
    btrfs subvolume or mount operations: the @snapshots subvolume and every snapshot
    already taken are left on disk, untouched. Re-running the setup restores everything.
    """
    if not shutil.which("alacritty"):
        log_info("alacritty not found, installing...")
        install_proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"], capture_output=True, text=True
        )
        if install_proc.returncode != 0:
            log_error(f"Failed to install alacritty: {install_proc.stderr}")
            return None

    script = r"""
set -o pipefail

echo '━━━ 1/3  Disabling snapshot timers ━━━'
for unit in snapper-cleanup.timer snapper-timeline.timer btrfsmaintenance-refresh.path \
            btrfs-scrub.timer btrfs-balance.timer btrfs-trim.timer; do
    if systemctl is-enabled "$unit" >/dev/null 2>&1 || systemctl is-active "$unit" >/dev/null 2>&1; then
        systemctl disable --now "$unit" >/dev/null 2>&1 && echo "disabled $unit" || echo "could not disable $unit"
    else
        echo "$unit already off"
    fi
done

echo ''
echo '━━━ 2/3  Removing snapper root config ━━━'
if [ -f /etc/snapper/configs/root ]; then
    rm -f /etc/snapper/configs/root
    echo 'removed /etc/snapper/configs/root'
else
    echo 'no snapper root config present'
fi
echo 'Snapshots already taken are KEPT in the @snapshots subvolume (not deleted).'
echo 'Use Btrfs Assistant if you ever want to view or remove them.'

echo ''
echo '━━━ 3/3  Removing snapshot packages ━━━'
to_remove=''
for p in snapper snap-pac btrfs-assistant btrfsmaintenance; do
    pacman -Q "$p" >/dev/null 2>&1 && to_remove="$to_remove $p"
done
if [ -n "$to_remove" ]; then
    echo "removing:$to_remove"
    pacman -R --noconfirm $to_remove
else
    echo 'none of the snapshot packages are installed'
fi

echo ''
echo 'The disk layout (@snapshots subvolume, /.snapshots mount) is unchanged.'
echo 'Re-run "Enable Kiro snapshots" to set it all up again.'

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
    process = subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return process


def launch_pacman_remove_recursive_in_terminal(packages, keep_config=False):
    """Recursively remove packages; keep_config=True uses -Rs (.pacsave backup) instead of -Rns."""
    import tempfile

    # -Rs keeps a .pacsave config backup (safer for newcomers); -Rns deletes config outright
    flag = "-Rs" if keep_config else "-Rns"

    if not shutil.which("alacritty"):
        log_info("alacritty not found, installing...")
        install_proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"], capture_output=True, text=True
        )
        if install_proc.returncode != 0:
            log_error(f"Failed to install alacritty: {install_proc.stderr}")
            return None

    temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".log")
    temp_path = temp_file.name
    temp_file.close()

    script = f"""
set -o pipefail
pacman {flag} --noconfirm {packages} 2>&1 | tee {temp_path}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Removal successful (package and unused dependencies removed)'
else
    echo '✗ Removal failed'
    if grep -q 'target not found' {temp_path}; then
        echo ''
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        echo 'REASON: Package might be removed already'
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        echo 'SOLUTION:'
        echo '. Check if package is installed: pacman -Q {packages}'
        echo '. Try manual removal: pacman {flag} {packages}'
        echo '. For forced removal: pacman -Rdd {packages}'
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    elif grep -qE 'error:|failed' {temp_path}; then
        echo ''
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        echo 'REASON: A dependency may be required by another package'
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        echo 'SOLUTION:'
        echo '. Check if package is installed: pacman -Q {packages}'
        echo '. Try manual removal: pacman {flag} {packages}'
        echo '. For forced removal: pacman -Rdd {packages}'
        echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    fi
fi

echo ''
echo '=== Operation Finished ==='
echo 'You can close this window'
read -p 'Press Enter to close...'
"""
    process = subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.temp_file = temp_path
    return process


def launch_aur_install_in_terminal(aur_helper, package, username=None):
    if not shutil.which("alacritty"):
        debug_print("[INFO] alacritty not found, installing...")
        install_proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"], capture_output=True, text=True
        )
        if install_proc.returncode != 0:
            debug_print(f"[ERROR] Failed to install alacritty: {install_proc.stderr}")
            return None
    if username is None:
        username = sudo_username
    script = (
        f"unset GIT_DIR GIT_WORK_TREE; sudo -H -u {username} {aur_helper} -S --noconfirm {package};"
        " echo ''; echo '=== Installation complete ==='"
        " && echo 'You can close this window'"
        " && read -p 'Press Enter to close...'"
    )
    return subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def launch_aur_remove_in_terminal(aur_helper, package, username=None):
    if not shutil.which("alacritty"):
        debug_print("[INFO] alacritty not found, installing...")
        install_proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"], capture_output=True, text=True
        )
        if install_proc.returncode != 0:
            debug_print(f"[ERROR] Failed to install alacritty: {install_proc.stderr}")
            return None
    if username is None:
        username = sudo_username
    script = (
        f"unset GIT_DIR GIT_WORK_TREE; sudo -H -u {username} {aur_helper} -Rs --noconfirm {package};"
        " echo ''; echo '=== Removal complete ==='"
        " && echo 'You can close this window'"
        " && read -p 'Press Enter to close...'"
    )
    return subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def launch_npm_install_in_terminal(npm_package):
    if not shutil.which("alacritty"):
        debug_print("[INFO] alacritty not found, installing...")
        install_proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"], capture_output=True, text=True
        )
        if install_proc.returncode != 0:
            debug_print(f"[ERROR] Failed to install alacritty: {install_proc.stderr}")
            return None
    if not ensure_nodejs_installed():
        debug_print("[ERROR] Node.js installation failed")
        return None
    script = (
        f"/usr/bin/npm install -g {npm_package};"
        " echo ''; echo '=== Installation complete ==='"
        " && echo 'You can close this window'"
        " && read -p 'Press Enter to close...'"
    )
    return subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def launch_npm_remove_in_terminal(npm_package):
    if not shutil.which("alacritty"):
        debug_print("[INFO] alacritty not found, installing...")
        install_proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"], capture_output=True, text=True
        )
        if install_proc.returncode != 0:
            debug_print(f"[ERROR] Failed to install alacritty: {install_proc.stderr}")
            return None
    if not ensure_nodejs_installed():
        debug_print("[ERROR] Node.js installation failed")
        return None
    script = (
        f"/usr/bin/npm uninstall -g {npm_package};"
        " echo ''; echo '=== Removal complete ==='"
        " && echo 'You can close this window'"
        " && read -p 'Press Enter to close...'"
    )
    return subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


# =====================================================
# =====================================================
# =====================================================
#              SECTION 7: THREADING & QUEUE
# =====================================================
# =====================================================
# =====================================================


def monitor_messages_queue(self):
    try:
        while True:
            message = self.messages_queue.get()
            GLib.idle_add(
                update_progress_textview,
                self,
                message,
                priority=GLib.PRIORITY_DEFAULT,
            )
    except Exception as e:
        logger.error("Exception in monitor_messages_queue(): %s" % e)


# =====================================================
# =====================================================
# =====================================================
#              SECTION 8: SERVICES (systemd)
# =====================================================
# =====================================================
# =====================================================


def enable_service(service):
    try:
        command = "systemctl enable " + service + ".service -f --now"
        subprocess.call(
            command.split(" "),
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        debug_print("We enabled the following service : " + service)
    except Exception as error:
        debug_print(error)


def restart_service(service):
    try:
        command = "systemctl reload-or-restart " + service + ".service"
        subprocess.call(
            command.split(" "),
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        debug_print("We restarted the following service (if available) : " + service)
    except Exception as error:
        debug_print(error)


def disable_service(service):
    try:
        command = "systemctl stop " + service
        subprocess.call(
            command.split(" "),
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        command = "systemctl disable " + service
        subprocess.call(
            command.split(" "),
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        debug_print("We stopped and disabled the following service " + service)
    except Exception as error:
        debug_print(error)


def enable_login_manager(self, loginmanager):
    if check_package_installed(loginmanager):
        try:
            command = "systemctl enable " + loginmanager + ".service -f"
            debug_print(command)
            subprocess.call(
                command.split(" "),
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            debug_print(loginmanager + " has been enabled - reboot")
            GLib.idle_add(
                show_in_app_notification,
                self,
                loginmanager + " has been enabled - reboot",
            )
        except Exception as error:
            debug_print(error)
    else:
        debug_print(loginmanager + " is not installed")
        GLib.idle_add(show_in_app_notification, self, loginmanager + " is not installed")


def add_autologin_group(self):
    com = subprocess.run(
        ["sh", "-c", "su - " + sudo_username + " -c groups"],
        check=True,
        shell=False,
        stdout=subprocess.PIPE,
    )
    groups = com.stdout.decode().strip().split(" ")
    if "autologin" not in groups:
        command = "groupadd autologin"
        try:
            subprocess.call(
                command.split(" "),
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as error:
            debug_print(error)
        try:
            subprocess.run(["gpasswd", "-a", sudo_username, "autologin"], check=True, shell=False)
        except Exception as error:
            debug_print(error)


def install_discovery(self):
    if not shutil.which("alacritty"):
        log_error("alacritty not found — install it first")
        show_in_app_notification(self, "alacritty not found")
        return None
    log_subsection("Install Network Discovery")
    show_in_app_notification(self, "Installing network discovery...")
    script = """
pacman -S --noconfirm --needed avahi nss-mdns gvfs-smb
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Packages installed'
    echo ''
    echo 'Enabling avahi-daemon...'
    systemctl enable avahi-daemon.service --now
    systemctl enable avahi-daemon.socket
    echo '✓ Network discovery enabled'
else
    echo '✗ Package installation failed'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
    try:
        return subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
    except Exception as error:
        log_error(f"Failed to launch terminal: {error}")
        return None


def remove_discovery(self):
    if not shutil.which("alacritty"):
        log_error("alacritty not found — install it first")
        show_in_app_notification(self, "alacritty not found")
        return None
    log_subsection("Disable Network Discovery")
    show_in_app_notification(self, "Disabling network discovery...")
    script = """
echo 'Stopping avahi-daemon...'
systemctl stop avahi-daemon.socket
systemctl disable avahi-daemon.socket
systemctl stop avahi-daemon.service
systemctl disable avahi-daemon.service
echo '✓ Network discovery stopped and disabled'

echo ''
echo 'Note: packages avahi, nss-mdns and gvfs-smb are NOT removed.'
echo 'They may be required by other packages on your system.'
echo 'To remove them manually: pacman -R avahi nss-mdns gvfs-smb'

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
    try:
        return subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
    except Exception as error:
        log_error(f"Failed to launch terminal: {error}")
        return None


def install_samba(self):
    if not shutil.which("alacritty"):
        log_error("alacritty not found — install it first")
        show_in_app_notification(self, "alacritty not found")
        return None
    log_subsection("Install Samba")
    show_in_app_notification(self, "Installing samba...")
    script = """
mkdir -p /var/cache/samba
pacman -S --noconfirm --needed samba gvfs-smb
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Packages installed'
    echo ''
    echo 'Enabling smb and nmb services...'
    systemctl enable smb.service
    systemctl enable nmb.service
    echo '✓ Samba services enabled (apply config and start them in step 2)'
else
    echo '✗ Package installation failed'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
    try:
        return subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
    except Exception as error:
        log_error(f"Failed to launch terminal: {error}")
        return None


def uninstall_samba(self):
    if not shutil.which("alacritty"):
        log_error("alacritty not found — install it first")
        show_in_app_notification(self, "alacritty not found")
        return None
    log_subsection("Uninstall Samba")
    show_in_app_notification(self, "Uninstalling samba...")
    script = """
echo 'Stopping samba services...'
systemctl stop smb.service
systemctl disable smb.service
systemctl stop nmb.service
systemctl disable nmb.service
echo '✓ Samba services stopped and disabled'

echo ''
echo 'Removing samba packages...'
pacman -Rs --noconfirm samba gvfs-smb
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Samba packages removed'
else
    echo 'Note: packages could not be fully removed (may have dependencies)'
    echo 'To remove manually: pacman -Rs samba gvfs-smb'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
    try:
        return subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
    except Exception as error:
        log_error(f"Failed to launch terminal: {error}")
        return None


def firewall_toggle_service(self, service, label, allowing):
    if not shutil.which("alacritty"):
        log_error("alacritty not found — install it first")
        show_in_app_notification(self, "alacritty not found")
        return None
    action = "--add-service" if allowing else "--remove-service"
    verb = "Allowing" if allowing else "Blocking"
    state = "open" if allowing else "closed"
    log_subsection(f"{verb} {label} in firewalld")
    show_in_app_notification(self, f"{verb} {label}...")
    script = f"""
echo '{verb} {label} through the firewall (firewalld)...'
echo ''
echo '+ firewall-cmd --permanent {action}={service}'
firewall-cmd --permanent {action}={service}
RESULT=$?
echo ''
echo '+ firewall-cmd --reload'
firewall-cmd --reload

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ {service} is now {state} in the firewall'
else
    echo '✗ firewall-cmd reported an error'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
    try:
        return subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
    except Exception as error:
        log_error(f"Failed to launch terminal: {error}")
        return None


def copy_samba(choice):
    src = f"/usr/share/archlinux-tweak-tool/data/samba/{choice}/smb.conf"
    if path.isfile(samba_config) and not path.isfile(samba_config + "-bak"):
        log_info_concise(f"  From: {samba_config}")
        log_info_concise(f"  To:   {samba_config}-bak")
        shutil.copy(samba_config, samba_config + "-bak")
    log_info_concise(f"  From: {src}")
    log_info_concise(f"  To:   {samba_config}")
    subprocess.run(["cp", src, samba_config], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if choice == "example":
        try:
            with open(samba_config, "r", encoding="utf-8") as f:
                lines = f.readlines()

            val = get_position(lines, "[SAMBASHARE]")
            lines[val + 1] = f"path = /home/{sudo_username}/Shared\n"
            log_info(f"Samba share path set to /home/{sudo_username}/Shared")

            with open(samba_config, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as error:
            log_error(f"Failed to configure samba share path: {error}")

    if choice == "usershares":
        if not path.isdir("/var/lib/samba/usershares"):
            makedirs("/var/lib/samba/usershares", 0o770)

        if not check_group("sambashare"):
            try:
                subprocess.run(
                    ["groupadd", "-r", "sambashare"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except Exception as error:
                log_error(f"Failed to create sambashare group: {error}")

        try:
            subprocess.run(
                ["gpasswd", "-a", sudo_username, "sambashare"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["chown", "root:sambashare", "/var/lib/samba/usershares"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["chmod", "1770", "/var/lib/samba/usershares"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as error:
            log_error(f"Failed to configure usershares directory: {error}")


def save_samba_config(self):
    # create smb.conf if there is none?
    if path.isfile(samba_config):
        if not path.isfile(samba_config + "-bak"):
            log_info_concise(f"  From: {samba_config}")
            log_info_concise(f"  To:   {samba_config}-bak")
            shutil.copy(samba_config, samba_config + "-bak")
        try:
            with open(samba_config, "r", encoding="utf-8") as f:
                lists = f.readlines()
                f.close()

            path_val = self.entry_path.get_text()
            browseable = self.samba_share_browseable.get_active()
            if browseable:
                browseable = "yes"
            else:
                browseable = "no"
            guest = self.samba_share_guest.get_active()
            if guest:
                guest = "yes"
            else:
                guest = "no"
            public = self.samba_share_public.get_active()
            if public:
                public = "yes"
            else:
                public = "no"
            writable = self.samba_share_writable.get_active()
            if writable:
                writable = "yes"
            else:
                writable = "no"

            val = get_position(lists, "[SAMBASHARE]")
            if lists[val] == ";[SAMBASHARE]\n":
                lists[val] = "[SAMBASHARE]" + "\n"
            lists[val + 1] = "path = " + path_val + "\n"
            lists[val + 2] = "browseable  = " + browseable + "\n"
            lists[val + 3] = "guest ok = " + guest + "\n"
            lists[val + 4] = "public = " + public + "\n"
            lists[val + 5] = "writable = " + writable + "\n"

            debug_print("These lines have been saved at the end of /etc/samba/smb.conf")
            debug_print("Edit this file to add more shares")
            debug_print(lists[val])
            debug_print(lists[val + 1])
            debug_print(lists[val + 2])
            debug_print(lists[val + 3])
            debug_print(lists[val + 4])
            debug_print(lists[val + 5])

            with open(samba_config, "w", encoding="utf-8") as f:
                f.writelines(lists)
                f.close()

            debug_print("Smb.conf has been saved")
            show_in_app_notification(self, "Smb.conf has been saved")
        except Exception:
            pass
    else:
        debug_print("Choose or create your own smb.conf in /etc/samba/smb.conf then change settings")
        show_in_app_notification(self, "Choose or create your own smb.conf")


def create_sddm_k_dir():
    if not path.isdir(sddm_default_d2_dir):
        try:
            mkdir(sddm_default_d2_dir)
        except Exception as error:
            debug_print(error)


# =====================================================
# =====================================================
# =====================================================
#              SECTION 9: NETWORK & SAMBA
# =====================================================
# =====================================================
# =====================================================


def copy_nsswitch(new_hosts_line):
    dest_file = "/etc/nsswitch.conf"
    try:
        with open(dest_file, "r") as f:
            dest_lines = f.readlines()

        if not path.isfile(dest_file + "-bak"):
            log_info_concise(f"  From: {dest_file}")
            log_info_concise(f"  To:   {dest_file}-bak")
            shutil.copy(dest_file, dest_file + "-bak")

        old_hosts_line = None
        updated_lines = []
        for line in dest_lines:
            if line.startswith("hosts:"):
                old_hosts_line = line.rstrip("\n")
                updated_lines.append("hosts: " + new_hosts_line + "\n")
            else:
                updated_lines.append(line)

        with open(dest_file, "w") as f:
            f.writelines(updated_lines)

        if old_hosts_line:
            debug_print(f"Previous: {old_hosts_line}")
            debug_print(f"New:      hosts: {new_hosts_line}")
    except Exception as e:
        log_error(f"Error updating nsswitch.conf: {e}")


# =====================================================
# =====================================================
# =====================================================
#              SECTION 10: SHELL
# =====================================================
# =====================================================
# =====================================================


def change_shell(self, shell):
    command = "sudo chsh " + sudo_username + " -s /bin/" + shell
    debug_print(f"  Command : {command}")
    debug_print(f"  User    : {sudo_username}")
    debug_print(f"  Shell   : /bin/{shell}")
    subprocess.call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    debug_print("  Result  : chsh completed")
    log_success("Shell changed to " + shell + " for the user - logout")
    GLib.idle_add(
        show_in_app_notification,
        self,
        "Shell changed to " + shell + " for user - logout",
    )


def source_shell(self):
    process = subprocess.run(["sh", "-c", 'echo "$SHELL"'], check=True, stdout=subprocess.PIPE)

    output = process.stdout.decode().strip()
    if output == "/bin/bash":
        subprocess.run(
            [
                "bash",
                "-c",
                "su - " + sudo_username + ' -c "source ' + home + '/.bashrc"',
            ],
            check=True,
            stdout=subprocess.PIPE,
        )
    elif output == "/bin/zsh":
        subprocess.run(
            ["zsh", "-c", "su - " + sudo_username + ' -c "source ' + home + '/.zshrc"'],
            check=True,
            stdout=subprocess.PIPE,
        )
    elif output == "/usr/bin/fish":
        subprocess.run(
            [
                "fish",
                "-c",
                "su - " + sudo_username + ' -c "source ' + home + '/.config/fish/config.fish"',
            ],
            check=True,
            stdout=subprocess.PIPE,
        )


def get_shell():
    try:
        shell = pwd.getpwnam(sudo_username).pw_shell
        if shell in ("/bin/bash", "/usr/bin/bash"):
            return "bash"
        elif shell in ("/bin/zsh", "/usr/bin/zsh"):
            return "zsh"
        elif shell in ("/bin/fish", "/usr/bin/fish"):
            return "fish"
    except Exception as error:
        debug_print(error)


def get_shell_config():
    # Get the actual user's home directory
    user_name = os.getlogin()
    user_home = pwd.getpwnam(user_name).pw_dir

    possible_configs = [
        os.path.join(user_home, ".bashrc"),
        os.path.join(user_home, ".zshrc"),
        os.path.join(user_home, ".config", "fish", "config.fish"),
    ]

    for config in possible_configs:
        if os.path.isfile(config):
            return config

    return None


# =====================================================
# =====================================================
# =====================================================
#              SECTION 11: PRIVACY
# =====================================================
# =====================================================
# =====================================================


def hblock_get_state(self):
    try:
        with open("/etc/hosts", "r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)
        if path.exists("/usr/bin/hblock") and lines > 100:
            return True
    except Exception:
        pass
    self.firstrun = False
    return False


def do_pulse(data, prog):
    prog.pulse()
    return True


# =====================================================
# =====================================================
# =====================================================
#              SECTION 12:  FASTFETCH
# =====================================================
# =====================================================
# =====================================================


def fastfetch_set_value(lists, pos, text, state):
    if state:
        if text in lists[pos]:
            if "#" in lists[pos]:
                lists[pos] = lists[pos].replace("#", "")
    else:
        if text in lists[pos]:
            if "#" not in lists[pos]:
                lists[pos] = "#" + lists[pos]

    return lists


def fastfetch_set_backend_value(lists, pos, text, value):
    if text in lists[pos] and "#" not in lists[pos]:
        lists[pos] = text + value + '"\n'


# =====================================================
# =====================================================
# =====================================================
#              SECTION 13: LOGGING / PACMAN LOG
# =====================================================
# =====================================================
# =====================================================


def create_log(self):
    debug_print(f"Writing package snapshot to {att_log_dir}")
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")
    destination = att_log_dir + "package-snapshot-" + timestamp + ".txt"
    result = subprocess.run(
        ["pacman", "-Q"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    with open(destination, "wb") as f:
        f.write(result.stdout)
    permissions(destination)


def _add_pacmanlog_queue(self):
    try:
        lines = []
        with open(pacman_logfile, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if line:
                    # encode in utf-8
                    # this fixes Gtk-CRITICAL **: gtk_text_buffer_emit_insert:
                    # assertion 'g_utf8_validate (text, len, NULL)' failed
                    lines.append(line.encode("utf-8"))
                    self.pacmanlog_queue.put(lines)
                else:
                    time.sleep(0.5)

    except Exception as e:
        logger.error("Exception in add_pacmanlog_queue() : %s" % e)
    finally:
        logger.debug("No new lines found inside the pacman log file")


def _update_textview_pacmanlog(self, textbuffer_pacmanlog, textview_pacmanlog):
    lines = self.pacmanlog_queue.get()

    try:
        if len(lines) > 0:
            end_iter = textbuffer_pacmanlog.get_end_iter()
            for line in lines:
                if len(line) > 0:
                    textbuffer_pacmanlog.insert(
                        end_iter,
                        line.decode("utf-8"),
                        len(line),
                    )

    except Exception as e:
        logger.error("Exception in update_textview_pacmanlog() : %s" % e)
    finally:
        self.pacmanlog_queue.task_done()

        if len(lines) > 0:
            text_mark_end = textbuffer_pacmanlog.create_mark("END", textbuffer_pacmanlog.get_end_iter(), False)
            # auto-scroll the textview to the bottom as new content is added

            textview_pacmanlog.scroll_mark_onscreen(text_mark_end)

        lines.clear()


def update_progress_textview(self, line):
    try:
        if len(line) > 0:
            self.textbuffer.insert(
                self.textbuffer.get_end_iter(),
                " %s" % line,
                len(" %s" % line),
            )

    except Exception as e:
        logger.error("Exception in update_progress_textview(): %s" % e)
    finally:
        self.messages_queue.task_done()
        text_mark_end = self.textbuffer.create_mark("end", self.textbuffer.get_end_iter(), False)
        # scroll to the end of the textview
        self.textview.scroll_mark_onscreen(text_mark_end)


def update_package_status_label(label, text):
    label.set_markup(text)


def check_pacman_lockfile():
    return os.path.exists(pacman_lockfile)


def wait_install_and_update(
    process, binary_path, label_widget, installed_markup, self_ref, notification, package_name=None
):
    def _wait():
        try:
            debug_print(f"Binary path: {binary_path}")
            debug_print("Waiting for process to complete...")

            process.communicate()
            time.sleep(1)
            invalidate_pkg_cache()

            error_output = ""
            if hasattr(process, "temp_file") and process.temp_file:
                try:
                    debug_print(f"Reading temp file: {process.temp_file}")
                    with open(process.temp_file, "r") as f:
                        error_output = f.read()
                    debug_print(f"Temp file contents: {len(error_output)} bytes")
                    import os as os_module

                    os_module.unlink(process.temp_file)
                except Exception as e:
                    log_warn(f"Error reading temp file: {e}")

            if path.exists(binary_path):
                log_success(f"{package_name or 'Package'} installed successfully")
                if label_widget:
                    GLib.idle_add(label_widget.set_markup, installed_markup)
                GLib.idle_add(show_in_app_notification, self_ref, notification)
                GLib.idle_add(getattr(self_ref, "refresh_aur_buttons", lambda: None))
            else:
                log_warn(f"Binary NOT found at {binary_path}, checking for errors...")
                if package_name:
                    debug_print(f"Calling check_missing_repo_error with package: {package_name}")
                    check_missing_repo_error(self_ref, error_output, package_name)
        except Exception as e:
            log_error(f"Exception in wait_install_and_update: {e}")
            import traceback

            traceback.print_exc()

    threading.Thread(target=_wait, daemon=True).start()


def wait_remove_and_update(process, binary_path, label_widget, plain_markup, self_ref, notification):
    def _wait():
        try:
            debug_print(f"Binary path to check: {binary_path}")
            debug_print("Waiting for removal process to complete...")

            stdout_data, stderr_data = process.communicate()
            debug_print("Process completed")
            time.sleep(1)
            invalidate_pkg_cache()

            error_output = ""
            if hasattr(process, "temp_file") and process.temp_file:
                try:
                    debug_print(f"Reading output from temp file: {process.temp_file}")
                    with open(process.temp_file, "r") as f:
                        error_output = f.read()
                    debug_print(f"Temp file size: {len(error_output)} bytes")
                    import os as os_module

                    os_module.unlink(process.temp_file)
                    debug_print("Cleaned up temp file")
                except Exception as e:
                    debug_print(f"Could not read temp file: {e}")

            debug_print(f"Checking if binary still exists at: {binary_path}")
            if not path.exists(binary_path):
                log_success("Package removed successfully")
                GLib.idle_add(label_widget.set_markup, plain_markup)
                GLib.idle_add(show_in_app_notification, self_ref, notification)
                GLib.idle_add(getattr(self_ref, "refresh_aur_buttons", lambda: None))
            else:
                log_warn("Removal may have failed or encountered issues")
        except Exception as e:
            log_error(f"Exception in wait_remove_and_update: {e}")
            import traceback

            traceback.print_exc()

    threading.Thread(target=_wait, daemon=True).start()


def wait_and_notify(process, self_ref, notification, on_done=None):
    def _wait():
        try:
            process.communicate()
            import os as os_module

            if hasattr(process, "temp_file") and process.temp_file:
                try:
                    os_module.unlink(process.temp_file)
                except Exception:
                    pass
            log_success(notification)
            GLib.idle_add(show_in_app_notification, self_ref, notification)
            # on_done touches widgets, so it must run on the main loop, not on this thread.
            if on_done is not None:
                GLib.idle_add(on_done)
        except Exception as e:
            log_error(f"Exception in wait_and_notify: {e}")

    threading.Thread(target=_wait, daemon=True).start()


def list_cursor_themes():
    return sorted(
        item for item in os.listdir("/usr/share/icons/") if path_check("/usr/share/icons/" + item + "/cursors/")
    )


def refresh_all_cursor_dropdowns(self):
    import maintenance as _maint
    import sddm as _sddm

    if hasattr(self, "cursor_themes"):
        _maint.pop_gtk_cursor_names(self.cursor_themes)
    if hasattr(self, "sddm_cursor_themes"):
        _sddm.pop_gtk_cursor_names(self.sddm_cursor_themes)


_XCURSOR_IMAGE_TYPE = 0xFFFD0002
_CURSOR_PREVIEW_SIZE = 24
_CURSOR_PREVIEW_NAMES = ("left_ptr", "default", "pointer", "arrow", "hand1", "hand2")


def _load_xcursor_pixbuf(cursor_path):
    try:
        with open(cursor_path, "rb") as f:
            data = f.read()
        magic, header_size, _version, toc_count = struct.unpack_from("<IIII", data, 0)
        if magic != 0x72756358:
            return None
        pixbufs = []
        toc_offset = header_size
        for pos in range(toc_count):
            entry_offset = toc_offset + pos * 12
            chunk_type, _subtype, chunk_pos = struct.unpack_from("<III", data, entry_offset)
            if chunk_type != _XCURSOR_IMAGE_TYPE:
                continue
            header, chunk_type, _subtype, _version = struct.unpack_from("<IIII", data, chunk_pos)
            if chunk_type != _XCURSOR_IMAGE_TYPE:
                continue
            width, height, _xhot, _yhot, _delay = struct.unpack_from("<IIIII", data, chunk_pos + 16)
            if width <= 0 or height <= 0:
                continue
            pixel_offset = chunk_pos + header
            pixel_count = width * height
            if pixel_offset + pixel_count * 4 > len(data):
                continue
            rgba = bytearray(pixel_count * 4)
            for pixel in range(pixel_count):
                argb = struct.unpack_from("<I", data, pixel_offset + pixel * 4)[0]
                p = pixel * 4
                rgba[p] = (argb >> 16) & 0xFF
                rgba[p + 1] = (argb >> 8) & 0xFF
                rgba[p + 2] = argb & 0xFF
                rgba[p + 3] = (argb >> 24) & 0xFF
            bytes_data = GLib.Bytes.new(bytes(rgba))
            pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
                bytes_data, GdkPixbuf.Colorspace.RGB, True, 8, width, height, width * 4
            )
            pixbufs.append(pixbuf)
        if not pixbufs:
            return None
        best = min(pixbufs, key=lambda p: abs(max(p.get_width(), p.get_height()) - _CURSOR_PREVIEW_SIZE))
        scale = _CURSOR_PREVIEW_SIZE / max(best.get_width(), best.get_height())
        w = max(1, round(best.get_width() * scale))
        h = max(1, round(best.get_height() * scale))
        return best.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR)
    except Exception:
        return None


def get_cursor_preview_pixbuf(cursor_theme):
    for name in _CURSOR_PREVIEW_NAMES:
        cursor_path = "/usr/share/icons/" + cursor_theme + "/cursors/" + name
        if path.isfile(cursor_path):
            pixbuf = _load_xcursor_pixbuf(cursor_path)
            if pixbuf:
                return pixbuf
    return None


def update_image(self, widget, image, theme_type, att_base, image_width, image_height):
    if get_combo_text(widget) is None:
        return

    sample_path = ""
    preview_path = ""
    random_option = False
    if theme_type == "zsh":
        sample_path = att_base + "/images/zsh-sample.jpg"
        preview_path = att_base + "/images/zsh_previews/" + get_combo_text(widget) + ".jpg"
        if get_combo_text(widget) == "random":
            random_option = True
    elif theme_type == "qtile":
        sample_path = att_base + "/images/qtile-sample.jpg"
        preview_path = att_base + "/themer_data/qtile/" + get_combo_text(widget) + ".jpg"
    elif theme_type == "leftwm":
        sample_path = att_base + "/images/leftwm-sample.jpg"
        preview_path = att_base + "/themer_data/leftwm/" + get_combo_text(widget) + ".jpg"
    elif theme_type == "i3":
        sample_path = att_base + "/images/i3-sample.jpg"
        preview_path = att_base + "/themer_data/i3/" + get_combo_text(widget) + ".jpg"
    elif theme_type == "awesome":
        name = get_combo_text(self.awesome_combo) or "multicolor"

        sample_path = att_base + "/images/awesome-sample.jpg"
        preview_path = att_base + "/themer_data/awesomewm/" + name + ".jpg"
    else:
        debug_print("Function update_image passed an incorrect value for theme_type. Value passed was: " + theme_type)
        debug_print(
            "Remember that the order for using this function is:"
            " self, widget, image, theme_type, att_base_path, image_width, image_height."
        )
    if path.isfile(preview_path) and not random_option:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(preview_path, image_width, image_height)
    else:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(sample_path, image_width, image_height)
    texture = Gdk.Texture.new_for_pixbuf(pixbuf)
    image.set_paintable(texture)


_KNOWN_BROWSERS = [
    ("Firefox", "/usr/bin/firefox"),
    ("Chromium", "/usr/bin/chromium"),
    ("Brave", "/usr/bin/brave"),
    ("LibreWolf", "/usr/bin/librewolf"),
    ("Vivaldi", "/usr/bin/vivaldi"),
    ("Opera", "/usr/bin/opera"),
    ("Google Chrome", "/usr/bin/google-chrome-stable"),
    ("Falkon", "/usr/bin/falkon"),
    ("qutebrowser", "/usr/bin/qutebrowser"),
    ("Epiphany", "/usr/bin/epiphany"),
    ("Thorium", "/usr/bin/thorium-browser"),
]


def get_installed_browsers():
    return [(name, p) for name, p in _KNOWN_BROWSERS if path.exists(p)]


def open_url_with_browser(url, binary):
    try:
        subprocess.Popen(
            ["sudo", "-u", sudo_username, "-H", *user_session_env_assignments(), binary, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        log_info(f"Opening {url} with {binary}")
    except Exception as error:
        log_error(f"Error opening browser: {error}")


def _open_with_and_close(url, binary, popover):
    open_url_with_browser(url, binary)
    popover.popdown()


def _copy_url_to_clipboard(self, url, popover):
    try:
        env = get_terminal_env()
        display = env.get("DISPLAY", ":0")
        wayland = env.get("WAYLAND_DISPLAY", "")

        candidates = []
        if wayland:
            candidates.append(f"sudo -u {sudo_username} WAYLAND_DISPLAY={wayland} wl-copy")
        candidates += [
            f"sudo -u {sudo_username} DISPLAY={display} xclip -selection clipboard",
            f"sudo -u {sudo_username} DISPLAY={display} xsel --clipboard --input",
        ]

        copied = False
        for cmd in candidates:
            try:
                proc = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
                proc.communicate(input=url.encode(), timeout=3)
                if proc.returncode == 0:
                    copied = True
                    break
            except subprocess.TimeoutExpired:
                proc.kill()

        if copied:
            log_info(f"Copied to clipboard: {url}")
            show_in_app_notification(self, "URL copied to clipboard")
        else:
            log_warn("No clipboard tool found (install xclip, xsel, or wl-clipboard)")
            show_in_app_notification(self, "Install xclip to enable copy")
        popover.popdown()
    except Exception as error:
        log_error(f"Clipboard error: {error}")


def _show_browser_popover(self, widget, url, x, y):
    browsers = get_installed_browsers()
    popover = Gtk.Popover()
    popover.set_parent(widget)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    vbox.set_margin_start(6)
    vbox.set_margin_end(6)
    vbox.set_margin_top(4)
    vbox.set_margin_bottom(4)

    lbl_url = Gtk.Label()
    lbl_url.set_markup(f"<small>{GLib.markup_escape_text(url)}</small>")
    lbl_url.set_wrap(True)
    lbl_url.set_max_width_chars(50)
    lbl_url.set_xalign(0)
    vbox.append(lbl_url)

    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_margin_top(4)
    sep.set_margin_bottom(2)
    vbox.append(sep)

    if browsers:
        for name, binary in browsers:
            browser_btn = Gtk.Button(label=f"Open with {name}")
            browser_btn.set_css_classes(["flat"])
            browser_btn.connect("clicked", lambda b, u=url, br=binary: _open_with_and_close(u, br, popover))
            vbox.append(browser_btn)
    else:
        vbox.append(Gtk.Label(label="No browsers detected"))

    sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep2.set_margin_top(2)
    sep2.set_margin_bottom(2)
    vbox.append(sep2)

    btn_copy = Gtk.Button(label="Copy URL")
    btn_copy.set_css_classes(["flat"])
    btn_copy.connect("clicked", lambda b: _copy_url_to_clipboard(self, url, popover))
    vbox.append(btn_copy)

    popover.set_child(vbox)

    rect = Gdk.Rectangle()
    rect.x = int(x)
    rect.y = int(y)
    rect.width = 1
    rect.height = 1
    popover.set_pointing_to(rect)
    popover.popup()


def attach_link_context_menu(self, widget, url):
    gesture = Gtk.GestureClick.new()
    gesture.set_button(3)
    gesture.connect("pressed", lambda g, n, x, y: _show_browser_popover(self, widget, url, x, y))
    widget.add_controller(gesture)


def read_att_settings():
    try:
        with open(att_settings, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def write_att_settings(data):
    try:
        with open(att_settings, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        permissions(att_settings)
    except OSError as e:
        log_error(f"Failed to write att_settings.json: {e}")

# ============================================================
# Author: Erik Dubois
# ============================================================
# Hybrid graphics page — logic.
#
# switcheroo-control's "Launch using Discrete Graphics" menu entry only exists in
# GNOME, Plasma and Cinnamon. Everywhere else (XFCE, the tiling WMs) the user has
# to know `prime-run` / `DRI_PRIME=1`. This page shows the GPUs, the commands, and
# can write per-app .desktop overrides that always launch on the discrete GPU.

import glob
import os
import re
import shutil
import subprocess

import functions as fn
from att_i18n import _, ngettext

PACKAGES = ("nvidia-prime", "switcheroo-control")
SWITCHEROO_SERVICE = "switcheroo-control"
SYSTEM_APPS_DIR = "/usr/share/applications"
USER_APPS_DIR = os.path.join(fn.home, ".local", "share", "applications")
# Marks the overrides ATT wrote, so Remove never touches a user's own .desktop copies.
MARKER = "X-ATT-Hybrid=true"

_VENDORS = {"0x8086": "intel", "0x1002": "amd", "0x10de": "nvidia"}
_CARD_RE = re.compile(r"^card\d+$")


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def _lspci_name(slot):
    try:
        out = subprocess.run(["lspci", "-s", slot], capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.split(": ", 1)[-1] if ": " in out else out


def list_gpus(with_names=False):
    """Return one dict per GPU found in /sys/class/drm (card, vendor, driver, boot_vga, slot, name)."""
    gpus = []
    for card_path in sorted(glob.glob("/sys/class/drm/card*")):
        card = os.path.basename(card_path)
        if not _CARD_RE.match(card):
            continue
        device = os.path.join(card_path, "device")
        driver_link = os.path.join(device, "driver")
        driver = os.path.basename(os.path.realpath(driver_link)) if os.path.exists(driver_link) else ""
        slot = os.path.basename(os.path.realpath(device))
        gpus.append({
            "card": card,
            "vendor": _VENDORS.get(_read(os.path.join(device, "vendor")), "other"),
            "driver": driver,
            "boot_vga": _read(os.path.join(device, "boot_vga")) == "1",
            "slot": slot,
            "name": _lspci_name(slot) if with_names else "",
        })
    return gpus


def is_hybrid():
    """Return True when the machine has two or more GPUs."""
    return len(list_gpus()) >= 2


def discrete_gpu(gpus):
    """Return the GPU that is not driving the boot display (the offload target), or None."""
    if len(gpus) < 2:
        return None
    candidates = [g for g in gpus if not g["boot_vga"]]
    nvidia = [g for g in candidates if g["vendor"] == "nvidia"]
    return (nvidia or candidates or gpus[1:])[0]


def offload_prefix(gpu):
    """Return the command prefix that runs an app on this GPU."""
    # prime-run only sets NVIDIA-proprietary env vars; nouveau/amdgpu/i915 use Mesa's DRI_PRIME.
    if gpu is None or gpu["driver"] == "nvidia":
        return "prime-run"
    return "env DRI_PRIME=1"


def desktop_has_menu_entry():
    """Return True on desktops whose app menu already offers 'Launch using Discrete Graphics'."""
    de = (os.environ.get("XDG_CURRENT_DESKTOP", "") + " " + (fn.desktop or "")).lower()
    return any(name in de for name in ("gnome", "kde", "plasma", "cinnamon"))


def switcheroo_list():
    """Return `switcherooctl list` output, or '' when it is not available."""
    if not shutil.which("switcherooctl"):
        return ""
    try:
        return subprocess.run(["switcherooctl", "list"], capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _desktop_fields(path):
    fields = {}
    try:
        with open(path, encoding="utf-8") as f:
            in_main = False
            for line in f:
                line = line.strip()
                if line.startswith("["):
                    in_main = line == "[Desktop Entry]"
                elif in_main and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    fields.setdefault(key.strip(), value.strip())
    except (OSError, UnicodeDecodeError):
        return {}
    return fields


def list_system_apps():
    """Return [(desktop_id, name)] for visible applications in /usr/share/applications, sorted by name."""
    apps = []
    for path in glob.glob(os.path.join(SYSTEM_APPS_DIR, "*.desktop")):
        fields = _desktop_fields(path)
        if fields.get("Type", "Application") != "Application" or "Exec" not in fields:
            continue
        if fields.get("NoDisplay", "").lower() == "true" or fields.get("Hidden", "").lower() == "true":
            continue
        apps.append((os.path.basename(path), fields.get("Name", os.path.basename(path))))
    return sorted(apps, key=lambda app: app[1].lower())


def _is_att_override(path):
    try:
        with open(path, encoding="utf-8") as f:
            return any(line.strip() == MARKER for line in f)
    except (OSError, UnicodeDecodeError):
        return False


def list_overrides():
    """Return [(desktop_id, name)] for the overrides ATT wrote."""
    overrides = []
    for path in sorted(glob.glob(os.path.join(USER_APPS_DIR, "*.desktop"))):
        if _is_att_override(path):
            overrides.append((os.path.basename(path), _desktop_fields(path).get("Name", os.path.basename(path))))
    return overrides


def _rewrite(lines, prefix):
    out = []
    for line in lines:
        if line.startswith("Exec=") and not line[len("Exec="):].startswith(prefix):
            line = "Exec=" + prefix + " " + line[len("Exec="):]
        elif line.startswith("DBusActivatable="):
            # A D-Bus activated app ignores Exec, so the offload prefix would never run.
            line = "DBusActivatable=false\n"
        out.append(line)
    for i, line in enumerate(out):
        if line.strip() == "[Desktop Entry]":
            out.insert(i + 1, MARKER + "\n")
            break
    return out


def make_override(desktop_id, prefix):
    """Write a user override of desktop_id that launches it with prefix; return (ok, message)."""
    src = os.path.join(SYSTEM_APPS_DIR, desktop_id)
    dst = os.path.join(USER_APPS_DIR, desktop_id)
    if os.path.exists(dst) and not _is_att_override(dst):
        fn.log_warn(f"{dst} exists and was not written by ATT — left alone")
        return False, _("{path} already exists (your own copy) — ATT leaves it alone").format(path=dst)
    try:
        with open(src, encoding="utf-8") as f:
            lines = f.readlines()
        # ATT runs as root: hand every directory it creates here, plus the file, back to the user.
        created = next((d for d in (os.path.join(fn.home, ".local"), os.path.join(fn.home, ".local", "share"),
                                    USER_APPS_DIR) if not os.path.isdir(d)), None)
        os.makedirs(USER_APPS_DIR, exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.writelines(_rewrite(lines, prefix))
    except OSError as error:
        fn.log_error(f"Writing {dst} failed: {error}")
        return False, _("Could not write {path}").format(path=dst)
    fn.permissions(created or dst)
    fn.log_success(f"Wrote {dst} (Exec prefixed with '{prefix}')")
    return True, _("Wrote {path}").format(path=dst)


def remove_overrides(desktop_ids):
    """Delete the given ATT overrides; return the paths removed."""
    removed = []
    for desktop_id in desktop_ids:
        path = os.path.join(USER_APPS_DIR, desktop_id)
        if not _is_att_override(path):
            continue
        try:
            os.remove(path)
            removed.append(path)
            fn.log_info(f"Removed {path}")
        except OSError as error:
            fn.log_error(f"Removing {path} failed: {error}")
    return removed


def _refresh_page(self):
    import hybrid_gui

    fn.invalidate_pkg_cache()
    hybrid_gui.refresh(self, fn)
    return False


def on_click_install(self, _widget):
    """Install the missing hybrid-graphics packages visibly, then enable switcheroo-control."""
    missing = [pkg for pkg in PACKAGES if not fn.check_package_installed(pkg)]
    if not missing:
        return
    fn.log_subsection(f"Installing {' '.join(missing)}")
    fn.show_in_app_notification(self, _("Opening terminal to install {packages}...").format(packages=" ".join(missing)))
    process = fn.launch_pacman_install_in_terminal(" ".join(missing))

    def wait_and_refresh():
        if process is not None:
            process.wait()
        if fn.check_package_installed(SWITCHEROO_SERVICE):
            subprocess.run(["systemctl", "enable", "--now", SWITCHEROO_SERVICE + ".service"],
                           capture_output=True, text=True)
            fn.log_info(f"Enabled {SWITCHEROO_SERVICE}.service")
        fn.log_success("Hybrid graphics packages install finished")
        fn.GLib.idle_add(_refresh_page, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_add_override(self, _widget):
    """Write an override for the app selected in the dropdown."""
    index = self.hybrid_app_dropdown.get_selected()
    if index >= len(self.hybrid_apps):
        return
    desktop_id, name = self.hybrid_apps[index]
    fn.log_subsection(f"Hybrid graphics: always run {desktop_id} on the discrete GPU")
    _ok, message = make_override(desktop_id, self.hybrid_prefix)
    fn.show_in_app_notification(self, message)
    _refresh_page(self)


def on_click_remove_override(self, desktop_id, _widget):
    """Remove one ATT override."""
    fn.log_subsection(f"Hybrid graphics: removing override {desktop_id}")
    removed = remove_overrides([desktop_id])
    fn.show_in_app_notification(self, _("Removed {path}").format(path=removed[0]) if removed else
                                _("Nothing removed"))
    _refresh_page(self)


def on_click_remove_all(self, _widget):
    """Remove every override ATT wrote, after confirmation."""
    overrides = list_overrides()
    if not overrides:
        return
    message = ngettext(
        "This deletes the launcher copy ATT wrote in\n<b>{folder}</b>.\n\n"
        "That app starts on the default GPU again and follows package updates again. "
        "Launchers you made yourself are not touched.",
        "This deletes the {count} launcher copies ATT wrote in\n<b>{folder}</b>.\n\n"
        "Those apps start on the default GPU again and follow package updates again. "
        "Launchers you made yourself are not touched.",
        len(overrides),
    ).format(count=len(overrides), folder=USER_APPS_DIR)
    if not fn.confirm_dialog(self, _("Remove all GPU overrides?"), message):
        fn.log_info("Hybrid graphics: remove all cancelled")
        return
    fn.log_subsection("Hybrid graphics: removing all overrides")
    removed = remove_overrides([desktop_id for desktop_id, _name in overrides])
    fn.show_in_app_notification(
        self, ngettext("Removed {count} override", "Removed {count} overrides", len(removed)).format(count=len(removed))
    )
    _refresh_page(self)

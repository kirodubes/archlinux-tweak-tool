# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
#
# Dev Diagnostics page.
#
# Layout (mirrors the order of pages in gui.py so a maintainer can
# walk "tab in ATT → row on DEV" 1:1):
#
#   1. Session diagnostics (distro / env / session / system)
#   2. Per-tab status — one section per stateful page, in gui.py order
#   3. Cross-cutting safeguards


import os
import shutil


# ── module-level helpers ────────────────────────────────────────────


def _detect_bootloader(fn):
    candidates = [
        ("/boot/efi/EFI/systemd/systemd-bootx64.efi", "systemd-boot"),
        ("/boot/EFI/systemd/systemd-bootx64.efi", "systemd-boot"),
        ("/efi/EFI/systemd/systemd-bootx64.efi", "systemd-boot"),
        ("/boot/grub/grub.cfg", "GRUB"),
        ("/boot/grub2/grub.cfg", "GRUB"),
        ("/boot/limine.cfg", "limine"),
        ("/boot/refind_linux.conf", "rEFInd"),
    ]
    for path, name in candidates:
        if fn.path.exists(path):
            return name
    return "unknown"


def _detect_display_manager(fn):
    dm_svc = "/etc/systemd/system/display-manager.service"
    if fn.path.islink(dm_svc):
        try:
            target = fn.readlink(dm_svc)
            return fn.path.basename(target).replace(".service", "")
        except OSError:
            pass
    return "unknown"


def _mkinitcpio_has_plymouth():
    try:
        for line in open("/etc/mkinitcpio.conf"):
            s = line.strip()
            if s.startswith("HOOKS=") and not s.startswith("#"):
                return "plymouth" in s
    except OSError:
        pass
    return False


def _count_pkgs_matching(fn, prefix):
    try:
        res = fn.subprocess.run(["pacman", "-Qq"], capture_output=True, text=True, timeout=5)
        return sum(1 for line in res.stdout.splitlines() if line.startswith(prefix))
    except Exception:
        return 0


def _tuned_active_profile(fn):
    try:
        res = fn.subprocess.run(["tuned-adm", "active"], capture_output=True, text=True, timeout=3)
        for line in res.stdout.splitlines():
            if ":" in line:
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "(unknown)"


def _ppd_active_profile(fn):
    # Query the org.freedesktop.UPower.PowerProfiles D-Bus interface
    # (served by power-profiles-daemon OR tuned-ppd). Helps spot
    # mismatches where the desktop power widget thinks one thing and
    # tuned thinks another — common with tuned-ppd + KDE/GNOME.
    try:
        res = fn.subprocess.run(
            ["busctl", "--system", "get-property",
             "net.hadess.PowerProfiles", "/net/hadess/PowerProfiles",
             "net.hadess.PowerProfiles", "ActiveProfile"],
            capture_output=True, text=True, timeout=3,
        )
        out = res.stdout.strip()
        # busctl prints e.g. `s "balanced"` — strip the type tag + quotes.
        if out.startswith("s "):
            return out[2:].strip().strip('"')
        return out or "(no PPD daemon)"
    except Exception:
        return "(no PPD daemon)"


def _hosts_has_hblock():
    try:
        with open("/etc/hosts") as f:
            return any("hblock" in line.lower() for line in f)
    except OSError:
        return False


def _pacman_conf_value(key):
    try:
        for line in open("/etc/pacman.conf"):
            s = line.strip()
            if s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            if k.strip() == key:
                return v.strip()
    except OSError:
        pass
    return None


def _pacman_repo_enabled(name):
    target = f"[{name}]"
    try:
        for line in open("/etc/pacman.conf"):
            s = line.strip()
            if s.startswith("#"):
                continue
            if s == target:
                return True
    except OSError:
        pass
    return False


def _localectl_field(fn, field):
    try:
        res = fn.subprocess.run(["localectl", "status"], capture_output=True, text=True, timeout=3)
        for line in res.stdout.splitlines():
            if field in line and ":" in line:
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "(unknown)"


def _timedatectl_field(fn, field):
    try:
        res = fn.subprocess.run(["timedatectl", "show"], capture_output=True, text=True, timeout=3)
        for line in res.stdout.splitlines():
            if line.startswith(field + "="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return "(unknown)"


def _autostart_entry_count(home):
    path = f"{home}/.config/autostart"
    try:
        return sum(1 for f in os.listdir(path) if f.endswith(".desktop"))
    except OSError:
        return 0


def _sudoers_d_count():
    try:
        return sum(1 for f in os.listdir("/etc/sudoers.d") if not f.startswith("."))
    except OSError:
        return 0


def _user_in_group(fn, group):
    user = fn.sudo_username
    try:
        res = fn.subprocess.run(["id", "-nG", user], capture_output=True, text=True, timeout=3)
        return group in res.stdout.split()
    except Exception:
        return False


# ── system-integrity helpers (mirror of kiro-audit's high-signal checks) ──

# pacman -Qk walks every file of every installed package, so it is the one
# expensive probe on this page. _populate() reruns on every tab revisit, so the
# result is cached for the process lifetime to keep revisits snappy — restart
# ATT for a fresh integrity scan. Everything else here is cheap and stays live.
_QK_CACHE = None

_QK_IGNORE = ("ohmychadwm-git:", "bind:", "cups:", "nfs-utils:")

_INSTALLER_LEFTOVERS = (
    "/root/.automated_script.sh",
    "/root/.zlogin",
    "/etc/systemd/system/getty@tty1.service.d",
    "/etc/sudoers.d/g_wheel",
    "/etc/polkit-1/rules.d/49-nopasswd_global.rules",
)


def _pkg_integrity(fn):
    """Return pacman -Qk lines for packages with missing files (known-noisy pkgs ignored)."""
    global _QK_CACHE
    if _QK_CACHE is not None:
        return _QK_CACHE
    bad = []
    try:
        res = fn.subprocess.run(["pacman", "-Qk"], capture_output=True, text=True, timeout=120)
        for line in res.stdout.splitlines():
            if "missing files" not in line or line.rstrip().endswith("0 missing files"):
                continue
            if any(line.startswith(p) for p in _QK_IGNORE):
                continue
            bad.append(line.strip())
    except Exception:
        bad = []
    _QK_CACHE = bad
    return bad


def _failed_units(fn):
    """Return the names of failed systemd units (system scope)."""
    try:
        res = fn.subprocess.run(["systemctl", "--failed", "--no-legend"],
                                capture_output=True, text=True, timeout=5)
        return [line.split()[0] for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _zram_state(fn):
    """Return (device_present, active_as_swap, compression_algorithm)."""
    present = fn.path.exists("/dev/zram0")
    active = False
    algo = "unknown"
    if present:
        try:
            res = fn.subprocess.run(["swapon", "--show=NAME", "--noheadings"],
                                    capture_output=True, text=True, timeout=5)
            active = any("zram0" in line for line in res.stdout.splitlines())
        except Exception:
            pass
        try:
            res = fn.subprocess.run(["zramctl", "--noheadings", "-o", "ALGORITHM", "/dev/zram0"],
                                    capture_output=True, text=True, timeout=5)
            algo = res.stdout.strip() or "unknown"
        except Exception:
            pass
    return present, active, algo


def _installer_leftovers(fn):
    """Return any live-only Calamares/archiso artifacts still present after install."""
    return [p for p in _INSTALLER_LEFTOVERS if fn.path.exists(p)]


def _is_vm(fn):
    """True when running inside a virtual machine (systemd-detect-virt --vm)."""
    try:
        res = fn.subprocess.run(["systemd-detect-virt", "--vm", "--quiet"],
                                capture_output=True, text=True, timeout=3)
        return res.returncode == 0
    except Exception:
        return False


def _oomd_state(fn):
    """Return (enabled, active) for systemd-oomd.service."""
    enabled = active = False
    try:
        enabled = fn.subprocess.run(["systemctl", "is-enabled", "systemd-oomd"],
                                    capture_output=True, text=True, timeout=3).returncode == 0
        active = fn.subprocess.run(["systemctl", "is-active", "systemd-oomd"],
                                   capture_output=True, text=True, timeout=3).returncode == 0
    except Exception:
        pass
    return enabled, active


def _mei_loaded(fn):
    """True if mei or mei_me kernel modules are currently loaded."""
    try:
        res = fn.subprocess.run(["lsmod"], capture_output=True, text=True, timeout=3)
        for line in res.stdout.splitlines():
            mod = line.split(" ", 1)[0]
            if mod in ("mei", "mei_me"):
                return True
    except Exception:
        pass
    return False


def _zswap_runtime(fn):
    """Read /sys/module/zswap/parameters/enabled — returns 'N', 'Y', '0', '1', or '?'."""
    path = "/sys/module/zswap/parameters/enabled"
    if not fn.path.exists(path):
        return "?"
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return "?"


_GLOSSARY_PATH = "/usr/share/doc/archlinux-tweak-tool/DEV_PAGE_GLOSSARY.md"


def _open_glossary(fn):
    fn.open_doc_in_editor(_GLOSSARY_PATH)


# ── main GUI builder ────────────────────────────────────────────────


def gui(self, Gtk, vboxstack_dev, fn):
    fn.log_info("Building Dev Diagnostics page")
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text("Dev Diagnostics")
    lbl_title.set_name("title")
    lbl_title.set_margin_start(10)
    lbl_title.set_margin_end(10)
    hbox_title.append(lbl_title)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hsep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep.set_hexpand(True)
    hbox_sep.append(hsep)

    # Help link — opens the local glossary in a detected GUI editor (as the
    # real user, not root). LinkButton's activate-link handler returns True
    # to suppress GTK's default xdg-open, which would launch a browser and
    # fail because ATT runs as root (Firefox refuses; XAUTHORITY is user-owned).
    # Every new _row(...) added in this file needs a matching glossary entry.
    hbox_help = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_help.set_margin_start(10)
    hbox_help.set_margin_end(10)
    hbox_help.set_margin_top(4)
    btn_glossary = Gtk.LinkButton.new_with_label(
        "kiro-glossary://open",
        "What do these rows mean? — read the Dev Page Glossary",
    )

    def _on_glossary_activate(_widget):
        _open_glossary(fn)
        return True  # suppress default xdg-open

    btn_glossary.connect("activate-link", _on_glossary_activate)
    hbox_help.append(btn_glossary)

    grid = Gtk.Grid()
    grid.set_column_spacing(30)
    grid.set_row_spacing(8)
    grid.set_margin_start(10)
    grid.set_margin_end(10)
    grid.set_margin_top(10)
    grid.set_margin_bottom(10)

    row = [0]

    def _header(text):
        if row[0] > 0:
            spacer = Gtk.Label()
            spacer.set_text("")
            grid.attach(spacer, 0, row[0], 3, 1)
            row[0] += 1
        lbl = Gtk.Label(xalign=0)
        lbl.set_markup(f"<b>{text}</b>")
        grid.attach(lbl, 0, row[0], 3, 1)
        row[0] += 1

    def _group(text):
        if row[0] > 0:
            spacer = Gtk.Label()
            spacer.set_text("")
            grid.attach(spacer, 0, row[0], 3, 1)
            row[0] += 1
        lbl = Gtk.Label(xalign=0)
        lbl.set_markup(f"<big><b>{text}</b></big>")
        grid.attach(lbl, 0, row[0], 3, 1)
        row[0] += 1

    def _row(check, value, status_markup=""):
        lbl_check = Gtk.Label(xalign=0)
        lbl_check.set_text(check)
        lbl_check.set_size_request(280, -1)

        lbl_value = Gtk.Label(xalign=0)
        lbl_value.set_text(str(value))
        lbl_value.set_size_request(200, -1)

        lbl_status = Gtk.Label(xalign=0)
        if status_markup:
            lbl_status.set_markup(status_markup)

        grid.attach(lbl_check, 0, row[0], 1, 1)
        grid.attach(lbl_value, 1, row[0], 1, 1)
        grid.attach(lbl_status, 2, row[0], 1, 1)
        row[0] += 1

    def _yes(b):
        return "<span foreground='green'>yes</span>" if b else ""

    def _active(b):
        return "<span foreground='green'>active</span>" if b else ""

    def _enabled(b):
        return "<span foreground='green'>enabled</span>" if b else ""

    def _state(state):
        colors = {"pass": "green", "warn": "orange", "fail": "red"}
        labels = {"pass": "PASS", "warn": "&#9888; WARN", "fail": "FAIL"}
        c = colors.get(state)
        return f"<span foreground='{c}'>{labels[state]}</span>" if c else ""

    def _pkg(name):
        installed = fn.check_package_installed(name)
        _row(f"{name}", installed, _yes(installed))
        return installed

    def _svc(label, service, installed=True):
        if not installed:
            _row(label, "(pkg not installed)")
            return
        en = fn.check_service_enabled(service)
        act = fn.check_service(service)
        status = " ".join(s for s in (_enabled(en), _active(act)) if s)
        _row(label, f"enabled={en} active={act}", status)

    def _populate():
        # Clear grid + reset row counter so we can rebuild on tab revisit.
        while grid.get_first_child() is not None:
            grid.remove(grid.get_first_child())
        row[0] = 0
        # Invalidate ATT's package/service caches — without this, the
        # rebuild would just re-render the cached state from app startup.
        try:
            fn.invalidate_pkg_cache()
        except AttributeError:
            pass
        try:
            fn.invalidate_pacman_conf_cache()
        except AttributeError:
            pass

        # ════════════════════════════════════════════════════════════════
        # 1. Session diagnostics — meta info about the running session
        # ════════════════════════════════════════════════════════════════
        _group("Session diagnostics")

        # ── Distro Detection ────────────────────────────────────────
        _header("Distro Detection")

        distr_label = fn.get_distro_label()
        # Kiro is an Arch-based rebrand (os-release ID=arch, IMAGE_ID=kiro), so base
        # "arch" + label "Kiro" is the expected pairing — not a detection mismatch.
        if fn.distr == "arch" and distr_label == "Kiro":
            distr_status = "<span foreground='green'>Arch-based (expected)</span>"
        elif fn.distr.lower() == distr_label.lower():
            distr_status = ""
        else:
            distr_status = "<span foreground='orange'>&#9888; mismatch</span>"

        _row("fn.distr", fn.distr)
        _row("get_distro_label()", distr_label, distr_status)

        # ── Environment ──────────────────────────────────────────────
        _header("Environment")

        desktop = fn.desktop if fn.desktop else "(not set)"
        _row("XDG_CURRENT_DESKTOP", desktop)
        _row("fn.sudo_username", fn.sudo_username)
        _row("fn.home", fn.home)

        # ── Session ──────────────────────────────────────────────────
        _header("Session")

        # WMs started via startx/.xinitrc often never export XDG_SESSION_TYPE,
        # so fall back to inferring it from the session's display variables.
        _term_env = fn.get_terminal_env()
        _session_type = (_term_env.get("XDG_SESSION_TYPE") or "").strip()
        if not _session_type:
            if _term_env.get("WAYLAND_DISPLAY"):
                _session_type = "wayland (inferred)"
            elif _term_env.get("DISPLAY"):
                _session_type = "x11 (inferred)"
            else:
                _session_type = "(not set)"
        _shell = fn.get_shell() or "(unknown)"

        _row("XDG_SESSION_TYPE", _session_type)
        _row("active shell", _shell)

        # ── System ───────────────────────────────────────────────────
        _header("System")

        _bootloader = _detect_bootloader(fn)

        try:
            _kernel = fn.subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip()
        except Exception:
            _kernel = "unknown"

        _is_openrc = fn.path.exists("/run/openrc") or fn.path.exists("/sbin/openrc")
        _init_system = "OpenRC" if _is_openrc else "systemd"
        _initramfs = "dracut" if fn.path.exists("/usr/bin/dracut") else "mkinitcpio"

        _row("bootloader", _bootloader)
        _row("running kernel", _kernel)
        _row("init system", _init_system)
        _row("initramfs", _initramfs)
        _row("systemd PID 1", fn.path.exists("/run/systemd/private"))

        # Shared variables consumed later by Safeguards group:
        _dm = _detect_display_manager(fn)
        _sddm_installed_shared = fn.check_package_installed("sddm")
        _plasma_login_shared = fn.check_service_enabled("plasma-login")
        _plasmalogin_shared = fn.check_service_enabled("plasmalogin")
        _sddm_service_hidden = _plasma_login_shared or _plasmalogin_shared

        # ════════════════════════════════════════════════════════════════
        # 2. Per-tab status — sections in gui.py registration order
        #    (skipping Dev/System/Logging which are viewers/self)
        # ════════════════════════════════════════════════════════════════
        _group("Per-tab status")

        # ── AI Tools ─────────────────────────────────────────────────
        # ATT detects these via binary paths, not pkg names (varied AUR sources).
        _header("AI Tools")
        for _bin in ("ollama", "open-webui", "aider", "claude"):
            _present = fn.path.exists(f"/usr/bin/{_bin}")
            _row(f"/usr/bin/{_bin}", _present, _yes(_present))
        _ollama_running = fn.check_service("ollama")
        _row("ollama.service active", _ollama_running, _active(_ollama_running))

        # ── Autostart ────────────────────────────────────────────────
        _header("Autostart")
        _auto_count = _autostart_entry_count(fn.home)
        _row("~/.config/autostart/*.desktop", _auto_count)

        # ── Desktop ──────────────────────────────────────────────────
        # Detect DEs/WMs via their session binary, not the meta-pkg —
        # several DE names (xfce4, gnome, mate, deepin, lxqt) are pacman
        # groups, not packages, so `pacman -Qi <group>` always fails. Tiling
        # WMs are listed alongside the DEs; the list is sorted alphabetically
        # (case-insensitive) at render time so new entries stay ordered.
        _header("Desktop")
        _desktop_bins = [
            ("Plasma", "/usr/bin/plasmashell"),
            ("GNOME", "/usr/bin/gnome-session"),
            ("XFCE", "/usr/bin/xfce4-session"),
            ("Cinnamon", "/usr/bin/cinnamon-session"),
            ("MATE", "/usr/bin/mate-session"),
            ("Budgie", "/usr/bin/budgie-desktop"),
            ("Deepin", "/usr/bin/startdde"),
            ("LXQt", "/usr/bin/lxqt-session"),
            ("awesome", "/usr/bin/awesome"),
            ("bspwm", "/usr/bin/bspwm"),
            ("chadwm", "/usr/bin/chadwm"),
            ("i3", "/usr/bin/i3"),
            ("leftwm", "/usr/bin/leftwm"),
            ("ohmychadwm", "/usr/bin/ohmychadwm"),
            ("qtile", "/usr/bin/qtile"),
        ]
        for _name, _bin in sorted(_desktop_bins, key=lambda _t: _t[0].lower()):
            _present = fn.path.exists(_bin)
            _row(f"{_name} ({_bin})", _present, _yes(_present))

        # ── Fastfetch ────────────────────────────────────────────────
        _header("Fastfetch")
        _pkg("fastfetch")
        _pkg("lolcat")
        _ff_cfg = f"{fn.home}/.config/fastfetch/config.jsonc"
        _row("user config exists", fn.path.exists(_ff_cfg), _yes(fn.path.exists(_ff_cfg)))

        # ── Icons ────────────────────────────────────────────────────
        _header("Icons")
        _n_sardi = _count_pkgs_matching(fn, "sardi-")
        _n_surfn = _count_pkgs_matching(fn, "surfn-")
        _n_neo = _count_pkgs_matching(fn, "neo-candy-")
        _row("sardi-* packs", _n_sardi, _yes(_n_sardi > 0))
        _row("surfn-* packs", _n_surfn, _yes(_n_surfn > 0))
        _row("neo-candy-* packs", _n_neo, _yes(_n_neo > 0))

        # ── Kernels ──────────────────────────────────────────────────
        # Enumerate /boot/vmlinuz-* (the actually-bootable kernels) rather
        # than a hardcoded pkg-name list — on Arch, Liquorix ships as
        # linux-lqx, CachyOS as linux-cachyos, etc., and the boot image is
        # the authoritative ground truth regardless of pkg name variations.
        _header("Kernels")
        try:
            _vmlinuz = sorted(f for f in os.listdir("/boot") if f.startswith("vmlinuz-"))
        except OSError:
            _vmlinuz = []
        if not _vmlinuz:
            _row("/boot/vmlinuz-*", "(none found)")
        _running_pkgbase = ""
        try:
            with open(f"/lib/modules/{_kernel}/pkgbase") as _pb:
                _running_pkgbase = _pb.read().strip()
        except OSError:
            pass
        for _img in _vmlinuz:
            _pkgname = _img[len("vmlinuz-"):]
            _running = _pkgname == _running_pkgbase
            _row(_pkgname, "/boot/" + _img,
                 "<span foreground='green'>running</span>" if _running else _yes(True))
            _row(f"{_pkgname}-headers", fn.check_package_installed(f"{_pkgname}-headers"),
                 _yes(fn.check_package_installed(f"{_pkgname}-headers")))

        # ── Locale ───────────────────────────────────────────────────
        _header("Locale")
        _row("LANG", os.getenv("LANG") or "(not set)")
        _row("keyboard (X11 layout)", _localectl_field(fn, "X11 Layout"))
        _row("vc keymap", _localectl_field(fn, "VC Keymap"))
        _row("timezone", _timedatectl_field(fn, "Timezone"))

        # ── Maintenance ──────────────────────────────────────────────
        _header("Maintenance")
        _pkg("reflector")
        _pkg("rate-mirrors")
        _pd = _pacman_conf_value("ParallelDownloads")
        _row("pacman ParallelDownloads", _pd if _pd else "(default 1)")

        # ── Network ──────────────────────────────────────────────────
        _header("Network")
        _avahi = _pkg("avahi")
        _svc("avahi-daemon.service", "avahi-daemon", installed=_avahi)
        _samba = _pkg("samba")
        _svc("smb.service", "smb", installed=_samba)
        _firewalld = _pkg("firewalld")
        _svc("firewalld.service", "firewalld", installed=_firewalld)
        _pkg("firewall-config")
        _fw_mdns = fn.check_firewall_service("mdns")
        _fw_samba = fn.check_firewall_service("samba")
        _row("firewalld allows mdns", _fw_mdns, _yes(_fw_mdns))
        _row("firewalld allows samba", _fw_samba, _yes(_fw_samba))

        # ── Packages (AUR helpers) ───────────────────────────────────
        _header("Packages")
        for _helper in ("yay", "paru", "trizen", "pikaur"):
            _present = shutil.which(_helper) is not None
            _row(f"{_helper} on PATH", _present, _yes(_present))

        # ── Pacman ───────────────────────────────────────────────────
        _header("Pacman")
        _row("chaotic-AUR active", fn.check_chaotic_aur_active(), _yes(fn.check_chaotic_aur_active()))
        _row("nemesis_repo active", fn.check_nemesis_repo_active(), _yes(fn.check_nemesis_repo_active()))
        _row("[multilib] enabled", _pacman_repo_enabled("multilib"), _yes(_pacman_repo_enabled("multilib")))
        _row("[testing] enabled", _pacman_repo_enabled("testing"), _yes(_pacman_repo_enabled("testing")))

        # ── Plymouth ─────────────────────────────────────────────────
        _header("Plymouth")

        # Plymouth on Arch is hook-driven, not service-driven — there's no
        # `plymouth.service` to enable. Boot-time firing is wired via the
        # initramfs hook + kernel cmdline (both checked below), so dropping
        # the misleading `is-enabled plymouth` row.
        _ply_installed = fn.check_package_installed("plymouth")

        _ply_theme = "(not installed)"
        if _ply_installed:
            try:
                _ply_theme = (
                    fn.subprocess.run(["plymouth-set-default-theme"], capture_output=True, text=True).stdout.strip()
                    or "(none)"
                )
            except Exception:
                _ply_theme = "(error)"

        if _initramfs == "mkinitcpio":
            _ply_hooks_ok = _mkinitcpio_has_plymouth()
            _hooks_label = "HOOKS contains plymouth"
        else:
            _ply_hooks_ok = fn.path.exists("/etc/dracut.conf.d/att-plymouth.conf")
            _hooks_label = "att-plymouth.conf exists"

        _row("plymouth installed", _ply_installed, _yes(_ply_installed))
        _row("active theme", _ply_theme)
        _row(
            _hooks_label,
            _ply_hooks_ok,
            _yes(_ply_hooks_ok) if _ply_hooks_ok else ("<span foreground='orange'>missing</span>" if _ply_installed else ""),
        )

        if _bootloader == "systemd-boot":
            _cmdline_exists = fn.path.exists("/etc/kernel/cmdline")
            _cmdline_ok = False
            if _cmdline_exists:
                try:
                    tokens = open("/etc/kernel/cmdline").read().split()
                    _cmdline_ok = "quiet" in tokens and "splash" in tokens
                except OSError:
                    pass
            _cmdline_status = (
                "<span foreground='green'>OK</span>"
                if _cmdline_ok
                else (
                    "<span foreground='orange'>missing quiet/splash</span>"
                    if _cmdline_exists
                    else "<span foreground='orange'>file not found</span>"
                )
            )
            _row("/etc/kernel/cmdline splash", _cmdline_ok, _cmdline_status)

        # ── Privacy ──────────────────────────────────────────────────
        _header("Privacy")
        _hblock = shutil.which("hblock") is not None
        _row("hblock on PATH", _hblock, _yes(_hblock))
        _row("/etc/hosts has hblock marker", _hosts_has_hblock(), _yes(_hosts_has_hblock()))
        _pkg("firefox-ublock-origin")

        # ── Performance ──────────────────────────────────────────────
        _header("Performance")
        _tuned = _pkg("tuned")
        _svc("tuned.service", "tuned", installed=_tuned)
        if _tuned:
            _row("active tuned profile", _tuned_active_profile(fn))
        _ppd = _pkg("tuned-ppd")
        _svc("tuned-ppd.service", "tuned-ppd", installed=_ppd)
        # Always read the PPD D-Bus active profile — mismatch with the
        # tuned profile above is a useful signal (desktop power widget
        # may be overriding what tuned thinks is active).
        _ppd_profile = _ppd_active_profile(fn)
        _tuned_profile = _tuned_active_profile(fn) if _tuned else ""
        # Resolve "performance" → "throughput-performance" etc. via
        # ppd.conf mapping for the comparison, but show raw PPD value.
        _mismatch_markup = ""
        if _tuned and _ppd_profile not in ("(no PPD daemon)", "(unknown)"):
            # Simple direct compare — common mappings agree
            # (balanced=balanced, power-saver=powersave, performance=throughput-performance).
            _agree = (
                _ppd_profile == _tuned_profile
                or (_ppd_profile == "performance" and _tuned_profile == "throughput-performance")
                or (_ppd_profile == "power-saver" and _tuned_profile == "powersave")
            )
            if not _agree:
                _mismatch_markup = "<span foreground='orange'>&#9888; mismatch with tuned</span>"
        _row("PPD active profile (D-Bus)", _ppd_profile, _mismatch_markup)
        _irq = _pkg("irqbalance")
        _svc("irqbalance.service", "irqbalance", installed=_irq)
        _ananicy = _pkg("ananicy-cpp")
        _svc("ananicy-cpp.service", "ananicy-cpp", installed=_ananicy)
        _preload = _pkg("preload")
        _svc("preload.service", "preload", installed=_preload)
        _pkg("gamemode")
        _pkg("cpupower")
        _fstrim_en = fn.check_service_enabled("fstrim.timer")
        _row("fstrim.timer enabled", _fstrim_en, _enabled(_fstrim_en))

        # ── SDDM ─────────────────────────────────────────────────────
        _header("SDDM")
        _row("active display manager", _dm)
        _row("sddm installed", _sddm_installed_shared, _yes(_sddm_installed_shared))
        _sddm_en = fn.check_service_enabled("sddm") if _sddm_installed_shared else False
        _row("sddm enabled", _sddm_en, _enabled(_sddm_en))
        # Current canonical spelling is `plasma-login` (hyphenated). The
        # `plasmalogin` no-hyphen variant was an older CachyOS form; it's
        # still checked in Safeguards' SDDM-hide OR-guard for legacy
        # systems, but a separate row here is just visual noise.
        _row("plasma-login enabled", _plasma_login_shared,
             "<span foreground='orange'>yes</span>" if _plasma_login_shared else "")

        # ── Services ─────────────────────────────────────────────────
        _header("Services")
        _cups = _pkg("cups")
        _svc("cups.service", "cups", installed=_cups)
        _bluez = _pkg("bluez")
        _svc("bluetooth.service", "bluetooth", installed=_bluez)
        _bta = _pkg("bluetooth-autoconnect")
        _svc("bluetooth-autoconnect.service", "bluetooth-autoconnect", installed=_bta)

        # ── Shells ───────────────────────────────────────────────────
        _header("Shells")
        for _s in ("bash", "bash-completion", "zsh", "zsh-completions", "zsh-syntax-highlighting",
                   "oh-my-zsh-git", "fish", "alacritty", "alacritty-tweak-tool"):
            _pkg(_s)

        # ── Software ─────────────────────────────────────────────────
        # ATT detects these via binary paths, not pkg names (Pamac, Discover,
        # GNOME Software etc. ship under varying pkg names per distro).
        _header("Software")
        _sw_bins = [
            ("Pamac", "/usr/bin/pamac-manager"),
            ("Octopi", "/usr/bin/octopi"),
            ("Bazaar", "/usr/bin/bazaar"),
            ("GNOME Software", "/usr/bin/gnome-software"),
            ("Plasma Discover", "/usr/bin/plasma-discover"),
            ("Flatpak", "/usr/bin/flatpak"),
            ("Snap", "/usr/bin/snap"),
            ("pacseek", "/usr/bin/pacseek"),
            ("pacui", "/usr/bin/pacui"),
            ("pachub", "/usr/bin/pachub"),
            ("app-manager", "/usr/bin/app-manager"),
        ]
        for _name, _bin in _sw_bins:
            _present = fn.path.exists(_bin)
            _row(f"{_name} ({_bin})", _present, _yes(_present))

        # ── Themer ───────────────────────────────────────────────────
        _header("Themer")
        for _t in ("kiro-awesome", "kiro-i3", "kiro-leftwm", "kiro-qtile"):
            _pkg(_t)

        # ── Themes ───────────────────────────────────────────────────
        # ArcoLinux is obsolete — themes ship as kiro-arc-* now (per HQ
        # project memory). Don't reintroduce an arcolinux-arc-* check.
        _header("Themes")
        _n_kiro = _count_pkgs_matching(fn, "kiro-arc-") + _count_pkgs_matching(fn, "kiro-neo-candy-") \
                  + _count_pkgs_matching(fn, "kiro-papirus-") + _count_pkgs_matching(fn, "kiro-vimix-")
        _row("kiro-* GTK themes", _n_kiro, _yes(_n_kiro > 0))

        # ── User ─────────────────────────────────────────────────────
        _header("User")
        _in_wheel = _user_in_group(fn, "wheel")
        _row(f"{fn.sudo_username} in wheel", _in_wheel, _yes(_in_wheel))
        _row("/etc/sudoers.d/ entries", _sudoers_d_count())

        # ── Wallpaper ────────────────────────────────────────────────
        _header("Wallpaper")
        _variety = _pkg("variety")
        if _variety:
            _vrun = False
            try:
                _vrun = fn.subprocess.run(["pgrep", "-x", "variety"], capture_output=True).returncode == 0
            except Exception:
                pass
            _row("variety process running", _vrun, _active(_vrun))

        # ════════════════════════════════════════════════════════════════
        # 3. Cross-cutting safeguards
        # ════════════════════════════════════════════════════════════════
        _group("Cross-cutting safeguards")
        _header("Safeguards")

        # On arch + systemd-boot the kernel-install pacman hook must be present
        # or kernel updates won't reach the ESP. Verify it rather than just
        # asserting it's required (otherwise every healthy box shows a warning).
        _kernel_hook_ok = fn.check_package_installed("pacman-hook-kernel-install")
        _kernel_hook_markup = (
            "<span foreground='green'>active — hook installed</span>"
            if _kernel_hook_ok
            else "<span foreground='orange'>&#9888; hook MISSING — install pacman-hook-kernel-install</span>"
        )

        _guard_rows = [
            (
                "Plymouth page hidden",
                "artix guard",
                fn.distr == "artix",
                "<span foreground='orange'>active — Plymouth page hidden</span>",
            ),
            (
                "SDDM page hidden",
                "prismlinux guard",
                fn.distr == "prismlinux",
                "<span foreground='orange'>active — SDDM page hidden</span>",
            ),
            (
                "SDDM page hidden",
                "plasma-login / plasmalogin service",
                _sddm_service_hidden,
                "<span foreground='orange'>active — SDDM page hidden</span>",
            ),
            (
                "Kernel: pacman-hook-kernel-install required",
                "arch + systemd-boot",
                fn.distr == "arch" and _bootloader == "systemd-boot",
                _kernel_hook_markup,
            ),
            (
                "User: visudo section shown",
                "arch guard",
                fn.distr == "arch",
                "<span foreground='green'>active</span>",
            ),
            (
                "Plymouth: omarchy marker on apply",
                "omarchy guard",
                fn.distr == "omarchy",
                "<span foreground='green'>active</span>",
            ),
        ]

        for _guard_name, _guard_condition, _active_b, _active_markup in _guard_rows:
            _row(_guard_name, _guard_condition, _active_markup if _active_b else "")

        # ════════════════════════════════════════════════════════════════
        # 4. System integrity — high-signal subset of the kiro-audit checks
        # ════════════════════════════════════════════════════════════════
        _group("System integrity (kiro-audit mirror)")

        # ── Microcode ────────────────────────────────────────────────
        # The correct ucode (intel OR amd) depends on the CPU — having the
        # matching one present is fine, not a warning. This check exists to
        # catch a specific bug: archiso can strip /boot/*-ucode.img while pacman
        # still records the package installed. So for each installed ucode
        # package, verify its /boot image is actually there.
        # In a VM there is no real CPU to patch, so a missing image is expected,
        # not a fault — mirror kiro-audit and report it benignly (PASS), don't
        # scare the user with a red FAIL.
        _header("Microcode")
        _vm = _is_vm(fn)
        _ucode_found = False
        for _vendor in ("intel", "amd"):
            if fn.check_package_installed(f"{_vendor}-ucode"):
                _ucode_found = True
                _img = fn.path.exists(f"/boot/{_vendor}-ucode.img")
                if _img:
                    _value, _status = f"/boot/{_vendor}-ucode.img", "pass"
                elif _vm:
                    _value, _status = "image not in /boot — expected in a VM (no real CPU to patch)", "pass"
                else:
                    _value, _status = "installed but image MISSING in /boot (archiso stripped it?)", "fail"
                _row(f"{_vendor}-ucode", _value, _state(_status))
        if not _ucode_found:
            _row("microcode package", "(none installed)", _state("warn"))

        # ── Audio stack (PipeWire) ───────────────────────────────────
        _header("Audio stack (PipeWire)")
        for _ap in ("pipewire", "pipewire-pulse", "wireplumber"):
            _ai = fn.check_package_installed(_ap)
            _row(_ap, _ai, _state("pass" if _ai else "fail"))
        _pulse = fn.check_package_installed("pulseaudio")
        _row("pulseaudio not installed", not _pulse, _state("pass" if not _pulse else "fail"))

        # ── ZRAM ─────────────────────────────────────────────────────
        _header("ZRAM")
        _zgen = fn.check_package_installed("zram-generator")
        _row("zram-generator", _zgen, _state("pass" if _zgen else "fail"))
        _zpresent, _zactive, _zalgo = _zram_state(fn)
        _row("/dev/zram0 present", _zpresent, _state("pass" if _zpresent else "fail"))
        if _zpresent:
            _row("active as swap", _zactive, _state("pass" if _zactive else "fail"))
            _row("compression", _zalgo, _state("pass" if _zalgo == "zstd" else "warn"))

        # ── Log rotation ─────────────────────────────────────────────
        # logrotate.timer is enabled on the installed system via Calamares so
        # file-based logs (pacman.log, Xorg/app logs) rotate; journald rotates
        # its own store separately. is-enabled is authoritative — a fresh
        # install can read active-but-disabled, which won't persist across boot.
        _header("Log rotation")
        _logrotate_en = fn.check_service_enabled("logrotate.timer")
        _row("logrotate.timer enabled", _logrotate_en, _enabled(_logrotate_en))

        # ── Calamares cleanup ────────────────────────────────────────
        _header("Calamares cleanup")
        for _cp in ("calamares", "mkinitcpio-archiso", "kiro-calamares-config-next"):
            _gone = not fn.check_package_installed(_cp)
            _row(f"{_cp} removed", _gone, _state("pass" if _gone else "fail"))
        _left = _installer_leftovers(fn)
        if _left:
            _row("installer leftovers", f"{len(_left)} present", _state("fail"))
            for _lp in _left:
                _row("  leftover", _lp, _state("fail"))
        else:
            _row("installer leftovers", "none", _state("pass"))

        # ── Package integrity (pacman -Qk) ───────────────────────────
        _header("Package integrity (pacman -Qk)")
        _bad = _pkg_integrity(fn)
        if _bad:
            _row("packages with missing files", len(_bad), _state("fail"))
            for _bl in _bad[:10]:
                _row("  missing", _bl, _state("fail"))
        else:
            _row("all packages intact", "0 missing files", _state("pass"))

        # ── Failed systemd units ─────────────────────────────────────
        _header("Failed systemd units")
        _funits = _failed_units(fn)
        if _funits:
            _row("failed units", len(_funits), _state("fail"))
            for _fu in _funits[:10]:
                _row("  unit", _fu, _state("fail"))
        else:
            _row("failed units", "0", _state("pass"))

        # ════════════════════════════════════════════════════════════════
        # 5. Userspace tuning — 5 items shipped by kiro-system-files that
        #    influence behaviour without depending on a specific kernel.
        # ════════════════════════════════════════════════════════════════
        _group("Userspace tuning")

        # ── OOM daemon (systemd-oomd) ────────────────────────────────
        _header("OOM daemon (systemd-oomd)")
        _oomd_enabled, _oomd_active = _oomd_state(fn)
        _row("systemd-oomd enabled", _oomd_enabled, _enabled(_oomd_enabled))
        _row("systemd-oomd active", _oomd_active, _active(_oomd_active))

        # ── Intel ME blacklist (mei / mei_me) ────────────────────────
        _header("Intel ME blacklist")
        _mei_conf = fn.path.exists("/etc/modprobe.d/blacklist-intel-me.conf")
        _row("blacklist-intel-me.conf", _mei_conf, _state("pass" if _mei_conf else "fail"))
        _mei_on = _mei_loaded(fn)
        _row("mei/mei_me not loaded", not _mei_on, _state("pass" if not _mei_on else "warn"))

        # ── Bluetooth USB reset ──────────────────────────────────────
        _header("Bluetooth USB reset")
        _bt_conf = fn.path.exists("/etc/modprobe.d/bluetooth-usb.conf")
        _row("bluetooth-usb.conf (btusb reset=1)", _bt_conf, _state("pass" if _bt_conf else "fail"))

        # ── Kernel zswap off (zram-generator owns swap) ──────────────
        _header("Kernel zswap")
        _zswap_conf = fn.path.exists("/etc/tmpfiles.d/disable-zswap.conf")
        _row("disable-zswap.conf tmpfile", _zswap_conf, _state("pass" if _zswap_conf else "fail"))
        _zswap_now = _zswap_runtime(fn)
        _zswap_off = _zswap_now in ("N", "0")
        _row(f"runtime state ({_zswap_now})", _zswap_off,
             _state("pass" if _zswap_off else "fail" if _zswap_now in ("Y", "1") else "warn"))

        # ── NetworkManager loopback unmanaged ────────────────────────
        _header("NetworkManager loopback")
        _nm_conf = fn.path.exists("/etc/NetworkManager/conf.d/unmanaged-lo.conf")
        _row("unmanaged-lo.conf", _nm_conf, _state("pass" if _nm_conf else "fail"))
    _populate()
    # Re-run _populate() every time the DEV box becomes visible (tab
    # revisit). The `map` signal fires after the widget is mapped to
    # the screen, so state changes made from other tabs show up here.
    vboxstack_dev.connect("map", lambda _w: _populate())

    vboxstack_dev.append(hbox_title)
    vboxstack_dev.append(hbox_sep)
    vboxstack_dev.append(hbox_help)
    vboxstack_dev.append(grid)

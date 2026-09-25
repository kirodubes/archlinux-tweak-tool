# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import datetime
import tempfile
from gi.repository import GLib  # noqa
import functions as fn
import desktopr

# Wayland window managers offered on the dedicated "Desktop - Wayland" page.
#
# Every entry is a curated Kiro edition published to nemesis_repo: installing it pulls
# the kiro-<wm> config package (which `depends` on its compositor + shared tools) and
# seeds that edition's config from /etc/skel into ~/.config.
#
# Fields:
#   key      row id + desktopr.check_desktop fallback; equals the session .desktop basename
#            (own-session editions use kiro-<wm>; base editions reuse the upstream session).
#   pkgname  the single package ATT installs/removes; its deps do the rest.
#   skel     /etc/skel/.config/* paths seeded home after install.
#   remove   packages passed to `pacman -R` — the config package ONLY. pacman deletes just
#            that package's files under /etc/skel and /usr; the user's ~/.config is never
#            touched, and the compositor + shared tools are kept (other WMs may use them).
#   proc     compositor process name for the running-session removal guard (pgrep -x).
#   link     upstream project page (wiki/github/codeberg). For shell-variant editions this
#            points at the distinguishing shell (Noctalia/DMS), not the shared compositor,
#            since the base compositor already has its own row and link.
#   shell    optional Quickshell-family tag ("dms" / "noctalia" / "noctura"). Two selected
#            editions whose shell tags differ CANNOT coexist — DMS editions pull the modern
#            upstream Quickshell while Noctalia editions pull noctalia-qs (a pinned fork that
#            Provides+Conflicts quickshell), and Noctura ships its own ~/.config/noctalia so it
#            Conflicts kiro-noctalia. Editions without a shell tag conflict with nothing.
#            selection_conflicts() reads this to warn before the pacman install fails.
#
# Status detection is package-based (fn.check_package_installed(pkgname)) so a row flips to
# "not installed" after `pacman -R kiro-<wm>` even when a base edition's upstream session
# .desktop (owned by the compositor package) remains on disk.
WAYLAND_WMS = [
    {"key": "hyprland", "pkgname": "kiro-hyprland", "label": "Hyprland", "backend": "aquamarine", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/kiro-hyprland", "/etc/skel/.config/waybar"], "ready": True, "proc": "Hyprland", "remove": ["kiro-hyprland"],
     "link": "https://wiki.hyprland.org/"},
    {"key": "kiro-hyprland-noctalia", "pkgname": "kiro-hyprland-noctalia", "label": "Hyprland Noctalia", "backend": "aquamarine", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/kiro-hyprland-noctalia"], "ready": True, "proc": "Hyprland", "remove": ["kiro-hyprland-noctalia"], "shell": "noctalia",
     "link": "https://github.com/noctalia-dev/noctalia"},
    {"key": "kiro-hyprland-noctura", "pkgname": "kiro-hyprland-noctura", "label": "Hyprland Noctura", "backend": "aquamarine", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/kiro-hyprland-noctura", "/etc/skel/.config/noctalia"], "ready": True, "proc": "Hyprland", "remove": ["kiro-hyprland-noctura"], "shell": "noctura",
     "link": "https://github.com/noctalia-dev/noctalia"},
    {"key": "kiro-hyprland-dms", "pkgname": "kiro-hyprland-dms", "label": "Hyprland Dank Material Shell", "backend": "aquamarine", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/kiro-hyprland-dms"], "ready": True, "proc": "Hyprland", "remove": ["kiro-hyprland-dms"], "shell": "dms",
     "link": "https://github.com/AvengeMedia/DankMaterialShell"},
    {"key": "kiro-ohmyniri", "pkgname": "kiro-ohmyniri", "label": "Ohmyniri", "backend": "smithay", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/gtklock", "/etc/skel/.config/kiro-ohmyniri", "/etc/skel/.config/waybar"], "ready": True, "proc": "niri", "remove": ["kiro-ohmyniri"],
     "link": "https://github.com/YaLTeR/niri"},
    {"key": "kiro-niri-noctalia", "pkgname": "kiro-niri-noctalia", "label": "Niri Noctalia", "backend": "smithay", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/kiro-niri-noctalia"], "ready": True, "proc": "niri", "remove": ["kiro-niri-noctalia"], "shell": "noctalia",
     "link": "https://github.com/noctalia-dev/noctalia"},
    {"key": "kiro-niri-dms", "pkgname": "kiro-niri-dms", "label": "Niri Dank Material Shell", "backend": "smithay", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/kiro-niri-dms"], "ready": True, "proc": "niri", "remove": ["kiro-niri-dms"], "shell": "dms",
     "link": "https://github.com/AvengeMedia/DankMaterialShell"},
    {"key": "kiro-mango", "pkgname": "kiro-mango", "label": "Mango", "backend": "wlroots 0.20", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/mango", "/etc/skel/.config/waybar"], "ready": True, "proc": "mango", "remove": ["kiro-mango"],
     "link": "https://github.com/DreamMaoMao/mango"},
    {"key": "miracle-wm", "pkgname": "kiro-miracle", "label": "Miracle", "backend": "Mir", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/miracle-wm", "/etc/skel/.config/waybar"], "ready": True, "proc": "miracle-wm", "remove": ["kiro-miracle"],
     "link": "https://github.com/mattkae/miracle-wm"},
    {"key": "river", "pkgname": "kiro-river", "label": "River", "backend": "wlroots 0.20", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/river", "/etc/skel/.config/waybar"], "ready": True, "proc": "river", "remove": ["kiro-river"],
     "link": "https://codeberg.org/river/river"},
    {"key": "wayfire", "pkgname": "kiro-wayfire", "label": "Wayfire", "backend": "wlroots 0.19", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/fuzzel", "/etc/skel/.config/nwg-drawer", "/etc/skel/.config/waybar", "/etc/skel/.config/wayfire", "/etc/skel/.config/wayfire.ini"],
     "ready": True, "proc": "wayfire", "remove": ["kiro-wayfire"], "link": "https://github.com/WayfireWM/wayfire"},
    {"key": "labwc", "pkgname": "kiro-labwc", "label": "Labwc", "backend": "wlroots 0.20", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/labwc", "/etc/skel/.config/waybar"], "ready": True, "proc": "labwc", "remove": ["kiro-labwc"],
     "link": "https://github.com/labwc/labwc"},
    {"key": "dwl", "pkgname": "kiro-dwl", "label": "Dwl", "backend": "wlroots", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/dwl"], "ready": True, "proc": "dwl", "remove": ["kiro-dwl"],
     "link": "https://codeberg.org/dwl/dwl"},
    {"key": "sway", "pkgname": "kiro-sway", "label": "Sway", "backend": "wlroots (swayfx)", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/sway", "/etc/skel/.config/waybar"], "ready": True, "proc": "sway", "remove": ["kiro-sway"],
     "link": "https://github.com/WillPower3309/swayfx"},
    {"key": "scroll", "pkgname": "kiro-scroll", "label": "Scroll", "backend": "wlroots (sway fork)", "repo": "nemesis_repo",
     "skel": ["/etc/skel/.config/scroll", "/etc/skel/.config/waybar"], "ready": True, "proc": "scroll", "remove": ["kiro-scroll"],
     "link": "https://github.com/dawsers/scroll"},
]


def get_wm(key):
    """Return the WAYLAND_WMS entry for a key, or None."""
    return next((wm for wm in WAYLAND_WMS if wm["key"] == key), None)


def is_installed(wm):
    """True if this WM's curated Kiro package is installed (the row's 'installed' state)."""
    return fn.check_package_installed(wm["pkgname"])


def selection_needs_nemesis(keys):
    """True if any selected WM ships from nemesis_repo (every curated Kiro edition does)."""
    return any((wm := get_wm(k)) and wm["repo"] == "nemesis_repo" for k in keys)


# Human-readable names for the mutually-exclusive Quickshell shell families (the "shell" field).
SHELL_NAMES = {
    "dms": "Dank Material Shell (Quickshell)",
    "noctalia": "Noctalia",
    "noctura": "Noctura",
}


def selection_conflicts(keys):
    """Return (label_a, label_b) pairs in the selection that cannot be installed together.

    Two editions clash when both carry a "shell" tag and the tags differ: DMS pulls the
    modern upstream Quickshell, while Noctalia/Noctura pull noctalia-qs (a fork that
    Provides+Conflicts quickshell), and Noctura additionally Conflicts kiro-noctalia — so
    pacman refuses any cross-family pair. Same-tag picks (two DMS, two Noctalia) coexist.
    """
    tagged = [wm for k in keys if (wm := get_wm(k)) and wm.get("shell")]
    return [(a["label"], b["label"])
            for i, a in enumerate(tagged) for b in tagged[i + 1:]
            if a["shell"] != b["shell"]]


def _backup_overwritten_configs(skel_dirs):
    to_backup = [fn.path.basename(p) for p in skel_dirs if fn.path.exists(fn.home + "/.config/" + fn.path.basename(p))]
    if not to_backup:
        fn.log_info("Selection overwrites no existing configs — nothing to back up")
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    backup_dir = fn.home + "/.config-att/config-att-" + timestamp
    fn.log_info(f"Backing up {len(to_backup)} config(s) the install will overwrite to {backup_dir}")
    fn.makedirs(backup_dir)
    for name in to_backup:
        fn.log_info(f"Backing up ~/.config/{name}")
        fn.copy_func(fn.home + "/.config/" + name, backup_dir + "/" + name, isdir=True)
    fn.permissions(fn.home + "/.config-att")


def install_wayland_selection(self, keys):
    """Install the selected Wayland WMs in one terminal, then seed configs for curated ones.

    Runs as a daemon-thread target. Mirrors desktopr.install_desktop for a set of WMs:
    union the packages, scoped-backup the configs about to be overwritten, run one
    pkexec pacman install, then copy /etc/skel configs home for the curated (ready) WMs.
    """
    selected = [wm for k in keys if (wm := get_wm(k)) and wm.get("ready")]
    if not selected:
        fn.log_warn("install_wayland_selection called with no installable WMs")
        return

    names = ", ".join(wm["label"] for wm in selected)
    fn.log_section(f"Installing Wayland WM(s): {names}")
    fn.show_in_app_notification(self, f"Opening terminal for: {names}")

    packages = [wm["pkgname"] for wm in selected]
    skel_dirs = [d for wm in selected if wm["ready"] for d in wm["skel"]]

    _backup_overwritten_configs(skel_dirs)

    fn.log_subsection(f"Installing {len(packages)} packages")
    fn.debug_print("Packages to install: " + str(packages))

    log_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False)
    log_path = log_file.name
    log_file.close()

    package_list = "\n".join([f"  • {pkg}" for pkg in packages])
    install_cmd = (
        f"( "
        f"RED=$(tput setaf 1); RESET=$(tput sgr0); "
        f"echo 'Installing Wayland window manager(s): {names}' && "
        f"echo '' && "
        f"echo 'The following packages will be installed:' && "
        f"echo '{package_list}' && "
        f"echo '' && "
        f"read -p 'Press Enter to begin installation... ' && "
        f"echo '' && "
        f"pkexec pacman -S {' '.join(packages)} --needed --noconfirm --ask=4 "
        f"&& echo '' && echo '=== Installation Complete ===' "
        f"|| ( echo '' && echo '=== Installation failed — see errors above ===' && echo '' && "
        f'echo "${{RED}}  [EE]  Package(s) not found in enabled repos.${{RESET}}" && '
        f'echo "${{RED}}  [EE]  Kiro Wayland editions need an extra repo (nemesis_repo, chaotic-aur or cachyos) — enable one in ATT > Pacman tab.${{RESET}}" ); '
        f"read -p 'Press Enter to close...' "
        f") 2>&1 | tee {log_path}"
    )

    fn.log_info("Starting package installation...")
    fn.debug_print(f"Terminal cmd: {install_cmd}")
    process = fn.subprocess.Popen(["alacritty", "-e", "bash", "-c", install_cmd])
    process.wait()
    fn.invalidate_pkg_cache()
    GLib.idle_add(_seed_and_refresh, self, selected)


def remove_wayland_selection(self, keys):
    """Remove the selected WMs' Kiro config packages, keeping the compositor and shared tools.

    Runs as a daemon-thread target. Uses plain `pacman -R` (no -s) on the kiro-<wm> config
    package(s) only, so pacman deletes just those packages' files under /etc/skel and /usr —
    the compositor, shared utilities, and the user's ~/.config are never touched. Refuses to
    remove a WM whose compositor is the current running session.
    """
    selected = [wm for k in keys if (wm := get_wm(k)) and wm.get("remove")]
    if not selected:
        fn.log_warn("remove_wayland_selection called with nothing removable")
        return

    for wm in selected:
        proc = wm.get("proc")
        if proc and fn.subprocess.run(["pgrep", "-x", proc], capture_output=True).returncode == 0:
            fn.log_warn(f"Refusing to remove {wm['label']} — it is the current running session")
            fn.show_in_app_notification(self, f"Cannot remove {wm['label']} — log out of it first")
            return

    names = ", ".join(wm["label"] for wm in selected)
    packages = [pkg for wm in selected for pkg in wm["remove"]]
    fn.log_section(f"Removing Wayland WM(s): {names}")
    fn.show_in_app_notification(self, f"Opening terminal to remove: {names}")

    log_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False)
    log_path = log_file.name
    log_file.close()

    package_list = "\n".join([f"  • {pkg}" for pkg in packages])
    remove_cmd = (
        f"( "
        f"echo 'Removing Wayland window manager(s): {names}' && "
        f"echo '' && "
        f"echo 'The following packages will be removed:' && "
        f"echo '{package_list}' && "
        f"echo '' && "
        f"echo 'Shared tools (waybar, rofi, polkit, pavucontrol, …) are kept.' && "
        f"echo 'Your ~/.config is left untouched.' && "
        f"echo '' && "
        f"read -p 'Press Enter to remove... ' && "
        f"echo '' && "
        f"pkexec pacman -R {' '.join(packages)} --noconfirm "
        f"|| {{ echo ''; echo 'ERROR: removal failed — a package may still be in use (see above)'; echo ''; }} ; "
        f"echo '=== Done ===' ; "
        f"read -p 'Press Enter to close...' "
        f") 2>&1 | tee {log_path}"
    )

    fn.debug_print(f"Remove command: {remove_cmd}")
    process = fn.subprocess.Popen(["alacritty", "-e", "bash", "-c", remove_cmd])
    process.wait()
    fn.invalidate_pkg_cache()
    GLib.idle_add(_reset_caches_and_refresh, self, names)


def _reset_caches_and_refresh(self, names):
    desktopr._xsession_files = None
    desktopr._wayland_files = None
    fn.log_success(f"Wayland removal finished: {names}")
    if hasattr(self, "wayland_refresh"):
        self.wayland_refresh()
    return False


def _seed_and_refresh(self, selected):
    # Reset desktopr's session-file caches so check_desktop re-scans and sees the
    # newly installed wayland-session files (mirrors desktopr._after_install).
    desktopr._xsession_files = None
    desktopr._wayland_files = None
    for wm in selected:
        if not (wm["ready"] and is_installed(wm)):
            continue
        fn.log_info(f"Seeding {wm['label']} config from /etc/skel")
        for src in wm["skel"]:
            if not (fn.path.isdir(src) or fn.path.isfile(src)):
                continue
            dest = src.replace("/etc/skel", fn.home)
            if fn.path.isdir(src):
                dest = fn.path.split(dest)[0]
            fn.log_info(f"Copying skel: {src}  →  {dest}")
            with fn.subprocess.Popen(desktopr.copy + [src, dest], bufsize=1, stdout=fn.subprocess.PIPE, universal_newlines=True) as p:
                for line in p.stdout:
                    fn.debug_print(line.strip())
            fn.permissions(dest)
    fn.log_success(f"Wayland install finished: {', '.join(wm['label'] for wm in selected)}")
    if hasattr(self, "wayland_refresh"):
        self.wayland_refresh()
    return False


def _refresh_htt_lbl(self):
    if fn.check_package_installed("hyprland-tweak-tool"):
        self.htt_status_lbl.set_markup("hyprland-tweak-tool is <b>installed</b>")
    else:
        self.htt_status_lbl.set_markup("hyprland-tweak-tool is <b>not installed</b>")


def _refresh_htt_launch_btn(self):
    self.btn_launch_htt.set_sensitive(fn.check_package_installed("hyprland-tweak-tool"))


def on_install_hyprland_tweak_tool_clicked(self, _widget):
    """Install hyprland-tweak-tool from nemesis repo via terminal."""
    if fn.check_package_installed("hyprland-tweak-tool"):
        fn.log_info("hyprland-tweak-tool is already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "hyprland-tweak-tool is already installed")
        return
    fn.log_subsection("Installing hyprland-tweak-tool...")
    process = fn.launch_pacman_install_in_terminal("hyprland-tweak-tool")
    fn.GLib.idle_add(fn.show_in_app_notification, self, "Opening terminal to install hyprland-tweak-tool")

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("hyprland-tweak-tool installed")
            fn.GLib.idle_add(_refresh_htt_lbl, self)
            fn.GLib.idle_add(_refresh_htt_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, "hyprland-tweak-tool installed")
        except Exception as e:
            fn.log_error(f"Error installing hyprland-tweak-tool: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_hyprland_tweak_tool_clicked(self, _widget):
    """Remove hyprland-tweak-tool via terminal."""
    if not fn.check_package_installed("hyprland-tweak-tool"):
        fn.log_info("hyprland-tweak-tool is not installed — nothing to remove")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "hyprland-tweak-tool is not installed")
        return
    fn.log_subsection("Removing hyprland-tweak-tool...")
    process = fn.launch_pacman_remove_in_terminal("hyprland-tweak-tool")
    fn.GLib.idle_add(fn.show_in_app_notification, self, "Opening terminal to remove hyprland-tweak-tool")

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("hyprland-tweak-tool removed")
            fn.GLib.idle_add(_refresh_htt_lbl, self)
            fn.GLib.idle_add(_refresh_htt_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, "hyprland-tweak-tool removed")
        except Exception as e:
            fn.log_error(f"Error removing hyprland-tweak-tool: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def on_click_launch_htt(self, _widget):
    """Launch Hyprland Tweak Tool as real user from the Wayland page."""
    if fn.check_package_installed("hyprland-tweak-tool"):
        fn.log_subsection("Launching Hyprland Tweak Tool...")
        fn.subprocess.Popen(
            "sudo -E -u " + fn.sudo_username + " env HOME=" + fn.home + " hyprland-tweak-tool &",
            shell=True,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        fn.GLib.idle_add(fn.show_in_app_notification, self, "Hyprland Tweak Tool launched")
    else:
        fn.log_info("hyprland-tweak-tool not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "hyprland-tweak-tool not installed")

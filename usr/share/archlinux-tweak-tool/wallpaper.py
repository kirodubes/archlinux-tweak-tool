# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import re
import shutil

import functions as fn
from gi.repository import GdkPixbuf, Gdk, Gtk, Gio, Pango


_DIR = fn.path.dirname(fn.path.abspath(__file__))
_ATT_WALLPAPERS = fn.path.join(_DIR, "wallpapers")
_VARIETY_CONF_SRC = fn.path.join(_DIR, "data", "variety")
_VARIETY_CONF_DEST = fn.path.join(fn.home, ".config", "variety")
_VARIETY_CONF_BAK = fn.path.join(fn.home, ".config", "variety-bak")
_VARIETY_DESKTOP_SRC = "/usr/share/applications/variety.desktop"
_VARIETY_AUTOSTART = fn.path.join(fn.home, ".config", "autostart", "variety.desktop")

_FEH_FLAGS = {
    "Fill": "--bg-fill",
    "Fit": "--bg-max",
    "Center": "--bg-center",
    "Tile": "--bg-tile",
    "Stretch": "--bg-scale",
}


_GNOME_MODES = {
    "Fill": "zoom",
    "Fit": "scaled",
    "Center": "centered",
    "Tile": "wallpaper",
    "Stretch": "stretched",
}


_SIMPLE_WMS = {
    "awesome",
    "berry",
    "bspwm",
    "ohmychadwm",
    "chadwm",
    "cwm",
    "dk",
    "dusk",
    "flexi",
    "dwm",
    "fvwm3",
    "herbstluftwm",
    "hypr",
    "i3",
    "i3-with-shmlog",
    "icewm",
    "icewm-session",
    "jwm",
    "leftwm",
    "nimdow",
    "openbox",
    "qtile",
    "spectrwm",
    "worm",
    "wmderland",
    "xmonad",
}

_HIDE_PICKER_DESKTOPS = frozenset(
    [
        "gnome",
        "unity",
        "kde",
        "xfce",
        "mate",
        "cinnamon",
        "x-cinnamon",
        "budgie",
        "deepin",
        "lxqt",
        "lxde",
        "pantheon",
    ]
)


# swaybg's -m modes match the Scale dropdown 1:1; awww/swww only know crop / fit / no
_SWAYBG_MODES = {"Fill": "fill", "Fit": "fit", "Center": "center", "Tile": "tile", "Stretch": "stretch"}
_SWWW_RESIZE = {"Fill": "crop", "Fit": "fit", "Center": "no"}


def _get_user_env(keys):
    result = {k: fn.os.environ.get(k, "") for k in keys}
    if any(result.values()):
        return result
    username = getattr(fn, "sudo_username", None)
    if not username:
        return result
    try:
        for pid in fn.os.listdir("/proc"):
            env_file = f"/proc/{pid}/environ"
            if not fn.path.isfile(env_file):
                continue
            try:
                with open(env_file, "rb") as f:
                    entries = dict(e.split(b"=", 1) for e in f.read().split(b"\x00") if b"=" in e)
                if entries.get(b"LOGNAME", b"").decode() == username:
                    for k in keys:
                        val = entries.get(k.encode(), b"").decode()
                        if val:
                            result[k] = val
                    if any(result.values()):
                        break
            except (PermissionError, OSError, ValueError):
                continue
    except Exception:
        pass
    return result


def should_show_picker():
    """Return True if the wallpaper picker should be shown (hidden on full DEs that manage wallpaper themselves)."""
    env = _get_user_env(["XDG_CURRENT_DESKTOP", "DESKTOP_SESSION", "XDG_SESSION_DESKTOP", "KDE_FULL_SESSION"])
    if env["KDE_FULL_SESSION"] == "true":
        return False
    desktop = (env["XDG_CURRENT_DESKTOP"] + " " + env["DESKTOP_SESSION"] + " " + env["XDG_SESSION_DESKTOP"]).lower()
    return not any(name in desktop for name in _HIDE_PICKER_DESKTOPS)


def on_restore_variety_backup(self, _widget=None):
    """Restore the variety config from ~/.config/variety-bak."""
    fn.log_subsection("Restore variety backup")
    if not fn.path.isdir(_VARIETY_CONF_BAK):
        fn.log_warn("No variety backup found at ~/.config/variety-bak")
        fn.show_in_app_notification(self, "No backup found")
        return
    try:
        if fn.path.isdir(_VARIETY_CONF_DEST):
            shutil.rmtree(_VARIETY_CONF_DEST)
        shutil.copytree(_VARIETY_CONF_BAK, _VARIETY_CONF_DEST)
        fn.permissions(_VARIETY_CONF_DEST)
        fn.log_success("Variety backup restored to ~/.config/variety")
        fn.show_in_app_notification(self, "Variety backup restored")
    except Exception as error:
        fn.log_error(f"Failed to restore variety backup: {error}")
        fn.show_in_app_notification(self, f"Restore failed: {error}")


def on_install_or_launch_variety(self, _widget=None):
    """Install variety if absent, or launch it if already installed."""
    if fn.check_package_installed("variety"):
        fn.log_subsection("Launch variety")
        uid = fn.subprocess.run(["id", "-u", fn.sudo_username], capture_output=True, text=True).stdout.strip()
        cmd = _variety_cmd(fn, uid, "")
        fn.debug_print(f"Launching: {cmd}")
        fn.subprocess.Popen(cmd, shell=True, stdout=fn.subprocess.PIPE, stderr=fn.subprocess.PIPE)
        fn.log_success("Variety launched")
        fn.show_in_app_notification(self, "Variety launched")
        return

    fn.log_subsection("Install variety")
    fn.show_in_app_notification(self, "Opening terminal to install variety...")
    process = fn.launch_pacman_install_in_terminal("variety")

    def refresh():
        installed = fn.check_package_installed("variety")
        _set_variety_widgets_sensitive(self, installed)
        fn.GLib.idle_add(self.lbl_variety_installed.set_visible, installed)
        if installed:
            fn.log_success("variety installed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, "variety installed — launching...")
            uid = fn.subprocess.run(["id", "-u", fn.sudo_username], capture_output=True, text=True).stdout.strip()
            cmd = _variety_cmd(fn, uid, "")
            fn.debug_print(f"Launching: {cmd}")
            fn.subprocess.Popen(cmd, shell=True, stdout=fn.subprocess.PIPE, stderr=fn.subprocess.PIPE)
            fn.log_success("Variety launched")
        else:
            fn.log_warn("variety installation did not complete")
            fn.GLib.idle_add(fn.show_in_app_notification, self, "variety installation failed or was cancelled")

    def wait_and_refresh():
        fn.debug_print("Waiting for variety install terminal to close...")
        if process:
            process.wait()
        fn.debug_print("Terminal closed — checking install result")
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(refresh)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_remove_variety(self, _widget=None):
    """Remove variety and update widget sensitivity."""
    if not fn.check_package_installed("variety"):
        fn.log_info("variety is not installed")
        fn.show_in_app_notification(self, "variety is not installed")
        return
    fn.log_subsection("Remove variety")
    fn.show_in_app_notification(self, "Opening terminal to remove variety...")
    process = fn.launch_pacman_remove_in_terminal("variety")

    def refresh():
        installed = fn.check_package_installed("variety")
        _set_variety_widgets_sensitive(self, installed)
        self.lbl_variety_installed.set_visible(installed)
        if not installed:
            fn.log_success("variety removed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, "variety removed")
        else:
            fn.log_info("variety still present after remove")

    def wait_and_refresh():
        fn.debug_print("Waiting for variety remove terminal to close...")
        if process:
            process.wait()
        fn.debug_print("Terminal closed — checking removal result")
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(refresh)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_variety_next(self, _widget=None):
    """Advance variety to the next wallpaper."""
    if not fn.check_package_installed("variety"):
        fn.log_info("variety is not installed")
        fn.show_in_app_notification(self, "variety is not installed")
        return
    fn.log_subsection("Variety: next wallpaper")
    uid = fn.subprocess.run(["id", "-u", fn.sudo_username], capture_output=True, text=True).stdout.strip()
    cmd = _variety_cmd(fn, uid, "-n")
    fn.debug_print(f"Launching: {cmd}")
    fn.subprocess.Popen(cmd, shell=True, stdout=fn.subprocess.PIPE, stderr=fn.subprocess.PIPE)
    fn.log_success("Variety: next wallpaper")


def on_variety_prev(self, _widget=None):
    """Rewind variety to the previous wallpaper."""
    if not fn.check_package_installed("variety"):
        fn.log_info("variety is not installed")
        fn.show_in_app_notification(self, "variety is not installed")
        return
    fn.log_subsection("Variety: previous wallpaper")
    uid = fn.subprocess.run(["id", "-u", fn.sudo_username], capture_output=True, text=True).stdout.strip()
    cmd = _variety_cmd(fn, uid, "-p")
    fn.debug_print(f"Launching: {cmd}")
    fn.subprocess.Popen(cmd, shell=True, stdout=fn.subprocess.PIPE, stderr=fn.subprocess.PIPE)
    fn.log_success("Variety: previous wallpaper")


_VARIETY_DESKTOP_FALLBACK = """\
[Desktop Entry]
Name=Variety
Comment=Variety Wallpaper Changer
Categories=System;Core;FileTools;FileManager;GNOME;GTK;Utility;
Exec=/usr/bin/variety --profile {home}/.config/variety/
MimeType=text/uri-list;x-scheme-handler/variety;x-scheme-handler/vrty;
Icon=variety
Terminal=false
Type=Application
StartupNotify=false
Actions=Next;Previous;PauseResume;History;Preferences;
Keywords=Wallpaper;Changer;Change;Download;Downloader;Variety;
X-GNOME-Autostart-Delay=20
StartupWMClass=Variety
Hidden=false
"""


def _ensure_variety_desktop():
    if fn.path.isfile(_VARIETY_DESKTOP_SRC):
        return True
    try:
        content = _VARIETY_DESKTOP_FALLBACK.format(home=fn.home)
        with open(_VARIETY_DESKTOP_SRC, "w", encoding="utf-8") as f:
            f.write(content)
        fn.log_success(f"Created fallback variety.desktop at {_VARIETY_DESKTOP_SRC}")
        return True
    except Exception as error:
        fn.log_error(f"Failed to create variety.desktop: {error}")
        return False


def on_add_variety_autostart(self, _widget=None):
    """Copy the variety desktop entry to ~/.config/autostart."""
    fn.log_subsection("Add variety to autostart")
    if not _ensure_variety_desktop():
        fn.show_in_app_notification(self, "Could not create variety.desktop")
        return
    try:
        fn.os.makedirs(fn.path.dirname(_VARIETY_AUTOSTART), exist_ok=True)
        shutil.copy2(_VARIETY_DESKTOP_SRC, _VARIETY_AUTOSTART)
        fn.permissions(_VARIETY_AUTOSTART)
        fn.log_success(f"variety added to autostart: {_VARIETY_AUTOSTART}")
        fn.show_in_app_notification(self, "Variety added to autostart")
        fn.GLib.idle_add(self.btn_add_variety_autostart.set_sensitive, False)
        fn.GLib.idle_add(self.btn_remove_variety_autostart.set_sensitive, True)
    except Exception as error:
        fn.log_error(f"Failed to add variety to autostart: {error}")
        fn.show_in_app_notification(self, f"Error: {error}")


def on_remove_variety_autostart(self, _widget=None):
    """Remove the variety entry from ~/.config/autostart."""
    fn.log_subsection("Remove variety from autostart")
    if not fn.path.isfile(_VARIETY_AUTOSTART):
        fn.log_info("variety autostart entry not found — nothing to remove")
        fn.show_in_app_notification(self, "Variety is not in autostart")
        return
    try:
        fn.os.remove(_VARIETY_AUTOSTART)
        fn.log_success("variety removed from autostart")
        fn.show_in_app_notification(self, "Variety removed from autostart")
        fn.GLib.idle_add(self.btn_add_variety_autostart.set_sensitive, True)
        fn.GLib.idle_add(self.btn_remove_variety_autostart.set_sensitive, False)
    except Exception as error:
        fn.log_error(f"Failed to remove variety from autostart: {error}")
        fn.show_in_app_notification(self, f"Error: {error}")


def _set_variety_widgets_sensitive(self, installed):
    self.btn_variety_next.set_sensitive(installed)
    self.btn_variety_prev.set_sensitive(installed)
    self.btn_save_variety_config.set_sensitive(installed)
    self.btn_open_variety_settings.set_sensitive(installed)
    self.btn_open_variety_selector.set_sensitive(installed)
    autostarts = fn.path.isfile(_VARIETY_AUTOSTART)
    self.btn_add_variety_autostart.set_sensitive(installed and not autostarts)
    self.btn_remove_variety_autostart.set_sensitive(autostarts)


def _fix_variety_conf_paths():
    conf = fn.path.join(_VARIETY_CONF_DEST, "variety.conf")
    if not fn.path.isfile(conf):
        return
    fn.log_info_concise(f"  Changing username in variety.conf → {fn.sudo_username}")
    with open(conf, "r", encoding="utf-8") as f:
        content = f.read()
    fixed = re.sub(r"/home/[^/]+/", fn.home + "/", content)
    if fixed != content:
        with open(conf, "w", encoding="utf-8") as f:
            f.write(fixed)
        fn.log_info_concise(f"  Paths updated to {fn.home}/")
        fn.debug_print(f"variety.conf home paths rewritten to {fn.home}/")


def on_save_variety_config(self, _widget=None):
    """Copy the ATT variety config to ~/.config/variety, rewriting home paths."""
    fn.log_subsection("Save ATT variety config")
    if not fn.path.isdir(_VARIETY_CONF_SRC):
        fn.log_warn(f"ATT variety config folder not found: {_VARIETY_CONF_SRC}")
        fn.show_in_app_notification(self, "ATT variety config not found in data folder")
        return
    try:
        if fn.path.isfile(fn.path.join(_VARIETY_CONF_DEST, "variety.conf")):
            if fn.path.isdir(_VARIETY_CONF_BAK):
                shutil.rmtree(_VARIETY_CONF_BAK)
            shutil.copytree(_VARIETY_CONF_DEST, _VARIETY_CONF_BAK)
            fn.permissions(_VARIETY_CONF_BAK)
            fn.log_info_concise(f"  Backed up: {_VARIETY_CONF_DEST} → {_VARIETY_CONF_BAK}")
            fn.GLib.idle_add(self.btn_restore_variety_backup.set_sensitive, True)
        fn.os.makedirs(_VARIETY_CONF_DEST, exist_ok=True)
        fn.permissions(_VARIETY_CONF_DEST)
        for item in fn.os.listdir(_VARIETY_CONF_SRC):
            src = fn.path.join(_VARIETY_CONF_SRC, item)
            dest = fn.path.join(_VARIETY_CONF_DEST, item)
            if fn.path.isdir(src):
                fn.log_info_concise(f"  From: {src}")
                fn.log_info_concise(f"  To:   {dest}")
                shutil.copytree(src, dest, dirs_exist_ok=True)
                fn.permissions(dest)
                fn.log_info_concise(f"  Done: {fn.path.basename(src)}/")
            else:
                fn.log_info_concise(f"  From: {src}")
                fn.log_info_concise(f"  To:   {dest}")
                shutil.copy2(src, dest)
                fn.permissions(dest)
                fn.log_info_concise(f"  Done: {fn.path.basename(src)}")
        _fix_variety_conf_paths()
        fn.log_success("ATT variety config saved to ~/.config/variety/")
        fn.log_tip("Store your wallpapers in ~/Templates/wallpapers — variety picks them up automatically")
        fn.show_in_app_notification(self, "Variety config saved")
    except Exception as error:
        fn.log_error(f"Failed to save variety config: {error}")
        fn.show_in_app_notification(self, f"Error: {error}")


def _variety_cmd(fn, uid, args):
    env = _get_user_env(["XDG_CURRENT_DESKTOP", "WAYLAND_DISPLAY", "XDG_SESSION_TYPE"])
    xdg_desktop = env.get("XDG_CURRENT_DESKTOP", "")
    on_wayland = bool(env.get("WAYLAND_DISPLAY")) or env.get("XDG_SESSION_TYPE") == "wayland"
    display_env = "WAYLAND_DISPLAY=$WAYLAND_DISPLAY" if on_wayland else "DISPLAY=$DISPLAY"
    wayland_backend = "GDK_BACKEND=wayland" if on_wayland else ""
    return (
        f"sudo -u {fn.sudo_username}"
        f" XDG_RUNTIME_DIR=/run/user/{uid}"
        f" DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus"
        f" XDG_CURRENT_DESKTOP={xdg_desktop}"
        f" {display_env}"
        f" {wayland_backend}"
        f" variety {args}"
    )


def on_open_variety_settings(self, _widget=None):
    """Open the variety preferences window."""
    fn.log_subsection("Open variety settings")
    uid = fn.subprocess.run(["id", "-u", fn.sudo_username], capture_output=True, text=True).stdout.strip()
    cmd = _variety_cmd(fn, uid, "--preferences")
    fn.debug_print(f"Launching: {cmd}")
    fn.subprocess.Popen(cmd, shell=True, stdout=fn.subprocess.PIPE, stderr=fn.subprocess.PIPE)
    fn.log_success("Variety settings launched")


def on_open_variety_selector(self, _widget=None):
    """Open the variety wallpaper selector."""
    fn.log_subsection("Open variety selector")
    uid = fn.subprocess.run(["id", "-u", fn.sudo_username], capture_output=True, text=True).stdout.strip()
    cmd = _variety_cmd(fn, uid, "--selector")
    fn.debug_print(f"Launching: {cmd}")
    fn.subprocess.Popen(cmd, shell=True, stdout=fn.subprocess.PIPE, stderr=fn.subprocess.PIPE)
    fn.log_success("Variety selector launched")


def on_browse_wallpaper_folder(self, _widget=None):
    """Open a folder chooser dialog to set the wallpaper source directory."""
    fn.log_subsection("Browse wallpaper folder")
    dialog = Gtk.FileDialog()
    dialog.set_title("Choose a wallpaper folder")
    current = self.wallpaper_folder_entry.get_text().strip()
    start = current if fn.path.isdir(current) else fn.home
    dialog.set_initial_folder(Gio.File.new_for_path(start))
    dialog.select_folder(self, None, lambda d, result: _on_folder_response(self, d, result))


def _on_folder_response(self, dialog, result):
    try:
        folder = dialog.select_folder_finish(result)
        if folder:
            folder_path = folder.get_path()
            fn.log_info_concise(f"  Folder selected: {folder_path}")
            fn.debug_print(f"Browse selected: {folder_path}")
            self.wallpaper_folder_entry.set_text(folder_path)
            _populate_wallpaper_thumbs(self, folder_path)
    except Exception:
        pass


def on_load_wallpaper_folder(self, _widget=None):
    """Load thumbnails from the folder path currently in the entry widget."""
    folder_path = self.wallpaper_folder_entry.get_text().strip()
    if fn.path.isdir(folder_path):
        _populate_wallpaper_thumbs(self, folder_path)
    else:
        fn.log_warn(f"Wallpaper folder not found: {folder_path}")
        fn.show_in_app_notification(self, "Folder not found")


def on_stop_wallpaper_loading(self, _widget=None):
    """Cancel any in-progress thumbnail loading."""
    fn.debug_print("Wallpaper loading stopped by user")
    self._wp_load_gen = getattr(self, "_wp_load_gen", 0) + 1


def _populate_wallpaper_thumbs(self, folder_path):
    self._wp_load_gen = getattr(self, "_wp_load_gen", 0) + 1
    current_gen = self._wp_load_gen

    child = self.wallpaper_thumb_flow.get_first_child()
    while child is not None:
        next_child = child.get_next_sibling()
        self.wallpaper_thumb_flow.remove(child)
        child = next_child

    exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    try:
        entries = sorted(fn.os.listdir(folder_path))
    except Exception:
        return

    image_paths = [fn.path.join(folder_path, n) for n in entries if n.lower().endswith(exts)]
    idx = [0]

    def load_next():
        if self._wp_load_gen != current_gen:
            return False
        if idx[0] >= len(image_paths):
            return False
        path = image_paths[idx[0]]
        idx[0] += 1
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 160, 100, True)
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            pic = Gtk.Picture.new_for_paintable(texture)
            pic.set_can_shrink(False)
            pic.set_size_request(160, 100)

            lbl = Gtk.Label()
            lbl.set_text(fn.path.basename(path))
            lbl.set_max_width_chars(18)
            lbl.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            box.set_margin_top(4)
            box.set_margin_bottom(4)
            box.set_margin_start(4)
            box.set_margin_end(4)
            box.append(pic)
            box.append(lbl)

            btn = Gtk.Button()
            btn.set_child(box)
            btn.connect("clicked", lambda w, p=path: _on_thumb_clicked(self, w, p))
            self.wallpaper_thumb_flow.append(btn)
        except Exception:
            pass
        return True

    fn.GLib.idle_add(load_next)


def _on_thumb_clicked(self, _widget, path):
    fn.log_info_concise(f"  Selected: {path}")
    fn.debug_print(f"Wallpaper selected: {path}")
    self.selected_wallpaper_path = path
    self.wallpaper_path_lbl.set_text(path)
    self.wallpaper_preview.set_filename(path)
    self.wallpaper_preview.get_parent().set_visible(True)


def on_apply_wallpaper(self, _widget=None):
    """Apply the selected wallpaper using the detected display server and desktop environment."""
    path = getattr(self, "selected_wallpaper_path", None)
    if not path or not fn.path.isfile(path):
        fn.log_info("No wallpaper selected")
        fn.show_in_app_notification(self, "Select a wallpaper first")
        return
    scale = fn.get_combo_text(self.wallpaper_scale_combo)
    _apply_wallpaper(self, path, scale)


def _apply_wallpaper(self, path, scale):
    env = _get_user_env(["WAYLAND_DISPLAY", "XDG_SESSION_TYPE"])
    if env["WAYLAND_DISPLAY"] or env["XDG_SESSION_TYPE"] == "wayland":
        fn.threading.Thread(target=_apply_wayland, args=(self, path, scale), daemon=True).start()
    else:
        _apply_x11(self, path, scale)


def _wayland_user_cmd():
    """Command prefix that runs as the session user with that user's Wayland env (pkexec strips it from ATT)."""
    uid = fn.subprocess.run(["id", "-u", fn.sudo_username], capture_output=True, text=True).stdout.strip()
    # queried one key at a time: _get_user_env stops at the first process holding any requested key,
    # and the compositor process itself does not carry WAYLAND_DISPLAY
    display = _get_user_env(["WAYLAND_DISPLAY"])["WAYLAND_DISPLAY"] or "wayland-1"
    hypr_sig = _get_user_env(["HYPRLAND_INSTANCE_SIGNATURE"])["HYPRLAND_INSTANCE_SIGNATURE"]
    cmd = ["sudo", "-u", fn.sudo_username, "env", f"XDG_RUNTIME_DIR=/run/user/{uid}", f"WAYLAND_DISPLAY={display}"]
    if hypr_sig:
        cmd.append(f"HYPRLAND_INSTANCE_SIGNATURE={hypr_sig}")
    return cmd


def _user_running(name):
    return fn.subprocess.run(["pgrep", "-u", fn.sudo_username, "-x", name], capture_output=True).returncode == 0


def _run_ok(cmd):
    try:
        result = fn.subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except (FileNotFoundError, fn.subprocess.TimeoutExpired) as e:
        fn.log_warn(f"  {cmd[-1]}: {e}")
        return False
    if result.returncode != 0:
        fn.log_warn(f"  failed (rc={result.returncode}): {(result.stderr or result.stdout).strip()[:200]}")
    return result.returncode == 0


def _start_daemon_and_img(user, daemon, client, path, scale):
    """Start awww/swww's daemon detached, wait until it answers, then set the image."""
    fn.subprocess.Popen(
        user + ["setsid", daemon], stdout=fn.subprocess.DEVNULL, stderr=fn.subprocess.DEVNULL, start_new_session=True
    )
    for _ in range(20):
        if fn.subprocess.run(user + [client, "query"], capture_output=True).returncode == 0:
            break
        fn.time.sleep(0.25)
    return _run_ok(user + [client, "img", "--resize", _SWWW_RESIZE.get(scale, "crop"), path])


def _set_hyprpaper(user, path):
    # preload is gone in newer hyprpaper — its failure is harmless, only `wallpaper` decides
    _run_ok(user + ["hyprctl", "hyprpaper", "preload", path])
    return _run_ok(user + ["hyprctl", "hyprpaper", "wallpaper", f",{path}"])


def _start_wbg(user, path):
    fn.subprocess.run(["pkill", "-u", fn.sudo_username, "-x", "wbg"])
    fn.subprocess.Popen(
        user + ["setsid", "wbg", path], stdout=fn.subprocess.DEVNULL, stderr=fn.subprocess.DEVNULL
    )
    return True


def _wayland_setters(user, path, scale):
    """Ordered fallback chain of (label, applicable, apply) — first applicable one that succeeds wins."""
    swww_resize = _SWWW_RESIZE.get(scale, "crop")
    script = fn.path.join(_DIR, "data", "bin", "att-set-wallpaper")
    return [
        # 1. a desktop shell that draws its own backdrop — anything started underneath it stays hidden
        (
            "ryogami (Ryoku)",
            lambda: shutil.which("ryogami") and _user_running("ryogami"),
            lambda: _run_ok(user + ["ryogami", "wallpaper", "set", path]),
        ),
        (
            "DankMaterialShell",
            lambda: shutil.which("dms") and _user_running("dms"),
            lambda: _run_ok(user + ["dms", "ipc", "call", "wallpaper", "set", path]),
        ),
        # 2. a wallpaper daemon already running in the session — reuse it rather than stacking a second one
        (
            "hyprpaper",
            lambda: shutil.which("hyprctl") and _user_running("hyprpaper"),
            lambda: _set_hyprpaper(user, path),
        ),
        (
            "awww",
            lambda: shutil.which("awww") and _user_running("awww-daemon"),
            lambda: _run_ok(user + ["awww", "img", "--resize", swww_resize, path]),
        ),
        (
            "swww",
            lambda: shutil.which("swww") and _user_running("swww-daemon"),
            lambda: _run_ok(user + ["swww", "img", "--resize", swww_resize, path]),
        ),
        # 3. nothing running — start a setter ourselves
        (
            "swaybg",
            lambda: shutil.which("swaybg"),
            lambda: _run_ok(user + ["bash", script, path, _SWAYBG_MODES.get(scale, "fill")]),
        ),
        (
            "awww (starting awww-daemon)",
            lambda: shutil.which("awww") and shutil.which("awww-daemon"),
            lambda: _start_daemon_and_img(user, "awww-daemon", "awww", path, scale),
        ),
        (
            "swww (starting swww-daemon)",
            lambda: shutil.which("swww") and shutil.which("swww-daemon"),
            lambda: _start_daemon_and_img(user, "swww-daemon", "swww", path, scale),
        ),
        ("wbg", lambda: shutil.which("wbg"), lambda: _start_wbg(user, path)),
    ]


def _apply_wayland(self, path, scale):
    name = fn.path.basename(path)
    user = _wayland_user_cmd()
    tried = []
    for label, applicable, apply in _wayland_setters(user, path, scale):
        if not applicable():
            continue
        tried.append(label)
        fn.log_subsection(f"Applying wallpaper — {label}: {path}")
        if apply():
            fn.log_success(f"Wallpaper set with {label}: {name}")
            fn.GLib.idle_add(fn.show_in_app_notification, self, f"Wallpaper set: {name}")
            return
    if tried:
        fn.log_error(f"Every Wayland wallpaper setter failed ({', '.join(tried)})")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "Setting the wallpaper failed — see the ATT log")
    else:
        fn.log_error("No Wayland wallpaper setter found (ryogami / dms / hyprpaper / awww / swww / swaybg / wbg)")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "No wallpaper setter found — install swaybg or awww")


def _apply_x11(self, path, scale):
    env = _get_user_env(["XDG_CURRENT_DESKTOP", "DESKTOP_SESSION", "XDG_SESSION_DESKTOP", "KDE_FULL_SESSION"])
    desktop = (env["XDG_CURRENT_DESKTOP"] + env["DESKTOP_SESSION"] + env["XDG_SESSION_DESKTOP"]).lower()
    kde = env["KDE_FULL_SESSION"] == "true"

    fn.debug_print(f"X11 DE detection: {env}")

    if kde:
        _set_kde(self, path)
    elif "gnome" in desktop or "unity" in desktop:
        _set_gnome(self, path, scale)
    elif "mate" in desktop:
        _set_mate(self, path, scale)
    elif "cinnamon" in desktop or "x-cinnamon" in desktop:
        _set_cinnamon(self, path, scale)
    else:
        _set_feh(self, path, scale)


def _set_feh(self, path, scale):
    flag = _FEH_FLAGS.get(scale, "--bg-fill")
    if shutil.which("feh"):
        fn.log_subsection(f"Applying wallpaper — feh {flag}: {path}")
        try:
            fn.subprocess.Popen(
                ["feh", flag, path],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.log_success(f"Wallpaper set: {fn.path.basename(path)}")
            fn.show_in_app_notification(self, f"Wallpaper set: {fn.path.basename(path)}")
        except FileNotFoundError:
            fn.log_error("feh not found")
            fn.show_in_app_notification(self, "feh not found — install feh or nitrogen")
    elif shutil.which("nitrogen"):
        fn.log_subsection(f"Applying wallpaper — nitrogen --set-zoom-fill: {path}")
        try:
            fn.subprocess.Popen(
                ["nitrogen", "--set-zoom-fill", "--save", path],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.log_success(f"Wallpaper set: {fn.path.basename(path)}")
            fn.show_in_app_notification(self, f"Wallpaper set: {fn.path.basename(path)}")
        except FileNotFoundError:
            fn.log_error("nitrogen not found")
            fn.show_in_app_notification(self, "nitrogen not found — install feh or nitrogen")
    else:
        fn.log_error("No wallpaper setter found — install feh or nitrogen")
        fn.show_in_app_notification(self, "No wallpaper setter found — install feh or nitrogen")


def _set_gnome(self, path, scale):
    fn.log_subsection(f"Applying wallpaper — gsettings (GNOME): {path}")
    mode = _GNOME_MODES.get(scale, "zoom")
    uri = f"file://{path}"
    try:
        fn.subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri], stderr=fn.subprocess.DEVNULL
        )
        fn.subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri], stderr=fn.subprocess.DEVNULL
        )
        fn.subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.background", "picture-options", mode], stderr=fn.subprocess.DEVNULL
        )
        fn.log_success(f"Wallpaper set: {fn.path.basename(path)}")
        fn.show_in_app_notification(self, f"Wallpaper set: {fn.path.basename(path)}")
    except FileNotFoundError:
        fn.log_error("gsettings not found")
        fn.show_in_app_notification(self, "gsettings not found")


def _set_mate(self, path, scale):
    fn.log_subsection(f"Applying wallpaper — gsettings (MATE): {path}")
    mode = _GNOME_MODES.get(scale, "zoom")
    try:
        fn.subprocess.run(
            ["gsettings", "set", "org.mate.background", "picture-filename", path], stderr=fn.subprocess.DEVNULL
        )
        fn.subprocess.run(
            ["gsettings", "set", "org.mate.background", "picture-options", mode], stderr=fn.subprocess.DEVNULL
        )
        fn.log_success(f"Wallpaper set: {fn.path.basename(path)}")
        fn.show_in_app_notification(self, f"Wallpaper set: {fn.path.basename(path)}")
    except FileNotFoundError:
        fn.log_error("gsettings not found")
        fn.show_in_app_notification(self, "gsettings not found")


def _set_cinnamon(self, path, scale):
    fn.log_subsection(f"Applying wallpaper — gsettings (Cinnamon): {path}")
    mode = _GNOME_MODES.get(scale, "zoom")
    uri = f"file://{path}"
    try:
        fn.subprocess.run(
            ["gsettings", "set", "org.cinnamon.desktop.background", "picture-uri", uri], stderr=fn.subprocess.DEVNULL
        )
        fn.subprocess.run(
            ["gsettings", "set", "org.cinnamon.desktop.background", "picture-options", mode],
            stderr=fn.subprocess.DEVNULL,
        )
        fn.log_success(f"Wallpaper set: {fn.path.basename(path)}")
        fn.show_in_app_notification(self, f"Wallpaper set: {fn.path.basename(path)}")
    except FileNotFoundError:
        fn.log_error("gsettings not found")
        fn.show_in_app_notification(self, "gsettings not found")


def _set_kde(self, path):
    fn.log_subsection(f"Applying wallpaper — PlasmaShell dbus (KDE): {path}")
    script = (
        "let allDesktops = desktops();"
        "for (let d of allDesktops) {"
        "  if (d.wallpaperPlugin == 'org.kde.image') {"
        "    d.currentConfigGroup = ['Wallpaper', 'org.kde.image', 'General'];"
        f"   d.writeConfig('Image', 'file://{path}');"
        "  }"
        "}"
    )
    try:
        fn.subprocess.run(
            [
                "dbus-send",
                "--type=method_call",
                "--dest=org.kde.plasmashell",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                f"string:{script}",
            ],
            stderr=fn.subprocess.DEVNULL,
        )
        fn.log_success(f"Wallpaper set: {fn.path.basename(path)}")
        fn.show_in_app_notification(self, f"Wallpaper set: {fn.path.basename(path)}")
    except FileNotFoundError:
        fn.log_error("dbus-send not found")
        fn.show_in_app_notification(self, "dbus-send not found")

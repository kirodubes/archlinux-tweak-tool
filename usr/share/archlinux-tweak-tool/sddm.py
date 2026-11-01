# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import sys
import glob
import json
import subprocess
import urllib.request
import urllib.parse
import functions as fn
import os
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf, Pango
from att_i18n import _

_SDDM_AVAILABLE_CACHE = "/etc/att/cache_sddm_available.json"
_SDDM_THEME_DIR = "/usr/share/sddm/themes"
_VETO_WORDS = {"manager", "configurator", "editor"}


def simplicity_theme():
    """Return (package, theme id) of the Simplicity login theme this system uses."""
    # KiroTux ships its own Simplicity theme; kiro-sddm-simplicity conflicts with it and would remove it
    if fn.is_kirotux():
        return "kirotux-sddm-simplicity", "simplicity-kirotux"
    return "kiro-sddm-simplicity", "edu-simplicity"


def set_default_theme():
    """Point Current= at this system's Simplicity theme after ATT's Kiro defaults were copied in."""
    _pkg, theme = simplicity_theme()
    if theme == "edu-simplicity" or not fn.path.isfile(fn.sddm_default_d2):
        return
    with open(fn.sddm_default_d2, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [f"Current={theme}\n" if line.startswith("Current=") else line for line in lines]
    with open(fn.sddm_default_d2, "w", encoding="utf-8") as f:
        f.writelines(lines)
    fn.log_info_concise(f"  Theme:  Current={theme} (KiroTux)")


def theme_background(theme_dir):
    """Return the background image path a theme's theme.conf points at."""
    try:
        with open(fn.path.join(theme_dir, "theme.conf"), "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("background="):
                    return fn.path.join(theme_dir, line.split("=", 1)[1].strip())
    except OSError:
        pass
    return fn.path.join(theme_dir, "images", "background.jpg")


def _sync_db_mtime():
    try:
        mtimes = [os.path.getmtime(f) for f in glob.glob("/var/lib/pacman/sync/*.db")]
        return max(mtimes) if mtimes else 0.0
    except OSError:
        return 0.0


def list_installed_sddm_themes():
    """Return a sorted list of installed SDDM theme directory names."""
    try:
        return sorted(d for d in os.listdir(_SDDM_THEME_DIR) if os.path.isdir(os.path.join(_SDDM_THEME_DIR, d)))
    except OSError:
        return []


def list_available_sddm_packages(force=False, use_aur=True):
    """Return SDDM theme package names not yet installed, queried via pacman or AUR helper."""
    if not force:
        try:
            with open(_SDDM_AVAILABLE_CACHE) as f:
                cache = json.loads(f.read())
            if cache.get("db_mtime") == _sync_db_mtime():
                fn.log_info(f"SDDM available themes (cached): {len(cache['packages'])} themes")
                return cache["packages"]
        except (OSError, KeyError, ValueError):
            pass

    aur_helper = fn.get_aur_helper() if use_aur else None
    search_cmd = [aur_helper, "-Ss", "sddm"] if aur_helper else ["pacman", "-Ss", "sddm"]
    fn.log_info(f"SDDM available themes: querying {search_cmd[0]} (use_aur={use_aur})...")
    try:
        raw = subprocess.run(search_cmd, capture_output=True, text=True).stdout.strip().splitlines()
        installed_set = set(
            subprocess.run(["pacman", "-Qq"], capture_output=True, text=True).stdout.strip().splitlines()
        )
    except Exception as e:
        fn.log_error(f"SDDM available themes query failed: {e}")
        return []

    packages = []
    i = 0
    while i < len(raw):
        line = raw[i]
        if line and not line.startswith(" "):
            repo_pkg = line.split()[0]
            parts = repo_pkg.split("/", 1)
            if len(parts) < 2:
                i += 1
                continue
            pkg = parts[1]
            desc = raw[i + 1].strip() if i + 1 < len(raw) else ""
            i += 2
            if pkg in installed_set:
                continue
            name_hit = "theme" in pkg.lower()
            desc_hit = "theme" in desc.lower()
            vetoed = any(w in desc.lower() for w in _VETO_WORDS)
            if (name_hit or desc_hit) and not vetoed:
                packages.append(pkg)
        else:
            i += 1

    result = sorted(packages)
    fn.log_info(f"SDDM available themes found: {len(result)} themes")

    try:
        os.makedirs("/etc/att", exist_ok=True)
        with open(_SDDM_AVAILABLE_CACHE, "w") as f:
            json.dump({"packages": result, "db_mtime": _sync_db_mtime()}, f)
    except OSError:
        pass

    return result


def fetch_aur_pkg_modified(packages):
    """Return {pkg_name: last_modified_unix_ts} for AUR packages in the list."""
    if not packages:
        return {}
    try:
        args = "&".join(f"arg[]={urllib.parse.quote(p)}" for p in packages)
        url = f"https://aur.archlinux.org/rpc/v5/info?{args}"
        req = urllib.request.Request(url, headers={"User-Agent": "archlinux-tweak-tool"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        result = {r["Name"]: r["LastModified"] for r in data.get("results", [])}
        fn.log_info(f"AUR last-modified fetched for {len(result)} packages")
        return result
    except Exception as e:
        fn.log_warn(f"AUR RPC fetch failed: {e}")
        return {}


def _refresh_cursor_theme_dropdown(self):
    try:
        fn.refresh_all_cursor_dropdowns(self)
    except Exception as error:
        fn.debug_print(f"Failed to refresh cursor dropdowns: {error}")


def _update_sddm_theme_preview(self):
    theme = fn.get_combo_text(self.theme_sddm)
    screenshot = ""
    if theme:
        meta = fn.path.join("/usr/share/sddm/themes", theme, "metadata.desktop")
        try:
            with open(meta, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Screenshot="):
                        screenshot = line.split("=", 1)[1].strip()
                        break
        except FileNotFoundError:
            pass
    if screenshot:
        full = fn.path.join("/usr/share/sddm/themes", theme, screenshot)
        try:
            self.sddm_theme_preview.set_filename(full)
            self.sddm_theme_preview.set_visible(True)
            return
        except Exception:
            pass
    self.sddm_theme_preview.set_filename(None)
    self.sddm_theme_preview.set_visible(False)


def _update_sddm_cursor_preview(self):
    cursor_theme = fn.get_combo_text(self.sddm_cursor_themes)
    if not cursor_theme:
        self.sddm_cursor_preview.set_paintable(None)
        return
    pixbuf = fn.get_cursor_preview_pixbuf(cursor_theme)
    if pixbuf:
        self.sddm_cursor_preview.set_paintable(Gdk.Texture.new_for_pixbuf(pixbuf))
    else:
        self.sddm_cursor_preview.set_paintable(None)


def check_sddmk_complete():
    """Return True if the SDDM drop-in config has all required keys."""
    try:
        with open(fn.sddm_default_d2, "r", encoding="utf-8") as f:
            lines = f.readlines()
        flag_a = False
        flag_s = False
        flag_u = False
        flag_t = False
        flag_c = False
        flag_ct = False
        flag_f = False

        for line in lines:
            if "[Autologin]" in line:
                flag_a = True
            if "Session=" in line:
                flag_s = True
            if "User=" in line:
                flag_u = True
            if "[Theme]" in line:
                flag_t = True
            if "Current=" in line:
                flag_c = True
            if "CursorTheme=" in line:
                flag_ct = True
            if "Font=" in line:
                flag_f = True

        return flag_a and flag_s and flag_u and flag_t and flag_c and flag_ct and flag_f
    except FileNotFoundError:
        fn.debug_print("If ATT does not launch, type 'fix-sddm-conf' in a terminal and restart")
        return False


def check_sddmk_session(value):
    """Return True if the SDDM drop-in config contains the given session value."""
    try:
        with open(fn.sddm_default_d2, "r", encoding="utf-8") as myfile:
            lines = myfile.readlines()
    except FileNotFoundError:
        return False
    for line in lines:
        if value in line:
            return True
    return False


def insert_session(text):
    """Insert a Session= line into the [Autologin] block of the SDDM drop-in config."""
    with open(fn.sddm_default_d2, "r", encoding="utf-8") as f:
        lines = f.readlines()
    pos = fn.get_position(lines, "[Autologin]")
    num = pos + 2

    lines.insert(num, text + "\n")

    with open(fn.sddm_default_d2, "w", encoding="utf-8") as f:
        f.writelines(lines)


def check_sddmk_user(value):
    """Return True if the SDDM drop-in config contains the given user value."""
    try:
        with open(fn.sddm_default_d2, "r", encoding="utf-8") as myfile:
            lines = myfile.readlines()
    except FileNotFoundError:
        return False
    for line in lines:
        if value in line:
            return True
    return False


def get_autologin_state():
    """Return True if SDDM autologin has a non-empty User= in [Autologin] section"""
    try:
        if not fn.path.isfile(fn.sddm_default_d2):
            return False
        with open(fn.sddm_default_d2, "r", encoding="utf-8") as f:
            lines = f.readlines()
        in_autologin = False
        for line in lines:
            if line.strip() == "[Autologin]":
                in_autologin = True
            elif line.startswith("["):
                in_autologin = False
            elif in_autologin and line.startswith("User="):
                return bool(line.split("=", 1)[1].strip())
        return False
    except Exception:
        return False


def insert_user(text):
    """Insert a User= line into the [Autologin] block of the SDDM drop-in config."""
    with open(fn.sddm_default_d2, "r", encoding="utf-8") as f:
        lines = f.readlines()
    pos = fn.get_position(lines, "[Autologin]")
    num = pos + 3

    lines.insert(num, text + "\n")

    with open(fn.sddm_default_d2, "w", encoding="utf-8") as f:
        f.writelines(lines)


def check_sddm(lists, value):
    """Return the raw line at the position of value in lists."""
    pos = fn.get_position(lists, value)
    val = lists[pos].strip()
    return val


def set_sddm_value(self, lists, value, session, state, theme, cursor):
    """Write autologin, theme, and cursor settings to the SDDM drop-in config file."""
    try:
        if state:
            fn.subprocess.run(["groupadd", "-f", "autologin"], check=True, shell=False)
            com = fn.subprocess.run(
                ["sh", "-c", "su - " + fn.sudo_username + " -c groups"],
                check=True,
                shell=False,
                stdout=fn.subprocess.PIPE,
            )
            groups = com.stdout.decode().strip().split(" ")
            if "autologin" not in groups:
                fn.subprocess.run(
                    ["gpasswd", "-a", fn.sudo_username, "autologin"],
                    check=True,
                    shell=False,
                )

        pos = fn.get_position(lists, "Session=")
        pos_session = fn.get_position(lists, "User=")

        if state:
            lists[pos_session] = "User=" + value + "\n"
            lists[pos] = "Session=" + session + "\n"
        else:
            if "#" not in lists[pos]:
                lists[pos] = "#" + lists[pos]
                lists[pos_session] = "#" + lists[pos_session]

        pos_theme = fn.get_position(lists, "Current=")
        lists[pos_theme] = "Current=" + theme + "\n"

        pos_theme = fn.get_position(lists, "CursorTheme=")
        lists[pos_theme] = "CursorTheme=" + cursor + "\n"

        with open(fn.sddm_default_d2, "w", encoding="utf-8") as f:
            f.writelines(lists)

    except Exception as error:
        fn.log_error(str(error))
        fn.messagebox(self, _("Failed!!"), _('There seems to have been a problem in "set_sddm_value"'))


def set_user_autologin_value(self, lists, value, session, state):
    """Write user autologin and session to the primary SDDM config file."""
    try:
        fn.add_autologin_group(self)
        pos_session = fn.get_positions(lists, "Session=")
        pos_session = pos_session[-1]
        pos_user = fn.get_position(lists, "User=" + value)

        if state:
            lists[pos_user] = "User=" + value + "\n"
            lists[pos_session] = "Session=" + session + "\n"
        else:
            if "#" not in lists[pos_user]:
                lists[pos_user] = "#" + lists[pos_user]
                lists[pos_session] = "#" + lists[pos_session]

        with open(fn.sddm_default_d1, "w", encoding="utf-8") as f:
            f.writelines(lists)

    except Exception as error:
        fn.log_error(str(error))
        fn.messagebox(self, _("Failed!!"), _('There seems to have been a problem in "set_sddm_value"'))


def get_sddm_lines(files):
    """Return lines from a file, or an empty list if the file does not exist."""
    if fn.path.isfile(files):
        with open(files, "r", encoding="utf-8") as f:
            return f.readlines()
    return []


def pop_box(self, combo):
    """Populate the session dropdown from installed desktop sessions."""
    coms = []
    _m = combo.get_model()
    _m.splice(0, _m.get_n_items(), [])

    # On Sway:
    # - FileNotFoundError: /usr/share/xsessions/ may not exist
    # - Check /usr/share/wayland-sessions too; see desktopr.py check_desktop()

    lines = get_sddm_lines(fn.sddm_default_d2)
    if os.path.exists("/usr/share/xsessions"):
        for items in fn.listdir("/usr/share/xsessions/"):
            coms.append(items.split(".")[0].lower())
    if os.path.exists("/usr/share/wayland-sessions"):
        for items in fn.listdir("/usr/share/wayland-sessions/"):
            coms.append(items.split(".")[0].lower())

    try:
        if lines is not None:
            name = check_sddm(lines, "Session=").split("=")[1]
    except IndexError:
        name = ""

    if "i3-with-shmlog" in coms:
        coms.remove("i3-with-shmlog")
    if "openbox-kde" in coms:
        coms.remove("openbox-kde")
    if "cinnamon2d" in coms:
        coms.remove("cinnamon2d")
    if "icewm-session" in coms:
        coms.remove("icewm-session")

    coms.sort()
    for i, item in enumerate(coms):
        combo.get_model().append(item)
        if name.lower() == item.lower():
            combo.set_selected(i)


def pop_theme_box(self, combo):
    """Populate the theme dropdown from installed SDDM themes."""
    coms = []
    _m = combo.get_model()
    _m.splice(0, _m.get_n_items(), [])

    if not fn.path.exists("/usr/share/sddm/themes/"):
        return

    for items in fn.listdir("/usr/share/sddm/themes/"):
        coms.append(items.split(".")[0])

    name = ""
    if fn.path.exists(fn.sddm_default_d2):
        lines = get_sddm_lines(fn.sddm_default_d2)
        try:
            name = check_sddm(lines, "Current=").split("=")[1]
        except (IndexError, TypeError):
            name = ""

    coms.sort()
    selected = None
    for i, item in enumerate(coms):
        combo.get_model().append(item)
        if name.lower() == item.lower():
            selected = i

    # A missing Current= theme gives SDDM's grey fallback screen; preselect ours so the next Apply repairs it
    if selected is None and name:
        _pkg, theme = simplicity_theme()
        fn.log_warn(f"SDDM theme '{name}' is not installed - the login screen falls back to the plain SDDM theme")
        if theme in coms:
            selected = coms.index(theme)
            fn.log_info(f"Preselected '{theme}' - press Apply settings to repair the login screen")
    if selected is not None:
        combo.set_selected(selected)


def pop_gtk_cursor_names(combo):
    """Populate the cursor theme dropdown from installed cursor themes."""
    _m = combo.get_model()
    _m.splice(0, _m.get_n_items(), [])

    if fn.path.isfile(fn.sddm_default_d2):
        lines = fn.get_lines(fn.sddm_default_d2)
        try:
            cursor_theme = check_sddm(lines, "CursorTheme=").split("=")[1]
        except IndexError:
            cursor_theme = ""

        for i, item in enumerate(fn.list_cursor_themes()):
            combo.get_model().append(item)
            if cursor_theme.lower() == item.lower():
                combo.set_selected(i)


def on_click_sddm_reset_original_att(self, _widget=None):
    """Apply the default ATT SDDM configuration"""
    try:
        import functions_backup as _fb

        fn.log_subsection("Apply ATT SDDM Configuration")
        _fb.backup_system_configs()
        fn.create_sddm_k_dir()
        fn.log_info_concise(f"  From: {fn.sddm_default_d1_kiro}")
        fn.log_info_concise(f"  To:   {fn.sddm_default_d1}")
        fn.shutil.copy(fn.sddm_default_d1_kiro, fn.sddm_default_d1)
        fn.log_info_concise(f"  From: {fn.sddm_default_d2_kiro}")
        fn.log_info_concise(f"  To:   {fn.sddm_default_d2}")
        fn.shutil.copy(fn.sddm_default_d2_kiro, fn.sddm_default_d2)
        set_default_theme()
        fn.log_success("ATT SDDM configuration applied")
        fn.messagebox(self, _("Success"), _("ATT SDDM configuration applied.\n\nRestarting ATT..."))
        fn.restart_program()
    except Exception as error:
        fn.log_error(f"Failed to apply ATT SDDM configuration: {error}")
        fn.messagebox(self, _("Error"), _("Failed to apply configuration: {error}").format(error=error))


def on_click_sddm_reset_original(self, _widget=None):
    """Apply the user's original SDDM configuration"""
    try:
        fn.log_subsection("Apply Original SDDM Configuration")
        d1_bak = fn.sddm_default_d1_bak
        d2_bak = fn.sddm_default_d2_bak
        if not fn.path.isfile(d1_bak) and not fn.path.isfile(d2_bak):
            fn.log_warn("No SDDM backup files found")
            fn.messagebox(
                self,
                _("No Backup Found"),
                _("No backup files found.\n\nApply the ATT configuration first to create a backup."),
            )
            return
        if fn.path.isfile(d1_bak):
            fn.log_info_concise(f"  From: {d1_bak}")
            fn.log_info_concise(f"  To:   {fn.sddm_default_d1}")
            fn.shutil.copy(d1_bak, fn.sddm_default_d1)
        if fn.path.isfile(d2_bak):
            fn.log_info_concise(f"  From: {d2_bak}")
            fn.log_info_concise(f"  To:   {fn.sddm_default_d2}")
            fn.shutil.copy(d2_bak, fn.sddm_default_d2)
        fn.log_success("Original SDDM configuration restored")
        fn.messagebox(self, _("Success"), _("Original SDDM configuration restored.\n\nRestarting ATT..."))
        fn.restart_program()
    except Exception as error:
        fn.log_error(f"Failed to apply original SDDM configuration: {error}")
        fn.messagebox(self, _("Error"), _("Failed to apply configuration: {error}").format(error=error))


def on_sddm_setting_changed(self, message, *_):
    """Log that a setting changed and prompt the user to apply."""
    fn.log_info(f"{message} — click 'Apply the above mentioned settings' to save")
    fn.show_in_app_notification(
        self, _("{message} — click 'Apply the above mentioned settings' to save").format(message=message)
    )


def on_autologin_sddm_activated(self, widget, _param_spec=None):
    """Handle autologin switch state change"""
    try:
        is_active = widget.get_active()
        on_sddm_setting_changed(self, _("Autologin enabled") if is_active else _("Autologin disabled"))
    except Exception as error:
        fn.log_error(f"Failed to configure autologin: {error}")


def on_browse_sddm_folder(self, _widget=None):
    """Open a folder chooser for the SDDM wallpaper directory."""
    fn.log_subsection("Browse SDDM wallpaper folder")
    dialog = Gtk.FileDialog()
    dialog.set_title(_("Choose a folder with wallpapers"))
    current = self.sddm_folder_entry.get_text().strip()
    start = current if fn.path.isdir(current) else fn.home
    dialog.set_initial_folder(Gio.File.new_for_path(start))
    dialog.select_folder(self, None, lambda d, result: _on_sddm_folder_response(self, d, result))


def _on_sddm_folder_response(self, dialog, result):
    try:
        folder = dialog.select_folder_finish(result)
        if folder:
            folder_path = folder.get_path()
            self.sddm_folder_entry.set_text(folder_path)
            _populate_sddm_thumbs(self, folder_path)
    except Exception as error:
        fn.debug_print(f"Folder dialog error: {error}")


def on_load_sddm_folder(self, _widget=None):
    """Load thumbnails from the folder path in the entry widget."""
    folder_path = self.sddm_folder_entry.get_text().strip()
    if fn.path.isdir(folder_path):
        _populate_sddm_thumbs(self, folder_path)
    else:
        fn.log_warn(f"SDDM wallpaper folder not found: {folder_path}")
        fn.show_in_app_notification(self, _("Folder not found"))


def on_stop_sddm_loading(self, _widget=None):
    """Cancel the current thumbnail loading pass."""
    fn.log_info("SDDM thumbnail loading stopped")
    self._sddm_load_gen = getattr(self, "_sddm_load_gen", 0) + 1


def _populate_sddm_thumbs(self, folder_path):
    self._sddm_load_gen = getattr(self, "_sddm_load_gen", 0) + 1
    current_gen = self._sddm_load_gen

    child = self.sddm_thumb_flow.get_first_child()
    while child is not None:
        next_child = child.get_next_sibling()
        self.sddm_thumb_flow.remove(child)
        child = next_child

    exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    try:
        entries = sorted(fn.os.listdir(folder_path))
    except Exception:
        return

    image_paths = [fn.path.join(folder_path, name) for name in entries if name.lower().endswith(exts)]

    idx = 0

    def load_next():
        nonlocal idx
        if self._sddm_load_gen != current_gen:
            return False
        if idx >= len(image_paths):
            return False
        path = image_paths[idx]
        idx += 1
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
            btn.connect("clicked", lambda w, p=path: on_sddm_thumb_clicked(self, w, p))
            self.sddm_thumb_flow.append(btn)
        except Exception:
            pass
        return True

    fn.GLib.idle_add(load_next)


def on_sddm_thumb_clicked(self, _widget, path):
    """Set the selected wallpaper path and update the preview."""
    fn.log_info(f"SDDM wallpaper selected: {path}")
    self.login_wallpaper_path = path
    self.sddm_wallpaper_lbl.set_text(path)
    self.sddm_wallpaper_preview.set_filename(path)
    self.sddm_wallpaper_preview.get_parent().set_visible(True)


def on_click_sddm_apply(self, _widget=None):
    """Apply SDDM settings from UI widgets"""
    import functions_sddm as _fs

    fn.log_subsection("Applying SDDM Settings")
    # Ensure all required keys exist in the config before writing UI values.
    _fs.setup_sddm_config(self, sys.modules["sddm"])
    try:
        autologin_state = self.autologin_sddm.get_active()
        session = fn.get_combo_text(self.sessions_sddm)
        theme = fn.get_combo_text(self.theme_sddm)
        cursor = fn.get_combo_text(self.sddm_cursor_themes)

        lines = get_sddm_lines(fn.sddm_default_d2)
        if lines:
            fn.debug_print(f"Found {len(lines)} lines in config file")
            current_user = fn.sudo_username
            fn.debug_print(f"Current user: {current_user}")
            set_sddm_value(self, lines, current_user, session, autologin_state, theme, cursor)
            fn.log_info_concise(f"  User:     {current_user}")
            fn.log_info_concise(f"  Session:  {session or 'default'}")
            fn.log_info_concise(f"  Theme:    {theme or 'default'}")
            fn.log_info_concise(f"  Cursor:   {cursor or 'default'}")
            fn.log_info_concise(f"  Autologin: {'enabled' if autologin_state else 'disabled'}")
            fn.log_info_concise(f"  Saved to: {fn.sddm_default_d2}")
            fn.debug_print("Config file written successfully")
            fn.log_success("SDDM settings applied successfully")
            fn.show_in_app_notification(self, _("SDDM settings applied successfully"))
        else:
            fn.messagebox(self, _("Error"), _("Could not read SDDM configuration"))
    except Exception as error:
        fn.log_error(f"Failed to apply SDDM settings: {error}")
        fn.messagebox(self, _("Error"), _("Failed to apply SDDM settings: {error}").format(error=error))


def _do_install_sddm_git(self, set_graphical_target=False):
    if fn.check_package_installed("sddm-git"):
        fn.log_info("sddm is already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("sddm is already installed"))
        return
    if not fn.check_chaotic_aur_active():
        fn.log_warn("sddm-git requires Chaotic AUR — enable it first in the Pacman tab")
        fn.GLib.idle_add(
            fn.show_in_app_notification, self, _("Enable Chaotic AUR first — sddm-git is not in standard repos")
        )
        return
    fn.log_subsection("Install and enable sddm-git")

    graphical_target_lines = ""
    if set_graphical_target:
        graphical_target_lines = (
            "\n    echo ''\n"
            "    echo 'Setting graphical target...'\n"
            "    systemctl set-default graphical.target && echo '✓ graphical.target set' || echo '✗ Failed'"
        )

    install_script = f"""
set -o pipefail
if pacman -Q sddm &>/dev/null; then
    echo 'Removing conflicting sddm package...'
    pacman -Rdd --noconfirm sddm && echo '✓ sddm removed' || echo '✗ Failed to remove sddm'
    echo ''
fi
pacman -S --noconfirm --needed sddm-git
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Installation successful'
    echo ''
    echo 'Enabling sddm...'
    systemctl enable sddm --force && echo '✓ sddm enabled' || echo '✗ Failed'{graphical_target_lines}
else
    echo '✗ Installation failed'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""

    def _run():
        try:
            fn.log_info("chaotic-aur is active — proceeding with sddm-git install")
            fn.debug_print("Terminal: pacman -S --noconfirm --needed sddm-git")
            fn.debug_print("Terminal: systemctl enable sddm --force")
            if set_graphical_target:
                fn.debug_print("Terminal: systemctl set-default graphical.target")
            fn.debug_print(f"Terminal cmd: {install_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", install_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            if proc:
                fn.debug_print("Waiting for sddm-git install terminal to close...")
                proc.wait()
            fn.debug_print("Terminal closed — checking sddm-git installation")
            fn.invalidate_pkg_cache()
            if fn.check_package_installed("sddm-git"):
                fn.log_success("sddm-git installed")
                fn.GLib.idle_add(fn.show_in_app_notification, self, _("sddm-git installed and enabled — please reboot"))
                fn.GLib.idle_add(self.rebuild_sddm_page)
            else:
                fn.log_warn("sddm-git installation did not complete")
                fn.GLib.idle_add(fn.show_in_app_notification, self, _("sddm-git installation failed or was cancelled"))
                fn.GLib.idle_add(self.rebuild_sddm_page)
        except Exception as error:
            fn.log_error(f"Failed to install sddm-git: {error}")

    fn.threading.Thread(target=_run, daemon=True).start()


def on_click_sddm_enable(self, _widget=None):
    """Install sddm-git and set graphical.target as the default."""
    _do_install_sddm_git(self, set_graphical_target=True)


def on_set_sddm_wallpaper(self, _widget=None):
    """Apply the selected image as the Simplicity theme wallpaper."""
    fn.log_subsection("Applying SDDM Wallpaper")
    _pkg, theme = simplicity_theme()
    theme_dir = fn.path.join(_SDDM_THEME_DIR, theme)
    simplicity_images = theme_dir + "/images"
    simplicity_conf = theme_dir + "/theme.conf"
    conf_bak = simplicity_conf + "-bak"
    dest = simplicity_images + "/background.jpg"
    dest_bak = simplicity_images + "/background.jpg-bak"

    path = getattr(self, "login_wallpaper_path", None)
    if not path or not fn.path.isfile(path):
        fn.show_in_app_notification(self, _("First choose a wallpaper image"))
        return

    if not fn.path.isdir(simplicity_images):
        fn.show_in_app_notification(self, _("{theme} theme not found - install it first").format(theme=theme))
        return

    try:
        for src, bak in ((dest, dest_bak), (simplicity_conf, conf_bak)):
            if fn.path.isfile(src) and not fn.path.isfile(bak):
                fn.log_info_concise(f"  From: {src}")
                fn.log_info_concise(f"  To:   {bak}")
                fn.shutil.copy(src, bak)
                fn.debug_print("[DEBUG] Backup created: " + bak)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        pixbuf.savev(dest, "jpeg", [], [])
        with open(simplicity_conf, "w", encoding="utf-8") as f:
            f.write("[General]\nbackground=images/background.jpg\n")
        fn.log_info_concise(f"  From: {path}")
        fn.log_info_concise(f"  To:   {dest}")
        fn.log_info_concise(f"  Theme: {theme}")
        fn.debug_print("[DEBUG] Wallpaper saved and theme config updated")
        fn.log_success("Simplicity wallpaper applied")
        fn.show_in_app_notification(self, _("Simplicity wallpaper applied"))
    except Exception as error:
        fn.log_error(str(error))
        fn.show_in_app_notification(self, _("Failed to apply wallpaper"))


def on_restore_sddm_wallpaper(self, _widget=None):
    """Restore the backed-up original Simplicity theme wallpaper."""
    fn.log_subsection("Restoring Default SDDM Wallpaper")
    _pkg, theme = simplicity_theme()
    theme_dir = fn.path.join(_SDDM_THEME_DIR, theme)
    simplicity_images = theme_dir + "/images"
    simplicity_conf = theme_dir + "/theme.conf"
    conf_bak = simplicity_conf + "-bak"
    dest = simplicity_images + "/background.jpg"
    dest_bak = simplicity_images + "/background.jpg-bak"

    if not fn.path.isdir(simplicity_images):
        fn.show_in_app_notification(self, _("{theme} theme not found - install it first").format(theme=theme))
        return

    if not fn.path.isfile(dest_bak) and not fn.path.isfile(conf_bak):
        fn.show_in_app_notification(self, _("No backup found - apply a wallpaper first"))
        return

    try:
        for bak, target in ((dest_bak, dest), (conf_bak, simplicity_conf)):
            if fn.path.isfile(bak):
                fn.log_info_concise(f"  From: {bak}")
                fn.log_info_concise(f"  To:   {target}")
                fn.shutil.copy(bak, target)
        # Older ATT versions backed up only the image; their theme.conf always pointed at background.jpg
        if not fn.path.isfile(conf_bak):
            with open(simplicity_conf, "w", encoding="utf-8") as f:
                f.write("[General]\nbackground=images/background.jpg\n")
        self.sddm_wallpaper_lbl.set_text(_("Default wallpaper restored"))
        self.sddm_wallpaper_preview.set_filename(theme_background(theme_dir))
        self.sddm_wallpaper_preview.get_parent().set_visible(True)
        self.login_wallpaper_path = ""
        fn.debug_print("[DEBUG] Backup restored and theme config updated")
        fn.log_success("Default wallpaper restored")
        fn.show_in_app_notification(self, _("Default wallpaper restored"))
    except Exception as error:
        fn.log_error(str(error))
        fn.show_in_app_notification(self, _("Failed to restore wallpaper"))


def on_click_install_bibata_cursor(self, _widget=None):
    """Install Bibata cursor theme"""
    fn.log_subsection("Install Bibata Cursors")
    if fn.check_package_installed("bibata-cursor-theme"):
        fn.log_info("Bibata cursors already installed")
        fn.show_in_app_notification(self, _("Bibata cursors already installed"))
        return
    fn.show_in_app_notification(self, _("Opening terminal to install Bibata cursors..."))
    process = fn.launch_pacman_install_in_terminal("bibata-cursor-theme")

    def wait_and_refresh():
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_cursor_theme_dropdown, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_remove_bibata_cursor(self, _widget=None):
    """Remove Bibata cursor theme"""
    fn.log_subsection("Remove Bibata Cursors")
    if not fn.check_package_installed("bibata-cursor-theme"):
        fn.log_info("Bibata cursors not installed")
        fn.show_in_app_notification(self, _("Bibata cursors not installed"))
        return
    fn.show_in_app_notification(self, _("Opening terminal to remove Bibata cursors..."))
    process = fn.launch_pacman_remove_in_terminal("bibata-cursor-theme")

    def wait_and_refresh():
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_cursor_theme_dropdown, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_install_bibatar_cursor(self, _widget=None):
    """Install Bibata extra cursors"""
    fn.log_subsection("Install Bibata Extra Cursors")
    if fn.check_package_installed("bibata-extra-cursor-theme"):
        fn.log_info("Bibata extra cursors already installed")
        fn.show_in_app_notification(self, _("Bibata extra cursors already installed"))
        return
    fn.show_in_app_notification(self, _("Opening terminal to install Bibata extra cursors..."))
    process = fn.launch_pacman_install_in_terminal("bibata-extra-cursor-theme")

    def wait_and_refresh():
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_cursor_theme_dropdown, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_remove_bibatar_cursor(self, _widget=None):
    """Remove Bibata extra cursors"""
    fn.log_subsection("Remove Bibata Extra Cursors")
    if not fn.check_package_installed("bibata-extra-cursor-theme"):
        fn.log_info("Bibata extra cursors not installed")
        fn.show_in_app_notification(self, _("Bibata extra cursors not installed"))
        return
    fn.show_in_app_notification(self, _("Opening terminal to remove Bibata extra cursors..."))
    process = fn.launch_pacman_remove_in_terminal("bibata-extra-cursor-theme")

    def wait_and_refresh():
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_cursor_theme_dropdown, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_install_simplicity(self, _widget=None):
    """Install this system's Simplicity theme and enable wallpaper widgets."""
    pkg, _theme = simplicity_theme()
    fn.log_subsection(f"Install {pkg}")
    fn.debug_print(f"Launching terminal to install {pkg}...")
    fn.show_in_app_notification(self, _("Opening terminal to install Simplicity theme..."))
    process = fn.launch_pacman_install_in_terminal(pkg)

    def refresh():
        if fn.check_package_installed(pkg):
            fn.debug_print("Simplicity theme installed — enabling wallpaper widgets")
            for btn in (
                self.btn_simplicity_browse,
                self.btn_simplicity_load,
                self.btn_simplicity_stop,
                self.btn_simplicity_apply,
                self.btn_simplicity_restore,
            ):
                btn.set_sensitive(True)
            self.sddm_folder_entry.set_sensitive(True)
            self.btn_install_simplicity.set_visible(False)
            self.btn_remove_simplicity.set_visible(not fn.is_kirotux())
            pop_theme_box(self, self.theme_sddm)
            folder_path = self.sddm_folder_entry.get_text().strip()
            if fn.path.isdir(folder_path):
                _populate_sddm_thumbs(self, folder_path)

    def wait_and_refresh():
        fn.debug_print("Waiting for Simplicity install terminal to close...")
        if process:
            process.wait()
        fn.debug_print("Terminal closed — checking install result")
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(refresh)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_remove_simplicity(self, _widget=None):
    """Remove this system's Simplicity theme and disable wallpaper widgets."""
    pkg, theme = simplicity_theme()
    fn.log_subsection(f"Remove {pkg}")
    fn.debug_print(f"Launching terminal to remove {pkg}...")
    fn.show_in_app_notification(self, _("Opening terminal to remove Simplicity theme..."))
    process = fn.launch_pacman_remove_in_terminal(pkg)

    def refresh():
        if not fn.check_package_installed(pkg):
            theme_dir = fn.path.join(_SDDM_THEME_DIR, theme)
            if fn.path.isdir(theme_dir):
                fn.shutil.rmtree(theme_dir, ignore_errors=True)
                fn.log_info("Removed leftover theme directory")
            fn.debug_print("Simplicity theme removed — disabling wallpaper widgets")
            for btn in (
                self.btn_simplicity_browse,
                self.btn_simplicity_load,
                self.btn_simplicity_stop,
                self.btn_simplicity_apply,
                self.btn_simplicity_restore,
            ):
                btn.set_sensitive(False)
            self.sddm_folder_entry.set_sensitive(False)
            self.btn_remove_simplicity.set_visible(False)
            self.btn_install_simplicity.set_visible(True)
            self._sddm_load_gen = getattr(self, "_sddm_load_gen", 0) + 1
            child = self.sddm_thumb_flow.get_first_child()
            while child is not None:
                next_child = child.get_next_sibling()
                self.sddm_thumb_flow.remove(child)
                child = next_child
            self.login_wallpaper_path = ""
            fallback = fn.path.join(fn.path.dirname(fn.path.abspath(__file__)), "data", "wallpaper", "wallpaper.jpg")
            self.sddm_wallpaper_preview.set_paintable(None)
            if fn.path.isfile(fallback):
                self.sddm_wallpaper_preview.set_filename(fallback)
            self.sddm_wallpaper_lbl.set_text(_("No wallpaper selected"))
        pop_theme_box(self, self.theme_sddm)

    def wait_and_refresh():
        fn.debug_print("Waiting for Simplicity remove terminal to close...")
        if process:
            process.wait()
        fn.debug_print("Terminal closed — checking removal result")
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(refresh)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_att_sddm_clicked(self, _widget=None):
    """Install sddm-git without changing the default systemd target."""
    _do_install_sddm_git(self, set_graphical_target=False)


def on_click_fix_sddm_conf(self, _widget):
    """Confirm and run the fix-sddm-config script to reset to ATT defaults."""
    message = (
        _("This will reset your SDDM configuration to the ATT defaults.\n\n"
        "• Backs up your current /etc/sddm.conf.d/ settings\n"
        "• Applies the default SDDM configuration from Kiro\n\n"
        "Your current settings will be saved as a backup before any changes are made.")
    )
    if not fn.confirm_dialog(self, _("Fix SDDM Configuration"), message):
        return

    fn.log_subsection("Fixing SDDM configuration...")
    fn.show_in_app_notification(self, _("Opening terminal to fix SDDM config..."))
    fn.debug_print("Terminal cmd: alacritty -e /usr/share/archlinux-tweak-tool/data/bin/fix-sddm-config")
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "/usr/share/archlinux-tweak-tool/data/bin/fix-sddm-config"],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

    def refresh():
        pop_box(self, self.sessions_sddm)
        pop_theme_box(self, self.theme_sddm)
        pop_gtk_cursor_names(self.sddm_cursor_themes)
        self.autologin_sddm.set_active(get_autologin_state())
        fn.log_success("SDDM configuration fixed")
        fn.show_in_app_notification(self, _("SDDM configuration fixed"))

    def wait_and_notify():
        process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(refresh)

    fn.threading.Thread(target=wait_and_notify, daemon=True).start()

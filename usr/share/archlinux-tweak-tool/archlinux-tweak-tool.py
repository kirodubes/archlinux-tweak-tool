#!/usr/bin/env python3

# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
# pylint:disable=C0103,C0115,C0116,C0411,C0413,E1101,E0213,I1101,R0902,R0904,R0912,R0913,R0914,R0915,R0916,R1705,W0613,W0621,W0622,W0702,W0703
# pylint:disable=C0301,C0302 #line too long

# ── Force Python UTF-8 mode on a non-UTF-8 locale ─────────────────────────
# ATT must never crash on a non-UTF-8 system locale (e.g. latin-1 fr_BE).
# Under such a locale Python encodes stdout and subprocess arguments with
# latin-1, so any non-ASCII glyph in a log line or shell script raises
# UnicodeEncodeError. UTF-8 mode forces UTF-8 for both, regardless of LANG.
# Re-exec only when the locale's encoding is not UTF-8 — a normal UTF-8 desktop
# is left untouched (sys.flags.utf8_mode is 0 there too, so it is the wrong
# signal). The guard is loop-safe: the re-exec'd process is UTF-8 already.
import codecs
import os
import sys

if codecs.lookup(sys.getfilesystemencoding()).name != "utf-8":
    os.environ["PYTHONUTF8"] = "1"
    os.execv(sys.executable, [sys.executable, "-X", "utf8", *sys.argv])

# Spawned terminals (pacman, etc.) inherit our locale; if it is not UTF-8 their
# output renders as mojibake. Keep the user's locale when it is already UTF-8,
# otherwise fall back to C.UTF-8 so child output stays readable.
_cur_locale = os.environ.get("LC_ALL") or os.environ.get("LC_CTYPE") or os.environ.get("LANG") or ""
if "utf-8" not in _cur_locale.lower() and "utf8" not in _cur_locale.lower():
    os.environ["LANG"] = "C.UTF-8"
    os.environ["LC_ALL"] = "C.UTF-8"

import signal  # noqa: E402
import time  # noqa: E402
import functions as fn  # noqa: E402
import gi  # noqa: E402

# Heavy modules are imported lazily in `_finish_startup_init()` so the window can
# appear quickly. These names are populated at runtime.
zsh_theme = None
user = None
themer = None
settings = None
services = None
sddm = None
pacman_functions = None
fastfetch = None
maintenance = None
gui = None
icons = None
themes = None
desktopr = None
autostart = None
PackagesPromptGui = None
fastfetch_gui = None

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GdkPixbuf, Gtk, Pango, GLib

# suppress harmless D-Bus session bus warning when running via pkexec


def _log_writer(_level, fields, _n_fields, _user_data):
    try:
        for field in fields:
            if field.key == "MESSAGE" and "Unable to acquire session bus" in (
                field.value if isinstance(field.value, str) else field.value.decode("utf-8", errors="replace")
            ):
                return GLib.LogWriterOutput.HANDLED
    except Exception:
        pass
    return GLib.LogWriterOutput.UNHANDLED


GLib.log_set_writer_func(_log_writer, None)


base_dir = fn.path.dirname(fn.path.realpath(__file__))
DEBUG = False


def _read_gtk_theme():
    theme = os.environ.get("GTK_THEME", "").strip("\"'") or None
    if not theme:
        try:
            with open("/etc/environment", "r", encoding="utf-8") as _f:
                for _line in _f:
                    _line = _line.strip()
                    if _line.startswith("GTK_THEME="):
                        theme = _line.split("=", 1)[1].strip().strip("\"'")
                        break
        except Exception:
            pass
    return theme


def _parse_gtk_theme(raw):
    if not raw:
        return None, False
    is_dark = raw.lower().endswith("-dark")
    return (raw[:-5] if is_dark else raw), is_dark


def _is_plasma_session():
    """True when the real user is in a live Plasma session.

    pkexec strips XDG_CURRENT_DESKTOP, so the most reliable signal from the root
    process is whether plasmashell runs for the user; env/fn.desktop are fallbacks
    for when ATT is launched directly without pkexec.
    """
    try:
        result = fn.subprocess.run(
            ["pgrep", "-u", fn.sudo_username, "-x", "plasmashell"],
            stdout=fn.subprocess.DEVNULL,
            stderr=fn.subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return True
    except Exception:
        pass
    de = (os.environ.get("XDG_CURRENT_DESKTOP", "") + " " + (fn.desktop or "")).lower()
    return "kde" in de or "plasma" in de


def _is_full_desktop():
    """True under a full desktop environment, False under a tiling/minimal WM.

    Full desktops get an FTT-style HeaderBar titlebar; tiling WMs (dwm/chadwm, i3, bspwm,
    Hyprland, sway, …) get none. Allow-list based, so an unrecognised WM defaults to no bar.
    Uses pgrep -u <real user> so it works under pkexec (which strips XDG_CURRENT_DESKTOP),
    mirroring _is_plasma_session().
    """
    de_processes = (
        "plasmashell",    # KDE Plasma
        "xfce4-session",  # XFCE
        "gnome-shell",    # GNOME
        "cinnamon",       # Cinnamon
        "mate-session",   # MATE
        "lxqt-session",   # LXQt
        "budgie-daemon",  # Budgie
    )
    for proc in de_processes:
        try:
            result = fn.subprocess.run(
                ["pgrep", "-u", fn.sudo_username, "-x", proc],
                stdout=fn.subprocess.DEVNULL,
                stderr=fn.subprocess.DEVNULL,
            )
            if result.returncode == 0:
                return True
        except Exception:
            continue
    return False


def _plasma_prefers_dark():
    """True if the user's Plasma colour scheme is dark, judged by window-background luminance."""
    background = None
    scheme_name = ""
    try:
        section = ""
        with open(fn.home + "/.config/kdeglobals", "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line.startswith("[") and _line.endswith("]"):
                    section = _line
                elif section == "[General]" and _line.startswith("ColorScheme="):
                    scheme_name = _line.split("=", 1)[1]
                elif section == "[Colors:Window]" and _line.startswith("BackgroundNormal="):
                    background = _line.split("=", 1)[1]
    except OSError:
        return False  # no kdeglobals → Plasma default is Breeze Light
    if background:
        try:
            r, g, b = (int(v) for v in background.split(",")[:3])
            return (0.299 * r + 0.587 * g + 0.114 * b) < 128
        except ValueError:
            pass
    return "dark" in scheme_name.lower()


def _pick_gtk_theme_for_mode(prefer_dark):
    """Closest GTK theme to Plasma for the given mode; Adwaita fallback when breeze-gtk is absent."""
    breeze = "Breeze-Dark" if prefer_dark else "Breeze"
    if fn.path.isdir("/usr/share/themes/" + breeze):
        return breeze
    return "Adwaita"  # always present; honours prefer-dark for its dark variant


def _resolve_effective_theme():
    """Resolve (theme_name, prefer_dark, source) ATT should apply at startup.

    A forced GTK_THEME wins; otherwise, on Plasma, follow its light/dark mode.
    """
    raw = _read_gtk_theme()
    if raw:
        name, dark = _parse_gtk_theme(raw)
        return name, dark, "GTK_THEME"
    if _is_plasma_session():
        dark = _plasma_prefers_dark()
        return _pick_gtk_theme_for_mode(dark), dark, "Plasma"
    return None, False, None


class Main(Gtk.ApplicationWindow):
    def __init__(self, app):
        print("=" * 75)
        print("Arch Linux Tweak Tool - GTK4 Edition")
        print("Error reporting: https://github.com/kirodubes/archlinux-tweak-tool")
        print("=" * 75)
        print("Supported distributions: AcreetionOS, Arch, ArchBang, Archcraft, Archman, Artix, Axyl,")
        print("BerserkerOS, BigLinux, BlendOS, Bluestar, CachyOS, Calam-arch, Crystal Linux,")
        print("EndeavourOS, Garuda, Helwan, Liya, LinuxHub Prime, Mabox, Manjaro, Nyarch, Omarchy,")
        print("ParchLinux, PrismLinux, RebornOS, Ryoku, StormOS (other Arch-based distros supported)")
        print("=" * 75)
        print("Backups: Files modified by ATT are backed up (-bak extension)")
        print("Support: https://github.com/kirodubes/archlinux-tweak-tool")
        print("=" * 75)

        _theme_name, _is_dark, _theme_src = _resolve_effective_theme()
        if _theme_name:
            _dark_str = " (dark mode)" if _is_dark else ""
            _src_str = " — following Plasma" if _theme_src == "Plasma" else ""
            print(
                f"[System] Distro={fn.distr} | Theme={_theme_name}{_dark_str}{_src_str} | User={fn.sudo_username}",
                flush=True,
            )
            print("=" * 75)
        else:
            print(f"[System] Distro={fn.distr} | Theme=not set | User={fn.sudo_username}", flush=True)
            print("=" * 75)
        fn.log_info(
            "To unlock all features, add Chaotic-AUR and Nemesis repo to your pacman.conf.\n"
            "For terminal operations and full transparency, alacritty must be installed"
        )

        fn.findgroup()
        fn.resolve_desktop()
        if DEBUG:
            fn.debug_print("[DEBUG] Debug mode enabled")
        super().__init__(application=app, title="Arch Linux Tweak Tool")
        self.connect("close-request", self.on_close)
        self.set_default_size(1100, 920)

        # Full desktops (XFCE, Plasma, …) get an FTT-style HeaderBar titlebar; tiling WMs
        # get none, so the window stays clean and the WM manages it.
        if _is_full_desktop():
            headerbar = Gtk.HeaderBar()
            headerbar.set_show_title_buttons(True)
            self.set_titlebar(headerbar)
            fn.log_info("Full desktop detected — using HeaderBar titlebar")
        else:
            fn.log_info("Tiling/minimal WM detected — no HeaderBar titlebar")

        self.opened = True
        self.firstrun = True
        self.timeout_id = None

        self.desktop_status = Gtk.Label()
        self.image_DE = Gtk.Picture()

        self.progress = Gtk.ProgressBar()
        self.progress.set_pulse_step(0.2)
        self.progress.set_visible(False)
        self.login_wallpaper_path = ""

        GLib.idle_add(self._finish_startup_init)

    def _finish_startup_init(self):
        """Deferred startup initialization.

        Runs after the window has had a chance to present itself.
        """
        global zsh_theme, user, themer, settings, services, sddm
        global pacman_functions, fastfetch, maintenance, gui, icons, themes
        global desktopr, autostart, PackagesPromptGui, fastfetch_gui
        global functions_makedir, functions_backup, functions_startup

        startup_start = time.time()
        fn.debug_print("Startup sequence initiated")

        _import_times = {}

        def _timed_import(label, do_import):
            t = time.time()
            result = do_import()
            elapsed = time.time() - t
            _import_times[label] = elapsed
            fn.debug_print(f"[LAZY] {label}: {elapsed:.3f}s")
            return result

        _zsh_theme = _timed_import("zsh_theme", lambda: __import__("zsh_theme"))
        _user = _timed_import("user", lambda: __import__("user"))
        _themer = _timed_import("themer", lambda: __import__("themer"))
        _settings = _timed_import("settings", lambda: __import__("settings"))
        _services = _timed_import("services", lambda: __import__("services"))
        _sddm = _timed_import("sddm", lambda: __import__("sddm"))
        _pacman_functions = _timed_import("pacman_functions", lambda: __import__("pacman_functions"))
        _fastfetch = _timed_import("fastfetch", lambda: __import__("fastfetch"))
        _maintenance = _timed_import("maintenance", lambda: __import__("maintenance"))
        _gui = _timed_import("gui", lambda: __import__("gui"))
        _icons = _timed_import("icons", lambda: __import__("icons"))
        _themes = _timed_import("themes", lambda: __import__("themes"))
        _desktopr = _timed_import("desktopr", lambda: __import__("desktopr"))
        _autostart = _timed_import("autostart", lambda: __import__("autostart"))
        _fastfetch_gui = _timed_import("fastfetch_gui", lambda: __import__("fastfetch_gui"))

        def _import_functions():
            import functions_makedir as _fm
            import functions_backup as _fb
            import functions_startup as _fs

            return _fm, _fb, _fs

        _fm_tuple = _timed_import("functions modules", _import_functions)
        _functions_makedir, _functions_backup, _functions_startup = _fm_tuple

        def _import_packages_gui():
            from packages_prompt_gui import PackagesPromptGui as _PPG

            return _PPG

        _PackagesPromptGui = _timed_import("packages_prompt_gui", _import_packages_gui)

        zsh_theme = _zsh_theme
        user = _user
        themer = _themer
        settings = _settings
        services = _services
        sddm = _sddm
        pacman_functions = _pacman_functions
        fastfetch = _fastfetch
        maintenance = _maintenance
        gui = _gui
        icons = _icons
        themes = _themes
        desktopr = _desktopr
        autostart = _autostart
        fastfetch_gui = _fastfetch_gui
        functions_makedir = _functions_makedir
        functions_backup = _functions_backup
        functions_startup = _functions_startup
        PackagesPromptGui = _PackagesPromptGui

        imports_time = time.time()
        _imports_total = imports_time - startup_start
        fn.debug_print("")
        fn.debug_print("=" * 75)
        fn.debug_print("LAZY IMPORT TIMING SUMMARY (slowest first)")
        fn.debug_print("=" * 75)
        fn.debug_print(f"{'Module':<40} {'Time (s)':<12}")
        fn.debug_print("=" * 75)
        for _label, _elapsed in sorted(_import_times.items(), key=lambda x: x[1], reverse=True):
            fn.debug_print(f"{_label:<40} {_elapsed:>11.3f}s")
        fn.debug_print("=" * 75)
        fn.debug_print(f"{'TOTAL (imports)':<40} {_imports_total:>11.3f}s")
        fn.debug_print("=" * 75)
        fn.debug_print("")

        # Ensure directories exist before building GUI
        functions_makedir.ensure_app_dirs()
        functions_makedir.ensure_root_config_dirs()

        makedirs_time = time.time()
        fn.debug_print(f"Makedirs completed in {makedirs_time - imports_time:.3f}s")

        functions_startup.setup_icon_theme()
        functions_startup.setup_fastfetch_config()

        self.on_desktop_changed = lambda: None
        self.rebuild_sddm_page = lambda: None

        # Build and display GUI
        gui.gui(self, Gtk, Gdk, GdkPixbuf, base_dir, os, Pango, GLib)

        self.initializing = True

        if not fn.path.isfile("/tmp/att.lock"):
            with open("/tmp/att.lock", "w", encoding="utf-8") as f:
                f.write("")

        try:
            self.present()
        except Exception:
            pass

        gui_time = time.time()
        fn.debug_print(f"[RESPONSIVE] Window visible after {gui_time - startup_start:.3f}s")

        fn.threading.Thread(
            target=self._finish_background_init,
            args=(startup_start,),
            daemon=True,
        ).start()

        return False

    def _finish_background_init(self, startup_start):
        """Run backups and permission fixes after the window is already visible."""
        bg_start = time.time()

        t1 = time.time()
        functions_backup.backup_gtk_config()
        t1_end = time.time()
        fn.debug_print(f"[TIMING] backup_gtk_config: {t1_end - t1:.3f}s")

        t2 = time.time()
        functions_backup.backup_system_configs()
        t2_end = time.time()
        fn.debug_print(f"[TIMING] backup_system_configs: {t2_end - t2:.3f}s")

        t3 = time.time()
        functions_backup.backup_user_configs()
        t3_end = time.time()
        fn.debug_print(f"[TIMING] backup_user_configs: {t3_end - t3:.3f}s")

        t4 = time.time()
        functions_startup.fix_permissions()
        t4_end = time.time()
        fn.debug_print(f"[TIMING] fix_permissions: {t4_end - t4:.3f}s")

        total_time = time.time()
        t_bg = total_time - bg_start

        fn.debug_print(f"[TIMING] Background init total: {t_bg:.3f}s")
        fn.debug_print("")
        fn.debug_print("=" * 75)
        fn.debug_print("BACKGROUND INIT TIMING SUMMARY")
        fn.debug_print("=" * 75)
        fn.debug_print(f"{'Component':<40} {'Time (s)':<12}")
        fn.debug_print("=" * 75)
        fn.debug_print(f"{'GTK config backup':<40} {t1_end - t1:>11.3f}s")
        fn.debug_print(f"{'System config backup':<40} {t2_end - t2:>11.3f}s")
        fn.debug_print(f"{'User config backup':<40} {t3_end - t3:>11.3f}s")
        fn.debug_print(f"{'Fix permissions':<40} {t4_end - t4:>11.3f}s")
        fn.debug_print("=" * 75)
        fn.debug_print(f"{'TOTAL (background init)':<40} {t_bg:>11.3f}s")
        fn.debug_print(f"{'TOTAL (incl. window setup)':<40} {total_time - startup_start:>11.3f}s")
        fn.debug_print("=" * 75)
        fn.debug_print("")
        fn.log_info("To unlock all features, add Chaotic-AUR and Nemesis repo to your pacman.conf.")
        fn.log_info("For terminal operations and full transparency, alacritty must be installed.")
        msg = "Config backups complete - Welcome to the ArchLinux Tweak Tool!"
        GLib.idle_add(fn.show_in_app_notification, self, msg)
        GLib.idle_add(lambda: setattr(self, "initializing", False) or False)
        GLib.idle_add(self._check_nanorc_prompt)

    def _check_nanorc_prompt(self):
        if self._nanorc_prompt_needed():
            self._show_nanorc_dialog()
        else:
            self._check_tweak_tools_prompt()
        return False

    def _nanorc_prompt_needed(self):
        if fn.read_att_settings().get("nano_declined", False):
            return False
        if fn.path.isfile(fn.nanorc):
            try:
                with open(fn.nanorc, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                if first_line == "## nanorc from Nemesis":
                    return False
            except OSError:
                return False
        return True

    def _check_tweak_tools_prompt(self, *_args):
        if fn.read_att_settings().get("tweak_tools_popup_hidden", False):
            return
        self._show_tweak_tools_dialog()

    def _show_tweak_tools_dialog(self):
        fn.log_info("Showing tweak tools overview at startup")
        dialog = Gtk.Window(title="More Tweak Tools", transient_for=self, modal=True)
        dialog.set_default_size(620, -1)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        lbl_intro = Gtk.Label(xalign=0)
        lbl_intro.set_wrap(True)
        lbl_intro.set_markup(
            "ATT can also <b>install and launch other tweak tools</b>, each dedicated to one application."
            " You find them on these pages:"
        )
        box.append(lbl_intro)

        tools = [
            ("Alacritty Tweak Tool", "choose from 300+ Alacritty themes or create new ones", "Shells, Software"),
            ("Fastfetch Tweak Tool", "configure what Fastfetch shows and how", "Fastfetch"),
            ("Fish Tweak Tool", "configure the fish shell", "Shells"),
            ("Hyprland Tweak Tool", "Hyprland setups, backups and restore", "Desktop - Wayland"),
        ]
        grid = Gtk.Grid(column_spacing=16, row_spacing=8)
        grid.set_margin_start(10)
        for row, (name, what, page) in enumerate(tools):
            lbl_name = Gtk.Label(xalign=0)
            lbl_name.set_markup(f"<b>{name}</b>")
            lbl_what = Gtk.Label(label=what, xalign=0)
            lbl_what.set_wrap(True)
            lbl_what.set_hexpand(True)
            lbl_page = Gtk.Label(xalign=0)
            lbl_page.set_markup(f"<i>{page}</i>")
            grid.attach(lbl_name, 0, row, 1, 1)
            grid.attach(lbl_what, 1, row, 1, 1)
            grid.attach(lbl_page, 2, row, 1, 1)
        box.append(grid)

        lbl_repo = Gtk.Label(xalign=0)
        lbl_repo.set_wrap(True)
        lbl_repo.set_markup("<i>They install from the Nemesis repo — enable it on the Pacman page first.</i>")
        box.append(lbl_repo)

        hbox_bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        chk_hide = Gtk.CheckButton(label="Don't show this again")
        chk_hide.set_hexpand(True)
        btn_close = Gtk.Button(label="Close")
        hbox_bottom.append(chk_hide)
        hbox_bottom.append(btn_close)
        box.append(hbox_bottom)

        def on_close_request(_window):
            # Saved on any close (button or window X) so the checkbox is never lost.
            if chk_hide.get_active():
                fn.log_info(f"Tweak tools popup hidden — preference saved to {fn.att_settings}")
                d = fn.read_att_settings()
                d["tweak_tools_popup_hidden"] = True
                fn.write_att_settings(d)
            return False

        dialog.connect("close-request", on_close_request)
        btn_close.connect("clicked", lambda _w: dialog.close())

        dialog.set_child(box)
        dialog.present()

    def _show_nanorc_dialog(self):
        fn.log_info("Offering ATT nanorc at startup")
        dialog = Gtk.Dialog(title="Nano Editor Colors", transient_for=self, modal=True)
        dialog.set_default_size(700, 400)

        content = dialog.get_content_area()
        content.set_spacing(12)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(16)
        content.set_margin_end(16)

        lbl = Gtk.Label()
        lbl.set_markup(
            "ATT includes a <b>colorful nanorc</b>. Click one to choose"
            " — a backup of /etc/nanorc is always created first."
        )
        lbl.set_wrap(True)
        lbl.set_xalign(0)
        content.append(lbl)

        hbox_images = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        hbox_images.set_hexpand(True)

        def make_image_button(image_path, label_text):
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            btn = Gtk.Button()
            btn.set_hexpand(True)
            picture = Gtk.Picture.new_for_filename(image_path)
            picture.set_can_shrink(True)
            picture.set_content_fit(Gtk.ContentFit.CONTAIN)
            picture.set_size_request(300, 280)
            btn.set_child(picture)
            caption = Gtk.Label(label=label_text)
            vbox.append(btn)
            vbox.append(caption)
            return vbox, btn

        vbox_default, btn_default = make_image_button(fn.nanorc_img_default, "Keep default")
        vbox_att, btn_att = make_image_button(fn.nanorc_img_att, "Apply ATT colors")

        hbox_images.append(vbox_default)
        hbox_images.append(vbox_att)
        content.append(hbox_images)

        def on_apply(_widget):
            fn.log_subsection("Applying ATT nanorc from startup prompt")
            import functions_backup as fb

            fb.backup_nanorc()
            try:
                fn.shutil.copy(fn.nanorc_att, fn.nanorc)
                fn.log_success("ATT nanorc applied to /etc/nanorc")
                fn.show_in_app_notification(self, "ATT nanorc applied to /etc/nanorc")
            except OSError as e:
                fn.log_error(f"Failed to apply ATT nanorc: {e}")
                fn.show_in_app_notification(self, "Failed to apply ATT nanorc")
            dialog.destroy()

        def on_decline(_widget):
            # Decline is remembered so this dialog never shows again.
            # Preference saved to ~/.config/archlinux-tweak-tool/att_settings.json
            fn.log_info(f"ATT nanorc offer declined — preference saved to {fn.att_settings}")
            d = fn.read_att_settings()
            d["nano_declined"] = True
            fn.write_att_settings(d)
            dialog.destroy()

        btn_att.connect("clicked", on_apply)
        btn_default.connect("clicked", on_decline)
        # Chained after the nanorc dialog so two modals never stack.
        dialog.connect("destroy", self._check_tweak_tools_prompt)

        dialog.present()

    def on_refresh_att_clicked(self, _widget):
        fn.log_subsection("Restart ATT")
        fn.restart_program()

    def on_close(self, _window):
        fn.log_info("ATT closing")
        try:
            fn.unlink("/tmp/att.lock")
        except FileNotFoundError:
            pass
        self.get_application().quit()
        return False


# Application entry point


_app_ref = None


def signal_handler(_sig, frame):
    fn.debug_print("\nATT is Closing.")
    fn.unlink("/tmp/att.lock")
    if _app_ref is not None:
        _app_ref.quit()


class ATTApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.kiro.archlinux-tweak-tool")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        fn.log_info("ATT application activated")
        # These lines offer protection and grace when a kernel has obfuscated
        # or removed basic OS functionality.
        os_function_support = True
        try:
            fn.getlogin()
        except Exception:
            os_function_support = False

        if not fn.path.isfile("/tmp/att.lock") and os_function_support:
            with open("/tmp/att.pid", "w", encoding="utf-8") as f:
                f.write(str(fn.getpid()))

            theme_name, prefer_dark, _theme_src = _resolve_effective_theme()
            settings = Gtk.Settings.get_default()
            if settings is None:
                fn.log_warn("No GTK display connection — skipping theme setup (launch via the proper launcher / att-dev)")
            elif theme_name:
                settings.set_property("gtk-theme-name", theme_name)
                settings.set_property("gtk-application-prefer-dark-theme", prefer_dark)

            style_provider = Gtk.CssProvider()
            style_provider.load_from_path(base_dir + "/icons.css")
            display = Gdk.Display.get_default()
            if display is not None:
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    style_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )
            Main(app)
        else:
            self._show_lock_or_unsupported_dialog(app, os_function_support)

    def _show_lock_or_unsupported_dialog(self, app, os_function_support):
        if os_function_support:
            md = Gtk.MessageDialog(
                transient_for=None,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Lock File Found",
            )
            md.props.secondary_text = (
                "The lock file has been found. This indicates there is already an instance of"
                " <b>ArchLinux Tweak Tool</b> running.\n"
                "Click yes to remove the lock file\n"
                "and try running ATT again"
            )
            md.props.secondary_use_markup = True
        else:
            md = Gtk.MessageDialog(
                transient_for=None,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.CLOSE,
                text="Kernel Not Supported",
            )
            md.props.secondary_text = (
                "Your current kernel does not support basic os function calls. <b>ArchLinux Tweak Tool</b> "
                "requires these to work."
            )
            md.props.secondary_use_markup = True

        result_holder = [None]
        loop = GLib.MainLoop()

        def on_lock_response(d, response_id):
            result_holder[0] = response_id
            loop.quit()
            d.destroy()

        md.set_default_response(Gtk.ResponseType.YES)
        md.connect("response", on_lock_response)
        md.present()
        loop.run()

        if result_holder[0] in (Gtk.ResponseType.OK, Gtk.ResponseType.YES):
            pid = ""
            try:
                with open("/tmp/att.pid", "r", encoding="utf-8") as f:
                    pid = f.read().strip()

                if fn.check_pid_is_running(int(pid)):
                    md2 = Gtk.MessageDialog(
                        transient_for=None,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.CLOSE,
                        text="You first need to close the existing application",
                    )
                    md2.props.secondary_text = "You first need to close the existing application"

                    md2.props.secondary_use_markup = True
                    loop2 = GLib.MainLoop()

                    def on_close_response(d, response_id):
                        loop2.quit()
                        d.destroy()

                    md2.connect("response", on_close_response)
                    md2.present()
                    loop2.run()
                else:
                    fn.unlink("/tmp/att.lock")
            except Exception:
                fn.debug_print("Make sure there is just one instance of ArchLinux Tweak Tool running")
                fn.debug_print("Then you can restart the application")

        app.quit()


if __name__ == "__main__":
    import sys

    if "--debug" in sys.argv:
        DEBUG = True
        sys.argv.remove("--debug")
        fn.set_debug(True)

    if "--dev" in sys.argv:
        sys.argv.remove("--dev")
        fn.set_dev(True)

    fn.init_session_log()
    signal.signal(signal.SIGINT, signal_handler)
    app = ATTApplication()
    _app_ref = app
    sys.exit(app.run(sys.argv))

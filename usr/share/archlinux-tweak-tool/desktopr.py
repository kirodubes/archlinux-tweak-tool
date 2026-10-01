# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import datetime
import tempfile
from gi.repository import GLib, Gtk  # noqa
import functions as fn

default_app = ["nano", "ttf-hack"]

# Desktops whose install is one-way — removal requires a full system reinstall.
ONE_WAY_DESKTOPS = ("plasma", "gnome")
_DESKTOP_DISPLAY_NAMES = {"plasma": "Plasma", "gnome": "GNOME"}


def desktop_display_name(desktop):
    """Return the human-friendly name for a desktop identifier."""
    return _DESKTOP_DISPLAY_NAMES.get(desktop, desktop.capitalize())


# /etc/environment vars that override Plasma's own theming: the QT_* pair forces a
# non-Breeze platform theme/style (triggering Plasma's yellow "unable to apply" warning
# popup), and GTK_THEME forces GTK apps dark regardless of Plasma's settings.
_PLASMA_CONFLICTING_ENV_VARS = ("QT_QPA_PLATFORMTHEME", "QT_STYLE_OVERRIDE", "GTK_THEME")


def conflicting_plasma_env_lines():
    """Return uncommented /etc/environment lines that clash with Plasma theming."""
    found = []
    try:
        with open("/etc/environment", encoding="utf-8") as env_file:
            for line in env_file:
                stripped = line.strip()
                if stripped.startswith("#") or "=" not in stripped:
                    continue
                key = stripped.split("=", 1)[0].strip()
                if key in _PLASMA_CONFLICTING_ENV_VARS:
                    found.append(stripped)
    except OSError as error:
        fn.log_warn(f"Could not read /etc/environment to check for Plasma theming conflicts: {error}")
    return found


# =================================================================
# =                         Desktops                             =
# =================================================================

desktops = [
    "awesome",
    "bspwm",
    "budgie-desktop",
    "cinnamon",
    "chadwm",
    "dusk",
    "gnome",
    "hlwm",
    "i3",
    "leftwm",
    "mate",
    "ohmychadwm",
    "plasma",
    "qtile",
    "xfce",
]
pkexec = ["pkexec", "pacman", "-S", "--needed", "--noconfirm", "--ask=4"]
pkexec_reinstall = ["pkexec", "pacman", "-S", "--noconfirm", "--ask=4"]
copy = ["cp", "-Rv"]

# =================================================================
# =                         Distros                               =
# =================================================================

if fn.distr:
    awesome = [
        "alacritty",
        "kiro-awesome",
        "awesome",
        "dmenu",
        "kiro-xfce",
        "feh",
        "lxappearance",
        "noto-fonts",
        "fastcompmgr-git",
        "polkit-gnome",
        "rofi",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "ttf-hack",
        "vicious",
        "volctl",
        "xfce4-terminal",
    ]
    bspwm = [
        "alacritty",
        "kiro-bspwm",
        "kiro-xfce",
        "kiro-polybar",
        "archlinux-logout",
        "kiro-rofi",
        "kiro-rofi-themes",
        "awesome-terminal-fonts",
        "bspwm",
        "dmenu",
        "feh",
        "lxappearance",
        "fastcompmgr-git",
        "polybar",
        "polkit-gnome",
        "rofi",
        "sxhkd",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "ttf-hack",
        "volctl",
        "xfce4-terminal",
    ]
    budgiedesktop = [
        "budgie-desktop",
        "budgie-extras",
        "dconf-editor",
        "guake",
        "ttf-hack",
    ]
    cinnamon = [
        "cinnamon",
        "cinnamon-translations",
        "gnome-screenshot",
        "gnome-system-monitor",
        "gnome-terminal",
        "nemo-fileroller",
        "kiro-cinnamon",
    ]
    chadwm = [
        "alacritty",
        "archlinux-logout",
        "kiro-chadwm",
        "kiro-rofi",
        "kiro-rofi-themes",
        "kiro-xfce",
        "dmenu",
        "feh",
        "lxappearance",
        "fastcompmgr-git",
        "polkit-gnome",
        "rofi",
        "sxhkd",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "ttf-hack",
        "ttf-jetbrains-mono-nerd",
        "volctl",
        "xfce4-notifyd",
        "xfce4-power-manager",
        "xfce4-screenshooter",
        "xfce4-settings",
        "xfce4-taskmanager",
        "xfce4-terminal",
    ]
    dusk = [
        "alacritty",
        "archlinux-logout",
        "kiro-dusk",
        "kiro-keybindings",
        "kiro-rofi",
        "kiro-rofi-themes",
        "kiro-xfce",
        "betterlockscreen",
        "brightnessctl",
        "dmenu",
        "feh",
        "flameshot",
        "fastcompmgr-git",
        "lxappearance",
        "maim",
        "network-manager-applet",
        "numlockx",
        "pavucontrol",
        "polkit-gnome",
        "rofi",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "ttf-hack",
        "ttf-jetbrains-mono-nerd",
        "volctl",
        "xclip",
        "xfce4-notifyd",
        "xfce4-power-manager",
        "xfce4-screenshooter",
        "xfce4-settings",
        "xfce4-taskmanager",
        "xfce4-terminal",
    ]
    hlwm = [
        "alacritty",
        "archlinux-logout",
        "kiro-hlwm",
        "kiro-keybindings",
        "kiro-polybar",
        "kiro-rofi",
        "kiro-rofi-themes",
        "kiro-xfce",
        "herbstluftwm",
        "polybar",
        "betterlockscreen",
        "brightnessctl",
        "dmenu",
        "feh",
        "flameshot",
        "fastcompmgr-git",
        "lxappearance",
        "maim",
        "network-manager-applet",
        "numlockx",
        "pamixer",
        "pavucontrol",
        "playerctl",
        "polkit-gnome",
        "rofi",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "ttf-hack",
        "ttf-jetbrains-mono-nerd",
        "xclip",
        "xfce4-notifyd",
        "xfce4-power-manager",
        "xfce4-screenshooter",
        "xfce4-settings",
        "xfce4-taskmanager",
        "xfce4-terminal",
    ]
    gnome = [
        "gnome",
        "gnome-tweaks",
        "ttf-hack",
    ]
    gnome_removal = [
        "gnome-session",
        "gnome-shell",
        "gdm",
        "gnome-settings-daemon",
        "gnome-desktop-4",
        "gnome-tweaks",
        "gnome-bluetooth-3.0",
        "decibels",
        "epiphany",
        "gdm",
        "gnome-backgrounds",
        "gnome-calculator",
        "gnome-calendar",
        "gnome-characters",
        "gnome-clocks",
        "gnome-color-manager",
        "gnome-connections",
        "gnome-console",
        "gnome-contacts",
        "gnome-control-center",
        "gnome-font-viewer",
        "gnome-logs",
        "gnome-maps",
        "gnome-music",
        "gnome-remote-desktop",
        "gnome-system-monitor",
        "gnome-text-editor",
        "gnome-tour",
        "gnome-user-docs",
        "gnome-user-share",
        "gnome-weather",
        "grilo-plugins",
        "gst-thumbnailers",
        "loupe",
        "malcontent",
        "nautilus",
        "orca",
        "papers",
        "rygel",
        "showtime",
        "snapshot",
        "sushi",
        "tecla",
        "xdg-desktop-portal-gnome",
        "yelp",
    ]
    i3 = [
        "alacritty",
        "kiro-i3",
        "archlinux-logout",
        "kiro-rofi",
        "kiro-rofi-themes",
        "kiro-xfce",
        "autotiling",
        "dmenu",
        "feh",
        "i3blocks",
        "i3-wm",
        "i3status",
        "lxappearance",
        "fastcompmgr-git",
        "polkit-gnome",
        "rofi",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "ttf-hack",
        "volctl",
        "xfce4-terminal",
    ]
    leftwm = [
        "alacritty",
        "archlinux-logout",
        "kiro-leftwm",
        "kiro-polybar",
        "kiro-rofi",
        "kiro-rofi-themes",
        "kiro-xfce",
        "dmenu",
        "feh",
        "leftwm-git",
        "leftwm-theme-git",
        "lxappearance",
        "fastcompmgr-git",
        "polybar",
        "polkit-gnome",
        "rofi",
        "sxhkd",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "ttf-hack",
        "ttf-iosevka-nerd",
        "ttf-material-design-iconic-font",
        "ttf-meslo-nerd-font-powerlevel10k",
        "volctl",
        "xfce4-appfinder",
        "xfce4-screenshooter",
        "xfce4-taskmanager",
        "xfce4-terminal",
    ]
    mate = [
        "mate",
        "mate-extra",
        "kiro-mate",
    ]
    ohmychadwm = [
        "alacritty",
        "archlinux-logout",
        "ohmychadwm",
        "kiro-rofi",
        "kiro-rofi-themes",
        "kiro-xfce",
        "dmenu",
        "feh",
        "lxappearance",
        "picom-git",
        "fastcompmgr-git",
        "polkit-gnome",
        "rofi",
        "sxhkd",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "ttf-hack",
        "ttf-jetbrains-mono-nerd",
        "noto-fonts-cjk",
        "volctl",
        "xfce4-notifyd",
        "xfce4-power-manager",
        "xfce4-screenshooter",
        "xfce4-settings",
        "xfce4-taskmanager",
        "xfce4-terminal",
    ]
    plasma = [
        "plasma",
        "kde-system-meta",
        "konsole",
    ]
    qtile = [
        "alacritty",
        "archlinux-logout",
        "kiro-qtile",
        "kiro-rofi",
        "kiro-rofi-themes",
        "kiro-xfce",
        "awesome-terminal-fonts",
        "dmenu",
        "feh",
        "lxappearance",
        "fastcompmgr-git",
        "polkit-gnome",
        "python-setuptools",
        "python-psutil",
        "qtile",
        "rofi",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "ttf-hack",
        "volctl",
        "xfce4-terminal",
    ]
    xfce = [
        "xfce4",
        "xfce4-goodies",
        "xfce4-panel-compiz",
        "catfish",
        "libxfce4ui",
        "alacritty",
        "kiro-xfce",
        "dmenu",
        "mugshot",
        "polkit-gnome",
        "ttf-hack",
    ]


_xsession_files = None
_wayland_files = None
_desktop_packages = None


def _get_desktop_packages():
    global _desktop_packages
    if _desktop_packages is None and fn.distr:
        _desktop_packages = {
            "awesome": awesome,
            "bspwm": bspwm,
            "budgie-desktop": budgiedesktop,
            "cinnamon": cinnamon,
            "chadwm": chadwm,
            "dusk": dusk,
            "gnome": gnome,
            "hlwm": hlwm,
            "i3": i3,
            "leftwm": leftwm,
            "mate": mate,
            "ohmychadwm": ohmychadwm,
            "plasma": plasma,
            "qtile": qtile,
            "xfce": xfce,
        }
    return _desktop_packages or {}


def desktop_needs_nemesis(desktop_name):
    nemesis_pkgs = fn.load_nemesis_packages()
    pkgs = _get_desktop_packages().get(desktop_name, [])
    return any(p in nemesis_pkgs or p.endswith("-git") for p in pkgs)


# Desktops whose session .desktop basename differs from the combo entry.
SESSION_FILE_ALIASES = {
    "hlwm": "herbstluftwm",
}


def check_desktop(desktop):
    global _xsession_files, _wayland_files

    if _xsession_files is None:
        _xsession_files = sorted(fn.listdir("/usr/share/xsessions/")) if fn.path.exists("/usr/share/xsessions") else []

    if _wayland_files is None:
        wayland_dir = "/usr/share/wayland-sessions"
        _wayland_files = sorted(fn.listdir(wayland_dir + "/")) if fn.path.exists(wayland_dir) else []

    target = SESSION_FILE_ALIASES.get(desktop, desktop) + ".desktop"
    if target in _xsession_files or target in _wayland_files:
        fn.debug_print(f"[check_desktop] found:     {target}")
        return True

    fn.debug_print(f"[check_desktop] not found: {target}")
    return False


def show_plasma_env_dialog(self):
    """Post-install dialog telling the user to comment out Plasma-conflicting /etc/environment vars."""
    conflicting_lines = conflicting_plasma_env_lines()
    if not conflicting_lines:
        return False
    lines_block = "\n".join(f"    {line}" for line in conflicting_lines)
    dialog = Gtk.MessageDialog(
        transient_for=self,
        message_type=Gtk.MessageType.WARNING,
        buttons=Gtk.ButtonsType.OK,
        text="Plasma installed — one more step for correct theming",
    )
    dialog.props.secondary_text = (
        "Your /etc/environment sets variables that override Plasma's own theme. "
        "Left active, Plasma shows dark elements and a yellow warning notification/popup.\n\n"
        "Edit /etc/environment, put a '#' in front of these lines, then log out and back in:\n"
        f"{lines_block}"
    )
    dialog.connect("response", lambda d, _r: d.destroy())
    dialog.show()
    fn.log_warn(
        "Plasma installed — reminder shown to comment out /etc/environment theme overrides: "
        + ", ".join(conflicting_lines)
    )
    return False


def check_lock(self, desktop):
    if fn.path.isfile("/var/lib/pacman/db.lck"):
        mess_dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Lock File Found",
        )
        mess_dialog.props.secondary_text = "pacman lock file found, do you want to remove it and continue?"

        mess_dialog.props.secondary_use_markup = True  # noqa

        result_holder = [None]
        loop = GLib.MainLoop()

        def on_lock_response(d, response_id):
            result_holder[0] = response_id
            loop.quit()
            d.destroy()

        mess_dialog.connect("response", on_lock_response)
        mess_dialog.show()
        loop.run()

        if result_holder[0] in (Gtk.ResponseType.OK, Gtk.ResponseType.YES):
            fn.unlink("/var/lib/pacman/db.lck")
            t1 = fn.threading.Thread(
                target=install_desktop,
                args=(self, fn.get_combo_text(self.d_combo)),
            )
            t1.daemon = True
            t1.start()
    else:
        t1 = fn.threading.Thread(target=install_desktop, args=(self, fn.get_combo_text(self.d_combo)))
        t1.daemon = True
        t1.start()

    return False


def _set_backup_notice(self, visible):
    if hasattr(self, "hbox_backup_notice"):
        self.hbox_backup_notice.set_visible(visible)
    return False


def check_package_and_remove(self, package):
    if fn.check_package_installed(package):
        fn.remove_package(self, package)


def install_desktop(self, desktop, on_complete=None):
    fn.log_section(f"Installing {desktop} desktop")
    fn.show_in_app_notification(self, f"Opening terminal for {desktop} installation...")

    src = []
    twm = False

    check_package_and_remove(self, "rofi-lbonn-wayland-git")
    check_package_and_remove(self, "rofi-lbonn-wayland-only-git")

    if desktop == "awesome":
        command = awesome + default_app
        src.append("/etc/skel/.config/awesome")
        twm = True
    elif desktop == "bspwm":
        command = bspwm + default_app
        src.append("/etc/skel/.config/bspwm")
        src.append("/etc/skel/.config/polybar")
        twm = True
    elif desktop == "budgie-desktop":
        check_package_and_remove(self, "catfish")
        command = budgiedesktop
    elif desktop == "chadwm":
        command = chadwm + default_app
        src.append("/etc/skel/.config/chadwm")
        twm = True
    elif desktop == "dusk":
        command = dusk + default_app
        src.append("/etc/skel/.config/dusk")
        twm = True
    elif desktop == "hlwm":
        command = hlwm + default_app
        src.append("/etc/skel/.config/herbstluftwm")
        src.append("/etc/skel/.config/polybar")
        twm = True
    elif desktop == "cinnamon":
        command = cinnamon
        fn.log_info(
            "Tip: iso-flag-png and mintlocale are useful Cinnamon packages (flag icons, locale switcher) "
            "but are not in the official Arch repos — install them manually from the AUR if needed"
        )
    elif desktop == "gnome":
        command = gnome
    elif desktop == "i3":
        command = i3 + default_app
        src.append("/etc/skel/.config/i3")
        twm = True
    elif desktop == "leftwm":
        command = leftwm + default_app
        src.append("/etc/skel/.config/leftwm")
        twm = True
    elif desktop == "ohmychadwm":
        command = ohmychadwm + default_app
        src.append("/etc/skel/.config/ohmychadwm")
        twm = True
    elif desktop == "mate":
        command = mate
        fn.log_info(
            "Tip: mate-tweak is a useful MATE configuration tool but is not in the official Arch repos "
            "— install it manually from the AUR if needed"
        )
    elif desktop == "plasma":
        check_package_and_remove(self, "qt5ct")
        command = plasma
    elif desktop == "qtile":
        command = qtile + default_app
        src.append("/etc/skel/.config/qtile")
        twm = True
    elif desktop == "xfce":
        command = xfce + default_app

    # ── Scoped backup: only the ~/.config entries this install will overwrite ──
    # The install's only write to ~/.config is the post-install skel copy of the
    # dirs in `src` (TWMs only); pacman never touches the user's home. Backing
    # those up covers everything at risk — no need for a full ~/.config copy,
    # which got slow as caches grew (mirrors the kiro-skell scoped approach).
    to_backup = [fn.path.basename(p) for p in src if fn.path.exists(fn.home + "/.config/" + fn.path.basename(p))]
    if to_backup:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        backup_dir = fn.home + "/.config-att/config-att-" + timestamp
        fn.log_info(f"Backing up {len(to_backup)} config(s) {desktop} will overwrite to {backup_dir}")
        GLib.idle_add(_set_backup_notice, self, True)
        fn.makedirs(backup_dir)
        for name in to_backup:
            fn.log_info(f"Backing up ~/.config/{name}")
            fn.copy_func(fn.home + "/.config/" + name, backup_dir + "/" + name, isdir=True)
        fn.permissions(fn.home + "/.config-att")
        GLib.idle_add(_set_backup_notice, self, False)
    else:
        fn.log_info(f"{desktop} overwrites no existing configs — nothing to back up")

    fn.log_subsection(f"Installing {len(command)} packages")
    fn.debug_print("Packages to install: " + str(command))

    log_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False)
    log_path = log_file.name
    log_file.close()

    package_list = "\n".join([f"  • {pkg}" for pkg in command])
    cache_clear = ""
    if self.ch1.get_active():
        cache_clear = "echo 'Clearing package cache...' && yes | pkexec pacman -Scc && echo '' && "

    install_cmd = (
        f"( "
        f"RED=$(tput setaf 1); RESET=$(tput sgr0); "
        f"echo 'Installing {desktop} desktop' && "
        f"echo '' && "
        f"echo 'The following packages will be installed:' && "
        f"echo '{package_list}' && "
        f"echo '' && "
        f"{cache_clear}"
        f"read -p 'Press Enter to begin installation... ' && "
        f"echo '' && "
        f"pkexec pacman -S {' '.join(command)} --needed --noconfirm --ask=4 "
        f"&& echo '' && echo '=== Installation Complete ===' "
        f"|| ( echo '' && echo '=== Installation failed — see errors above ===' && echo '' && "
        f'echo "${{RED}}  [EE]  Package(s) not found in enabled repos.${{RESET}}" && '
        f'echo "${{RED}}  [EE]  Enable chaotic-AUR first (ATT > Pacman tab > Chaotic-AUR switch).${{RESET}}" ); '
        f"read -p 'Press Enter to close...' "
        f") 2>&1 | tee {log_path}"
    )

    def _do_install():
        fn.log_info(f"Starting package installation for {desktop}...")
        fn.debug_print(f"Terminal cmd: {install_cmd}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", install_cmd],
        )
        process.wait()
        fn.invalidate_pkg_cache()
        GLib.idle_add(_after_install)

    def _after_install():
        global _xsession_files, _wayland_files
        _xsession_files = None
        _wayland_files = None
        fn.debug_print(f"Installation terminal closed for {desktop}")
        if check_desktop(desktop):
            fn.log_info(f"Copying {len(src)} config files from /etc/skel to {fn.home}...")
            if twm is True:
                for x in src:
                    if fn.path.isdir(x) or fn.path.isfile(x):
                        dest = x.replace("/etc/skel", fn.home)
                        if fn.path.isdir(x):
                            dest = fn.path.split(dest)[0]
                        fn.log_info(f"Copying skel: {x}  →  {dest}")
                        l2 = copy + [x, dest]
                        with fn.subprocess.Popen(
                            l2,
                            bufsize=1,
                            stdout=fn.subprocess.PIPE,
                            universal_newlines=True,
                        ) as p:
                            for line in p.stdout:
                                fn.debug_print(line.strip())
                        fn.permissions(dest)

            GLib.idle_add(
                self.desktop_status.set_markup,
                '<span size="x-large"><b>This desktop is installed</b></span>',
            )
            fn.log_success(f"{desktop} desktop has been installed successfully")
            GLib.idle_add(refresh_installed_desktops, self)
            if hasattr(self, "sessions_sddm"):
                import sddm

                GLib.idle_add(sddm.pop_box, self, self.sessions_sddm)
            if hasattr(self, "on_desktop_changed"):
                GLib.idle_add(self.on_desktop_changed)
            GLib.idle_add(
                fn.show_in_app_notification,
                self,
                f"{desktop} has been installed",
            )
            if on_complete is None and desktop == "plasma":
                GLib.idle_add(show_plasma_env_dialog, self)
            fn.debug_print("Installation complete — config backed up to ~/.config-att/")
        else:
            not_found = []
            try:
                with open(log_path, "r") as f:
                    log_content = f.read()
                fn.debug_print("========== Installation Output ==========")
                fn.debug_print(log_content if log_content else "(no output captured)")
                fn.debug_print("===================================================")
                for line in log_content.splitlines():
                    if "error: target not found:" in line:
                        not_found.append(line.split("error: target not found:")[-1].strip())
            except Exception as e:
                fn.debug_print(f"Could not read log file: {e}")

            failed_packages = [pkg for pkg in command if not fn.check_package_installed(pkg)]

            if not_found:
                fn.log_error(f"{desktop} installation failed — not found in enabled repos: {', '.join(not_found)}")
                fn.log_warn("Enable chaotic-aur or nemesis_repo in the Pacman tab and retry")
            else:
                fn.log_error(f"{desktop} installation failed")

            if failed_packages:
                fn.log_warn(f"Not installed ({len(failed_packages)}): {', '.join(failed_packages)}")

            notification_msg = (
                f"{desktop} failed — not found: {', '.join(not_found)} — enable chaotic-aur in Pacman tab"
                if not_found
                else f"{desktop} installation failed — check console for details"
            )
            GLib.idle_add(
                self.desktop_status.set_markup,
                '<span size="x-large"><b>This desktop is NOT installed</b></span>',
            )
            GLib.idle_add(fn.show_in_app_notification, self, notification_msg)
        fn.create_log(self)
        try:
            fn.unlink(log_path)
        except Exception:
            pass
        if on_complete:
            on_complete()

    t1 = fn.threading.Thread(target=_do_install, daemon=True)
    t1.start()


# ====================================================================
# DESKTOPR CALLBACKS
# ====================================================================


def uninstall_desktop(self, desktop, on_complete=None, removing_desktops=None):
    fn.log_section(f"Removing {desktop} desktop")
    fn.show_in_app_notification(self, f"Starting removal of {desktop}...")

    # Special handling for plasma: yakuake depends on kwayland (part of plasma group)
    if desktop == "plasma":
        if fn.check_package_installed("yakuake"):
            fn.log_info("yakuake is installed and depends on kwayland (part of plasma)")
            fn.log_info("Consider removing yakuake first, or kwayland will be protected")

    essential_packages = {
        "alacritty",
        "feh",
        "dmenu",
        "noto-fonts",
        "thunar",
        "thunar-archive-plugin",
        "thunar-volman",
        "python-psutil",
        "python-setuptools",
    }

    gnome_critical = {
        "baobab",
        "gnome-disk-utility",
        "gnome-software",
        "simple-scan",
        "gnome-app-list",
        "gnome-bluetooth",
        "gnome-desktop",
        "gnome-desktop-common",
        "gnome-screenshot",
        "gnome-themes-extra",
        "gvfs",
        "gvfs-afc",
        "gvfs-dnssd",
        "gvfs-goa",
        "gvfs-gphoto2",
        "gvfs-mtp",
        "gvfs-nfs",
        "gvfs-onedrive",
        "gvfs-smb",
        "gvfs-wsdd",
        "gnome-menus",
        "gnome-keyring",
        "xdg-user-dirs-gtk",
        "polkit-gnome",
    }

    removing_set = set(removing_desktops) if removing_desktops else set()
    all_other_packages = set()
    for desk_name in desktops:
        if desk_name != desktop and desk_name not in removing_set:
            desktop_list = globals().get(desk_name.replace("-", ""))
            if desktop_list:
                all_other_packages.update(desktop_list)

    # Get the install array for this desktop (prefer a dedicated _removal list if one exists)
    key = desktop.replace("-", "")
    desktop_list = globals().get(key + "_removal") or globals().get(key)
    if not desktop_list:
        fn.log_error(f"Desktop '{desktop}' not found in configuration")
        return

    # For GNOME, protect packages with external system dependencies (skipped in remove-all context)
    critical_set = gnome_critical if desktop == "gnome" and not removing_desktops else set()

    # Special handling for XFCE: detect which panel is actually installed and adapt the list
    desktop_list_adapted = list(desktop_list)
    if desktop == "xfce":
        # Check which panel variant is actually installed
        has_panel = fn.check_package_installed("xfce4-panel")
        has_panel_compiz = fn.check_package_installed("xfce4-panel-compiz")
        fn.log_info(f"Panel detection: xfce4-panel={has_panel}, xfce4-panel-compiz={has_panel_compiz}")
        fn.debug_print(f"[uninstall_desktop] Panel: xfce4-panel={has_panel}, xfce4-panel-compiz={has_panel_compiz}")

        # Replace the panel variant in the list with what's actually installed
        if "xfce4-panel-compiz" in desktop_list_adapted:
            idx = desktop_list_adapted.index("xfce4-panel-compiz")
            # Remove the compiz variant from the list
            desktop_list_adapted.pop(idx)
            # Add the actual installed variant(s) back
            if has_panel:
                desktop_list_adapted.insert(idx, "xfce4-panel")
                fn.log_info("Will remove xfce4-panel (actual installation)")
                fn.debug_print("[uninstall_desktop] Will remove xfce4-panel (actual installation)")
            if has_panel_compiz:
                desktop_list_adapted.insert(idx, "xfce4-panel-compiz")
                fn.log_info("Will remove xfce4-panel-compiz (actual installation)")
                fn.debug_print("[uninstall_desktop] Will remove xfce4-panel-compiz (actual installation)")

    # Filter packages to remove: exclude essentials, packages used by other desktops, and critical packages
    # For XFCE: exclude all xfce4-* EXCEPT the panels (which we adapted above to match actual install)
    panel_to_remove = None
    if desktop == "xfce":
        # Find which panel we're removing
        panel_choices = ("xfce4-panel", "xfce4-panel-compiz")
        panel_to_remove = next((pkg for pkg in desktop_list_adapted if pkg in panel_choices), None)

    packages_to_remove = []
    for pkg in desktop_list_adapted:
        is_essential = pkg in essential_packages or (pkg.startswith("xfce4-") and pkg != panel_to_remove)
        is_system_critical = pkg in critical_set
        is_used_elsewhere = pkg in all_other_packages
        if not is_essential and not is_system_critical and not is_used_elsewhere:
            packages_to_remove.append(pkg)

    packages_to_remove = [pkg for pkg in packages_to_remove if fn.check_package_installed(pkg)]

    if not packages_to_remove:
        fn.log_info(f"No packages to safely remove for {desktop} (all are either essential or shared)")
        fn.show_in_app_notification(self, f"No packages to safely remove for {desktop}")
        if on_complete:
            on_complete()
        return

    fn.log_info(f"Found {len(packages_to_remove)} packages to remove (preserving shared + essential packages)")
    fn.debug_print(f"Packages to remove: {packages_to_remove}")

    log_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False)
    log_path = log_file.name
    log_file.close()

    pacman_flag = "-Rdd" if desktop in ("plasma", "xfce") or removing_desktops else "-Rs"
    warning_msg = ""
    confirm_prompt = ""
    if desktop in ("plasma", "xfce"):
        desktop_name = "Plasma" if desktop == "plasma" else "XFCE"
        warning_msg = (
            f"echo 'WARNING: Using force removal (-Rdd) for {desktop_name} packages' && echo '' && "
            "echo 'This will remove packages even if other system utilities depend on them' && echo '' && "
        )
        confirm_prompt = (
            "read -p 'Press Enter to confirm removal (or type anything to cancel): ' confirm && "
            "if [ ! -z \"$confirm\" ]; then echo 'Removal cancelled'; exit 0; fi && echo '' && "
        )

    cleanup_step = ""
    if desktop == "plasma":
        cleanup_step = (
            "echo '' && echo 'Removing leftover KDE packages...' && echo '' && "
            "pkexec pacman -Rdd "
            "signon-kwallet-extension kaccounts-integration "
            "kdeclarative kdesu kded kde-inotify-survey "
            "dolphin kcron khelpcenter kio-admin kio-extras kjournald ksystemlog partitionmanager "
            "--noconfirm 2>/dev/null; "
            "echo 'KDE cleanup complete' && echo '' && "
        )
    elif desktop == "xfce":
        cleanup_step = (
            "echo '' && echo 'Removing leftover XFCE packages and plugins...' && echo '' && "
            "pkexec pacman -Rdd "
            "$(pacman -Q 2>/dev/null | grep '^xfce' | awk '{print $1}') "
            "mousepad parole ristretto xfburn "
            "thunar-archive-plugin thunar-media-tags-plugin "
            "--noconfirm 2>/dev/null; "
            "echo 'XFCE cleanup complete' && echo '' && "
        )

    package_list_str = "\n".join([f"  • {pkg}" for pkg in packages_to_remove])
    remove_cmd = (
        f"( "
        f"echo 'The following packages will be removed:' && echo '' && "
        f"echo '{package_list_str}' && echo '' && "
        f"{warning_msg}"
        f"{confirm_prompt}"
        f"pkexec pacman {pacman_flag} {' '.join(packages_to_remove)} --noconfirm "
        f"|| {{ echo ''; echo 'ERROR: removal failed — see above'; echo ''; }} ; "
        f"{cleanup_step}"
        f"echo '=== Done ===' ; "
        f"read -p 'Press Enter to close...' "
        f") 2>&1 | tee {log_path}"
    )

    fn.debug_print(f"Remove command: {remove_cmd}")

    def _do_remove():
        fn.log_info(f"Starting package removal for {desktop}...")
        try:
            fn.debug_print(f"Launching alacritty for {desktop} removal")
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", remove_cmd],
            )
            fn.debug_print(f"Alacritty launched (PID: {process.pid})")
            process.wait()
            fn.invalidate_pkg_cache()
            fn.debug_print("Alacritty closed")
        except Exception as e:
            fn.log_error(f"Failed to launch alacritty: {e}")
            fn.debug_print(f"Exception details: {type(e).__name__}: {e}")
        GLib.idle_add(_show_removal_dialog)

    def _show_removal_dialog():
        try:
            with open(log_path, "r") as f:
                log_content = f.read()
                if log_content:
                    fn.debug_print(f"[Removal Log]\n{log_content}")
        except Exception as e:
            fn.debug_print(f"Could not read removal log: {e}")

        removal_text = (
            f'<span size="x-large"><b>{desktop} has been removed</b></span>\n\n'
            "We do not remove code from your home directory,\nonly packages without dependencies"
        )
        GLib.idle_add(self.desktop_status.set_markup, removal_text)
        fn.log_success(f"{desktop} desktop removal complete")
        global _xsession_files, _wayland_files
        _xsession_files = None
        _wayland_files = None
        GLib.idle_add(refresh_installed_desktops, self)
        if hasattr(self, "sessions_sddm"):
            import sddm

            GLib.idle_add(sddm.pop_box, self, self.sessions_sddm)
        if hasattr(self, "on_desktop_changed"):
            GLib.idle_add(self.on_desktop_changed)
        fn.show_in_app_notification(self, f"{desktop} has been removed")
        fn.debug_print(f"Removal of {desktop} complete — user home directory untouched")
        if on_complete:
            on_complete()

        def _clear_removal_text():
            GLib.idle_add(
                self.desktop_status.set_markup,
                '<span size="x-large"><b>This desktop is NOT installed</b></span>',
            )
            try:
                fn.unlink(log_path)
            except Exception:
                pass
            return False

        GLib.timeout_add(5000, _clear_removal_text)

    t1 = fn.threading.Thread(target=_do_remove, daemon=True)
    t1.start()


def refresh_installed_desktops(self):
    xsessions = (
        [f[:-8] for f in fn.listdir("/usr/share/xsessions/") if f.endswith(".desktop")]
        if fn.path.exists("/usr/share/xsessions")
        else []
    )
    wayland = (
        [f[:-8] for f in fn.listdir("/usr/share/wayland-sessions/") if f.endswith(".desktop")]
        if fn.path.exists("/usr/share/wayland-sessions")
        else []
    )
    installed = sorted(set(xsessions + wayland))
    text = "Installed: " + ", ".join(installed) if installed else "No desktops installed"
    self.label_installed_desktops.set_text(text)


def on_d_combo_changed(self, _widget, _pspec=None):
    fn.log_info(f"Desktop selected: {fn.get_combo_text(self.d_combo)}")
    from gi.repository import Gdk, GdkPixbuf
    import desktopr_gui

    try:
        pixbuf3 = GdkPixbuf.Pixbuf.new_from_file_at_size(
            self.base_dir + "/desktop_data/" + fn.get_combo_text(self.d_combo) + ".jpg",
            desktopr_gui.IMAGE_PREVIEW_LOAD,
            desktopr_gui.IMAGE_PREVIEW_LOAD,
        )
        texture = Gdk.Texture.new_for_pixbuf(pixbuf3)
        self.image_DE.set_paintable(texture)
    except Exception:
        self.image_DE.set_paintable(None)
    if check_desktop(fn.get_combo_text(self.d_combo)):
        self.desktop_status.set_markup('<span size="x-large"><b>This desktop is installed</b></span>')
    else:
        self.desktop_status.set_markup('<span size="x-large"><b>This desktop is NOT installed</b></span>')
    desktopr_gui.update_button_state(self, fn)


def on_install_clicked(self, _widget):
    fn.create_log(self)
    fn.log_warn("chaotic-AUR and nemesis_repo must be enabled — many desktop packages are sourced from these repos")
    fn.show_in_app_notification(self, "Enable chaotic-AUR and nemesis_repo before installing a desktop")
    desktop = fn.get_combo_text(self.d_combo)
    fn.debug_print("installing " + desktop)

    if desktop in ONE_WAY_DESKTOPS:
        de_name = desktop_display_name(desktop)
        fn.log_warn(f"{de_name} is a one-way install — removal requires a full system reinstall")
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Installing {de_name} is a one-way operation",
        )
        secondary_text = (
            f"{de_name} cannot be removed through ATT once installed.\n"
            "A fresh system reinstall is required to completely remove it.\n\n"
        )
        if desktop == "plasma":
            conflicting_lines = conflicting_plasma_env_lines()
            if conflicting_lines:
                lines_block = "\n".join(f"    {line}" for line in conflicting_lines)
                secondary_text += (
                    "IMPORTANT — Plasma theming:\n"
                    "Your /etc/environment sets variables that override Plasma's own theme. "
                    "Left active, Plasma shows dark elements and a yellow warning notification/popup. "
                    "After installing, edit /etc/environment, put a '#' in front of these lines, "
                    "then log out and back in:\n"
                    f"{lines_block}\n\n"
                )
                fn.log_warn(
                    "Plasma: /etc/environment has theme-override variables that should be commented out — "
                    + ", ".join(conflicting_lines)
                )
                fn.show_in_app_notification(
                    self, "Plasma: comment out the QT_*/GTK_THEME lines in /etc/environment to avoid theming issues"
                )
        secondary_text += "Do you want to continue?"
        dialog.props.secondary_text = secondary_text
        result_holder = [None]
        loop = GLib.MainLoop()

        def on_oneway_warn_response(d, response_id):
            result_holder[0] = response_id
            loop.quit()
            d.destroy()

        dialog.connect("response", on_oneway_warn_response)
        dialog.show()
        loop.run()

        if result_holder[0] != Gtk.ResponseType.YES:
            fn.log_warn(f"{de_name} install cancelled by user")
            return

    check_lock(self, desktop)


def on_uninstall_clicked(self, _widget):
    fn.create_log(self)
    desktop = fn.get_combo_text(self.d_combo)
    fn.log_subsection(f"Uninstall Desktop: {desktop}")

    if desktop in ONE_WAY_DESKTOPS:
        de_name = desktop_display_name(desktop)
        fn.log_warn(f"{de_name} removal is not supported — a fresh system reinstall is required to remove {de_name}")
        fn.show_in_app_notification(self, f"{de_name} cannot be removed — reinstall system to switch DEs")
        return

    if not check_desktop(desktop):
        fn.log_info(f"{desktop} is not installed — nothing to remove")
        fn.show_in_app_notification(self, f"{desktop} is not installed")
        return
    uninstall_desktop(self, desktop)


def on_default_clicked(self, _widget):
    fn.create_log(self)
    fn.log_subsection(f"Set Default Desktop: {fn.get_combo_text(self.d_combo)}")
    if check_desktop(fn.get_combo_text(self.d_combo)) is True:
        import settings

        secs = settings.read_section()
        if "DESKTOP" in secs:
            settings.write_settings("DESKTOP", "default", fn.get_combo_text(self.d_combo))
        else:
            settings.new_settings("DESKTOP", {"default": fn.get_combo_text(self.d_combo)})
    else:
        fn.log_info("Desktop is not installed — cannot set as default")
        fn.show_in_app_notification(self, "That desktop is not installed")


# Install tiling WMs first (share packages via --needed), then full DEs smallest to largest.
INSTALL_ORDER = [
    "awesome",
    "bspwm",
    "i3",
    "qtile",
    "leftwm",
    "chadwm",
    "ohmychadwm",
    "dusk",
    "hlwm",
    "xfce",
    "mate",
    "cinnamon",
    "gnome",
    "budgie-desktop",
    "plasma",
]

# Tiling WMs only (shared packages installed via --needed); same relative order as INSTALL_ORDER.
TWM_INSTALL_ORDER = [
    "awesome",
    "bspwm",
    "i3",
    "qtile",
    "leftwm",
    "chadwm",
    "ohmychadwm",
    "dusk",
    "hlwm",
]

# Remove most exclusive/large DEs first; tiling WMs last (heavily shared packages, protected until final removal).
REMOVE_ORDER = [
    "plasma",
    "gnome",
    "budgie-desktop",
    "cinnamon",
    "mate",
    "xfce",
    "dusk",
    "hlwm",
    "qtile",
    "leftwm",
    "ohmychadwm",
    "chadwm",
    "bspwm",
    "i3",
    "awesome",
]


def install_all_desktops(self):
    fn.log_section("Install All Desktops — dev test")

    def _run():
        for desktop in INSTALL_ORDER:
            if check_desktop(desktop):
                fn.log_info(f"{desktop} already installed, skipping")
                continue
            fn.log_subsection(f"Installing {desktop}")
            GLib.idle_add(fn.show_in_app_notification, self, f"Starting {desktop} installation...")
            done = fn.threading.Event()
            GLib.idle_add(install_desktop, self, desktop, done.set)
            done.wait()
        fn.log_success("Install-all sequence complete")
        GLib.idle_add(fn.show_in_app_notification, self, "All desktops install sequence complete")

    fn.threading.Thread(target=_run, daemon=True).start()


def install_all_twms(self):
    fn.log_section("Install All TWMs — dev test")

    def _run():
        for desktop in TWM_INSTALL_ORDER:
            if check_desktop(desktop):
                fn.log_info(f"{desktop} already installed, skipping")
                continue
            fn.log_subsection(f"Installing {desktop}")
            GLib.idle_add(fn.show_in_app_notification, self, f"Starting {desktop} installation...")
            done = fn.threading.Event()
            GLib.idle_add(install_desktop, self, desktop, done.set)
            done.wait()
        fn.log_success("Install-all-TWMs sequence complete")
        GLib.idle_add(fn.show_in_app_notification, self, "All TWMs install sequence complete")

    fn.threading.Thread(target=_run, daemon=True).start()


def remove_all_desktops(self):
    fn.log_section("Remove All Desktops — dev test")

    def _run():
        for desktop in REMOVE_ORDER:
            if not check_desktop(desktop):
                fn.log_info(f"{desktop} not installed, skipping")
                continue
            fn.log_subsection(f"Removing {desktop}")
            GLib.idle_add(fn.show_in_app_notification, self, f"Starting {desktop} removal...")
            done = fn.threading.Event()
            GLib.idle_add(uninstall_desktop, self, desktop, done.set, REMOVE_ORDER)
            done.wait()
        fn.log_success("Remove-all sequence complete")
        GLib.idle_add(fn.show_in_app_notification, self, "All desktops removed")

    fn.threading.Thread(target=_run, daemon=True).start()

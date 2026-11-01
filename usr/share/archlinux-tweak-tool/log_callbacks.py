# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
from att_i18n import _


def on_click_log_current_boot(self, _widget):
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching current boot log viewer...")
        fn.show_in_app_notification(self, _("Opening current boot journal..."))
        cmd = "alacritty -e bash -c 'journalctl -b 0 | bat --language=syslog --color=always --pager=never | fzf --ansi'"
        fn.debug_print(f"Terminal cmd: {cmd}")
        fn.subprocess.Popen(cmd, shell=True)
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_log_prev_boot(self, _widget):
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching previous boot log viewer...")
        fn.show_in_app_notification(self, _("Opening previous boot journal..."))
        cmd = (
            "alacritty -e bash -c 'journalctl -b -1 | bat --language=syslog --color=always --pager=never | fzf --ansi'"
        )
        fn.debug_print(f"Terminal cmd: {cmd}")
        fn.subprocess.Popen(cmd, shell=True)
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_log_errors(self, _widget):
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching system errors log viewer...")
        fn.show_in_app_notification(self, _("Opening journal errors viewer..."))
        cmd = "alacritty -e bash -c 'SYSTEMD_COLORS=1 journalctl -b -p err | fzf --ansi'"
        fn.debug_print(f"Terminal cmd: {cmd}")
        fn.subprocess.Popen(cmd, shell=True)
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_log_recent(self, _widget):
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching recent logs viewer...")
        fn.show_in_app_notification(self, _("Opening recent journal (last 20 min)..."))
        cmd = "alacritty -e bash -c 'SYSTEMD_COLORS=1 journalctl --since \"20 minutes ago\" | fzf --ansi'"
        fn.debug_print(f"Terminal cmd: {cmd}")
        fn.subprocess.Popen(cmd, shell=True)
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_log_xorg(self, _widget):
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching Xorg log viewer...")
        fn.show_in_app_notification(self, _("Opening Xorg log..."))
        cmd = "alacritty -e bash -c 'bat --color=always /var/log/Xorg.0.log | fzf --ansi'"
        fn.debug_print(f"Terminal cmd: {cmd}")
        fn.subprocess.Popen(cmd, shell=True)
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_log_pacman(self, _widget):
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching pacman log viewer...")
        fn.show_in_app_notification(self, _("Opening pacman log..."))
        cmd = "alacritty -e bash -c 'bat --color=always /var/log/pacman.log | fzf --ansi'"
        fn.debug_print(f"Terminal cmd: {cmd}")
        fn.subprocess.Popen(cmd, shell=True)
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_log_xsession(self, _widget):
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching X session log viewer...")
        fn.show_in_app_notification(self, _("Opening X session errors log..."))
        cmd = (
            "alacritty -e bash -c '"
            "found=; "
            "for f in ~/.xsession-errors ~/.local/share/xorg/Xorg.0.log /var/log/Xorg.0.log; do "
            '  [ -s "$f" ] && { found=$f; break; }; '
            "done; "
            'if [ -n "$found" ]; then bat --color=always "$found" | fzf --ansi; '
            'else echo "No X session error file found"; read; fi\''
        )
        fn.debug_print(f"Terminal cmd: {cmd}")
        fn.subprocess.Popen(cmd, shell=True)
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_log_wayland(self, _widget):
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    if not fn.is_wayland_session():
        fn.log_info("Running X11 session — showing X session log instead")
        fn.show_in_app_notification(self, _("X11 session detected — showing X session log"))
        if not fn.check_package_installed("bat"):
            fn.log_info("bat is not installed — please install it first")
            fn.show_in_app_notification(self, _("bat is required — install it first"))
            return
        try:
            fn.log_subsection("Launching X session log viewer (X11 session)...")
            cmd = (
                "alacritty -e bash -c '"
                "found=; "
                "for f in ~/.xsession-errors ~/.local/share/xorg/Xorg.0.log /var/log/Xorg.0.log; do "
                '  [ -s "$f" ] && { found=$f; break; }; '
                "done; "
                'if [ -n "$found" ]; then bat --color=always "$found" | fzf --ansi; '
                'else echo "No X session error file found"; read; fi\''
            )
            fn.debug_print(f"Terminal cmd: {cmd}")
            fn.subprocess.Popen(cmd, shell=True)
        except Exception as error:
            fn.log_error(f"Error: {error}")
        return
    try:
        fn.log_subsection("Launching Wayland compositor log viewer...")
        fn.show_in_app_notification(self, _("Opening Wayland compositor journal..."))
        script = (
            "pat='sway|kwin_wayland|gnome-shell|mutter|weston|hyprland|river|wayfire'; "
            'comp=$(ps -eo comm= | grep -xE "$pat" | head -1); '
            'if [ -n "$comp" ]; then '
            '  SYSTEMD_COLORS=1 journalctl --user -b _COMM="$comp" | fzf --ansi; '
            "else "
            "  SYSTEMD_COLORS=1 journalctl --user -b | fzf --ansi; "
            "fi"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        fn.subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_log_blame(self, _widget):
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching boot blame analyzer...")
        fn.show_in_app_notification(self, _("Opening boot performance analyzer..."))
        cmd = "alacritty -e bash -c 'systemd-analyze blame | fzf --ansi'"
        fn.debug_print(f"Terminal cmd: {cmd}")
        fn.subprocess.Popen(cmd, shell=True)
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_log_dmesg(self, _widget):
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching kernel messages viewer...")
        fn.show_in_app_notification(self, _("Opening kernel ring buffer (dmesg)..."))
        cmd = "alacritty -e bash -c 'sudo dmesg --color=always | fzf --ansi'"
        fn.debug_print(f"Terminal cmd: {cmd}")
        fn.subprocess.Popen(cmd, shell=True)
    except Exception as error:
        fn.log_error(f"Error: {error}")

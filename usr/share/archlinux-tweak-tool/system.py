# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
# pylint:disable=C0301,I1101,W0104

import pwd

import functions as fn
from att_i18n import _
from gi.repository import GLib


def _run_cmd(cmd):
    env = fn.get_terminal_env()
    # Force a known-good terminal type rather than setdefault: a desktop launcher can hand us TERM
    # unset OR set to junk ("unknown"/"dumb"), and setdefault only covers the unset case — which lets
    # tput abort any child running under `set -e`. See kirodubes/kiro-iso-builder#1.
    env["TERM"] = "xterm-256color"
    env["SYSTEMD_COLORS"] = "1"
    fn.debug_print(f"Terminal cmd: {cmd}")
    fn.threading.Thread(
        target=lambda: fn.subprocess.Popen(
            cmd, shell=True, env=env, stdout=fn.subprocess.PIPE, stderr=fn.subprocess.STDOUT
        ),
        daemon=True,
    ).start()


def on_click_system_cpu(self, _widget):
    """Show CPU info via lscpu with bat+fzf filtering in a terminal."""
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching CPU info viewer...")
        _run_cmd("alacritty -e bash -c 'lscpu | bat --color=always -l conf | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_memory_disk(self, _widget):
    """Show memory and disk usage with free and df in a terminal."""
    try:
        fn.log_subsection("Launching memory and disk usage viewer...")
        _run_cmd(
            "alacritty -e bash -c "
            '\'printf "\\033[1;36m=== MEMORY ===\\033[0m\\n"; free -h; '
            'echo; printf "\\033[1;36m=== DISK USAGE ===\\033[0m\\n"; df -h; '
            'read -p "Press enter to close"\''
        )
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_lsblk(self, _widget):
    """Show block devices with lsblk using fzf filtering in a terminal."""
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching block devices viewer...")
        _run_cmd("alacritty -e bash -c 'lsblk -f -o+SIZE --color=always | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_lspci(self, _widget):
    """Show PCI devices with lspci using fzf filtering in a terminal."""
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching PCI devices viewer...")
        _run_cmd("alacritty -e bash -c 'lspci -vnn --color=always | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_lsusb(self, _widget):
    """Show USB devices with lsusb using fzf filtering in a terminal."""
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching USB devices viewer...")
        _run_cmd("alacritty -e bash -c 'lsusb | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_lsmod(self, _widget):
    """Show loaded kernel modules with lsmod using bat+fzf in a terminal."""
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching loaded modules viewer...")
        _run_cmd("alacritty -e bash -c 'lsmod | bat --color=always -l conf | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_inxi(self, _widget):
    """Show full system info with inxi, installing it first if missing."""
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching system information viewer...")
        if fn.check_package_installed("inxi"):
            _run_cmd("alacritty -e bash -c 'inxi -Fxx -c 2 --za | fzf --ansi'")
        else:
            fn.show_in_app_notification(self, _("Installing inxi first..."))
            process = fn.launch_pacman_install_in_terminal("inxi")

            def wait_and_run():
                if process:
                    process.wait()
                fn.invalidate_pkg_cache()
                if fn.check_package_installed("inxi"):
                    fn.log_success("inxi installed — launching viewer")
                    _run_cmd("alacritty -e bash -c 'inxi -Fxx -c 2 --za | fzf --ansi'")
                else:
                    fn.log_warn("inxi installation did not complete")
                    fn.GLib.idle_add(fn.show_in_app_notification, self, _("inxi installation failed or was cancelled"))

            fn.threading.Thread(target=wait_and_run, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_hwinfo(self, _widget):
    """Show hardware info with hwinfo using bat+fzf in a terminal."""
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching hardware information viewer...")
        fn.install_package(self, "hwinfo")
        _run_cmd("alacritty -e bash -c 'hwinfo --short | bat --color=always -l conf | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_fdisk(self, _widget):
    """Show disk partition table with fdisk using bat+fzf in a terminal."""
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching disk partitioning viewer...")
        _run_cmd("alacritty -e bash -c 'sudo fdisk -l | bat --color=always -l conf | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_fstab(self, _widget):
    """Show /etc/fstab with bat+fzf in a terminal."""
    for pkg in ("fzf", "bat"):
        if not fn.check_package_installed(pkg):
            fn.log_info(f"{pkg} is not installed — please install it first")
            fn.show_in_app_notification(self, _("{pkg} is required — install it first").format(pkg=pkg))
            return
    try:
        fn.log_subsection("Launching fstab viewer...")
        _run_cmd("alacritty -e bash -c 'bat --color=always /etc/fstab | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_hostnamectl(self, _widget):
    """Show hostname settings via hostnamectl in a terminal."""
    try:
        fn.log_subsection("Launching hostname settings viewer...")
        _run_cmd("alacritty -e bash -c 'hostnamectl; read -p \"Press enter to close\"'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_localectl(self, _widget):
    """Show locale and timezone settings via localectl in a terminal."""
    try:
        fn.log_subsection("Launching locale settings viewer...")
        _run_cmd(
            "alacritty -e bash -c '"
            "localectl; echo; "
            'echo "Timezone: $(timedatectl show --property=Timezone --value)"; '
            'read -p "Press enter to close"\''
        )
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_services(self, _widget):
    """Show all system services using systemctl and fzf in a terminal."""
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching system services viewer...")
        _run_cmd("alacritty -e bash -c 'export SYSTEMD_COLORS=1; systemctl list-units --type=service | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_services_enabled(self, _widget):
    """Show enabled system services using systemctl and fzf in a terminal."""
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching enabled services viewer...")
        _run_cmd(
            "alacritty -e bash -c 'export SYSTEMD_COLORS=1; systemctl list-unit-files"
            " --type=service --state=enabled | fzf --ansi'"
        )
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_services_failed(self, _widget):
    """Show failed system services using systemctl and fzf in a terminal."""
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching failed services viewer...")
        _run_cmd("alacritty -e bash -c 'export SYSTEMD_COLORS=1; systemctl list-units --failed | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_timers_enabled(self, _widget):
    """Show enabled system and user timers using systemctl and fzf in a terminal."""
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching enabled timers viewer...")
        uid = pwd.getpwnam(fn.sudo_username).pw_uid
        cmd = (
            'alacritty -e bash -c \'{ export SYSTEMD_COLORS=1; echo "=== System Timers ==="; '
            "systemctl list-unit-files --type=timer --state=enabled; "
            "echo; "
            'echo "=== User Timers ==="; '
            "sudo -u "
            + fn.sudo_username
            + " XDG_RUNTIME_DIR=/run/user/"
            + str(uid)
            + " DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/"
            + str(uid)
            + "/bus"
            " SYSTEMD_COLORS=1"
            " systemctl --user list-unit-files --type=timer --state=enabled; "
            "} | fzf --ansi'"
        )
        _run_cmd(cmd)
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_system_dmesg(self, _widget):
    """Show kernel ring buffer messages via dmesg with fzf in a terminal."""
    if not fn.check_package_installed("fzf"):
        fn.log_info("fzf is not installed — please install it first")
        fn.show_in_app_notification(self, _("fzf is required — install it first"))
        return
    try:
        fn.log_subsection("Launching kernel messages viewer...")
        _run_cmd("alacritty -e bash -c 'sudo dmesg --color=always | fzf --ansi'")
    except Exception as error:
        fn.log_error(f"Error: {error}")


def _refresh_gparted_label(self):
    self.lbl_gparted.set_markup(
        _("Inspect with GParted <b>installed</b>")
        if fn.path.exists("/usr/bin/gparted")
        else _("Inspect with GParted")
    )


def _refresh_partitionmanager_label(self):
    self.lbl_partitionmanager.set_markup(
        _("Inspect with Partition Manager <b>installed</b>")
        if fn.path.exists("/usr/bin/partitionmanager")
        else _("Inspect with Partition Manager")
    )


def _partition_tool_launch_cmd(binary):
    uid = pwd.getpwnam(fn.sudo_username).pw_uid
    return (
        f"sudo -u {fn.sudo_username}"
        f" XDG_RUNTIME_DIR=/run/user/{uid}"
        f" DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus"
        " DISPLAY=$DISPLAY WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
        f" {binary}"
    )


def on_click_system_partitionmanager(self, _widget):
    """Launch Partition Manager or install it if not present."""
    try:
        if fn.path.exists("/usr/bin/partitionmanager"):
            fn.log_subsection("Launching Partition Manager...")
            _run_cmd(_partition_tool_launch_cmd("partitionmanager"))
            GLib.idle_add(fn.show_in_app_notification, self, _("Partition Manager launched"))
        else:
            fn.log_subsection("Installing partitionmanager...")
            process = fn.launch_pacman_install_in_terminal("partitionmanager")
            GLib.idle_add(fn.show_in_app_notification, self, _("partitionmanager installation started"))

            def wait_install():
                try:
                    fn.debug_print("Waiting for partitionmanager installation to complete...")
                    process.wait()
                    fn.debug_print("Installation process completed")
                    if fn.path.exists("/usr/bin/partitionmanager"):
                        fn.log_success("partitionmanager installed successfully")
                        GLib.idle_add(fn.show_in_app_notification, self, _("partitionmanager <b>installed</b>"))
                        GLib.idle_add(_refresh_partitionmanager_label, self)
                        fn.log_subsection("Launching Partition Manager...")
                        _run_cmd(_partition_tool_launch_cmd("partitionmanager"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("Partition Manager launched"))
                    else:
                        fn.log_warn("partitionmanager binary NOT found, installation may have failed")
                except Exception as e:
                    fn.log_error(f"Error during installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with partitionmanager: {error}")


def on_click_system_partitionmanager_remove(self, _widget):
    """Remove the partitionmanager package."""
    try:
        if not fn.path.exists("/usr/bin/partitionmanager"):
            fn.log_info("partitionmanager is not installed")
            fn.show_in_app_notification(self, _("partitionmanager is not installed"))
            return
        fn.log_subsection("Removing partitionmanager...")
        process = fn.launch_pacman_remove_in_terminal("partitionmanager")
        GLib.idle_add(fn.show_in_app_notification, self, _("partitionmanager removal started"))

        def wait_remove():
            try:
                process.wait()
                GLib.idle_add(_refresh_partitionmanager_label, self)
            except Exception as e:
                fn.log_error(f"Error waiting for partitionmanager removal: {e}")

        fn.threading.Thread(target=wait_remove, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error removing partitionmanager: {error}")


def _launch_gparted(self):
    fn.log_subsection("Launching gparted...")
    _run_cmd(_partition_tool_launch_cmd("gparted"))
    GLib.idle_add(fn.show_in_app_notification, self, _("GParted launched"))


def on_click_system_gparted(self, _widget):
    """Launch gparted or install it if not present."""
    try:
        if fn.path.exists("/usr/bin/gparted"):
            _launch_gparted(self)
            return
        fn.log_subsection("Installing gparted...")
        process = fn.launch_pacman_install_in_terminal("gparted")
        GLib.idle_add(fn.show_in_app_notification, self, _("gparted installation started"))

        def wait_install():
            try:
                fn.debug_print("Waiting for gparted installation to complete...")
                process.wait()
                fn.debug_print("Installation process completed")
                if fn.path.exists("/usr/bin/gparted"):
                    fn.log_success("gparted installed successfully")
                    GLib.idle_add(fn.show_in_app_notification, self, _("gparted installed"))
                    GLib.idle_add(_refresh_gparted_label, self)
                    _launch_gparted(self)
                else:
                    fn.log_warn("gparted binary NOT found, installation may have failed")
            except Exception as e:
                fn.log_error(f"Error during installation: {e}")

        fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with gparted: {error}")


def on_click_system_gparted_remove(self, _widget):
    """Remove the gparted package."""
    try:
        if not fn.path.exists("/usr/bin/gparted"):
            fn.log_info("gparted is not installed")
            fn.show_in_app_notification(self, _("gparted is not installed"))
            return
        fn.log_subsection("Removing gparted...")
        process = fn.launch_pacman_remove_in_terminal("gparted")
        GLib.idle_add(fn.show_in_app_notification, self, _("gparted removal started"))

        def wait_remove():
            try:
                process.wait()
                GLib.idle_add(_refresh_gparted_label, self)
            except Exception as e:
                fn.log_error(f"Error waiting for gparted removal: {e}")

        fn.threading.Thread(target=wait_remove, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error removing gparted: {error}")


# ── Solaar (Logitech receivers and devices) ──────────────────────────────────


def _refresh_solaar_label(self):
    self.lbl_solaar.set_markup(
        _("Logitech devices (Solaar) <b>installed</b>")
        if fn.path.exists("/usr/bin/solaar")
        else _("Logitech devices (Solaar)")
    )


def _launch_solaar(self):
    fn.log_subsection("Launching solaar...")
    # Solaar talks to the receiver through its udev rule as the real user; as root it
    # would also miss the user's tray and session bus.
    _run_cmd(_partition_tool_launch_cmd("solaar"))
    GLib.idle_add(fn.show_in_app_notification, self, _("Solaar launched"))


def on_click_system_solaar(self, _widget):
    """Launch Solaar or install it if not present."""
    try:
        if fn.path.exists("/usr/bin/solaar"):
            _launch_solaar(self)
            return
        fn.log_subsection("Installing solaar...")
        process = fn.launch_pacman_install_in_terminal("solaar")
        GLib.idle_add(fn.show_in_app_notification, self, _("solaar installation started"))

        def wait_install():
            try:
                process.wait()
                if fn.path.exists("/usr/bin/solaar"):
                    fn.log_success("solaar installed successfully")
                    fn.log_info("If no device shows up, unplug and replug the receiver so the new udev rule applies")
                    GLib.idle_add(
                        fn.show_in_app_notification,
                        self,
                        _("Solaar installed - replug the receiver if no device shows up"),
                    )
                    GLib.idle_add(_refresh_solaar_label, self)
                    _launch_solaar(self)
                else:
                    fn.log_warn("solaar binary NOT found, installation may have failed")
            except Exception as e:
                fn.log_error(f"Error during installation: {e}")

        fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with solaar: {error}")


def on_click_system_solaar_remove(self, _widget):
    """Remove the solaar package."""
    try:
        if not fn.path.exists("/usr/bin/solaar"):
            fn.log_info("solaar is not installed")
            fn.show_in_app_notification(self, _("solaar is not installed"))
            return
        fn.log_subsection("Removing solaar...")
        process = fn.launch_pacman_remove_in_terminal("solaar")
        GLib.idle_add(fn.show_in_app_notification, self, _("solaar removal started"))

        def wait_remove():
            try:
                process.wait()
                GLib.idle_add(_refresh_solaar_label, self)
            except Exception as e:
                fn.log_error(f"Error waiting for solaar removal: {e}")

        fn.threading.Thread(target=wait_remove, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error removing solaar: {error}")


# ── Firmware (GNOME Firmware + fwupd) ────────────────────────────────────────


def _refresh_firmware_label(self):
    self.lbl_firmware.set_markup(
        _("Update firmware (GNOME Firmware) <b>installed</b>")
        if fn.path.exists("/usr/bin/gnome-firmware")
        else _("Update firmware (GNOME Firmware)")
    )


def _launch_firmware(self):
    fn.log_subsection("Launching gnome-firmware...")
    # polkit inside the app handles the privilege escalation to the fwupd daemon,
    # so launch it as the real user (never as root) like the partition tools.
    _run_cmd(_partition_tool_launch_cmd("gnome-firmware"))
    GLib.idle_add(fn.show_in_app_notification, self, _("GNOME Firmware launched"))


def on_click_system_firmware(self, _widget):
    """Launch GNOME Firmware or install it (pulls fwupd) if not present."""
    try:
        if fn.path.exists("/usr/bin/gnome-firmware"):
            _launch_firmware(self)
            return
        fn.log_subsection("Installing gnome-firmware...")
        process = fn.launch_pacman_install_in_terminal("gnome-firmware")
        GLib.idle_add(fn.show_in_app_notification, self, _("gnome-firmware installation started"))

        def wait_install():
            try:
                process.wait()
                if fn.path.exists("/usr/bin/gnome-firmware"):
                    fn.log_success("gnome-firmware installed successfully")
                    GLib.idle_add(fn.show_in_app_notification, self, _("gnome-firmware installed"))
                    GLib.idle_add(_refresh_firmware_label, self)
                    _launch_firmware(self)
                else:
                    fn.log_warn("gnome-firmware binary NOT found, installation may have failed")
            except Exception as e:
                fn.log_error(f"Error during gnome-firmware installation: {e}")

        fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with gnome-firmware: {error}")


def on_click_system_firmware_remove(self, _widget):
    """Remove the gnome-firmware package."""
    try:
        if not fn.path.exists("/usr/bin/gnome-firmware"):
            fn.log_info("gnome-firmware is not installed")
            fn.show_in_app_notification(self, _("gnome-firmware is not installed"))
            return
        fn.log_subsection("Removing gnome-firmware...")
        process = fn.launch_pacman_remove_in_terminal("gnome-firmware")
        GLib.idle_add(fn.show_in_app_notification, self, _("gnome-firmware removal started"))

        def wait_remove():
            try:
                process.wait()
                # Removing the GUI should not leave the LVFS metadata timer running,
                # so disable + stop it too (no-op if it was never enabled).
                if _firmware_timer_enabled():
                    fn.log_subsection("Disabling fwupd-refresh.timer after removal...")
                    fn.subprocess.run(
                        ["systemctl", "disable", "--now", "fwupd-refresh.timer"],
                        stdout=fn.subprocess.PIPE,
                        stderr=fn.subprocess.PIPE,
                    )
                    fn.log_success("fwupd-refresh.timer disabled")
                    GLib.idle_add(_refresh_firmware_timer_label, self)
                GLib.idle_add(_refresh_firmware_label, self)
            except Exception as e:
                fn.log_error(f"Error waiting for gnome-firmware removal: {e}")

        fn.threading.Thread(target=wait_remove, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error removing gnome-firmware: {error}")


def _firmware_timer_enabled():
    # Read live (not via the cached fn.check_service_enabled) so the label is
    # accurate right after the user toggles it.
    result = fn.subprocess.run(
        ["systemctl", "is-enabled", "fwupd-refresh.timer"],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )
    return result.stdout.decode().strip() == "enabled"


def _refresh_firmware_timer_label(self):
    # Show "enabled" only when the timer is on; otherwise show nothing (mirrors the
    # firmware label's "installed"/blank) — no stale "disabled" after the package is gone.
    self.lbl_firmware_timer.set_markup(
        _("Metadata refresh timer (fwupd-refresh.timer) <b>enabled</b>")
        if _firmware_timer_enabled()
        else _("Metadata refresh timer (fwupd-refresh.timer)")
    )


def on_click_system_firmware_timer_enable(self, _widget):
    """Enable and start fwupd-refresh.timer (periodic LVFS metadata refresh)."""
    # fn.enable_service() hardcode-appends ".service", so it cannot drive a timer
    # unit — call systemctl directly here.
    fn.log_subsection("Enabling fwupd-refresh.timer...")
    GLib.idle_add(fn.show_in_app_notification, self, _("Enabling firmware metadata timer..."))

    def worker():
        try:
            fn.subprocess.run(
                ["systemctl", "enable", "--now", "fwupd-refresh.timer"],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.log_success("fwupd-refresh.timer enabled")
            GLib.idle_add(_refresh_firmware_timer_label, self)
            GLib.idle_add(fn.show_in_app_notification, self, _("Firmware metadata timer enabled"))
        except Exception as e:
            fn.log_error(f"Error enabling fwupd-refresh.timer: {e}")

    fn.threading.Thread(target=worker, daemon=True).start()


def on_click_system_firmware_timer_disable(self, _widget):
    """Stop and disable fwupd-refresh.timer."""
    fn.log_subsection("Disabling fwupd-refresh.timer...")
    GLib.idle_add(fn.show_in_app_notification, self, _("Disabling firmware metadata timer..."))

    def worker():
        try:
            fn.subprocess.run(
                ["systemctl", "disable", "--now", "fwupd-refresh.timer"],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.log_success("fwupd-refresh.timer disabled")
            GLib.idle_add(_refresh_firmware_timer_label, self)
            GLib.idle_add(fn.show_in_app_notification, self, _("Firmware metadata timer disabled"))
        except Exception as e:
            fn.log_error(f"Error disabling fwupd-refresh.timer: {e}")

    fn.threading.Thread(target=worker, daemon=True).start()

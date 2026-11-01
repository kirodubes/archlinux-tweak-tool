# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import pwd

import functions as fn
from functions import GLib
from att_i18n import _, N_
from gi.repository import Gtk

NSSWITCH_OPTIONS = {
    "Kiro default": "mymachines files mdns_minimal [NOTFOUND=return] resolve [!UNAVAIL=return] dns wins myhostname",
    "Standard (systemd default)": "mymachines resolve [!UNAVAIL=return] files myhostname dns",
    "With mdns + wins": "mymachines resolve [!UNAVAIL=return] files dns mdns wins myhostname",
    "With mdns_minimal": "mymachines mdns_minimal [NOTFOUND=return] resolve [!UNAVAIL=return] files myhostname dns",
    "With mdns4_minimal": "mymachines mdns4_minimal [NOTFOUND=return] resolve [!UNAVAIL=return] files myhostname dns",
    "Custom order (no systemd)": "files mymachines myhostname mdns_minimal [NOTFOUND=return] resolve [!UNAVAIL=return] dns wins",
}


def choose_nsswitch(self):
    """Apply the selected nsswitch preset to /etc/nsswitch.conf."""
    fn.log_subsection("Apply Nsswitch Configuration")
    label = fn.get_combo_text(self.nsswitch_choices)

    if label in NSSWITCH_OPTIONS:
        hosts_line = NSSWITCH_OPTIONS[label]
        fn.log_info(f"  Preset : {label}")
        fn.log_info(f"  hosts: : {hosts_line}")
        fn.debug_print("  File   : /etc/nsswitch.conf")
        fn.copy_nsswitch(hosts_line)
        fn.log_success("Nsswitch configuration applied")
        GLib.idle_add(fn.show_in_app_notification, self, _("Nsswitch: {label}").format(label=label))
    else:
        fn.log_warn(f"Unknown nsswitch preset: {label}")


def choose_smb_conf(self):
    """Copy the ATT Samba config template, creating the Shared folder if needed."""
    fn.log_subsection("Apply Samba Configuration")
    shared_path = f"/home/{fn.sudo_username}/Shared"

    def _apply():
        fn.debug_print("  Config : example smb.conf")
        fn.copy_samba("example")
        fn.log_success("Samba configuration applied")
        GLib.idle_add(fn.show_in_app_notification, self, _("Smb.conf ATT configuration applied"))

    if fn.path.isdir(shared_path):
        fn.debug_print(f"  Folder : {shared_path} already exists")
        _apply()
        return

    dialog = Gtk.MessageDialog(
        transient_for=self,
        modal=True,
        message_type=Gtk.MessageType.QUESTION,
        buttons=Gtk.ButtonsType.YES_NO,
        text=_(
            "Create Shared folder?\n\nATT will create {path} as your samba share folder.\n"
            "If you choose No, create the folder yourself before connecting."
        ).format(path=shared_path),
    )

    def on_response(_dialog, response):
        _dialog.destroy()
        if response == Gtk.ResponseType.YES:
            fn.makedirs(shared_path, 0o755)
            fn.permissions(shared_path)
            fn.debug_print(f"  Created : {shared_path}")
        else:
            fn.debug_print("  Skipped : folder creation — user declined")
        _apply()

    dialog.connect("response", on_response)
    dialog.present()


def create_samba_user(self):
    """Open a terminal to set a Samba password for the current user."""
    username = fn.sudo_username

    if not username:
        fn.log_warn("Could not determine current user for samba password")
        return

    fn.log_subsection("Create Samba User")
    fn.debug_print(f"  Username : {username}")
    fn.debug_print("  Note     : Samba uses a separate password from Linux user accounts")

    script = f"""
echo 'Creating samba password for user: {username}'
echo 'Samba uses a separate password from your Linux login.'
echo ''

if ! command -v smbpasswd &>/dev/null; then
    echo '✗ smbpasswd not found — please install samba first'
    echo ''
    echo '=== Operation Finished ==='
    read -p 'Press Enter to close...'
    exit 1
fi

smbpasswd -a {username}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Samba password set successfully'
else
    echo '✗ Failed to set samba password'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""

    def _launch():
        try:
            fn.subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("Setting samba password for {username}...").format(username=username))
        except Exception as error:
            fn.GLib.idle_add(fn.log_error, f"Failed to open terminal: {error}")

    fn.threading.Thread(target=_launch, daemon=True).start()


def check_audio_server(expected):
    """Return True if the expected audio server is running, None on error."""
    try:
        result = fn.subprocess.run(["pactl", "info"], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "Server Name" in line:
                    fn.log_info_concise(f"  Active: {line.strip()}")
                    if expected.lower() in line.lower():
                        return True
        return False
    except Exception as e:
        fn.debug_print(f"Could not verify audio server: {e}")
        return None


def restart_smb(self):
    """Restart smb (and nmb if active) services and update the status label."""
    fn.log_subsection("SAMBA SERVICE RESTART - STATUS CHECKLIST")
    fn.debug_print(f"Configuration: {fn.samba_config}")

    smb_active = fn.check_service("smb")
    nmb_active = fn.check_service("nmb")
    avahi_active = fn.check_service("avahi-daemon")

    fn.debug_print(f"✓ Samba (smb):           {'✓ ACTIVE' if smb_active else '✗ INACTIVE'}")
    fn.debug_print(f"✓ NetBIOS (nmb):         {'✓ ACTIVE' if nmb_active else '✗ INACTIVE'}")
    fn.debug_print(f"✓ Avahi (discovery):     {'✓ ACTIVE' if avahi_active else '✗ INACTIVE'}")

    if not smb_active:
        fn.log_error("smb service is not running — enable it first")
        GLib.idle_add(
            fn.show_in_app_notification,
            self,
            _("✗ Samba is installed but the smb service is not running."),
        )
        return

    def _restart():
        fn.debug_print("Restarting samba services...")
        fn.subprocess.run(["systemctl", "restart", "smb"], check=False)
        if nmb_active:
            fn.subprocess.run(["systemctl", "restart", "nmb"], check=False)
        fn.log_success("Samba services restarted successfully")
        GLib.idle_add(update_network_status, self)
        GLib.idle_add(
            fn.show_in_app_notification,
            self,
            _("✓ Samba restarted. Check other services in the status bar."),
        )

    fn.threading.Thread(target=_restart, daemon=True).start()


# ── Services callbacks ───────────────────────────────────────────────


def on_click_switch_to_pulseaudio(self, _widget):
    """Open a terminal to install and switch to PulseAudio."""
    fn.log_subsection("Switch to PulseAudio — opening terminal")
    cmd = (
        "alacritty -e bash -c '/usr/share/archlinux-tweak-tool/data/bin/install-pulseaudio.sh;"
        ' read -p "Press Enter to close..."\''
    )

    def _wait():
        try:
            fn.subprocess.Popen(cmd, shell=True).wait()
            fn.log_success("PulseAudio install completed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("PulseAudio install completed"))
        except Exception as error:
            fn.log_error(f"Failed to open terminal: {error}")

    fn.threading.Thread(target=_wait, daemon=True).start()


def on_click_switch_to_pipewire(self, _widget):
    """Open a terminal to install and switch to PipeWire."""
    fn.log_subsection("Switch to PipeWire — opening terminal")
    cmd = (
        "alacritty -e bash -c '/usr/share/archlinux-tweak-tool/data/bin/install-pipewire.sh;"
        ' read -p "Press Enter to close..."\''
    )

    def _wait():
        try:
            fn.subprocess.Popen(cmd, shell=True).wait()
            fn.log_success("PipeWire install completed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("PipeWire install completed"))
        except Exception as error:
            fn.log_error(f"Failed to open terminal: {error}")

    fn.threading.Thread(target=_wait, daemon=True).start()


def on_click_install_bluetooth(self, _widget):
    """Install bluez and bluez-utils and enable the Bluetooth service controls."""
    fn.log_subsection("Install Bluetooth")

    def wait_and_update():
        process = fn.launch_pacman_install_in_terminal("bluez bluez-utils")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed("bluez"):
            GLib.idle_add(self.bluez_label.set_markup, _("Bluez packages are already <b>installed</b>"))
            GLib.idle_add(self.enable_bt.set_sensitive, True)
            GLib.idle_add(self.disable_bt.set_sensitive, True)
            GLib.idle_add(self.restart_bt.set_sensitive, True)
            GLib.idle_add(fn.log_success, "Bluetooth installed and controls enabled")
        else:
            GLib.idle_add(fn.log_warn, "Bluetooth package not found after installation")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_bluetooth(self, _widget):
    """Remove bluez and bluez-utils and disable the Bluetooth service controls."""
    fn.log_subsection("Remove Bluetooth")

    def wait_and_update():
        process = fn.launch_pacman_remove_in_terminal("bluez bluez-utils")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed("bluez"):
            GLib.idle_add(self.bluez_label.set_markup, _("Install bluetooth packages"))
            GLib.idle_add(self.enable_bt.set_sensitive, False)
            GLib.idle_add(self.disable_bt.set_sensitive, False)
            GLib.idle_add(self.restart_bt.set_sensitive, False)
            GLib.idle_add(fn.log_success, "Bluetooth removed and controls disabled")
        else:
            GLib.idle_add(fn.log_warn, "Bluetooth package still present after removal")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_install_blueberry(self, _widget):
    """Install the Blueberry Bluetooth manager."""
    fn.log_subsection("Install Blueberry")

    def wait_and_update():
        process = fn.launch_pacman_install_in_terminal("blueberry")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed("blueberry"):
            GLib.idle_add(self.blueberry_label.set_markup, _("   Blueberry is already <b>installed</b>"))
            GLib.idle_add(fn.log_success, "Blueberry installed")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_blueberry(self, _widget):
    """Remove the Blueberry Bluetooth manager."""
    fn.log_subsection("Remove Blueberry")

    def wait_and_update():
        process = fn.launch_pacman_remove_in_terminal("blueberry")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed("blueberry"):
            GLib.idle_add(self.blueberry_label.set_markup, _("   Install blueberry"))
            GLib.idle_add(fn.log_success, "Blueberry removed")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_install_blueman(self, _widget):
    """Install the Blueman Bluetooth manager."""
    fn.log_subsection("Install Blueman")

    def wait_and_update():
        process = fn.launch_pacman_install_in_terminal("blueman")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed("blueman"):
            GLib.idle_add(self.blueman_label.set_markup, _("   Blueman is already <b>installed</b>"))
            GLib.idle_add(fn.log_success, "Blueman installed")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_blueman(self, _widget):
    """Remove the Blueman Bluetooth manager."""
    fn.log_subsection("Remove Blueman")

    def wait_and_update():
        process = fn.launch_pacman_remove_in_terminal("blueman")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed("blueman"):
            GLib.idle_add(self.blueman_label.set_markup, _("   Install blueman"))
            GLib.idle_add(fn.log_success, "Blueman removed")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_install_bluedevil(self, _widget):
    """Install the Bluedevil Bluetooth manager (Plasma dependency)."""
    fn.log_subsection("Install Bluedevil")

    def wait_and_update():
        process = fn.launch_pacman_install_in_terminal("bluedevil")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed("bluedevil"):
            GLib.idle_add(self.bluedevil_label.set_markup, _("   Bluedevil is already <b>installed</b>"))
            GLib.idle_add(fn.log_success, "Bluedevil installed")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_bluedevil(self, _widget):
    """Remove the Bluedevil Bluetooth manager."""
    fn.log_subsection("Remove Bluedevil")

    def wait_and_update():
        process = fn.launch_pacman_remove_recursive_in_terminal("bluedevil")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed("bluedevil"):
            GLib.idle_add(self.bluedevil_label.set_markup, _("   Install bluedevil (Plasma dependencies)"))
            GLib.idle_add(fn.log_success, "Bluedevil removed")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


_BT_CONF = "/etc/bluetooth/main.conf"


def get_bluetooth_autoenable() -> bool:
    """Return True if AutoEnable=true is active (uncommented) in main.conf."""
    try:
        with open(_BT_CONF) as fh:
            for line in fh:
                stripped = line.strip()
                if stripped.lower() == "autoenable=true":
                    return True
        return False
    except OSError:
        return False


def set_bluetooth_autoenable(enabled: bool):
    """Write AutoEnable=true/false under [Policy] in main.conf, preserving all comments."""
    target = f"AutoEnable={'true' if enabled else 'false'}"
    try:
        with open(_BT_CONF) as fh:
            lines = fh.readlines()

        in_policy = False
        found = False
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("["):
                in_policy = stripped.lower() == "[policy]"
            if in_policy and stripped.lower().startswith("autoenable=") and not stripped.startswith("#"):
                new_lines.append(f"{target}\n")
                found = True
                continue
            if in_policy and stripped.lower() == "#autoenable=true" and not found:
                new_lines.append(f"{target}\n")
                found = True
                continue
            new_lines.append(line)

        if not found:
            new_lines.append(f"\n[Policy]\n{target}\n")

        with open(_BT_CONF, "w") as fh:
            fh.writelines(new_lines)
    except OSError as error:
        fn.log_error(f"Failed to write {_BT_CONF}: {error}")


def on_bt_autoconnect_toggled(self, switch, _gparam):
    """Write AutoEnable to main.conf and restart bluetooth so it takes effect."""
    if getattr(self, "bt_autoconnect_initializing", False):
        return
    enabled = switch.get_active()
    fn.log_subsection("Bluetooth Auto-Connect")
    set_bluetooth_autoenable(enabled)
    state = "enabled" if enabled else "disabled"
    try:
        fn.restart_service("bluetooth")
        fn.log_success(f"Bluetooth auto-connect {state}; service restarted")
        fn.show_in_app_notification(self, _("Auto-connect enabled") if enabled else _("Auto-connect disabled"))
    except Exception as error:
        fn.log_error(f"Failed to restart bluetooth: {error}")


def on_click_install_bt_autoconnect(self, _widget):
    """Install bluetooth-autoconnect and enable its service."""
    fn.log_subsection("Install bluetooth-autoconnect")
    fn.show_in_app_notification(self, _("Opening terminal to install bluetooth-autoconnect..."))

    def wait_and_update():
        process = fn.launch_pacman_install_in_terminal("bluetooth-autoconnect")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed("bluetooth-autoconnect"):
            fn.enable_service("bluetooth-autoconnect")
            GLib.idle_add(
                self.bt_autoconnect_pkg_label.set_markup,
                _("   bluetooth-autoconnect is <b>installed</b> and enabled"),
            )
            GLib.idle_add(fn.log_success, "bluetooth-autoconnect installed and enabled")
        else:
            GLib.idle_add(fn.log_warn, "bluetooth-autoconnect not found after installation")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_bt_autoconnect(self, _widget):
    """Disable and remove bluetooth-autoconnect."""
    fn.log_subsection("Remove bluetooth-autoconnect")
    if not fn.check_package_installed("bluetooth-autoconnect"):
        fn.log_info("bluetooth-autoconnect is not installed")
        fn.show_in_app_notification(self, _("bluetooth-autoconnect is not installed"))
        return
    fn.disable_service("bluetooth-autoconnect")

    def wait_and_update():
        process = fn.launch_pacman_remove_in_terminal("bluetooth-autoconnect")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed("bluetooth-autoconnect"):
            GLib.idle_add(
                self.bt_autoconnect_pkg_label.set_markup,
                _("   Install bluetooth-autoconnect"),
            )
            GLib.idle_add(fn.log_success, "bluetooth-autoconnect removed")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_enable_bluetooth(self, _widget):
    """Enable the bluetooth systemd service."""
    fn.log_subsection("Enable Bluetooth Service")
    try:
        fn.enable_service("bluetooth")
        fn.log_success("Bluetooth service enabled")
        fn.show_in_app_notification(self, _("Bluetooth has been enabled"))
    except Exception as error:
        fn.log_error(f"Failed to enable bluetooth: {error}")


def on_click_disable_bluetooth(self, _widget):
    """Disable the bluetooth systemd service."""
    fn.log_subsection("Disable Bluetooth Service")
    try:
        fn.disable_service("bluetooth")
        fn.log_success("Bluetooth service disabled")
        fn.show_in_app_notification(self, _("Bluetooth has been disabled"))
    except Exception as error:
        fn.log_error(f"Failed to disable bluetooth: {error}")


def on_click_restart_bluetooth(self, _widget):
    """Start or restart the bluetooth systemd service."""
    fn.log_subsection("Restart Bluetooth Service")
    try:
        fn.restart_service("bluetooth")
        fn.log_success("Bluetooth service restarted")
        fn.show_in_app_notification(self, _("Bluetooth has been restarted"))
    except Exception as error:
        fn.log_error(f"Failed to restart bluetooth: {error}")


def on_click_install_cups(self, _widget):
    """Install CUPS and update the status label on completion."""
    fn.log_subsection("Install CUPS")
    fn.show_in_app_notification(self, _("Opening terminal to install cups..."))
    process = fn.launch_pacman_install_in_terminal("cups")

    def wait_and_update():
        try:
            if process:
                process.wait()
            fn.invalidate_pkg_cache()
            if fn.check_package_installed("cups"):
                fn.log_success("CUPS installed")
                GLib.idle_add(fn.show_in_app_notification, self, _("CUPS installed"))
                GLib.idle_add(self.cups_install_label.set_markup, _("Cups printing is <b>installed</b>"))
            else:
                fn.log_warn("CUPS installation did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, _("CUPS installation failed or was cancelled"))
        except Exception as error:
            fn.log_error(f"Failed to install CUPS: {error}")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_cups(self, _widget):
    """Remove CUPS and update the status label on completion."""
    fn.log_subsection("Remove CUPS")
    fn.show_in_app_notification(self, _("Opening terminal to remove cups..."))
    process = fn.launch_pacman_remove_in_terminal("cups cups-filters")

    def wait_and_update():
        try:
            if process:
                process.wait()
            fn.invalidate_pkg_cache()
            if not fn.check_package_installed("cups"):
                fn.log_success("CUPS removed")
                GLib.idle_add(fn.show_in_app_notification, self, _("CUPS removed"))
                GLib.idle_add(self.cups_install_label.set_markup, _("Install cups printing"))
            else:
                fn.log_warn("CUPS removal did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, _("CUPS removal failed or was cancelled"))
        except Exception as error:
            fn.log_error(f"Failed to remove CUPS: {error}")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_install_cups_pdf(self, _widget):
    """Install cups-pdf and update the status label on completion."""
    fn.log_subsection("Install CUPS PDF")
    fn.show_in_app_notification(self, _("Opening terminal to install cups-pdf..."))
    process = fn.launch_pacman_install_in_terminal("cups-pdf")

    def wait_and_update():
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed("cups-pdf"):
            fn.log_success("CUPS PDF printer installed")
            GLib.idle_add(fn.show_in_app_notification, self, _("cups-pdf installed"))
            GLib.idle_add(self.cups_pdf_label.set_markup, _("Cups-pdf is <b>installed</b>"))
        else:
            fn.log_warn("cups-pdf installation did not complete")
            GLib.idle_add(fn.show_in_app_notification, self, _("cups-pdf installation failed or was cancelled"))

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_cups_pdf(self, _widget):
    """Remove cups-pdf and update the status label on completion."""
    fn.log_subsection("Remove CUPS PDF")
    fn.show_in_app_notification(self, _("Opening terminal to remove cups-pdf..."))
    process = fn.launch_pacman_remove_in_terminal("cups-pdf")

    def wait_and_update():
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed("cups-pdf"):
            fn.log_success("CUPS PDF printer removed")
            GLib.idle_add(fn.show_in_app_notification, self, _("cups-pdf removed"))
            GLib.idle_add(self.cups_pdf_label.set_markup, _("Install cups-pdf printing"))
        else:
            fn.log_warn("cups-pdf removal did not complete")
            GLib.idle_add(fn.show_in_app_notification, self, _("cups-pdf removal failed or was cancelled"))

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def update_cups_status(self):
    """Refresh the CUPS service and socket status label."""
    status1 = fn.check_service("cups")
    if status1 is True:
        status1 = _("<b>active</b>")
    else:
        status1 = _("inactive")

    status2 = fn.check_socket("cups")
    if status2 is True:
        status2 = _("<b>active</b>")
    else:
        status2 = _("inactive")

    GLib.idle_add(
        self.cups_status_label.set_markup,
        _("Cups service : {service}   Cups socket : {socket}").format(service=status1, socket=status2),
    )


def on_click_enable_cups(self, _widget):
    """Enable the CUPS service and refresh the status label."""
    fn.log_subsection("Enable CUPS Service")
    try:
        fn.enable_service("cups")
        fn.log_success("CUPS service enabled")
        update_cups_status(self)
    except Exception as error:
        fn.log_error(f"Failed to enable CUPS: {error}")


def on_click_disable_cups(self, _widget):
    """Disable the CUPS service and refresh the status label."""
    fn.log_subsection("Disable CUPS Service")
    try:
        fn.disable_service("cups")
        fn.log_success("CUPS service disabled")
        update_cups_status(self)
    except Exception as error:
        fn.log_error(f"Failed to disable CUPS: {error}")


def on_click_restart_cups(self, _widget):
    """Start or restart the CUPS service and refresh the status label."""
    fn.log_subsection("Restart CUPS Service")
    try:
        fn.restart_service("cups")
        fn.log_success("CUPS service restarted")
        update_cups_status(self)
    except Exception as error:
        fn.log_error(f"Failed to restart CUPS: {error}")


def on_click_install_printer_drivers(self, _widget):
    """Install common printer driver packages (foomatic, gutenprint, ghostscript)."""
    fn.log_subsection("Install Printer Drivers")

    def wait_and_update():
        packages = (
            "foomatic-db-engine foomatic-db foomatic-db-ppds "
            "foomatic-db-nonfree foomatic-db-nonfree-ppds "
            "gutenprint foomatic-db-gutenprint-ppds ghostscript gsfonts"
        )
        process = fn.launch_pacman_install_in_terminal(packages)
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed("foomatic-db"):
            GLib.idle_add(
                self.printer_drivers_label.set_markup,
                _("   Install common printer drivers (foomatic, gutenprint, ...) - <b>Installed</b>"),
            )
            GLib.idle_add(fn.log_success, "Printer drivers installed successfully")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_printer_drivers(self, _widget):
    """Remove common printer driver packages."""
    fn.log_subsection("Remove Printer Drivers")

    def wait_and_update():
        packages = (
            "foomatic-db-engine foomatic-db foomatic-db-ppds "
            "foomatic-db-nonfree foomatic-db-nonfree-ppds "
            "gutenprint foomatic-db-gutenprint-ppds ghostscript gsfonts"
        )
        process = fn.launch_pacman_remove_in_terminal(packages)
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed("foomatic-db"):
            GLib.idle_add(
                self.printer_drivers_label.set_markup, _("   Install common printer drivers (foomatic, gutenprint, ...)")
            )
            GLib.idle_add(fn.log_success, "Printer drivers removed successfully")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_install_hplip(self, _widget):
    """Install the HPLIP HP printer driver."""
    fn.log_subsection("Install HPLIP")

    def wait_and_update():
        process = fn.launch_pacman_install_in_terminal("hplip")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed("hplip"):
            GLib.idle_add(self.hplip_label.set_markup, _("   HP drivers have been <b>installed</b>"))
            GLib.idle_add(fn.log_success, "HPLIP installed")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_hplip(self, _widget):
    """Remove the HPLIP HP printer driver."""
    fn.log_subsection("Remove HPLIP")

    def wait_and_update():
        process = fn.launch_pacman_remove_in_terminal("hplip")
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed("hplip"):
            GLib.idle_add(self.hplip_label.set_markup, _("   Install HP drivers"))
            GLib.idle_add(fn.log_success, "HPLIP removed")

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_install_system_config_printer(self, _widget):
    """Install system-config-printer and update the status label."""
    fn.log_subsection("Install System Config Printer")
    fn.show_in_app_notification(self, _("Opening terminal to install system-config-printer..."))
    process = fn.launch_pacman_install_in_terminal("system-config-printer")

    def wait_and_update():
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed("system-config-printer"):
            fn.log_success("System Config Printer installed")
            GLib.idle_add(fn.show_in_app_notification, self, _("system-config-printer installed"))
            GLib.idle_add(
                self.system_config_printer_label.set_markup, _("Install System-config-printer - <b>Installed</b>")
            )
        else:
            fn.log_warn("system-config-printer installation did not complete")
            GLib.idle_add(
                fn.show_in_app_notification, self, _("system-config-printer installation failed or was cancelled")
            )

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def on_click_remove_system_config_printer(self, _widget):
    """Remove system-config-printer and update the status label."""
    fn.log_subsection("Remove System Config Printer")
    fn.show_in_app_notification(self, _("Opening terminal to remove system-config-printer..."))
    process = fn.launch_pacman_remove_in_terminal("system-config-printer")

    def wait_and_update():
        if process:
            process.wait()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed("system-config-printer"):
            fn.log_success("System Config Printer removed")
            GLib.idle_add(fn.show_in_app_notification, self, _("system-config-printer removed"))
            GLib.idle_add(self.system_config_printer_label.set_markup, _("Install System-config-printer"))
        else:
            fn.log_warn("system-config-printer removal did not complete")
            GLib.idle_add(fn.show_in_app_notification, self, _("system-config-printer removal failed or was cancelled"))

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def update_network_status(self):
    """Refresh the Samba/nmb/Avahi status label and toggle button text."""
    smb_active = fn.check_service("smb")
    if hasattr(self, "network_status_label"):
        status1_text = _("<b>active</b>") if smb_active else _("inactive")
        status2 = fn.check_service("nmb")
        status2_text = _("<b>active</b>") if status2 else _("inactive")
        status3 = fn.check_service("avahi-daemon")
        status3_text = _("<b>active</b>") if status3 else _("inactive")
        status_fw = fn.check_service("firewalld")
        status_fw_text = _("<b>active</b>") if status_fw else _("inactive")
        self.network_status_label.set_markup(
            _("Samba: {smb}   Nmb: {nmb}   Avahi: {avahi}   Firewall: {firewall}").format(
                smb=status1_text, nmb=status2_text, avahi=status3_text, firewall=status_fw_text
            )
        )
    if hasattr(self, "btn_toggle_smb"):
        self.btn_toggle_smb.set_label(_("Disable Samba") if smb_active else _("Enable Samba"))
    if hasattr(self, "btn_toggle_firewalld"):
        fw_active = fn.check_service("firewalld")
        self.btn_toggle_firewalld.set_label(_("Disable firewall") if fw_active else _("Enable firewall"))
        if hasattr(self, "lbl_firewall_info"):
            self.lbl_firewall_info.set_markup(
                _("Firewall (firewalld) is <b>active</b> — Kiro enables it by default to keep you protected.")
                if fw_active
                else _("Firewall (firewalld) is <b>inactive</b>.")
            )
    if hasattr(self, "btn_fw_mdns"):
        mdns_open = fn.check_firewall_service("mdns")
        self.btn_fw_mdns.set_label(
            _("Block network discovery (mDNS)") if mdns_open else _("Allow network discovery (mDNS)")
        )
    if hasattr(self, "btn_fw_samba"):
        samba_open = fn.check_firewall_service("samba")
        self.btn_fw_samba.set_label(
            _("Block Samba file sharing") if samba_open else _("Allow Samba file sharing")
        )
    if hasattr(self, "lbl_firewall_status"):
        self.lbl_firewall_status.set_markup(fn.firewall_status_markup())


def on_install_discovery_clicked(self, _widget):
    """Install network discovery packages and refresh the status label."""
    fn.log_subsection("Install Network Discovery")

    def _wait(process):
        if process is None:
            return
        process.wait()
        fn.invalidate_pkg_cache()
        GLib.idle_add(update_network_status, self)

    proc = fn.install_discovery(self)
    fn.threading.Thread(target=_wait, args=(proc,), daemon=True).start()


def on_remove_discovery_clicked(self, _widget):
    """Remove network discovery packages and refresh the status label."""
    fn.log_subsection("Remove Network Discovery")

    def _wait(process):
        if process is None:
            return
        process.wait()
        fn.invalidate_pkg_cache()
        GLib.idle_add(update_network_status, self)

    proc = fn.remove_discovery(self)
    fn.threading.Thread(target=_wait, args=(proc,), daemon=True).start()


def on_click_reset_nsswitch(self, _widget):
    """Restore /etc/nsswitch.conf from the ATT backup file."""
    fn.log_subsection("Reset Nsswitch Configuration")
    if fn.path.isfile(fn.nsswitch_config + "-bak"):
        try:
            fn.log_info_concise(f"  From: {fn.nsswitch_config}-bak")
            fn.log_info_concise(f"  To:   {fn.nsswitch_config}")
            fn.shutil.copy(fn.nsswitch_config + "-bak", fn.nsswitch_config)
            fn.debug_print(f"Restored from backup: {fn.nsswitch_config}-bak")
            fn.log_success("Nsswitch configuration reset to original")
            fn.show_in_app_notification(self, _("Nsswitch config reset"))
        except Exception as error:
            fn.log_error(f"Failed to reset nsswitch: {error}")
    else:
        fn.log_warn("No backup configuration file found")
        fn.show_in_app_notification(self, _("No nsswitch backup available"))


def on_click_edit_nsswitch(self, _widget):
    """Open /etc/nsswitch.conf in the nano editor."""
    fn.log_subsection("Edit Nsswitch Configuration")
    try:
        fn.subprocess.Popen(
            ["alacritty", "-e", "nano", fn.nsswitch_config],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        fn.debug_print(f"File: {fn.nsswitch_config}")
        fn.log_success("Nsswitch configuration opened in nano editor")
        fn.show_in_app_notification(self, _("nsswitch.conf opened in terminal"))
    except Exception as e:
        fn.log_error(f"Failed to open nsswitch configuration: {e}")


def on_click_apply_nsswitch(self, _widget):
    """Apply the selected nsswitch preset."""
    fn.log_subsection("Apply Nsswitch Configuration")
    choose_nsswitch(self)


def on_click_create_samba_user(self, _widget):
    """Open a terminal to create a Samba user account."""
    fn.log_subsection("Create Samba User")
    create_samba_user(self)


def on_click_toggle_smb(self, _widget):
    """Toggle Samba (smb + nmb) services on or off."""
    fn.log_subsection("Toggle Samba Services")
    if not fn.check_package_installed("samba"):
        fn.log_info("Samba is not installed")
        fn.show_in_app_notification(self, _("Samba is not yet installed."))
        return
    if fn.check_service("smb"):
        fn.disable_service("smb")
        fn.disable_service("nmb")
        fn.log_success("Samba services (smb + nmb) disabled")
        fn.show_in_app_notification(self, _("Samba disabled"))
        if hasattr(self, "btn_toggle_smb"):
            GLib.idle_add(self.btn_toggle_smb.set_label, _("Enable Samba"))
    else:
        fn.enable_service("smb")
        fn.enable_service("nmb")
        fn.log_success("Samba services (smb + nmb) enabled")
        fn.show_in_app_notification(self, _("Samba enabled"))
        if hasattr(self, "btn_toggle_smb"):
            GLib.idle_add(self.btn_toggle_smb.set_label, _("Disable Samba"))


def on_click_toggle_firewalld(self, _widget):
    """Toggle the firewalld service (enable+start / disable+stop)."""
    fn.log_subsection("Toggle Firewall (firewalld)")
    if not fn.check_package_installed("firewalld"):
        fn.show_in_app_notification(self, _("firewalld is not installed."))
        return
    disabling = fn.check_service("firewalld")

    def _toggle():
        if disabling:
            fn.subprocess.run(["systemctl", "disable", "--now", "firewalld"], check=False)
            fn.log_success("firewalld disabled")
            msg = _("Firewall disabled")
        else:
            fn.subprocess.run(["systemctl", "enable", "--now", "firewalld"], check=False)
            fn.log_success("firewalld enabled")
            msg = _("Firewall enabled")
        GLib.idle_add(update_network_status, self)
        GLib.idle_add(fn.show_in_app_notification, self, msg)

    fn.threading.Thread(target=_toggle, daemon=True).start()


def on_click_firewall_toggle_mdns(self, _widget):
    """Toggle the mDNS service in firewalld (needed for .local network discovery)."""
    _firewall_toggle_service(self, "mdns", N_("network discovery (mDNS)"))


def on_click_firewall_toggle_samba(self, _widget):
    """Toggle the Samba service in firewalld (needed for file sharing)."""
    _firewall_toggle_service(self, "samba", N_("Samba file sharing"))


def on_click_firewall_config(self, _widget):
    """Launch the graphical firewall editor, or install it if missing."""
    fn.log_subsection("firewall-config (graphical firewall editor)")
    if fn.path.exists("/usr/bin/firewall-config"):
        def _launch():
            try:
                fn.subprocess.Popen(["firewall-config"])
                GLib.idle_add(fn.show_in_app_notification, self, _("Launching firewall-config..."))
            except Exception as error:
                GLib.idle_add(fn.log_error, f"Failed to launch firewall-config: {error}")

        fn.threading.Thread(target=_launch, daemon=True).start()
        return

    def _install():
        script = "sudo pacman -S --needed firewall-config; read -p 'Press Enter to close...'"
        fn.subprocess.Popen(["alacritty", "-e", "bash", "-c", script]).wait()
        fn.invalidate_pkg_cache()
        if fn.path.exists("/usr/bin/firewall-config"):
            fn.log_success("firewall-config installed")
            GLib.idle_add(
                self.lbl_firewall_config.set_markup,
                _("Graphical firewall editor (firewall-config) - <b>installed</b>"),
            )
            GLib.idle_add(self.btn_firewall_config.set_label, _("Launch firewall-config"))
        GLib.idle_add(fn.show_in_app_notification, self, _("firewall-config install finished"))

    fn.threading.Thread(target=_install, daemon=True).start()


def _firewall_toggle_service(self, service, label):
    if not fn.check_service("firewalld"):
        fn.show_in_app_notification(self, _("Enable the firewall first."))
        return
    allowing = not fn.check_firewall_service(service)
    fn.debug_print(f"firewalld {service}: currently {'closed' if allowing else 'open'} -> "
                   f"opening terminal to {'add' if allowing else 'remove'} the service")

    def _wait(process):
        if process is None:
            return
        process.wait()
        GLib.idle_add(update_network_status, self)

    proc = fn.firewall_toggle_service(self, service, label, allowing)
    fn.threading.Thread(target=_wait, args=(proc,), daemon=True).start()


def on_click_restart_smb(self, _widget):
    """Restart Samba services if the package is installed."""
    fn.log_subsection("Restart SMB Service")
    if not fn.check_package_installed("samba"):
        fn.log_info("Samba is not installed")
        fn.show_in_app_notification(self, _("Samba is not yet installed."))
        return
    restart_smb(self)


def on_click_save_samba_share(self, _widget):
    """Save the current Samba share configuration."""
    fn.log_subsection("Save Samba Share Configuration")
    try:
        fn.save_samba_config(self)
        fn.log_success("Samba share configuration saved")
    except Exception as error:
        fn.log_error(f"Failed to save samba configuration: {error}")


def on_click_apply_samba(self, _widget):
    """Apply the ATT Samba config template."""
    fn.log_subsection("Apply Samba Configuration")
    try:
        choose_smb_conf(self)
        fn.debug_print("Samba configuration applied from selected template")
        fn.log_success("Samba configuration applied successfully")
        fn.show_in_app_notification(self, _("Samba configuration applied"))
    except Exception as error:
        fn.log_error(f"Failed to apply samba configuration: {error}")


def on_click_reset_samba(self, _widget):
    """Restore smb.conf from the ATT backup file."""
    fn.log_subsection("Reset Samba Configuration")
    if fn.path.isfile(fn.samba_config + "-bak"):
        try:
            fn.log_info_concise(f"  From: {fn.samba_config}-bak")
            fn.log_info_concise(f"  To:   {fn.samba_config}")
            fn.shutil.copy(fn.samba_config + "-bak", fn.samba_config)
            fn.debug_print(f"Restored from backup: {fn.samba_config}-bak")
            fn.log_success("Samba configuration reset to original")
            fn.show_in_app_notification(self, _("Original smb.conf is applied"))
        except Exception as error:
            fn.log_error(f"Failed to reset samba configuration: {error}")
    else:
        fn.log_warn("No backup configuration file found")
        fn.debug_print(f"Missing: {fn.samba_config}-bak")
        fn.show_in_app_notification(self, _("No backup configuration present"))


def on_click_edit_samba_nano(self, _widget):
    """Open smb.conf in the nano editor."""
    fn.log_subsection("Edit Samba Configuration")
    try:
        fn.subprocess.Popen(
            ["alacritty", "-e", "nano", fn.samba_config],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        fn.debug_print(f"File: {fn.samba_config}")
        fn.log_success("Samba configuration opened in nano editor")
        fn.show_in_app_notification(self, _("Opening samba.conf in terminal with nano"))
    except Exception as error:
        fn.log_error(f"Failed to open samba configuration: {error}")


def on_click_install_samba(self, _widget):
    """Install Samba and apply the default config."""
    fn.log_subsection("Install Samba")

    def _wait(process):
        if process is None:
            return
        process.wait()
        fn.invalidate_pkg_cache()
        GLib.idle_add(choose_smb_conf, self)
        GLib.idle_add(update_network_status, self)

    proc = fn.install_samba(self)
    fn.threading.Thread(target=_wait, args=(proc,), daemon=True).start()


def on_click_uninstall_samba(self, _widget):
    """Uninstall Samba and update the network status."""
    fn.log_subsection("Uninstall Samba")

    def _wait(process):
        if process is None:
            return
        process.wait()
        fn.invalidate_pkg_cache()
        GLib.idle_add(update_network_status, self)

    proc = fn.uninstall_samba(self)
    fn.threading.Thread(target=_wait, args=(proc,), daemon=True).start()


def get_user_services():
    """Return the real user's active --user services, custom units flagged first."""
    fn.log_subsection("Reading user systemd services")
    try:
        pw = pwd.getpwnam(fn.sudo_username)
    except KeyError:
        fn.log_warn(f"Cannot resolve user '{fn.sudo_username}' — no user services listed")
        return []
    uid = pw.pw_uid
    custom_prefixes = (f"{pw.pw_dir}/.config/systemd/user", "/etc/systemd/user")

    cmd = [
        "sudo",
        "-u",
        fn.sudo_username,
        f"XDG_RUNTIME_DIR=/run/user/{uid}",
        f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus",
        "systemctl",
        "--user",
        "show",
        "*",
        "--type=service",
        "-p",
        "Id",
        "-p",
        "Description",
        "-p",
        "ActiveState",
        "-p",
        "SubState",
        "-p",
        "UnitFileState",
        "-p",
        "FragmentPath",
    ]
    try:
        result = fn.subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except Exception as error:
        fn.log_error(f"Failed to read user services: {error}")
        return []
    if result.returncode != 0:
        fn.log_warn("systemctl --user returned no session (is a user session running?)")
        return []

    services = []
    for block in result.stdout.strip().split("\n\n"):
        props = dict(line.split("=", 1) for line in block.splitlines() if "=" in line)
        if not props.get("Id"):
            continue
        if props.get("ActiveState") != "active":
            continue
        fragment = props.get("FragmentPath", "")
        services.append(
            {
                "id": props["Id"],
                "description": props.get("Description", ""),
                "active": props.get("ActiveState", ""),
                "sub": props.get("SubState", ""),
                "enabled": props.get("UnitFileState", "") or "—",
                "custom": fragment.startswith(custom_prefixes),
            }
        )

    services.sort(key=lambda s: (not s["custom"], s["id"]))
    custom_count = sum(1 for s in services if s["custom"])
    fn.log_info(f"  {len(services)} active user services ({custom_count} custom)")
    return services

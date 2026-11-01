# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools

import functions as fn
from att_i18n import _

ALLOWLIST_PATH = "/etc/hblock/allow.list"


def _refresh_ublock_label(self):
    installed = fn.check_package_installed("firefox-ublock-origin")
    self.lbl_ublock.set_markup(
        _("{name} for Firefox <b>installed</b>").format(name="uBlock Origin")
        if installed
        else _("{name} for Firefox").format(name="uBlock Origin")
    )


def _is_hblock_active():
    try:
        with open("/etc/hosts", "r") as f:
            return any("hblock" in line for line in f)
    except OSError:
        return False


def _refresh_hblock_label(self):
    installed = fn.check_package_installed("hblock")
    self.lbl_hblock.set_markup(
        _("{name} — ad/tracker blocking via /etc/hosts <b>installed</b>").format(name="hblock")
        if installed
        else _("{name} — ad/tracker blocking via /etc/hosts").format(name="hblock")
    )
    self.btn_enable_hblock.set_sensitive(installed)
    self.btn_disable_hblock.set_sensitive(installed)
    self.btn_add_whitelist.set_sensitive(installed)
    active = _is_hblock_active()
    self.lbl_hblock_status.set_markup(
        _("Enable or disable {name} — check /etc/hosts <b>active</b>").format(name="hblock")
        if active
        else _("Enable or disable {name} — check /etc/hosts inactive").format(name="hblock")
    )


def _normalize_host(raw):
    """Reduce a pasted URL or host to the bare hostname hblock matches."""
    host = raw.strip()
    host = fn.re.sub(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", "", host)
    host = host.split("/")[0]
    host = host.split("@")[-1]
    host = host.split(":")[0]
    return host.strip().lower()


def _read_allowlist():
    """Return the hosts in the hblock allowlist, skipping comments and blanks."""
    try:
        with open(ALLOWLIST_PATH, "r") as f:
            lines = f.readlines()
    except OSError:
        return []
    return [entry.strip() for entry in lines if entry.strip() and not entry.startswith("#")]


def _write_allowlist(hosts):
    """Write the hblock allowlist, creating /etc/hblock if needed."""
    fn.os.makedirs("/etc/hblock", exist_ok=True)
    with open(ALLOWLIST_PATH, "w") as f:
        f.write("# hblock allowlist — managed by ArchLinux Tweak Tool\n")
        for host in hosts:
            f.write(host + "\n")


def _refresh_allowlist_box(self):
    """Repopulate the whitelist ListBox from the allowlist file."""
    child = self.listbox_whitelist.get_first_child()
    while child is not None:
        self.listbox_whitelist.remove(child)
        child = self.listbox_whitelist.get_first_child()

    hosts = _read_allowlist()
    if not hosts:
        placeholder = fn.Gtk.Label(xalign=0)
        placeholder.set_markup(_("<i>No hosts whitelisted yet</i>"))
        placeholder.set_margin_start(6)
        placeholder.set_margin_top(4)
        placeholder.set_margin_bottom(4)
        self.listbox_whitelist.append(placeholder)
        return

    for host in hosts:
        hbox_row = fn.Gtk.Box(orientation=fn.Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_row.set_margin_start(6)
        hbox_row.set_margin_end(6)
        hbox_row.set_margin_top(2)
        hbox_row.set_margin_bottom(2)
        lbl_host = fn.Gtk.Label(xalign=0, label=host)
        lbl_host.set_hexpand(True)
        btn_remove = fn.Gtk.Button(label=_("Remove"))
        btn_remove.connect("clicked", functools.partial(on_click_remove_whitelist, self, host))
        hbox_row.append(lbl_host)
        hbox_row.append(btn_remove)
        self.listbox_whitelist.append(hbox_row)


def _reapply_hblock(self, action_msg):
    """Re-run hblock so allowlist edits take effect, with progress feedback."""
    if not fn.check_package_installed("hblock"):
        return
    if not _is_hblock_active():
        fn.log_info("hblock not active — allowlist will apply when hblock is enabled")
        return

    def run():
        stop_pulse = fn.threading.Event()

        def _pulse():
            while not stop_pulse.is_set():
                fn.GLib.idle_add(self.progress.pulse)
                fn.time.sleep(0.1)

        fn.GLib.idle_add(self.btn_add_whitelist.set_sensitive, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_text, action_msg)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, True)
        fn.GLib.idle_add(self.progress.set_visible, True)
        fn.threading.Thread(target=_pulse, daemon=True).start()
        fn.subprocess.run(
            ["/usr/bin/hblock"],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        stop_pulse.set()
        fn.log_success("hblock re-applied with updated allowlist")
        fn.GLib.idle_add(self.progress.set_visible, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, False)
        fn.GLib.idle_add(self.btn_add_whitelist.set_sensitive, True)

    fn.threading.Thread(target=run, daemon=True).start()


def on_click_add_whitelist(self, _widget):
    """Add the entered host/URL to the hblock allowlist and re-apply hblock."""
    host = _normalize_host(self.entry_whitelist.get_text())
    if not host:
        fn.log_warn("Whitelist: no host entered")
        fn.show_in_app_notification(self, _("Enter a host to whitelist"))
        return
    fn.log_subsection(f"Whitelist add: {host}")

    hosts = _read_allowlist()
    if host in hosts:
        fn.log_info(f"{host} is already whitelisted")
        fn.show_in_app_notification(self, _("{host} is already whitelisted").format(host=host))
        return

    hosts.append(host)
    try:
        _write_allowlist(hosts)
    except OSError as err:
        fn.log_error(f"Could not write allowlist: {err}")
        fn.show_in_app_notification(self, _("Could not write the allowlist file"))
        return

    fn.log_success(f"Added {host} to the hblock allowlist")
    fn.show_in_app_notification(self, _("Whitelisted {host}").format(host=host))
    self.entry_whitelist.set_text("")
    _refresh_allowlist_box(self)
    _reapply_hblock(self, _("Whitelisting {host}...").format(host=host))


def on_click_remove_whitelist(self, host, _widget):
    """Remove a host from the hblock allowlist and re-apply hblock."""
    fn.log_subsection(f"Whitelist remove: {host}")
    hosts = [h for h in _read_allowlist() if h != host]
    try:
        _write_allowlist(hosts)
    except OSError as err:
        fn.log_error(f"Could not write allowlist: {err}")
        fn.show_in_app_notification(self, _("Could not write the allowlist file"))
        return

    fn.log_success(f"Removed {host} from the hblock allowlist")
    fn.show_in_app_notification(self, _("Removed {host} from whitelist").format(host=host))
    _refresh_allowlist_box(self)
    _reapply_hblock(self, _("Re-blocking {host}...").format(host=host))


def on_click_install_ublock(self, _widget):
    """Install the firefox-ublock-origin package via a terminal."""
    if fn.check_package_installed("firefox-ublock-origin"):
        fn.log_info("uBlock Origin is already installed")
        fn.show_in_app_notification(self, _("{name} is already installed").format(name="uBlock Origin"))
        return
    fn.log_subsection("Install uBlock Origin")
    script = "sudo pacman -S firefox-ublock-origin --needed; read -p 'Press enter to close'"
    fn.debug_print(f"Terminal cmd: {script}")
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

    def wait_and_refresh():
        process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_ublock_label, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_remove_ublock(self, _widget):
    """Remove the firefox-ublock-origin package via a terminal."""
    if not fn.check_package_installed("firefox-ublock-origin"):
        fn.log_info("uBlock Origin is not installed")
        fn.show_in_app_notification(self, _("{name} is not installed").format(name="uBlock Origin"))
        return
    fn.log_subsection("Remove uBlock Origin")
    script = "sudo pacman -Rs firefox-ublock-origin; read -p 'Press enter to close'"
    fn.debug_print(f"Terminal cmd: {script}")
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

    def wait_and_refresh():
        process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_ublock_label, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_install_hblock(self, _widget):
    """Install the hblock package via a terminal."""
    if fn.check_package_installed("hblock"):
        fn.log_info("hblock is already installed")
        fn.show_in_app_notification(self, _("{name} is already installed").format(name="hblock"))
        return
    fn.log_subsection("Install hblock")
    script = "sudo pacman -S hblock --needed; read -p 'Press enter to close'"
    fn.debug_print(f"Terminal cmd: {script}")
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

    def wait_and_refresh():
        process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_hblock_label, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_remove_hblock(self, _widget):
    """Disable hblock, restore original /etc/hosts, then remove the package."""
    if not fn.check_package_installed("hblock"):
        fn.log_info("hblock is not installed")
        fn.show_in_app_notification(self, _("{name} is not installed").format(name="hblock"))
        return
    fn.log_subsection("Remove hblock")

    try:
        fn.subprocess.run(
            ["sh", "-c", "HBLOCK_SOURCES='' /usr/bin/hblock"],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        fn.log_info("hblock cleared /etc/hosts before removal")
    except OSError as err:
        fn.log_warn(f"Could not run hblock --clear: {err}")

    if fn.path.exists("/etc/hosts-bak"):
        try:
            fn.shutil.copy2("/etc/hosts-bak", "/etc/hosts")
            fn.os.remove("/etc/hosts-bak")
            fn.log_info("Restored /etc/hosts from /etc/hosts-bak")
        except OSError as err:
            fn.log_warn(f"Could not restore /etc/hosts-bak: {err}")

    script = "sudo pacman -Rs hblock; read -p 'Press enter to close'"
    fn.debug_print(f"Terminal cmd: {script}")
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

    def wait_and_refresh():
        process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_hblock_label, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_enable_hblock(self, _widget):
    """Run hblock to populate /etc/hosts with blocklists."""
    if not fn.check_package_installed("hblock"):
        fn.log_info("hblock is not installed")
        fn.show_in_app_notification(self, _("{name} is not installed — install it first").format(name="hblock"))
        return
    fn.log_subsection("Enable hblock")

    if not fn.path.exists("/etc/hosts-bak"):
        try:
            fn.shutil.copy2("/etc/hosts", "/etc/hosts-bak")
            fn.log_info("Backed up /etc/hosts → /etc/hosts-bak")
        except OSError as err:
            fn.log_warn(f"Could not back up /etc/hosts: {err}")

    def run_enable():
        stop_pulse = fn.threading.Event()

        def _pulse():
            while not stop_pulse.is_set():
                fn.GLib.idle_add(self.progress.pulse)
                fn.time.sleep(0.1)

        fn.GLib.idle_add(self.btn_enable_hblock.set_sensitive, False)
        fn.GLib.idle_add(self.btn_disable_hblock.set_sensitive, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_text, _("Enabling {name}...").format(name="hblock"))
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, True)
        fn.GLib.idle_add(self.progress.set_visible, True)
        fn.threading.Thread(target=_pulse, daemon=True).start()
        fn.subprocess.run(
            ["/usr/bin/hblock"],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        stop_pulse.set()
        fn.log_success("hblock enabled")
        fn.GLib.idle_add(self.progress.set_visible, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_text, _("{name} enabled").format(name="hblock"))
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, False)
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("{name} enabled").format(name="hblock"))
        fn.GLib.idle_add(
            self.lbl_hblock_status.set_markup,
            _("Enable or disable {name} — check /etc/hosts <b>enabled</b>").format(name="hblock"),
        )
        fn.GLib.idle_add(self.btn_enable_hblock.set_sensitive, True)
        fn.GLib.idle_add(self.btn_disable_hblock.set_sensitive, True)

    fn.threading.Thread(target=run_enable, daemon=True).start()


def on_click_disable_hblock(self, _widget):
    """Run hblock with empty sources to restore a clean /etc/hosts."""
    if not fn.check_package_installed("hblock"):
        fn.log_info("hblock is not installed")
        fn.show_in_app_notification(self, _("{name} is not installed").format(name="hblock"))
        return
    fn.log_subsection("Disable hblock")

    def run_disable():
        stop_pulse = fn.threading.Event()

        def _pulse():
            while not stop_pulse.is_set():
                fn.GLib.idle_add(self.progress.pulse)
                fn.time.sleep(0.1)

        fn.GLib.idle_add(self.btn_enable_hblock.set_sensitive, False)
        fn.GLib.idle_add(self.btn_disable_hblock.set_sensitive, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_text, _("Disabling {name}...").format(name="hblock"))
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, True)
        fn.GLib.idle_add(self.progress.set_visible, True)
        fn.threading.Thread(target=_pulse, daemon=True).start()
        fn.subprocess.run(
            ["sh", "-c", "HBLOCK_SOURCES='' /usr/bin/hblock"],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        stop_pulse.set()
        fn.log_success("hblock disabled")
        fn.GLib.idle_add(self.progress.set_visible, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_text, _("{name} disabled").format(name="hblock"))
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, False)
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("{name} disabled").format(name="hblock"))
        fn.GLib.idle_add(
            self.lbl_hblock_status.set_markup,
            _("Enable or disable {name} — check /etc/hosts disabled").format(name="hblock"),
        )
        fn.GLib.idle_add(self.btn_enable_hblock.set_sensitive, True)
        fn.GLib.idle_add(self.btn_disable_hblock.set_sensitive, True)

    fn.threading.Thread(target=run_disable, daemon=True).start()

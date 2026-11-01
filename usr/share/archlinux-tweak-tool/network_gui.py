# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
import services
from att_i18n import _


def _refresh(self, fn):
    if fn.check_package_installed("samba"):
        self.lbl_samba_install.set_markup(_("1. Install the samba server - <b>installed</b>"))
    else:
        self.lbl_samba_install.set_text(_("1. Install the samba server"))

    if fn.check_package_installed("avahi"):
        self.lbl_discovery.set_markup(_("Discover other computers in your network - <b>installed</b>"))
    else:
        self.lbl_discovery.set_text(_("Discover other computers in your network"))

    if hasattr(self, "btn_toggle_smb"):
        self.btn_toggle_smb.set_label(_("Disable Samba") if fn.check_service("smb") else _("Enable Samba"))

    if hasattr(self, "btn_fw_mdns"):
        self.btn_fw_mdns.set_label(
            _("Block network discovery (mDNS)") if fn.check_firewall_service("mdns")
            else _("Allow network discovery (mDNS)")
        )

    if hasattr(self, "btn_fw_samba"):
        self.btn_fw_samba.set_label(
            _("Block Samba file sharing") if fn.check_firewall_service("samba")
            else _("Allow Samba file sharing")
        )

    if hasattr(self, "lbl_firewall_status"):
        self.lbl_firewall_status.set_markup(fn.firewall_status_markup())

    if hasattr(self, "btn_firewall_config"):
        if fn.path.exists("/usr/bin/firewall-config"):
            self.lbl_firewall_config.set_markup(_("Graphical firewall editor (firewall-config) - <b>installed</b>"))
            self.btn_firewall_config.set_label(_("Launch firewall-config"))
        else:
            self.lbl_firewall_config.set_text(_("Graphical firewall editor (firewall-config)"))
            self.btn_firewall_config.set_label(_("Install firewall-config"))

    if hasattr(self, "network_status_label"):
        self.network_status_label.set_markup(_status_text(self, fn))


def _status_text(self, fn):
    def fmt(service_name):
        return _("<b>active</b>") if fn.check_service(service_name) else _("inactive")

    return _("Samba: {smb}   Nmb: {nmb}   Avahi: {avahi}   Firewall: {firewall}").format(
        smb=fmt("smb"), nmb=fmt("nmb"), avahi=fmt("avahi-daemon"), firewall=fmt("firewalld")
    )


def gui(self, Gtk, vboxstack_network, fn):
    """Create the network configuration GUI (Network / Samba / Firewall tabs)."""

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_title_label = Gtk.Label(xalign=0)
    hbox_title_label.set_text(_("Network"))
    hbox_title_label.set_name("title")
    hbox_title_label.set_margin_start(10)
    hbox_title_label.set_margin_end(10)
    hbox_title.append(hbox_title_label)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_sep.append(hseparator)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    # ── Pinned status summary (visible on every tab) ──────────────
    hbox_status_summary = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.network_status_label = Gtk.Label(xalign=0)
    self.network_status_label.set_markup(_status_text(self, fn))
    self.network_status_label.set_hexpand(True)
    self.network_status_label.set_margin_start(10)
    self.network_status_label.set_margin_end(10)
    hbox_status_summary.append(self.network_status_label)

    # ── Tab containers ────────────────────────────────────────────
    vboxstack_net = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_samba = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_fw = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    stack.set_transition_duration(350)
    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)

    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
    stack_switcher.set_stack(stack)

    # ══════════════════════════════════════════════════════════════
    # Network tab — discovery + name resolution
    # ══════════════════════════════════════════════════════════════

    hbox_section_discovery = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_section_discovery = Gtk.Label(xalign=0)
    label_section_discovery.set_markup(_("<b>Network Discovery</b>"))
    label_section_discovery.set_margin_start(10)
    label_section_discovery.set_margin_end(10)
    hbox_section_discovery.append(label_section_discovery)

    hbox_discovery_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    discovery_status_label = Gtk.Label(xalign=0)
    if fn.check_service("avahi-daemon"):
        discovery_status_label.set_markup(_("<b>✓ Network discovery installed</b>"))
    else:
        discovery_status_label.set_markup(_("✗ Network discovery not installed"))
    discovery_status_label.set_margin_start(10)
    discovery_status_label.set_margin_end(10)
    hbox_discovery_status.append(discovery_status_label)

    hbox_discovery = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.lbl_discovery = Gtk.Label(xalign=0)
    self.lbl_discovery.set_text(_("Discover other computers in your network"))
    button_install_discovery = Gtk.Button(label=_("Install network discovery"))
    button_install_discovery.connect("clicked", functools.partial(services.on_install_discovery_clicked, self))
    button_remove_discovery = Gtk.Button(label=_("Uninstall network discovery"))
    button_remove_discovery.connect("clicked", functools.partial(services.on_remove_discovery_clicked, self))
    self.lbl_discovery.set_margin_start(10)
    self.lbl_discovery.set_margin_end(10)
    self.lbl_discovery.set_hexpand(True)
    hbox_discovery.append(self.lbl_discovery)
    button_install_discovery.set_margin_start(10)
    button_install_discovery.set_margin_end(10)
    hbox_discovery.append(button_install_discovery)
    button_remove_discovery.set_margin_start(10)
    button_remove_discovery.set_margin_end(10)
    hbox_discovery.append(button_remove_discovery)

    hbox_section_resolution = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_section_resolution = Gtk.Label(xalign=0)
    label_section_resolution.set_markup(_("<b>Name Resolution</b>"))
    label_section_resolution.set_margin_start(10)
    label_section_resolution.set_margin_end(10)
    hbox_section_resolution.append(label_section_resolution)

    hbox_nsswitch_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_nsswitch_desc = Gtk.Label(xalign=0)
    label_nsswitch_desc.set_text(_("Select hosts: line for name resolution (connect to computers/NAS)"))
    label_nsswitch_desc.set_margin_start(10)
    label_nsswitch_desc.set_margin_end(10)
    hbox_nsswitch_desc.append(label_nsswitch_desc)

    hbox_nsswitch_dropdown = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.nsswitch_choices = Gtk.DropDown.new_from_strings(
        [
            _("Kiro default"),
            _("Standard (systemd default)"),
            _("With mdns + wins"),
            _("With mdns_minimal"),
            _("With mdns4_minimal"),
            _("Custom order (no systemd)"),
        ]
    )
    self.nsswitch_choices.set_selected(0)
    self.nsswitch_choices.set_margin_start(10)
    self.nsswitch_choices.set_margin_end(10)
    hbox_nsswitch_dropdown.append(self.nsswitch_choices)

    hbox_nsswitch_preview = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_nsswitch_preview = Gtk.Label(xalign=0)
    label_nsswitch_preview.set_margin_start(10)
    label_nsswitch_preview.set_margin_end(10)

    def _update_nsswitch_preview(*args):
        key = fn.get_combo_text(self.nsswitch_choices)
        hosts_line = services.NSSWITCH_OPTIONS.get(key, "")
        label_nsswitch_preview.set_markup(f"<tt>hosts: {hosts_line}</tt>")
        if args:
            fn.log_info(f"  Selected : {key}")
            fn.log_info(f"  hosts:   : {hosts_line}")

    _update_nsswitch_preview()
    self.nsswitch_choices.connect("notify::selected", _update_nsswitch_preview)
    hbox_nsswitch_preview.append(label_nsswitch_preview)

    hbox_nsswitch_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_apply_nsswitch = Gtk.Button(label=_("Apply selected nsswitch.conf"))
    button_apply_nsswitch.connect("clicked", functools.partial(services.on_click_apply_nsswitch, self))
    button_reset_nsswitch = Gtk.Button(label=_("Reset to your default nsswitch.conf"))
    button_reset_nsswitch.connect("clicked", functools.partial(services.on_click_reset_nsswitch, self))
    button_apply_nsswitch.set_margin_start(10)
    button_apply_nsswitch.set_margin_end(10)
    hbox_nsswitch_buttons.append(button_apply_nsswitch)
    button_reset_nsswitch.set_margin_start(10)
    button_reset_nsswitch.set_margin_end(10)
    hbox_nsswitch_buttons.append(button_reset_nsswitch)

    hbox_edit_nsswitch = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_edit_nsswitch = Gtk.Button(label=_("Edit the /etc/nsswitch.conf in terminal"))
    button_edit_nsswitch.connect("clicked", functools.partial(services.on_click_edit_nsswitch, self))
    button_edit_nsswitch.set_margin_start(10)
    button_edit_nsswitch.set_margin_end(10)
    hbox_edit_nsswitch.append(button_edit_nsswitch)

    for widget in (
        hbox_section_discovery,
        hbox_discovery_status,
        hbox_discovery,
        hbox_section_resolution,
        hbox_nsswitch_desc,
        hbox_nsswitch_dropdown,
        hbox_nsswitch_preview,
        hbox_nsswitch_buttons,
        hbox_edit_nsswitch,
    ):
        vboxstack_net.append(widget)

    # ══════════════════════════════════════════════════════════════
    # Samba tab — install, configure, password, service
    # ══════════════════════════════════════════════════════════════

    hbox_section_samba = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_section_samba = Gtk.Label(xalign=0)
    label_section_samba.set_markup(_("<b>Samba File Sharing</b>"))
    label_section_samba.set_margin_start(10)
    label_section_samba.set_margin_end(10)
    hbox_section_samba.append(label_section_samba)

    hbox_header_samba = Gtk.Label(xalign=0)
    hbox_header_samba.set_markup(
        _("You install a samba server if you need to \
share a folder and its contents in your home network\n\
The purpose is to create <b>one</b> shared folder - the current user can later \
access this folder from other computers\n\
We will create the folder 'Shared' in your home directory \
if it is not already there\n ")
    )
    hbox_header_samba.set_margin_start(10)
    hbox_header_samba.set_margin_end(10)

    hbox_samba_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.lbl_samba_install = Gtk.Label(xalign=0)
    self.lbl_samba_install.set_text(_("1. Install the samba server"))
    button_install_samba = Gtk.Button(label=_("Install Samba"))
    button_install_samba.connect("clicked", functools.partial(services.on_click_install_samba, self))
    button_uninstall_samba = Gtk.Button(label=_("Uninstall Samba"))
    button_uninstall_samba.connect("clicked", functools.partial(services.on_click_uninstall_samba, self))
    self.lbl_samba_install.set_margin_start(10)
    self.lbl_samba_install.set_margin_end(10)
    self.lbl_samba_install.set_hexpand(True)
    hbox_samba_install.append(self.lbl_samba_install)
    button_install_samba.set_margin_start(10)
    button_install_samba.set_margin_end(10)
    hbox_samba_install.append(button_install_samba)
    button_uninstall_samba.set_margin_start(10)
    button_uninstall_samba.set_margin_end(10)
    hbox_samba_install.append(button_uninstall_samba)

    hbox_samba_conf_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_samba_conf_desc = Gtk.Label(xalign=0)
    label_samba_conf_desc.set_text(_("2. Apply the configuration"))
    label_samba_conf_desc.set_margin_start(10)
    label_samba_conf_desc.set_margin_end(10)
    hbox_samba_conf_desc.append(label_samba_conf_desc)

    hbox_samba_conf_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_apply_samba = Gtk.Button(label=_("Apply default samba.conf"))
    button_apply_samba.connect("clicked", functools.partial(services.on_click_apply_samba, self))
    button_reset_samba = Gtk.Button(label=_("Reset to your default samba.conf"))
    button_reset_samba.connect("clicked", functools.partial(services.on_click_reset_samba, self))
    button_apply_samba.set_margin_start(10)
    button_apply_samba.set_margin_end(10)
    hbox_samba_conf_buttons.append(button_apply_samba)
    button_reset_samba.set_margin_start(10)
    button_reset_samba.set_margin_end(10)
    hbox_samba_conf_buttons.append(button_reset_samba)

    hbox_edit_samba = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_edit_samba = Gtk.Button(label=_("Edit samba.conf in terminal"))
    button_edit_samba.connect("clicked", functools.partial(services.on_click_edit_samba_nano, self))
    button_edit_samba.set_margin_start(10)
    button_edit_samba.set_margin_end(10)
    hbox_edit_samba.append(button_edit_samba)

    hbox_samba_password_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_samba_password_desc = Gtk.Label(xalign=0)
    label_samba_password_desc.set_text(
        _("3. Create a password for the current user to be able to access the Samba server")
    )
    label_samba_password_desc.set_margin_start(10)
    label_samba_password_desc.set_margin_end(10)
    hbox_samba_password_desc.append(label_samba_password_desc)

    hbox_samba_password_button = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_create_samba_user = Gtk.Button(label=_("Create a password for the current user (pop-up)"))
    button_create_samba_user.connect("clicked", functools.partial(services.on_click_create_samba_user, self))
    button_create_samba_user.set_margin_start(10)
    button_create_samba_user.set_margin_end(10)
    hbox_samba_password_button.append(button_create_samba_user)

    hbox_samba_service = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_samba_service = Gtk.Label(xalign=0)
    label_samba_service.set_text(_("4. Start the Samba service"))
    label_samba_service.set_hexpand(True)
    label_samba_service.set_margin_start(10)
    label_samba_service.set_margin_end(10)
    hbox_samba_service.append(label_samba_service)
    self.btn_toggle_smb = Gtk.Button(label=_("Disable Samba") if fn.check_service("smb") else _("Enable Samba"))
    self.btn_toggle_smb.connect("clicked", functools.partial(services.on_click_toggle_smb, self))
    self.btn_toggle_smb.set_margin_start(10)
    self.btn_toggle_smb.set_margin_end(10)
    hbox_samba_service.append(self.btn_toggle_smb)
    button_restart_smb = Gtk.Button(label=_("Restart Samba (smb + nmb)"))
    button_restart_smb.connect("clicked", functools.partial(services.on_click_restart_smb, self))
    button_restart_smb.set_margin_start(10)
    button_restart_smb.set_margin_end(10)
    hbox_samba_service.append(button_restart_smb)

    hbox_samba_reboot_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_samba_reboot_note = Gtk.Label(xalign=0)
    label_samba_reboot_note.set_markup(_("You can now reboot and enjoy the <b>'Shared'</b> folder"))
    label_samba_reboot_note.set_margin_start(10)
    label_samba_reboot_note.set_margin_end(10)
    hbox_samba_reboot_note.append(label_samba_reboot_note)

    for widget in (
        hbox_section_samba,
        hbox_header_samba,
        hbox_samba_install,
        hbox_samba_conf_desc,
        hbox_samba_conf_buttons,
        hbox_edit_samba,
        hbox_samba_password_desc,
        hbox_samba_password_button,
        hbox_samba_service,
        hbox_samba_reboot_note,
    ):
        vboxstack_samba.append(widget)

    # ══════════════════════════════════════════════════════════════
    # Firewall tab — firewalld + service toggles + help
    # ══════════════════════════════════════════════════════════════

    hbox_section_firewall = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label_section_firewall = Gtk.Label(xalign=0)
    label_section_firewall.set_markup(_("<b>Firewall</b>"))
    label_section_firewall.set_margin_start(10)
    label_section_firewall.set_margin_end(10)
    hbox_section_firewall.append(label_section_firewall)
    vboxstack_fw.append(hbox_section_firewall)

    if fn.check_package_installed("firewalld"):
        _fw_active = fn.check_service("firewalld")

        hbox_firewall_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_firewall_info = Gtk.Label(xalign=0)
        self.lbl_firewall_info.set_markup(
            _("Firewall (firewalld) is <b>active</b> — Kiro enables it by default to keep you protected.")
            if _fw_active
            else _("Firewall (firewalld) is <b>inactive</b>.")
        )
        self.lbl_firewall_info.set_margin_start(10)
        self.lbl_firewall_info.set_margin_end(10)
        hbox_firewall_info.append(self.lbl_firewall_info)

        hbox_firewall_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.btn_toggle_firewalld = Gtk.Button(label=_("Disable firewall") if _fw_active else _("Enable firewall"))
        self.btn_toggle_firewalld.connect("clicked", functools.partial(services.on_click_toggle_firewalld, self))
        self.btn_fw_mdns = Gtk.Button(
            label=_("Block network discovery (mDNS)") if fn.check_firewall_service("mdns")
            else _("Allow network discovery (mDNS)")
        )
        self.btn_fw_mdns.connect("clicked", functools.partial(services.on_click_firewall_toggle_mdns, self))
        self.btn_fw_samba = Gtk.Button(
            label=_("Block Samba file sharing") if fn.check_firewall_service("samba")
            else _("Allow Samba file sharing")
        )
        self.btn_fw_samba.connect("clicked", functools.partial(services.on_click_firewall_toggle_samba, self))
        self.btn_toggle_firewalld.set_margin_start(10)
        hbox_firewall_buttons.append(self.btn_toggle_firewalld)
        hbox_firewall_buttons.append(self.btn_fw_mdns)
        hbox_firewall_buttons.append(self.btn_fw_samba)

        hbox_firewall_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_firewall_status = Gtk.Label(xalign=0)
        self.lbl_firewall_status.set_markup(fn.firewall_status_markup())
        self.lbl_firewall_status.set_margin_start(10)
        self.lbl_firewall_status.set_margin_end(10)
        hbox_firewall_status.append(self.lbl_firewall_status)

        hbox_firewall_config = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_firewall_config = Gtk.Label(xalign=0)
        fwconfig_installed = fn.path.exists("/usr/bin/firewall-config")
        if fwconfig_installed:
            self.lbl_firewall_config.set_markup(_("Graphical firewall editor (firewall-config) - <b>installed</b>"))
        else:
            self.lbl_firewall_config.set_text(_("Graphical firewall editor (firewall-config)"))
        self.lbl_firewall_config.set_hexpand(True)
        self.lbl_firewall_config.set_margin_start(10)
        self.lbl_firewall_config.set_margin_end(10)
        self.btn_firewall_config = Gtk.Button(
            label=_("Launch firewall-config") if fwconfig_installed else _("Install firewall-config")
        )
        self.btn_firewall_config.connect("clicked", functools.partial(services.on_click_firewall_config, self))
        self.btn_firewall_config.set_margin_start(10)
        self.btn_firewall_config.set_margin_end(10)
        hbox_firewall_config.append(self.lbl_firewall_config)
        hbox_firewall_config.append(self.btn_firewall_config)

        hbox_firewall_help = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label_firewall_help = Gtk.Label(xalign=0)
        label_firewall_help.set_text(
            _("With the Avahi daemon (network discovery) running on both the server \
and client,\nthe file manager on the client should automatically find the server.\n\
Firewall: a server sharing files needs both 'Allow network discovery (mDNS)' and \
'Allow Samba file sharing'.\nA client only needs 'Allow network discovery (mDNS)' — \
it connects outward, so Samba does not need opening on the client.")
        )
        label_firewall_help.set_margin_start(10)
        label_firewall_help.set_margin_end(10)
        label_firewall_help.set_hexpand(True)
        hbox_firewall_help.append(label_firewall_help)

        for widget in (
            hbox_firewall_info,
            hbox_firewall_buttons,
            hbox_firewall_status,
            hbox_firewall_config,
            hbox_firewall_help,
        ):
            vboxstack_fw.append(widget)
    else:
        hbox_firewall_absent = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label_firewall_absent = Gtk.Label(xalign=0)
        label_firewall_absent.set_markup(_("firewalld is <b>not installed</b> — no firewall controls available."))
        label_firewall_absent.set_margin_start(10)
        label_firewall_absent.set_margin_end(10)
        hbox_firewall_absent.append(label_firewall_absent)
        vboxstack_fw.append(hbox_firewall_absent)

    # ── Pack tabs into the stack ──────────────────────────────────
    stack.add_titled(vboxstack_net, "stack_net", _("Network"))
    stack.add_titled(vboxstack_samba, "stack_samba", "Samba")
    stack.add_titled(vboxstack_fw, "stack_fw", _("Firewall"))

    hbox_status_summary.set_margin_start(10)
    vbox.append(hbox_status_summary)
    vbox.append(stack_switcher)
    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vbox.append(stack)

    vboxstack_network.append(hbox_title)
    vboxstack_network.append(hbox_sep)
    vbox.set_hexpand(True)
    vbox.set_vexpand(True)
    vboxstack_network.append(vbox)

    vboxstack_network.connect("map", lambda _w: _refresh(self, fn))
    _refresh(self, fn)

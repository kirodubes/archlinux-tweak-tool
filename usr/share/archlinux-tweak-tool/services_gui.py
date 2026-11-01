# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
import services
from att_i18n import _

from gi.repository import Gtk


def _refresh(self, fn):
    if fn.check_package_installed("cups"):
        self.cups_install_label.set_markup(_("Cups printing is <b>installed</b>"))
    else:
        self.cups_install_label.set_markup(_("Install cups printing"))

    if fn.check_package_installed("cups-pdf"):
        self.cups_pdf_label.set_markup(_("Cups-pdf is <b>installed</b>"))
    else:
        self.cups_pdf_label.set_markup(_("Install cups-pdf printing"))

    if fn.check_package_installed("foomatic-db"):
        self.printer_drivers_label.set_markup(
            _("   Install common printer drivers (foomatic, gutenprint, ...) - <b>Installed</b>")
        )
    else:
        self.printer_drivers_label.set_markup(_("   Install common printer drivers (foomatic, gutenprint, ...)"))

    if fn.check_package_installed("hplip"):
        self.hplip_label.set_markup(_("   HP drivers have been <b>installed</b>"))
    else:
        self.hplip_label.set_markup(_("   Install HP drivers"))

    if fn.check_package_installed("system-config-printer"):
        self.system_config_printer_label.set_markup(_("Install system-config-printer - <b>Installed</b>"))
    else:
        self.system_config_printer_label.set_markup(_("Install system-config-printer"))

    if fn.check_package_installed("bluez"):
        self.bluez_label.set_markup(_("Bluez packages are already <b>installed</b>"))
    else:
        self.bluez_label.set_markup(_("Install bluetooth packages"))

    if fn.check_package_installed("blueberry"):
        self.blueberry_label.set_markup(_("   Blueberry is already <b>installed</b>"))
    else:
        self.blueberry_label.set_markup(_("   Install blueberry"))

    if fn.check_package_installed("blueman"):
        self.blueman_label.set_markup(_("   Blueman is already <b>installed</b>"))
    else:
        self.blueman_label.set_markup(_("   Install blueman"))

    if fn.check_package_installed("bluedevil"):
        self.bluedevil_label.set_markup(_("   Bluedevil is already <b>installed</b>"))
    else:
        self.bluedevil_label.set_markup(_("   Install bluedevil (Plasma dependencies)"))

    if fn.check_package_installed("bluetooth-autoconnect"):
        self.bt_autoconnect_pkg_label.set_markup(_("   bluetooth-autoconnect is <b>installed</b> and enabled"))
    else:
        self.bt_autoconnect_pkg_label.set_markup(_("   Install bluetooth-autoconnect"))

    bluez_ok = fn.check_package_installed("bluez")
    self.enable_bt.set_sensitive(bluez_ok)
    self.disable_bt.set_sensitive(bluez_ok)
    self.restart_bt.set_sensitive(bluez_ok)

    _refresh_user_services(self, fn)


def gui(self, Gtk, vboxstack_services, fn):
    """Create the Services configuration GUI (printing, audio, bluetooth)."""
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_title_label = Gtk.Label(xalign=0)
    hbox_title_label.set_text(_("Services"))
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

    vboxstack_cups = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_audio = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_bluetooth = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_user_services = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    stack.set_transition_duration(350)
    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)

    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
    stack_switcher.set_stack(stack)

    # ── CUPS tab ─────────────────────────────────────────────────────

    hbox_cups_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_cups_desc_label = Gtk.Label(xalign=0)
    hbox_cups_desc_label.set_markup(
        _("Printing can be a challenge. We recommend reading the Arch wiki cups page. Check before you buy.\n\
There are also printer specific pages. Lastly the AUR might contain the driver you need.")
    )
    hbox_cups_desc.append(hbox_cups_desc_label)

    hbox_cups = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.cups_install_label = Gtk.Label(xalign=0)
    self.cups_install_label.set_markup(_("Install cups printing"))

    btn_install_cups = Gtk.Button(label=_("Install cups"))
    btn_install_cups.connect("clicked", functools.partial(services.on_click_install_cups, self))
    btn_remove_cups = Gtk.Button(label=_("Remove cups"))
    btn_remove_cups.connect("clicked", functools.partial(services.on_click_remove_cups, self))
    self.cups_install_label.set_margin_start(20)
    self.cups_install_label.set_margin_end(10)
    self.cups_install_label.set_hexpand(True)
    hbox_cups.append(self.cups_install_label)
    btn_install_cups.set_margin_start(10)
    btn_install_cups.set_margin_end(10)
    hbox_cups.append(btn_install_cups)
    btn_remove_cups.set_margin_start(10)
    btn_remove_cups.set_margin_end(10)
    hbox_cups.append(btn_remove_cups)

    hbox_cups_pdf = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.cups_pdf_label = Gtk.Label(xalign=0)
    self.cups_pdf_label.set_markup(_("Install cups-pdf printing"))
    btn_install_cups_pdf = Gtk.Button(label=_("Install cups-pdf"))
    btn_install_cups_pdf.connect("clicked", functools.partial(services.on_click_install_cups_pdf, self))
    btn_remove_cups_pdf = Gtk.Button(label=_("Remove cups-pdf"))
    btn_remove_cups_pdf.connect("clicked", functools.partial(services.on_click_remove_cups_pdf, self))
    self.cups_pdf_label.set_margin_start(20)
    self.cups_pdf_label.set_margin_end(10)
    self.cups_pdf_label.set_hexpand(True)
    hbox_cups_pdf.append(self.cups_pdf_label)
    btn_install_cups_pdf.set_margin_start(10)
    btn_install_cups_pdf.set_margin_end(10)
    hbox_cups_pdf.append(btn_install_cups_pdf)
    btn_remove_cups_pdf.set_margin_start(10)
    btn_remove_cups_pdf.set_margin_end(10)
    hbox_cups_pdf.append(btn_remove_cups_pdf)

    hbox_printer_drivers = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.printer_drivers_label = Gtk.Label(xalign=0)
    self.printer_drivers_label.set_markup(_("   Install common printer drivers (foomatic, gutenprint, ...)"))
    btn_install_printer_drivers = Gtk.Button(label=_("Install drivers"))
    btn_install_printer_drivers.connect("clicked", functools.partial(services.on_click_install_printer_drivers, self))
    btn_remove_printer_drivers = Gtk.Button(label=_("Remove drivers"))
    btn_remove_printer_drivers.connect("clicked", functools.partial(services.on_click_remove_printer_drivers, self))
    self.printer_drivers_label.set_margin_start(10)
    self.printer_drivers_label.set_margin_end(10)
    self.printer_drivers_label.set_hexpand(True)
    hbox_printer_drivers.append(self.printer_drivers_label)
    btn_install_printer_drivers.set_margin_start(10)
    btn_install_printer_drivers.set_margin_end(10)
    hbox_printer_drivers.append(btn_install_printer_drivers)
    btn_remove_printer_drivers.set_margin_start(10)
    btn_remove_printer_drivers.set_margin_end(10)
    hbox_printer_drivers.append(btn_remove_printer_drivers)

    hbox_hplip = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.hplip_label = Gtk.Label(xalign=0)
    self.hplip_label.set_markup(_("   Install HP drivers"))
    btn_install_hplip = Gtk.Button(label=_("Install hplip"))
    btn_install_hplip.connect("clicked", functools.partial(services.on_click_install_hplip, self))
    btn_remove_hplip = Gtk.Button(label=_("Uninstall hplip"))
    btn_remove_hplip.connect("clicked", functools.partial(services.on_click_remove_hplip, self))
    self.hplip_label.set_margin_start(10)
    self.hplip_label.set_margin_end(10)
    self.hplip_label.set_hexpand(True)
    hbox_hplip.append(self.hplip_label)
    btn_install_hplip.set_margin_start(10)
    btn_install_hplip.set_margin_end(10)
    hbox_hplip.append(btn_install_hplip)
    btn_remove_hplip.set_margin_start(10)
    btn_remove_hplip.set_margin_end(10)
    hbox_hplip.append(btn_remove_hplip)

    hbox_system_config_printer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.system_config_printer_label = Gtk.Label(xalign=0)
    self.system_config_printer_label.set_markup(_("Install system-config-printer"))
    btn_install_system_config_printer = Gtk.Button(label=_("Install system-config-printer"))
    btn_install_system_config_printer.connect(
        "clicked", functools.partial(services.on_click_install_system_config_printer, self)
    )
    btn_remove_system_config_printer = Gtk.Button(label=_("Remove system-config-printer"))
    btn_remove_system_config_printer.connect(
        "clicked", functools.partial(services.on_click_remove_system_config_printer, self)
    )
    self.system_config_printer_label.set_margin_start(10)
    self.system_config_printer_label.set_margin_end(10)
    self.system_config_printer_label.set_hexpand(True)
    hbox_system_config_printer.append(self.system_config_printer_label)
    btn_install_system_config_printer.set_margin_start(10)
    btn_install_system_config_printer.set_margin_end(10)
    hbox_system_config_printer.append(btn_install_system_config_printer)
    btn_remove_system_config_printer.set_margin_start(10)
    btn_remove_system_config_printer.set_margin_end(10)
    hbox_system_config_printer.append(btn_remove_system_config_printer)

    hbox_cups_service_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_cups_service_title_lbl = Gtk.Label(xalign=0)
    hbox_cups_service_title_lbl.set_markup(_("<b>CUPS Service</b>"))
    hbox_cups_service_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_cups_service_title_sep.set_hexpand(True)
    hbox_cups_service_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_cups_service_title.append(hbox_cups_service_title_lbl)
    hbox_cups_service_title.append(hbox_cups_service_title_sep)

    hbox_drivers_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_drivers_title_lbl = Gtk.Label(xalign=0)
    hbox_drivers_title_lbl.set_markup(_("<b>Printer Drivers</b>"))
    hbox_drivers_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_drivers_title_sep.set_hexpand(True)
    hbox_drivers_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_drivers_title.append(hbox_drivers_title_lbl)
    hbox_drivers_title.append(hbox_drivers_title_sep)

    hbox_tools_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_tools_title_lbl = Gtk.Label(xalign=0)
    hbox_tools_title_lbl.set_markup(_("<b>Tools</b>"))
    hbox_tools_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_tools_title_sep.set_hexpand(True)
    hbox_tools_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_tools_title.append(hbox_tools_title_lbl)
    hbox_tools_title.append(hbox_tools_title_sep)

    hbox_status_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_status_title_lbl = Gtk.Label(xalign=0)
    hbox_status_title_lbl.set_markup(_("<b>Status</b>"))
    hbox_status_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_status_title_sep.set_hexpand(True)
    hbox_status_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_status_title.append(hbox_status_title_lbl)
    hbox_status_title.append(hbox_status_title_sep)

    hbox_cups_service_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    enable_cups = Gtk.Button(label=_("Enable cups"))
    enable_cups.connect("clicked", functools.partial(services.on_click_enable_cups, self))
    disable_cups = Gtk.Button(label=_("Disable cups"))
    disable_cups.connect("clicked", functools.partial(services.on_click_disable_cups, self))
    restart_cups = Gtk.Button(label=_("Start/Restart cups"))
    restart_cups.connect("clicked", functools.partial(services.on_click_restart_cups, self))
    restart_cups.set_margin_start(10)
    restart_cups.set_margin_end(10)
    hbox_cups_service_buttons.append(restart_cups)
    enable_cups.set_margin_start(10)
    enable_cups.set_margin_end(10)
    hbox_cups_service_buttons.append(enable_cups)
    disable_cups.set_margin_start(10)
    disable_cups.set_margin_end(10)
    hbox_cups_service_buttons.append(disable_cups)

    hbox_cups_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.cups_status_label = Gtk.Label(xalign=0)

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

    self.cups_status_label.set_markup(
        _("Cups service : {service}   Cups socket : {socket}").format(service=status1, socket=status2)
    )
    self.cups_status_label.set_margin_start(10)
    self.cups_status_label.set_margin_end(10)
    hbox_cups_status.append(self.cups_status_label)

    # ── Audio control ────────────────────────────────────────────────

    hbox_audio_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_audio_desc_label = Gtk.Label(xalign=0)
    hbox_audio_desc_label.set_markup(
        _("You have two major choices: \n\
  - <b>Pulseaudio</b>\n\
  - <b>Pipewire</b>\n\
Reboot after installing pulseaudio or pipewire\n\
With an 'inxi -A' in a terminal you can see what sound server is running\n\
There are packages that conflict with each other.\n\
Report them if that is the case")
    )
    hbox_audio_desc_label.set_margin_start(0)
    hbox_audio_desc_label.set_margin_end(10)
    hbox_audio_desc.append(hbox_audio_desc_label)

    hbox_pulseaudio = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_pulseaudio_label = Gtk.Label(xalign=0)
    hbox_pulseaudio_label.set_markup(_("Install and switch to Pulseaudio"))
    btn_install_pulseaudio = Gtk.Button(label=_("Install and switch to Pulseaudio"))
    btn_install_pulseaudio.connect("clicked", functools.partial(services.on_click_switch_to_pulseaudio, self))
    hbox_pulseaudio_label.set_margin_start(10)
    hbox_pulseaudio_label.set_margin_end(10)
    hbox_pulseaudio_label.set_hexpand(True)
    hbox_pulseaudio.append(hbox_pulseaudio_label)
    btn_install_pulseaudio.set_margin_start(10)
    btn_install_pulseaudio.set_margin_end(10)
    hbox_pulseaudio.append(btn_install_pulseaudio)

    hbox_pipewire = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_pipewire_label = Gtk.Label(xalign=0)
    hbox_pipewire_label.set_markup(_("Install and switch to Pipewire"))
    btn_install_pipewire = Gtk.Button(label=_("Install and switch to Pipewire"))
    btn_install_pipewire.connect("clicked", functools.partial(services.on_click_switch_to_pipewire, self))
    hbox_pipewire_label.set_margin_start(10)
    hbox_pipewire_label.set_margin_end(10)
    hbox_pipewire_label.set_hexpand(True)
    hbox_pipewire.append(hbox_pipewire_label)
    btn_install_pipewire.set_margin_start(10)
    btn_install_pipewire.set_margin_end(10)
    hbox_pipewire.append(btn_install_pipewire)

    hbox_audio_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_audio_status_label = Gtk.Label(xalign=0.5)
    text1 = ""
    text2 = ""
    status1 = fn.check_if_process_is_running("pulseaudio")
    if status1 is True:
        text1 = _("<b>active</b>")
    else:
        text1 = _("inactive")

    status2 = fn.check_if_process_is_running("pipewire")
    if status2 is True:
        text2 = _("<b>active</b>")
    else:
        text2 = _("inactive")

    hbox_audio_status_label.set_markup(
        _("Pulseaudio service : {pulseaudio}   Pipewire service : {pipewire}").format(pulseaudio=text1, pipewire=text2)
    )
    hbox_audio_status_label.set_hexpand(True)
    hbox_audio_status_label.set_halign(Gtk.Align.CENTER)
    hbox_audio_status.append(hbox_audio_status_label)

    # ── Bluetooth control ────────────────────────────────────────────

    hbox_bt_packages_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bt_packages_title_lbl = Gtk.Label(xalign=0)
    hbox_bt_packages_title_lbl.set_markup(_("<b>Packages</b>"))
    hbox_bt_packages_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_bt_packages_title_sep.set_hexpand(True)
    hbox_bt_packages_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_bt_packages_title.append(hbox_bt_packages_title_lbl)
    hbox_bt_packages_title.append(hbox_bt_packages_title_sep)

    hbox_bt_tools_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bt_tools_title_lbl = Gtk.Label(xalign=0)
    hbox_bt_tools_title_lbl.set_markup(_("<b>Tools</b>"))
    hbox_bt_tools_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_bt_tools_title_sep.set_hexpand(True)
    hbox_bt_tools_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_bt_tools_title.append(hbox_bt_tools_title_lbl)
    hbox_bt_tools_title.append(hbox_bt_tools_title_sep)

    hbox_bt_autoconnect_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bt_autoconnect_title_lbl = Gtk.Label(xalign=0)
    hbox_bt_autoconnect_title_lbl.set_markup(_("<b>Auto-Connect</b>"))
    hbox_bt_autoconnect_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_bt_autoconnect_title_sep.set_hexpand(True)
    hbox_bt_autoconnect_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_bt_autoconnect_title.append(hbox_bt_autoconnect_title_lbl)
    hbox_bt_autoconnect_title.append(hbox_bt_autoconnect_title_sep)

    hbox_bt_autoconnect = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_bt_autoconnect = Gtk.Label(xalign=0)
    lbl_bt_autoconnect.set_text(_("Reconnect paired headsets at login (AutoEnable). Works with PipeWire and PulseAudio."))
    lbl_bt_autoconnect.set_hexpand(True)
    lbl_bt_autoconnect.set_margin_start(10)
    lbl_bt_autoconnect.set_margin_end(10)
    self.bt_autoconnect_switch = Gtk.Switch()
    self.bt_autoconnect_switch.set_valign(Gtk.Align.CENTER)
    self.bt_autoconnect_switch.set_margin_end(10)
    self.bt_autoconnect_initializing = True
    self.bt_autoconnect_switch.set_active(services.get_bluetooth_autoenable())
    self.bt_autoconnect_initializing = False
    self.bt_autoconnect_switch.connect("notify::active", functools.partial(services.on_bt_autoconnect_toggled, self))
    hbox_bt_autoconnect.append(lbl_bt_autoconnect)
    hbox_bt_autoconnect.append(self.bt_autoconnect_switch)

    hbox_bt_autoconnect_pkg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.bt_autoconnect_pkg_label = Gtk.Label(xalign=0)
    if fn.check_package_installed("bluetooth-autoconnect"):
        self.bt_autoconnect_pkg_label.set_markup(_("   bluetooth-autoconnect is <b>installed</b> and enabled"))
    else:
        self.bt_autoconnect_pkg_label.set_markup(_("   Install bluetooth-autoconnect"))
    self.bt_autoconnect_pkg_label.set_hexpand(True)
    self.bt_autoconnect_pkg_label.set_margin_start(10)
    self.bt_autoconnect_pkg_label.set_margin_end(10)
    btn_install_bt_autoconnect = Gtk.Button(label=_("Install"))
    btn_install_bt_autoconnect.connect("clicked", functools.partial(services.on_click_install_bt_autoconnect, self))
    btn_remove_bt_autoconnect = Gtk.Button(label=_("Remove"))
    btn_remove_bt_autoconnect.connect("clicked", functools.partial(services.on_click_remove_bt_autoconnect, self))
    btn_install_bt_autoconnect.set_margin_start(10)
    btn_install_bt_autoconnect.set_margin_end(10)
    btn_remove_bt_autoconnect.set_margin_start(10)
    btn_remove_bt_autoconnect.set_margin_end(10)
    hbox_bt_autoconnect_pkg.append(self.bt_autoconnect_pkg_label)
    hbox_bt_autoconnect_pkg.append(btn_install_bt_autoconnect)
    hbox_bt_autoconnect_pkg.append(btn_remove_bt_autoconnect)

    hbox_bt_service_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bt_service_title_lbl = Gtk.Label(xalign=0)
    hbox_bt_service_title_lbl.set_markup(_("<b>Status</b>"))
    hbox_bt_service_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_bt_service_title_sep.set_hexpand(True)
    hbox_bt_service_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_bt_service_title.append(hbox_bt_service_title_lbl)
    hbox_bt_service_title.append(hbox_bt_service_title_sep)

    hbox_bluetooth_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bluetooth_desc_label = Gtk.Label(xalign=0)
    hbox_bluetooth_desc_label.set_text(_("You can install all the bluetooth packages here and enable the service."))
    hbox_bluetooth_desc_label.set_margin_start(10)
    hbox_bluetooth_desc_label.set_margin_end(10)
    hbox_bluetooth_desc.append(hbox_bluetooth_desc_label)

    hbox_bluez = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.bluez_label = Gtk.Label(xalign=0)
    self.bluez_label.set_markup(_("Install bluetooth packages"))
    btn_install_bt = Gtk.Button(label=_("Install bluetooth"))
    btn_install_bt.connect("clicked", functools.partial(services.on_click_install_bluetooth, self))
    btn_remove_bt = Gtk.Button(label=_("Remove bluetooth"))
    btn_remove_bt.connect("clicked", functools.partial(services.on_click_remove_bluetooth, self))
    self.bluez_label.set_margin_start(10)
    self.bluez_label.set_margin_end(10)
    self.bluez_label.set_hexpand(True)
    hbox_bluez.append(self.bluez_label)
    btn_install_bt.set_margin_start(10)
    btn_install_bt.set_margin_end(10)
    hbox_bluez.append(btn_install_bt)
    btn_remove_bt.set_margin_start(10)
    btn_remove_bt.set_margin_end(10)
    hbox_bluez.append(btn_remove_bt)

    hbox_bluetooth_tools_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bluetooth_tools_desc_label = Gtk.Label(xalign=0)
    hbox_bluetooth_tools_desc_label.set_text(_("Choose one of these tools to connect to your bluetooth devices:"))
    hbox_bluetooth_tools_desc_label.set_margin_start(10)
    hbox_bluetooth_tools_desc_label.set_margin_end(10)
    hbox_bluetooth_tools_desc.append(hbox_bluetooth_tools_desc_label)

    hbox_blueberry = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.blueberry_label = Gtk.Label(xalign=0)
    self.blueberry_label.set_markup(_("   Install blueberry"))
    btn_install_blueberry = Gtk.Button(label=_("Install blueberry"))
    btn_install_blueberry.connect("clicked", functools.partial(services.on_click_install_blueberry, self))
    btn_remove_blueberry = Gtk.Button(label=_("Remove blueberry"))
    btn_remove_blueberry.connect("clicked", functools.partial(services.on_click_remove_blueberry, self))
    self.blueberry_label.set_margin_start(10)
    self.blueberry_label.set_margin_end(10)
    self.blueberry_label.set_hexpand(True)
    hbox_blueberry.append(self.blueberry_label)
    btn_install_blueberry.set_margin_start(10)
    btn_install_blueberry.set_margin_end(10)
    hbox_blueberry.append(btn_install_blueberry)
    btn_remove_blueberry.set_margin_start(10)
    btn_remove_blueberry.set_margin_end(10)
    hbox_blueberry.append(btn_remove_blueberry)

    hbox_blueman = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.blueman_label = Gtk.Label(xalign=0)
    self.blueman_label.set_markup(_("   Install blueman"))
    btn_install_blueman = Gtk.Button(label=_("Install blueman"))
    btn_install_blueman.connect("clicked", functools.partial(services.on_click_install_blueman, self))
    btn_remove_blueman = Gtk.Button(label=_("Remove blueman"))
    btn_remove_blueman.connect("clicked", functools.partial(services.on_click_remove_blueman, self))
    self.blueman_label.set_margin_start(10)
    self.blueman_label.set_margin_end(10)
    self.blueman_label.set_hexpand(True)
    hbox_blueman.append(self.blueman_label)
    btn_install_blueman.set_margin_start(10)
    btn_install_blueman.set_margin_end(10)
    hbox_blueman.append(btn_install_blueman)
    btn_remove_blueman.set_margin_start(10)
    btn_remove_blueman.set_margin_end(10)
    hbox_blueman.append(btn_remove_blueman)

    hbox_bluedevil = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.bluedevil_label = Gtk.Label(xalign=0)
    self.bluedevil_label.set_markup(_("   Install bluedevil (Plasma dependencies)"))
    btn_install_bluedevil = Gtk.Button(label=_("Install bluedevil"))
    btn_install_bluedevil.connect("clicked", functools.partial(services.on_click_install_bluedevil, self))
    btn_remove_bluedevil = Gtk.Button(label=_("Remove bluedevil"))
    btn_remove_bluedevil.connect("clicked", functools.partial(services.on_click_remove_bluedevil, self))
    self.bluedevil_label.set_margin_start(10)
    self.bluedevil_label.set_margin_end(10)
    self.bluedevil_label.set_hexpand(True)
    hbox_bluedevil.append(self.bluedevil_label)
    btn_install_bluedevil.set_margin_start(10)
    btn_install_bluedevil.set_margin_end(10)
    hbox_bluedevil.append(btn_install_bluedevil)
    btn_remove_bluedevil.set_margin_start(10)
    btn_remove_bluedevil.set_margin_end(10)
    hbox_bluedevil.append(btn_remove_bluedevil)

    hbox_bluetooth_service_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.enable_bt = Gtk.Button(label=_("Enable bluetooth"))
    self.enable_bt.connect("clicked", functools.partial(services.on_click_enable_bluetooth, self))
    self.disable_bt = Gtk.Button(label=_("Disable bluetooth"))
    self.disable_bt.connect("clicked", functools.partial(services.on_click_disable_bluetooth, self))
    self.restart_bt = Gtk.Button(label=_("Start/Restart bluetooth"))
    self.restart_bt.connect("clicked", functools.partial(services.on_click_restart_bluetooth, self))
    self.restart_bt.set_margin_start(10)
    self.restart_bt.set_margin_end(10)
    hbox_bluetooth_service_buttons.append(self.restart_bt)
    self.enable_bt.set_margin_start(10)
    self.enable_bt.set_margin_end(10)
    hbox_bluetooth_service_buttons.append(self.enable_bt)
    self.disable_bt.set_margin_start(10)
    self.disable_bt.set_margin_end(10)
    hbox_bluetooth_service_buttons.append(self.disable_bt)

    hbox_bluetooth_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bluetooth_status_label = Gtk.Label(xalign=0)

    status1 = fn.check_service("bluetooth")
    if status1 is True:
        status1 = _("<b>active</b>")
    else:
        status1 = _("inactive")

    hbox_bluetooth_status_label.set_markup(_("bluetooth service : {status}").format(status=status1))
    hbox_bluetooth_status_label.set_margin_start(10)
    hbox_bluetooth_status_label.set_margin_end(10)
    hbox_bluetooth_status.append(hbox_bluetooth_status_label)

    self.enable_bt.set_sensitive(False)
    self.disable_bt.set_sensitive(False)
    self.restart_bt.set_sensitive(False)

    # ── Stack assembly ───────────────────────────────────────────────

    # cups
    hbox_cups_desc.set_margin_start(10)
    hbox_cups_desc.set_margin_end(10)
    vboxstack_cups.append(hbox_cups_desc)
    hbox_cups_service_title.set_margin_start(10)
    hbox_cups_service_title.set_margin_end(10)
    vboxstack_cups.append(hbox_cups_service_title)
    vboxstack_cups.append(hbox_cups)
    vboxstack_cups.append(hbox_cups_pdf)
    hbox_drivers_title.set_margin_start(10)
    hbox_drivers_title.set_margin_end(10)
    vboxstack_cups.append(hbox_drivers_title)
    vboxstack_cups.append(hbox_printer_drivers)
    vboxstack_cups.append(hbox_hplip)
    hbox_tools_title.set_margin_start(10)
    hbox_tools_title.set_margin_end(10)
    vboxstack_cups.append(hbox_tools_title)
    hbox_system_config_printer.set_margin_start(10)
    hbox_system_config_printer.set_margin_end(10)
    vboxstack_cups.append(hbox_system_config_printer)
    hbox_cups_service_buttons.set_margin_start(10)
    hbox_cups_service_buttons.set_margin_end(10)
    vboxstack_cups.append(hbox_cups_service_buttons)
    hbox_status_title.set_margin_start(10)
    hbox_status_title.set_margin_end(10)
    hbox_status_title.set_margin_top(20)
    vboxstack_cups.append(hbox_status_title)
    hbox_cups_status.set_margin_start(10)
    hbox_cups_status.set_margin_end(10)
    vboxstack_cups.append(hbox_cups_status)

    # audio
    hbox_audio_desc.set_margin_start(10)
    hbox_audio_desc.set_margin_end(10)
    vboxstack_audio.append(hbox_audio_desc)
    vboxstack_audio.append(hbox_pulseaudio)
    vboxstack_audio.append(hbox_pipewire)
    hbox_audio_status.set_margin_top(40)
    vboxstack_audio.append(hbox_audio_status)

    # bluetooth
    hbox_bt_packages_title.set_margin_start(10)
    hbox_bt_packages_title.set_margin_end(10)
    vboxstack_bluetooth.append(hbox_bt_packages_title)
    vboxstack_bluetooth.append(hbox_bluetooth_desc)
    vboxstack_bluetooth.append(hbox_bluez)
    hbox_bt_tools_title.set_margin_start(10)
    hbox_bt_tools_title.set_margin_end(10)
    vboxstack_bluetooth.append(hbox_bt_tools_title)
    vboxstack_bluetooth.append(hbox_bluetooth_tools_desc)
    vboxstack_bluetooth.append(hbox_blueberry)
    vboxstack_bluetooth.append(hbox_blueman)
    vboxstack_bluetooth.append(hbox_bluedevil)
    hbox_bt_autoconnect_title.set_margin_start(10)
    hbox_bt_autoconnect_title.set_margin_end(10)
    hbox_bt_autoconnect_title.set_margin_top(10)
    vboxstack_bluetooth.append(hbox_bt_autoconnect_title)
    hbox_bt_autoconnect.set_margin_start(10)
    hbox_bt_autoconnect.set_margin_end(10)
    vboxstack_bluetooth.append(hbox_bt_autoconnect)
    hbox_bt_autoconnect_pkg.set_margin_start(10)
    hbox_bt_autoconnect_pkg.set_margin_end(10)
    vboxstack_bluetooth.append(hbox_bt_autoconnect_pkg)

    hbox_bt_service_title.set_margin_start(10)
    hbox_bt_service_title.set_margin_end(10)
    hbox_bt_service_title.set_margin_top(10)
    vboxstack_bluetooth.append(hbox_bt_service_title)
    hbox_bluetooth_status.set_margin_start(10)
    hbox_bluetooth_status.set_margin_end(10)
    vboxstack_bluetooth.append(hbox_bluetooth_status)
    hbox_bluetooth_service_buttons.set_margin_start(10)
    hbox_bluetooth_service_buttons.set_margin_end(10)
    vboxstack_bluetooth.append(hbox_bluetooth_service_buttons)

    # ── User Services tab ────────────────────────────────────────────
    hbox_user_services_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_user_services_title_lbl = Gtk.Label(xalign=0)
    hbox_user_services_title_lbl.set_markup(_("<b>User Services</b>"))
    hbox_user_services_title.append(hbox_user_services_title_lbl)
    hbox_user_services_title.set_margin_start(10)
    hbox_user_services_title.set_margin_end(10)
    hbox_user_services_title.set_margin_top(10)
    vboxstack_user_services.append(hbox_user_services_title)

    hbox_user_services_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_user_services_desc_lbl = Gtk.Label(xalign=0)
    hbox_user_services_desc_lbl.set_markup(
        _("Active services in your <b>--user</b> session (read-only). Custom units you added are flagged.")
    )
    hbox_user_services_desc.append(hbox_user_services_desc_lbl)
    hbox_user_services_desc.set_margin_start(10)
    hbox_user_services_desc.set_margin_end(10)
    vboxstack_user_services.append(hbox_user_services_desc)

    hbox_user_services_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.user_services_count_label = Gtk.Label(xalign=0)
    self.user_services_count_label.set_hexpand(True)
    btn_user_services_refresh = Gtk.Button(label=_("Refresh"))
    btn_user_services_refresh.connect("clicked", functools.partial(_on_refresh_user_services, self, fn))
    hbox_user_services_controls.append(self.user_services_count_label)
    hbox_user_services_controls.append(btn_user_services_refresh)
    hbox_user_services_controls.set_margin_start(10)
    hbox_user_services_controls.set_margin_end(10)
    hbox_user_services_controls.set_margin_top(6)
    vboxstack_user_services.append(hbox_user_services_controls)

    user_services_scrolled = Gtk.ScrolledWindow()
    user_services_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    user_services_scrolled.set_hexpand(True)
    user_services_scrolled.set_vexpand(True)
    user_services_scrolled.set_margin_start(10)
    user_services_scrolled.set_margin_end(10)
    user_services_scrolled.set_margin_top(6)
    user_services_scrolled.set_margin_bottom(10)
    self.user_services_listbox = Gtk.ListBox()
    self.user_services_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
    user_services_scrolled.set_child(self.user_services_listbox)
    vboxstack_user_services.append(user_services_scrolled)

    # ── Pack to stack ────────────────────────────────────────────────
    stack.add_titled(vboxstack_audio, "stack4", _("Audio"))
    stack.add_titled(vboxstack_bluetooth, "stack5", _("Bluetooth"))
    stack.add_titled(vboxstack_cups, "stack3", _("Printing"))
    stack.add_titled(vboxstack_user_services, "stack6", _("User Services"))

    vbox.append(stack_switcher)
    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vbox.append(stack)

    vboxstack_services.append(hbox_title)
    vboxstack_services.append(hbox_sep)
    vbox.set_hexpand(True)
    vbox.set_vexpand(True)
    vboxstack_services.append(vbox)

    vboxstack_services.connect("map", lambda _w: _refresh(self, fn))
    _refresh(self, fn)


def _on_refresh_user_services(self, fn, _widget):
    _refresh_user_services(self, fn)


def _refresh_user_services(self, fn):
    """Fetch user services off the UI thread, then repopulate the list."""

    def worker():
        services_list = services.get_user_services()
        fn.GLib.idle_add(_populate_user_services, self, fn, services_list)

    fn.threading.Thread(target=worker, daemon=True).start()


def _populate_user_services(self, fn, services_list):
    child = self.user_services_listbox.get_first_child()
    while child is not None:
        nxt = child.get_next_sibling()
        self.user_services_listbox.remove(child)
        child = nxt

    custom = sum(1 for svc in services_list if svc["custom"])
    self.user_services_count_label.set_markup(
        _("<b>{count}</b> active user services  ·  <b>{custom}</b> custom").format(
            count=len(services_list), custom=custom
        )
    )
    for svc in services_list:
        self.user_services_listbox.append(_build_user_service_row(fn, svc))
    return False


def _build_user_service_row(fn, svc):
    row = Gtk.ListBoxRow()
    row.set_selectable(False)
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    hbox.set_margin_start(8)
    hbox.set_margin_end(8)
    hbox.set_margin_top(4)
    hbox.set_margin_bottom(4)

    name = fn.GLib.markup_escape_text(svc["id"])
    name_label = Gtk.Label(xalign=0)
    if svc["custom"]:
        name_label.set_markup(
            _("<b>{name}</b>  <span foreground='#4e9a06'>● custom</span>").format(name=name)
        )
    else:
        name_label.set_markup(name)
    name_label.set_size_request(320, -1)

    desc_label = Gtk.Label(xalign=0)
    desc_label.set_markup(f"<span foreground='#888888'>{fn.GLib.markup_escape_text(svc['description'])}</span>")
    desc_label.set_hexpand(True)

    state_label = Gtk.Label(xalign=1)
    state_label.set_markup(
        f"{fn.GLib.markup_escape_text(svc['sub'])} · {fn.GLib.markup_escape_text(svc['enabled'])}"
    )

    hbox.append(name_label)
    hbox.append(desc_label)
    hbox.append(state_label)
    row.set_child(hbox)
    return row

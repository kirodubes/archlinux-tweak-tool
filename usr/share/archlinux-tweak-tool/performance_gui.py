# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
from att_i18n import _


def _refresh(self, fn):
    def _do():
        irq_ok = fn.check_package_installed("irqbalance")
        ananicy_ok = fn.check_package_installed("ananicy-cpp")
        rules_ok = fn.check_package_installed("cachyos-ananicy-rules-git")
        gm_ok = fn.check_package_installed("gamemode")
        pl_ok = fn.check_package_installed("preload")
        fn.GLib.idle_add(_apply, irq_ok, ananicy_ok, rules_ok, gm_ok, pl_ok)

    def _apply(irq_ok, ananicy_ok, rules_ok, gm_ok, pl_ok):
        if irq_ok:
            self.irqbalance_package_label.set_markup(_("irqbalance package is <b>installed</b>"))
        else:
            self.irqbalance_package_label.set_text(_("Install irqbalance"))
        self.enable_irqbalance.set_sensitive(irq_ok)
        self.disable_irqbalance.set_sensitive(irq_ok)

        if ananicy_ok and rules_ok:
            self.ananicy_package_label.set_markup(_("ananicy-cpp and cachyos-ananicy-rules-git are <b>installed</b>"))
        elif ananicy_ok:
            self.ananicy_package_label.set_markup(
                _("ananicy-cpp is <b>installed</b> (cachyos-ananicy-rules-git not installed)")
            )
        else:
            self.ananicy_package_label.set_text(_("Install ananicy-cpp and cachyos-ananicy-rules-git"))
        self.enable_ananicy.set_sensitive(ananicy_ok)
        self.disable_ananicy.set_sensitive(ananicy_ok)

        if gm_ok:
            self.gamemode_package_label.set_markup(_("gamemode package is <b>installed</b>"))
        else:
            self.gamemode_package_label.set_text(_("Install gamemode"))
        self.enable_gamemode.set_sensitive(gm_ok)
        self.disable_gamemode.set_sensitive(gm_ok)

        if pl_ok:
            self.preload_package_label.set_markup(_("preload package is <b>installed</b>"))
        else:
            self.preload_package_label.set_text(_("Install preload"))
        self.enable_preload.set_sensitive(pl_ok)
        self.disable_preload.set_sensitive(pl_ok)

    fn.threading.Thread(target=_do, daemon=True).start()


def gui(self, Gtk, vboxstack_performance, performance, fn):
    """Create the performance configuration GUI."""
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_title_label = Gtk.Label(xalign=0)
    hbox_title_label.set_text(_("Performance"))
    hbox_title_label.set_name("title")
    hbox_title_label.set_margin_start(10)
    hbox_title_label.set_margin_end(10)
    hbox_title.append(hbox_title_label)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_sep.append(hseparator)

    # ── Sub-tab infrastructure (Build / Tuning / Storage & Memory) ─────────
    vbox_stack_holder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    vboxstack_build = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_power = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_responsiveness = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_storage = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    stack.set_transition_duration(350)
    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)

    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
    stack_switcher.set_stack(stack)

    # ── Tuned ──────────────────────────────────────────────────────────────

    hbox_sep_tuned = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator_tuned = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator_tuned.set_hexpand(True)
    hbox_sep_tuned.append(hseparator_tuned)

    hbox_tuned_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_tuned_title_label = Gtk.Label(xalign=0)
    hbox_tuned_title_label.set_markup(_("<b>Tuned</b>"))
    hbox_tuned_title_label.set_margin_start(10)
    hbox_tuned_title_label.set_margin_end(10)
    hbox_tuned_title.append(hbox_tuned_title_label)

    hbox_tuned_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_tuned_desc_label = Gtk.Label(xalign=0)
    hbox_tuned_desc_label.set_markup(
        _("<b>Tuned</b> - Dynamic system tuning for power management\n"
        "<b>Tuned-PPD</b> - Power Profiles Daemon integration for desktop environments\n"
        "If <b>TLP</b> is installed, it will be disabled when Tuned is enabled (they conflict).\n"
        "If <b>power-profiles-daemon</b> is installed, it will be removed before installing Tuned-PPD (they conflict).")
    )
    hbox_tuned_desc_label.set_margin_start(10)
    hbox_tuned_desc_label.set_margin_end(10)
    hbox_tuned_desc.append(hbox_tuned_desc_label)

    # ── tuned: package row ─────────────────────────────────────────────────
    hbox_tuned_pkg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.tuned_package_label = Gtk.Label(xalign=0)
    self.tuned_package_label.set_text(_("tuned is not installed"))
    self.tuned_package_label.set_margin_start(10)
    self.tuned_package_label.set_margin_end(10)
    self.tuned_package_label.set_hexpand(True)
    hbox_tuned_pkg.append(self.tuned_package_label)
    self.btn_install_tuned = Gtk.Button(label=_("Install tuned"))
    self.btn_install_tuned.connect("clicked", functools.partial(performance.install_tuned, self))
    self.btn_install_tuned.set_margin_start(10)
    self.btn_install_tuned.set_margin_end(10)
    hbox_tuned_pkg.append(self.btn_install_tuned)
    self.btn_remove_tuned = Gtk.Button(label=_("Remove tuned"))
    self.btn_remove_tuned.connect("clicked", functools.partial(performance.remove_tuned, self))
    self.btn_remove_tuned.set_margin_start(10)
    self.btn_remove_tuned.set_margin_end(10)
    hbox_tuned_pkg.append(self.btn_remove_tuned)

    # ── tuned: service row ─────────────────────────────────────────────────
    hbox_tuned_service = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.tuned_status_label = Gtk.Label(xalign=0)
    self.tuned_status_label.set_markup(_("tuned service : …"))
    self.tuned_status_label.set_margin_start(10)
    self.tuned_status_label.set_margin_end(10)
    self.tuned_status_label.set_hexpand(True)
    hbox_tuned_service.append(self.tuned_status_label)
    self.enable_tuned = Gtk.Button(label=_("Enable tuned"))
    self.enable_tuned.connect("clicked", functools.partial(performance.enable_tuned, self))
    self.enable_tuned.set_margin_start(10)
    self.enable_tuned.set_margin_end(10)
    hbox_tuned_service.append(self.enable_tuned)
    self.disable_tuned = Gtk.Button(label=_("Disable tuned"))
    self.disable_tuned.connect("clicked", functools.partial(performance.disable_tuned, self))
    self.disable_tuned.set_margin_start(10)
    self.disable_tuned.set_margin_end(10)
    hbox_tuned_service.append(self.disable_tuned)
    self.restart_tuned = Gtk.Button(label=_("Restart tuned"))
    self.restart_tuned.connect("clicked", functools.partial(performance.restart_tuned_service, self))
    self.restart_tuned.set_margin_start(10)
    self.restart_tuned.set_margin_end(10)
    hbox_tuned_service.append(self.restart_tuned)

    # ── tuned-ppd: package row ─────────────────────────────────────────────
    hbox_tuned_ppd_pkg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.tuned_ppd_package_label = Gtk.Label(xalign=0)
    self.tuned_ppd_package_label.set_text(_("tuned-ppd is not installed"))
    self.tuned_ppd_package_label.set_margin_start(10)
    self.tuned_ppd_package_label.set_margin_end(10)
    self.tuned_ppd_package_label.set_hexpand(True)
    hbox_tuned_ppd_pkg.append(self.tuned_ppd_package_label)
    self.btn_install_tuned_ppd = Gtk.Button(label=_("Install tuned-ppd"))
    self.btn_install_tuned_ppd.connect("clicked", functools.partial(performance.install_tuned_ppd, self))
    self.btn_install_tuned_ppd.set_margin_start(10)
    self.btn_install_tuned_ppd.set_margin_end(10)
    hbox_tuned_ppd_pkg.append(self.btn_install_tuned_ppd)
    self.btn_remove_tuned_ppd = Gtk.Button(label=_("Remove tuned-ppd"))
    self.btn_remove_tuned_ppd.connect("clicked", functools.partial(performance.remove_tuned_ppd, self))
    self.btn_remove_tuned_ppd.set_margin_start(10)
    self.btn_remove_tuned_ppd.set_margin_end(10)
    hbox_tuned_ppd_pkg.append(self.btn_remove_tuned_ppd)

    # ── tuned-ppd: service row ─────────────────────────────────────────────
    hbox_tuned_ppd_service = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.tuned_ppd_status_label = Gtk.Label(xalign=0)
    self.tuned_ppd_status_label.set_markup(_("tuned-ppd service : …"))
    self.tuned_ppd_status_label.set_margin_start(10)
    self.tuned_ppd_status_label.set_margin_end(10)
    self.tuned_ppd_status_label.set_hexpand(True)
    hbox_tuned_ppd_service.append(self.tuned_ppd_status_label)
    self.enable_tuned_ppd = Gtk.Button(label=_("Enable tuned-ppd"))
    self.enable_tuned_ppd.connect("clicked", functools.partial(performance.enable_tuned_ppd, self))
    self.enable_tuned_ppd.set_margin_start(10)
    self.enable_tuned_ppd.set_margin_end(10)
    hbox_tuned_ppd_service.append(self.enable_tuned_ppd)
    self.disable_tuned_ppd = Gtk.Button(label=_("Disable tuned-ppd"))
    self.disable_tuned_ppd.connect("clicked", functools.partial(performance.disable_tuned_ppd, self))
    self.disable_tuned_ppd.set_margin_start(10)
    self.disable_tuned_ppd.set_margin_end(10)
    hbox_tuned_ppd_service.append(self.disable_tuned_ppd)
    self.restart_tuned_ppd = Gtk.Button(label=_("Restart tuned-ppd"))
    self.restart_tuned_ppd.connect("clicked", functools.partial(performance.restart_tuned_ppd_service, self))
    self.restart_tuned_ppd.set_margin_start(10)
    self.restart_tuned_ppd.set_margin_end(10)
    hbox_tuned_ppd_service.append(self.restart_tuned_ppd)

    hbox_tuned_profile_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.tuned_profile_status_label = Gtk.Label(xalign=0)
    self.tuned_profile_status_label.set_markup(_("Active tuned profile : …"))
    self.tuned_profile_status_label.set_margin_start(10)
    self.tuned_profile_status_label.set_margin_end(10)
    self.tuned_profile_status_label.set_hexpand(True)
    hbox_tuned_profile_status.append(self.tuned_profile_status_label)

    hbox_tuned_profile_select = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.tuned_profile_choices = Gtk.DropDown.new_from_strings([])
    self.btn_apply_tuned_profile = Gtk.Button(label=_("Apply Profile"))
    self.btn_apply_tuned_profile.connect("clicked", functools.partial(performance.apply_tuned_profile, self))
    hbox_tuned_profile_select_label = Gtk.Label(xalign=0)
    hbox_tuned_profile_select_label.set_text(_("Select profile:"))
    hbox_tuned_profile_select_label.set_margin_start(10)
    hbox_tuned_profile_select_label.set_margin_end(10)
    hbox_tuned_profile_select.append(hbox_tuned_profile_select_label)
    self.tuned_profile_choices.set_margin_start(10)
    self.tuned_profile_choices.set_margin_end(10)
    hbox_tuned_profile_select.append(self.tuned_profile_choices)
    self.btn_apply_tuned_profile.set_margin_start(10)
    self.btn_apply_tuned_profile.set_margin_end(10)
    hbox_tuned_profile_select.append(self.btn_apply_tuned_profile)

    self.enable_tuned.set_sensitive(False)
    self.disable_tuned.set_sensitive(False)
    self.restart_tuned.set_sensitive(False)
    self.enable_tuned_ppd.set_sensitive(False)
    self.disable_tuned_ppd.set_sensitive(False)
    self.restart_tuned_ppd.set_sensitive(False)
    self.tuned_profile_choices.set_sensitive(False)
    self.btn_apply_tuned_profile.set_sensitive(False)

    # ── Swap management ────────────────────────────────────────────────────

    hbox_sep_swap = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator_zram = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator_zram.set_hexpand(True)
    hbox_sep_swap.append(hseparator_zram)

    hbox_swap_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_swap_title_label = Gtk.Label(xalign=0)
    hbox_swap_title_label.set_markup(_("<b>Swap Management</b>"))
    hbox_swap_title_label.set_margin_start(10)
    hbox_swap_title_label.set_margin_end(10)
    hbox_swap_title.append(hbox_swap_title_label)

    hbox_swapfile = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.swapfile_label = Gtk.Label(xalign=0)
    self.swapfile_label.set_text(_("Create or manage a swapfile at /swapfile"))
    self.swapfile_label.set_margin_start(10)
    self.swapfile_label.set_margin_end(10)
    self.swapfile_label.set_hexpand(True)
    self.swapfile_size = Gtk.DropDown.new_from_strings(["1G", "2G", "4G", "8G", "16G", "32G"])
    self.swapfile_size.set_selected(1)
    btn_create_swapfile = Gtk.Button(label=_("Create"))
    btn_create_swapfile.connect("clicked", functools.partial(performance.create_swapfile, self))
    btn_remove_swapfile = Gtk.Button(label=_("Remove"))
    btn_remove_swapfile.connect("clicked", functools.partial(performance.remove_swapfile, self))
    hbox_swapfile.append(self.swapfile_label)
    self.swapfile_size.set_margin_start(10)
    self.swapfile_size.set_margin_end(10)
    hbox_swapfile.append(self.swapfile_size)
    btn_create_swapfile.set_margin_start(10)
    btn_create_swapfile.set_margin_end(10)
    hbox_swapfile.append(btn_create_swapfile)
    btn_remove_swapfile.set_margin_start(10)
    btn_remove_swapfile.set_margin_end(10)
    hbox_swapfile.append(btn_remove_swapfile)

    hbox_zram = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.zram_status_label = Gtk.Label(xalign=0)
    self.zram_status_label.set_markup(_("zram : …"))
    self.zram_status_label.set_margin_start(10)
    self.zram_status_label.set_margin_end(10)
    self.zram_status_label.set_hexpand(True)
    self.zram_size = Gtk.DropDown.new_from_strings(["ram / 4", "ram / 2", "ram * 3 / 4", "ram", "1024", "2048", "4096"])
    self.zram_size.set_selected(1)
    btn_enable_zram = Gtk.Button(label=_("Enable"))
    btn_enable_zram.connect("clicked", functools.partial(performance.enable_zram, self))
    btn_disable_zram = Gtk.Button(label=_("Disable"))
    btn_disable_zram.connect("clicked", functools.partial(performance.disable_zram, self))
    hbox_zram.append(self.zram_status_label)
    self.zram_size.set_margin_start(10)
    self.zram_size.set_margin_end(10)
    hbox_zram.append(self.zram_size)
    btn_enable_zram.set_margin_start(10)
    btn_enable_zram.set_margin_end(10)
    hbox_zram.append(btn_enable_zram)
    btn_disable_zram.set_margin_start(10)
    btn_disable_zram.set_margin_end(10)
    hbox_zram.append(btn_disable_zram)

    # ── SSD/NVMe TRIM ──────────────────────────────────────────────────────

    hbox_sep_fstrim = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator_fstrim = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator_fstrim.set_hexpand(True)
    hbox_sep_fstrim.append(hseparator_fstrim)

    hbox_fstrim_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fstrim_title_label = Gtk.Label(xalign=0)
    hbox_fstrim_title_label.set_markup(_("<b>SSD/NVMe TRIM</b>"))
    hbox_fstrim_title_label.set_margin_start(10)
    hbox_fstrim_title_label.set_margin_end(10)
    hbox_fstrim_title.append(hbox_fstrim_title_label)

    hbox_fstrim = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.fstrim_status_label = Gtk.Label(xalign=0)
    self.fstrim_status_label.set_markup(_("fstrim.timer : …"))
    self.fstrim_status_label.set_margin_start(10)
    self.fstrim_status_label.set_margin_end(10)
    self.fstrim_status_label.set_hexpand(True)
    btn_enable_fstrim = Gtk.Button(label=_("Enable fstrim.timer"))
    btn_enable_fstrim.connect("clicked", functools.partial(performance.enable_fstrim_timer, self))
    btn_disable_fstrim = Gtk.Button(label=_("Disable"))
    btn_disable_fstrim.connect("clicked", functools.partial(performance.disable_fstrim_timer, self))
    hbox_fstrim.append(self.fstrim_status_label)
    btn_enable_fstrim.set_margin_start(10)
    btn_enable_fstrim.set_margin_end(10)
    hbox_fstrim.append(btn_enable_fstrim)
    btn_disable_fstrim.set_margin_start(10)
    btn_disable_fstrim.set_margin_end(10)
    hbox_fstrim.append(btn_disable_fstrim)

    # ── IRQ balancing ──────────────────────────────────────────────────────

    hbox_sep_irqbalance = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator_irqbalance = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator_irqbalance.set_hexpand(True)
    hbox_sep_irqbalance.append(hseparator_irqbalance)

    hbox_irqbalance_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_irqbalance_title_label = Gtk.Label(xalign=0)
    hbox_irqbalance_title_label.set_markup(_("<b>IRQ Balancing</b>"))
    hbox_irqbalance_title_label.set_margin_start(10)
    hbox_irqbalance_title_label.set_margin_end(10)
    hbox_irqbalance_title.append(hbox_irqbalance_title_label)

    hbox_irqbalance_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.irqbalance_package_label = Gtk.Label(xalign=0)
    self.irqbalance_package_label.set_text(_("Install irqbalance"))
    btn_install_irqbalance = Gtk.Button(label=_("Install irqbalance"))
    btn_install_irqbalance.connect("clicked", functools.partial(performance.install_irqbalance, self))
    btn_remove_irqbalance = Gtk.Button(label=_("Remove irqbalance"))
    btn_remove_irqbalance.connect("clicked", functools.partial(performance.remove_irqbalance, self))
    self.irqbalance_package_label.set_margin_start(10)
    self.irqbalance_package_label.set_margin_end(10)
    self.irqbalance_package_label.set_hexpand(True)
    hbox_irqbalance_install.append(self.irqbalance_package_label)
    btn_install_irqbalance.set_margin_start(10)
    btn_install_irqbalance.set_margin_end(10)
    hbox_irqbalance_install.append(btn_install_irqbalance)
    btn_remove_irqbalance.set_margin_start(10)
    btn_remove_irqbalance.set_margin_end(10)
    hbox_irqbalance_install.append(btn_remove_irqbalance)

    hbox_irqbalance_service = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.irqbalance_status_label = Gtk.Label(xalign=0)
    self.irqbalance_status_label.set_markup(_("irqbalance service : …"))
    self.irqbalance_status_label.set_margin_start(10)
    self.irqbalance_status_label.set_margin_end(10)
    self.irqbalance_status_label.set_hexpand(True)
    self.enable_irqbalance = Gtk.Button(label=_("Enable irqbalance"))
    self.enable_irqbalance.connect("clicked", functools.partial(performance.enable_irqbalance_service, self))
    self.disable_irqbalance = Gtk.Button(label=_("Disable irqbalance"))
    self.disable_irqbalance.connect("clicked", functools.partial(performance.disable_irqbalance_service, self))
    hbox_irqbalance_service.append(self.irqbalance_status_label)
    self.enable_irqbalance.set_margin_start(10)
    self.enable_irqbalance.set_margin_end(10)
    hbox_irqbalance_service.append(self.enable_irqbalance)
    self.disable_irqbalance.set_margin_start(10)
    self.disable_irqbalance.set_margin_end(10)
    hbox_irqbalance_service.append(self.disable_irqbalance)

    self.enable_irqbalance.set_sensitive(False)
    self.disable_irqbalance.set_sensitive(False)

    # ── Ananicy ────────────────────────────────────────────────────────────

    hbox_sep_ananicy = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator_ananicy = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator_ananicy.set_hexpand(True)
    hbox_sep_ananicy.append(hseparator_ananicy)

    hbox_ananicy_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_ananicy_title_label = Gtk.Label(xalign=0)
    hbox_ananicy_title_label.set_markup(_("<b>Ananicy</b>"))
    hbox_ananicy_title_label.set_margin_start(10)
    hbox_ananicy_title_label.set_margin_end(10)
    hbox_ananicy_title.append(hbox_ananicy_title_label)

    hbox_ananicy_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.ananicy_package_label = Gtk.Label(xalign=0)
    self.ananicy_package_label.set_text(_("Install ananicy-cpp and cachyos-ananicy-rules-git"))
    btn_install_ananicy = Gtk.Button(label=_("Install"))
    btn_install_ananicy.connect("clicked", functools.partial(performance.install_ananicy, self))
    btn_remove_ananicy = Gtk.Button(label=_("Remove"))
    btn_remove_ananicy.connect("clicked", functools.partial(performance.remove_ananicy, self))
    self.ananicy_package_label.set_margin_start(10)
    self.ananicy_package_label.set_margin_end(10)
    self.ananicy_package_label.set_hexpand(True)
    hbox_ananicy_install.append(self.ananicy_package_label)
    btn_install_ananicy.set_margin_start(10)
    btn_install_ananicy.set_margin_end(10)
    hbox_ananicy_install.append(btn_install_ananicy)
    btn_remove_ananicy.set_margin_start(10)
    btn_remove_ananicy.set_margin_end(10)
    hbox_ananicy_install.append(btn_remove_ananicy)

    hbox_ananicy_service = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.ananicy_status_label = Gtk.Label(xalign=0)
    self.ananicy_status_label.set_markup(_("ananicy-cpp service : …"))
    self.ananicy_status_label.set_margin_start(10)
    self.ananicy_status_label.set_margin_end(10)
    self.ananicy_status_label.set_hexpand(True)
    self.enable_ananicy = Gtk.Button(label=_("Enable ananicy-cpp"))
    self.enable_ananicy.connect("clicked", functools.partial(performance.enable_ananicy_service, self))
    self.disable_ananicy = Gtk.Button(label=_("Disable ananicy-cpp"))
    self.disable_ananicy.connect("clicked", functools.partial(performance.disable_ananicy_service, self))
    hbox_ananicy_service.append(self.ananicy_status_label)
    self.enable_ananicy.set_margin_start(10)
    self.enable_ananicy.set_margin_end(10)
    hbox_ananicy_service.append(self.enable_ananicy)
    self.disable_ananicy.set_margin_start(10)
    self.disable_ananicy.set_margin_end(10)
    hbox_ananicy_service.append(self.disable_ananicy)

    self.enable_ananicy.set_sensitive(False)
    self.disable_ananicy.set_sensitive(False)

    # ── GameMode ───────────────────────────────────────────────────────────

    hbox_sep_gamemode = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator_gamemode = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator_gamemode.set_hexpand(True)
    hbox_sep_gamemode.append(hseparator_gamemode)

    hbox_gamemode_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_gamemode_title_label = Gtk.Label(xalign=0)
    hbox_gamemode_title_label.set_markup(_("<b>GameMode</b>"))
    hbox_gamemode_title_label.set_margin_start(10)
    hbox_gamemode_title_label.set_margin_end(10)
    hbox_gamemode_title.append(hbox_gamemode_title_label)

    hbox_gamemode_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.gamemode_package_label = Gtk.Label(xalign=0)
    self.gamemode_package_label.set_text(_("Install gamemode"))
    btn_install_gamemode = Gtk.Button(label=_("Install"))
    btn_install_gamemode.connect("clicked", functools.partial(performance.install_gamemode, self))
    btn_remove_gamemode = Gtk.Button(label=_("Remove"))
    btn_remove_gamemode.connect("clicked", functools.partial(performance.remove_gamemode, self))
    self.gamemode_package_label.set_margin_start(10)
    self.gamemode_package_label.set_margin_end(10)
    self.gamemode_package_label.set_hexpand(True)
    hbox_gamemode_install.append(self.gamemode_package_label)
    btn_install_gamemode.set_margin_start(10)
    btn_install_gamemode.set_margin_end(10)
    hbox_gamemode_install.append(btn_install_gamemode)
    btn_remove_gamemode.set_margin_start(10)
    btn_remove_gamemode.set_margin_end(10)
    hbox_gamemode_install.append(btn_remove_gamemode)

    hbox_gamemode_service = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.gamemode_status_label = Gtk.Label(xalign=0)
    self.gamemode_status_label.set_markup(_("gamemode service : …"))
    self.gamemode_status_label.set_margin_start(10)
    self.gamemode_status_label.set_margin_end(10)
    self.gamemode_status_label.set_hexpand(True)
    self.enable_gamemode = Gtk.Button(label=_("Enable gamemode"))
    self.enable_gamemode.connect("clicked", functools.partial(performance.enable_gamemode_service, self))
    self.disable_gamemode = Gtk.Button(label=_("Disable gamemode"))
    self.disable_gamemode.connect("clicked", functools.partial(performance.disable_gamemode_service, self))
    hbox_gamemode_service.append(self.gamemode_status_label)
    self.enable_gamemode.set_margin_start(10)
    self.enable_gamemode.set_margin_end(10)
    hbox_gamemode_service.append(self.enable_gamemode)
    self.disable_gamemode.set_margin_start(10)
    self.disable_gamemode.set_margin_end(10)
    hbox_gamemode_service.append(self.disable_gamemode)

    self.enable_gamemode.set_sensitive(False)
    self.disable_gamemode.set_sensitive(False)

    # ── Preload ────────────────────────────────────────────────────────────

    hbox_sep_preload = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator_preload = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator_preload.set_hexpand(True)
    hbox_sep_preload.append(hseparator_preload)

    hbox_preload_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_preload_title_label = Gtk.Label(xalign=0)
    hbox_preload_title_label.set_markup(_("<b>Preload</b>"))
    hbox_preload_title_label.set_margin_start(10)
    hbox_preload_title_label.set_margin_end(10)
    hbox_preload_title.append(hbox_preload_title_label)

    hbox_preload_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.preload_package_label = Gtk.Label(xalign=0)
    self.preload_package_label.set_text(_("Install preload"))
    btn_install_preload = Gtk.Button(label=_("Install"))
    btn_install_preload.connect("clicked", functools.partial(performance.install_preload, self))
    btn_remove_preload = Gtk.Button(label=_("Remove"))
    btn_remove_preload.connect("clicked", functools.partial(performance.remove_preload, self))
    self.preload_package_label.set_margin_start(10)
    self.preload_package_label.set_margin_end(10)
    self.preload_package_label.set_hexpand(True)
    hbox_preload_install.append(self.preload_package_label)
    btn_install_preload.set_margin_start(10)
    btn_install_preload.set_margin_end(10)
    hbox_preload_install.append(btn_install_preload)
    btn_remove_preload.set_margin_start(10)
    btn_remove_preload.set_margin_end(10)
    hbox_preload_install.append(btn_remove_preload)

    hbox_preload_service = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.preload_status_label = Gtk.Label(xalign=0)
    self.preload_status_label.set_markup(_("preload service : …"))
    self.preload_status_label.set_margin_start(10)
    self.preload_status_label.set_margin_end(10)
    self.preload_status_label.set_hexpand(True)
    self.enable_preload = Gtk.Button(label=_("Enable preload"))
    self.enable_preload.connect("clicked", functools.partial(performance.enable_preload_service, self))
    self.disable_preload = Gtk.Button(label=_("Disable preload"))
    self.disable_preload.connect("clicked", functools.partial(performance.disable_preload_service, self))
    hbox_preload_service.append(self.preload_status_label)
    self.enable_preload.set_margin_start(10)
    self.enable_preload.set_margin_end(10)
    hbox_preload_service.append(self.enable_preload)
    self.disable_preload.set_margin_start(10)
    self.disable_preload.set_margin_end(10)
    hbox_preload_service.append(self.disable_preload)

    self.enable_preload.set_sensitive(False)
    self.disable_preload.set_sensitive(False)

    # ── Build Settings (makepkg.conf) ──────────────────────────────────────

    hbox_sep_makepkg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator_makepkg = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator_makepkg.set_hexpand(True)
    hbox_sep_makepkg.append(hseparator_makepkg)

    hbox_makepkg_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_makepkg_title_label = Gtk.Label(xalign=0)
    hbox_makepkg_title_label.set_markup(_("<b>Build Settings (makepkg.conf)</b>"))
    hbox_makepkg_title_label.set_margin_start(10)
    hbox_makepkg_title_label.set_margin_end(10)
    hbox_makepkg_title.append(hbox_makepkg_title_label)

    hbox_makepkg_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_makepkg_desc_label = Gtk.Label(xalign=0)
    hbox_makepkg_desc_label.set_markup(
        _("Set <b>MAKEFLAGS</b> in <tt>/etc/makepkg.conf</tt> — all cores for max build speed, "
        "or keep 2 free to stay responsive while building.\n"
        "ATT writes <tt>/etc/makepkg.conf-bak</tt> at startup — Restore brings it back.")
    )
    hbox_makepkg_desc_label.set_margin_start(10)
    hbox_makepkg_desc_label.set_margin_end(10)
    hbox_makepkg_desc.append(hbox_makepkg_desc_label)

    hbox_makepkg_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.makepkg_status_label = Gtk.Label(xalign=0)
    self.makepkg_status_label.set_markup(_("MAKEFLAGS : …"))
    self.makepkg_status_label.set_margin_start(10)
    self.makepkg_status_label.set_margin_end(10)
    self.makepkg_status_label.set_hexpand(True)
    hbox_makepkg_status.append(self.makepkg_status_label)

    ncores_detected = performance.get_makepkg_status()[1]
    btn_optimize_makepkg = Gtk.Button(label=_("Optimize for all {ncores_detected} cores").format(ncores_detected=ncores_detected))
    btn_optimize_makepkg.connect("clicked", functools.partial(performance.optimize_makepkg, self))
    # Second button only makes sense with enough cores to genuinely keep 2 free.
    btn_reserve_makepkg = None
    if ncores_detected >= 4:
        btn_reserve_makepkg = Gtk.Button(label=_("Keep 2 cores free (-j{value})").format(value=ncores_detected - 2))
        btn_reserve_makepkg.set_tooltip_text(
            _("Build with 2 cores reserved so the desktop and mouse stay responsive")
        )
        btn_reserve_makepkg.connect("clicked", functools.partial(performance.optimize_makepkg, self, reserved=2))
    btn_edit_makepkg = Gtk.Button(label=_("Edit makepkg.conf in terminal"))
    btn_edit_makepkg.connect("clicked", functools.partial(performance.edit_makepkg_conf, self))
    self.btn_restore_makepkg = Gtk.Button(label=_("Restore backup"))
    self.btn_restore_makepkg.connect("clicked", functools.partial(performance.restore_makepkg, self))

    hbox_makepkg_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_optimize_makepkg.set_margin_start(10)
    btn_optimize_makepkg.set_margin_end(10)
    hbox_makepkg_buttons.append(btn_optimize_makepkg)
    if btn_reserve_makepkg is not None:
        btn_reserve_makepkg.set_margin_end(10)
        hbox_makepkg_buttons.append(btn_reserve_makepkg)
    btn_edit_makepkg.set_margin_start(10)
    btn_edit_makepkg.set_margin_end(10)
    hbox_makepkg_buttons.append(btn_edit_makepkg)
    self.btn_restore_makepkg.set_margin_start(10)
    self.btn_restore_makepkg.set_margin_end(10)
    hbox_makepkg_buttons.append(self.btn_restore_makepkg)

    # ── Vbox stack ─────────────────────────────────────────────────────────

    # ── Build sub-tab (makepkg.conf) ───────────────────────────────────────
    vboxstack_build.append(hbox_makepkg_title)
    vboxstack_build.append(hbox_makepkg_desc)
    vboxstack_build.append(hbox_makepkg_status)
    vboxstack_build.append(hbox_makepkg_buttons)

    # ── Power sub-tab (Tuned + Tuned-PPD + IRQ balance) ────────────────────
    vboxstack_power.append(hbox_tuned_title)
    vboxstack_power.append(hbox_tuned_desc)
    vboxstack_power.append(hbox_tuned_pkg)
    vboxstack_power.append(hbox_tuned_service)
    vboxstack_power.append(hbox_tuned_ppd_pkg)
    vboxstack_power.append(hbox_tuned_ppd_service)
    vboxstack_power.append(hbox_tuned_profile_status)
    vboxstack_power.append(hbox_tuned_profile_select)
    vboxstack_power.append(hbox_sep_irqbalance)
    vboxstack_power.append(hbox_irqbalance_title)
    vboxstack_power.append(hbox_irqbalance_install)
    vboxstack_power.append(hbox_irqbalance_service)

    # ── Responsiveness sub-tab (Ananicy + GameMode + Preload) ──────────────
    vboxstack_responsiveness.append(hbox_ananicy_title)
    vboxstack_responsiveness.append(hbox_ananicy_install)
    vboxstack_responsiveness.append(hbox_ananicy_service)
    vboxstack_responsiveness.append(hbox_sep_gamemode)
    vboxstack_responsiveness.append(hbox_gamemode_title)
    vboxstack_responsiveness.append(hbox_gamemode_install)
    vboxstack_responsiveness.append(hbox_gamemode_service)
    vboxstack_responsiveness.append(hbox_sep_preload)
    vboxstack_responsiveness.append(hbox_preload_title)
    vboxstack_responsiveness.append(hbox_preload_install)
    vboxstack_responsiveness.append(hbox_preload_service)

    # ── Storage & Memory sub-tab (Swap + zram + TRIM) ──────────────────────
    vboxstack_storage.append(hbox_swap_title)
    if performance.get_root_filesystem_type() != "btrfs":
        vboxstack_storage.append(hbox_swapfile)
    vboxstack_storage.append(hbox_zram)
    vboxstack_storage.append(hbox_sep_fstrim)
    vboxstack_storage.append(hbox_fstrim_title)
    vboxstack_storage.append(hbox_fstrim)

    # ── Pack sub-tabs into Stack + StackSwitcher ───────────────────────────
    stack.add_titled(vboxstack_build, "stack_build", _("Build"))
    stack.add_titled(vboxstack_power, "stack_power", _("Power"))
    stack.add_titled(vboxstack_responsiveness, "stack_responsiveness", _("Responsiveness"))
    stack.add_titled(vboxstack_storage, "stack_storage", _("Storage & Memory"))
    stack.set_visible_child_name("stack_build")
    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vbox_stack_holder.append(stack_switcher)
    vbox_stack_holder.append(stack)
    vbox_stack_holder.set_hexpand(True)
    vbox_stack_holder.set_vexpand(True)

    vboxstack_performance.append(hbox_title)
    vboxstack_performance.append(hbox_sep)
    vboxstack_performance.append(vbox_stack_holder)

    # ── Lazy-load with per-session cache ───────────────────────────────────
    # Each sub-tab refreshes once on its first map; subsequent tab clicks within
    # the same Performance visit are instant. Flags reset when the user navigates
    # away from Performance and returns, so external state changes are picked up
    # on the next visit. ATT's own actions (Install/Remove/Enable/Disable) refresh
    # directly from their handlers, so internal changes always propagate.
    subtab_loaded = {"build": False, "power": False, "responsiveness": False, "storage": False}

    def _invalidate_subtab_cache():
        for key in subtab_loaded:
            subtab_loaded[key] = False

    def _refresh_build_subtab():
        if subtab_loaded["build"]:
            return
        subtab_loaded["build"] = True
        performance.refresh_makepkg_status_label(self)

    def _refresh_power_subtab():
        if subtab_loaded["power"]:
            return
        subtab_loaded["power"] = True
        _refresh(self, fn)
        performance.refresh_tuned_package_label(self)
        performance.refresh_tuned_buttons(self)
        self.tuned_status_label.set_markup(
            _("tuned service : {status}").format(status=performance.get_service_status("tuned"))
        )
        self.tuned_ppd_status_label.set_markup(
            _("tuned-ppd service : {status}").format(status=performance.get_service_status("tuned-ppd"))
        )
        self.tuned_profile_status_label.set_markup(performance.get_tuned_profile_status_markup())
        performance.refresh_tuned_profile_choices(self)
        self.irqbalance_status_label.set_markup(performance.get_irqbalance_status_markup())

    def _refresh_responsiveness_subtab():
        if subtab_loaded["responsiveness"]:
            return
        subtab_loaded["responsiveness"] = True
        _refresh(self, fn)
        self.ananicy_status_label.set_markup(performance.get_ananicy_status_markup())
        self.gamemode_status_label.set_markup(performance.get_gamemode_status_markup())
        self.preload_status_label.set_markup(performance.get_preload_status_markup())

    def _refresh_storage_subtab():
        if subtab_loaded["storage"]:
            return
        subtab_loaded["storage"] = True
        _swapfile_size = performance.get_swapfile_size_label()
        if _swapfile_size:
            self.swapfile_label.set_markup(
                _("Create or manage a swapfile at /swapfile - {size} <b>present</b>").format(size=_swapfile_size)
            )
        else:
            self.swapfile_label.set_text(_("Create or manage a swapfile at /swapfile"))
        self.zram_status_label.set_markup(performance.get_zram_status_markup())
        self.fstrim_status_label.set_markup(performance.get_fstrim_status_markup())

    vboxstack_performance.connect("map", lambda _w: _invalidate_subtab_cache())
    vboxstack_build.connect("map", lambda _w: _refresh_build_subtab())
    vboxstack_power.connect("map", lambda _w: _refresh_power_subtab())
    vboxstack_responsiveness.connect("map", lambda _w: _refresh_responsiveness_subtab())
    vboxstack_storage.connect("map", lambda _w: _refresh_storage_subtab())
    fn.GLib.idle_add(_refresh_build_subtab)

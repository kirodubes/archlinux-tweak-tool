# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
from att_i18n import _
import pacman
import pacman_gui


def _update_cursor_preview(self, fn, Gdk):
    cursor_theme = fn.get_combo_text(self.cursor_themes)
    if not cursor_theme:
        self.cursor_theme_preview.set_paintable(None)
        return
    pixbuf = fn.get_cursor_preview_pixbuf(cursor_theme)
    if pixbuf:
        self.cursor_theme_preview.set_paintable(Gdk.Texture.new_for_pixbuf(pixbuf))
    else:
        self.cursor_theme_preview.set_paintable(None)


def _refresh_boot_status(self, fn, maintenance):
    """Refresh the Boot/Initramfs status labels (HOOKS line, resume presence, real swap)."""
    idx, tokens = maintenance.read_hooks_line()
    if idx is None:
        self.lbl_hooks_value.set_text(_("HOOKS line not found in /etc/mkinitcpio.conf"))
        self.lbl_resume_value.set_text(_("unknown"))
    else:
        self.lbl_hooks_value.set_text(" ".join(tokens))
        self.lbl_resume_value.set_text(_("present") if "resume" in tokens else _("absent"))

    real_swap = maintenance.detect_real_swap()
    if real_swap:
        self.lbl_swap_value.set_text(_("{swap}  (hibernation may be in use)").format(swap=", ".join(real_swap)))
    else:
        self.lbl_swap_value.set_text(_("none (ZRAM-only or no swap)"))

    # Disable the remove button if there's nothing to remove
    if idx is not None and "resume" not in tokens:
        self.btn_remove_resume.set_sensitive(False)
        self.btn_remove_resume.set_label(_("Resume hook already absent"))
    else:
        self.btn_remove_resume.set_sensitive(True)
        self.btn_remove_resume.set_label(_("Remove resume hook"))


def gui(self, Gtk, Gdk, GdkPixbuf, vboxstack_maintenance, fn, maintenance):
    """Create the maintenance GUI with a tabbed Stack: System / Mirrors / Keys & GPG / Pacman / Cursors / Boot."""
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text(_("Maintenance"))
    lbl_title.set_name("title")
    lbl_title.set_margin_start(10)
    lbl_title.set_margin_end(10)
    hbox_title.append(lbl_title)

    hbox_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_separator.append(hseparator)

    # ── Stack + StackSwitcher ────────────────────────────────────
    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
    stack.set_transition_duration(350)
    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)
    stack.set_hexpand(True)
    stack.set_vexpand(True)

    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
    stack_switcher.set_halign(Gtk.Align.CENTER)
    stack_switcher.set_stack(stack)

    vbox_system = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_mirrors = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_keys = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_pacman = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_cursors = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_initramfs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    # ── System tab rows ──────────────────────────────────────────
    hbox_update_system = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_update_system = Gtk.Label(xalign=0)
    lbl_update_system.set_text(_("Update system"))
    btn_update_system = Gtk.Button(label=_("Update"))
    btn_update_system.connect("clicked", functools.partial(maintenance.on_click_update_system, self))
    lbl_update_system.set_margin_start(10)
    lbl_update_system.set_margin_end(10)
    lbl_update_system.set_hexpand(True)
    hbox_update_system.append(lbl_update_system)
    btn_update_system.set_margin_start(10)
    btn_update_system.set_margin_end(10)
    hbox_update_system.append(btn_update_system)

    hbox_clean_cache = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_clean_cache = Gtk.Label(xalign=0)
    lbl_clean_cache.set_text(_("Clean cache"))
    btn_clean_cache = Gtk.Button(label=_("Clean"))
    btn_clean_cache.connect("clicked", functools.partial(maintenance.on_click_clean_cache, self))
    lbl_clean_cache.set_margin_start(10)
    lbl_clean_cache.set_margin_end(10)
    lbl_clean_cache.set_hexpand(True)
    hbox_clean_cache.append(lbl_clean_cache)
    btn_clean_cache.set_margin_start(10)
    btn_clean_cache.set_margin_end(10)
    hbox_clean_cache.append(btn_clean_cache)

    hbox_remove_lock = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_remove_lock = Gtk.Label(xalign=0)
    lbl_remove_lock.set_text(_("Remove pacman lock"))
    btn_remove_pacman_lock = Gtk.Button(label=_("Remove"))
    btn_remove_pacman_lock.connect("clicked", functools.partial(maintenance.on_click_remove_pacman_lock, self))
    lbl_remove_lock.set_margin_start(10)
    lbl_remove_lock.set_margin_end(10)
    lbl_remove_lock.set_hexpand(True)
    hbox_remove_lock.append(lbl_remove_lock)
    btn_remove_pacman_lock.set_margin_start(10)
    btn_remove_pacman_lock.set_margin_end(10)
    hbox_remove_lock.append(btn_remove_pacman_lock)

    hbox_probe = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_probe = Gtk.Label(xalign=0)
    lbl_probe.set_text(_("Provide probe link (hardware diagnostics)"))
    btn_probe = Gtk.Button(label=_("Get probe link"))
    btn_probe.connect("clicked", functools.partial(maintenance.on_click_probe, self))
    lbl_probe.set_margin_start(10)
    lbl_probe.set_margin_end(10)
    lbl_probe.set_hexpand(True)
    hbox_probe.append(lbl_probe)
    btn_probe.set_margin_start(10)
    btn_probe.set_margin_end(10)
    hbox_probe.append(btn_probe)

    # ── Keys & GPG tab rows ──────────────────────────────────────
    hbox_keyring = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_keyring = Gtk.Label(xalign=0)
    lbl_keyring.set_text(_("Re-install archlinux-keyring"))
    btn_install_arch_keyring = Gtk.Button(label=_("Install keyring (local)"))
    btn_install_arch_keyring.connect("clicked", functools.partial(maintenance.on_click_install_arch_keyring, self))
    btn_install_arch_keyring_online = Gtk.Button(label=_("Install keyring (online)"))
    btn_install_arch_keyring_online.connect(
        "clicked", functools.partial(maintenance.on_click_install_arch_keyring_online, self)
    )
    lbl_keyring.set_margin_start(10)
    lbl_keyring.set_margin_end(10)
    lbl_keyring.set_hexpand(True)
    hbox_keyring.append(lbl_keyring)
    btn_install_arch_keyring.set_margin_start(10)
    btn_install_arch_keyring.set_margin_end(10)
    hbox_keyring.append(btn_install_arch_keyring)
    btn_install_arch_keyring_online.set_margin_start(10)
    btn_install_arch_keyring_online.set_margin_end(10)
    hbox_keyring.append(btn_install_arch_keyring_online)

    hbox_fix_keys = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_fix_keys = Gtk.Label(xalign=0)
    lbl_fix_keys.set_text(_("Reset and reload pacman keys"))
    btn_apply_pacman_key_fix = Gtk.Button(label=_("Fix keys"))
    btn_apply_pacman_key_fix.connect("clicked", functools.partial(maintenance.on_click_fix_pacman_keys, self))
    lbl_fix_keys.set_margin_start(10)
    lbl_fix_keys.set_margin_end(10)
    lbl_fix_keys.set_hexpand(True)
    hbox_fix_keys.append(lbl_fix_keys)
    btn_apply_pacman_key_fix.set_margin_start(10)
    btn_apply_pacman_key_fix.set_margin_end(10)
    hbox_fix_keys.append(btn_apply_pacman_key_fix)

    hbox_gpg_conf = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_gpg_conf = Gtk.Label(xalign=0)
    lbl_gpg_conf.set_text(_("Get the best keyservers for /etc/pacman.d/gnupg/gpg.conf"))
    btn_apply_pacman_gpg_conf = Gtk.Button(label=_("Backup and reset gpg.conf"))
    btn_apply_pacman_gpg_conf.connect("clicked", functools.partial(maintenance.on_click_fix_pacman_gpg_conf, self))
    lbl_gpg_conf.set_margin_start(10)
    lbl_gpg_conf.set_margin_end(10)
    lbl_gpg_conf.set_hexpand(True)
    hbox_gpg_conf.append(lbl_gpg_conf)
    btn_apply_pacman_gpg_conf.set_margin_start(10)
    btn_apply_pacman_gpg_conf.set_margin_end(10)
    hbox_gpg_conf.append(btn_apply_pacman_gpg_conf)

    hbox_gpg_conf_local = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_gpg_conf_local = Gtk.Label(xalign=0)
    lbl_gpg_conf_local.set_text(_("Get the best keyservers for ~/.gnupg/gpg.conf"))
    btn_apply_pacman_gpg_conf_local = Gtk.Button(label=_("Backup and reset gpg.conf"))
    btn_apply_pacman_gpg_conf_local.connect(
        "clicked", functools.partial(maintenance.on_click_fix_pacman_gpg_conf_local, self)
    )
    lbl_gpg_conf_local.set_margin_start(10)
    lbl_gpg_conf_local.set_margin_end(10)
    lbl_gpg_conf_local.set_hexpand(True)
    hbox_gpg_conf_local.append(lbl_gpg_conf_local)
    btn_apply_pacman_gpg_conf_local.set_margin_start(10)
    btn_apply_pacman_gpg_conf_local.set_margin_end(10)
    hbox_gpg_conf_local.append(btn_apply_pacman_gpg_conf_local)

    # ── Mirrors tab rows ─────────────────────────────────────────
    hbox_mainstream_servers = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_mainstream_servers = Gtk.Label(xalign=0)
    lbl_mainstream_servers.set_text(_("Set the mainstream servers from Arch Linux"))
    btn_apply_osbeck = Gtk.Button(label=_("Set mainstream"))
    btn_apply_osbeck.connect("clicked", functools.partial(maintenance.on_click_fix_mainstream, self))
    button_reset_mirrorlist = Gtk.Button(label=_("Reset your mirrorlist"))
    button_reset_mirrorlist.connect("clicked", functools.partial(maintenance.on_click_reset_mirrorlist, self))
    lbl_mainstream_servers.set_margin_start(10)
    lbl_mainstream_servers.set_margin_end(10)
    lbl_mainstream_servers.set_hexpand(True)
    hbox_mainstream_servers.append(lbl_mainstream_servers)
    btn_apply_osbeck.set_margin_start(10)
    btn_apply_osbeck.set_margin_end(10)
    hbox_mainstream_servers.append(btn_apply_osbeck)
    button_reset_mirrorlist.set_margin_start(10)
    button_reset_mirrorlist.set_margin_end(10)
    hbox_mainstream_servers.append(button_reset_mirrorlist)

    hbox_run_mirror_tools = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_run_mirror_tools = Gtk.Label(xalign=0)
    lbl_run_mirror_tools.set_text(_("Get the best Arch Linux servers (takes a while)"))
    self.btn_run_reflector = Gtk.Button(label=_("Run reflector"))
    self.btn_run_reflector.connect("clicked", functools.partial(maintenance.on_click_get_arch_mirrors, self))
    self.btn_run_rate_mirrors = Gtk.Button(label=_("Run rate-mirrors"))
    self.btn_run_rate_mirrors.connect("clicked", functools.partial(maintenance.on_click_get_arch_mirrors2, self))
    lbl_run_mirror_tools.set_margin_start(10)
    lbl_run_mirror_tools.set_margin_end(10)
    lbl_run_mirror_tools.set_hexpand(True)
    hbox_run_mirror_tools.append(lbl_run_mirror_tools)
    self.btn_run_rate_mirrors.set_margin_start(10)
    self.btn_run_rate_mirrors.set_margin_end(10)
    hbox_run_mirror_tools.append(self.btn_run_rate_mirrors)
    self.btn_run_reflector.set_margin_start(10)
    self.btn_run_reflector.set_margin_end(10)
    hbox_run_mirror_tools.append(self.btn_run_reflector)

    hbox_reflector_timer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_reflector_timer = Gtk.Label(xalign=0)
    lbl_reflector_timer.set_text(_("Automatically refresh mirrors on a schedule (reflector.timer)"))
    timer_label = (
        _("Disable reflector timer") if fn.check_service_enabled("reflector.timer") else _("Enable reflector timer")
    )
    self.btn_toggle_reflector_timer = Gtk.Button(label=timer_label)
    self.btn_toggle_reflector_timer.connect(
        "clicked", functools.partial(maintenance.on_click_toggle_reflector_timer, self)
    )
    lbl_reflector_timer.set_margin_start(10)
    lbl_reflector_timer.set_margin_end(10)
    lbl_reflector_timer.set_hexpand(True)
    hbox_reflector_timer.append(lbl_reflector_timer)
    self.btn_toggle_reflector_timer.set_margin_start(10)
    self.btn_toggle_reflector_timer.set_margin_end(10)
    hbox_reflector_timer.append(self.btn_toggle_reflector_timer)

    hbox_install_mirror_tools = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_install_mirror_tools = Gtk.Label(xalign=0)
    lbl_install_mirror_tools.set_text(_("Install apps to find the best Arch Linux servers"))
    reflector_label = _("Remove reflector") if fn.path.exists("/usr/bin/reflector") else _("Install reflector")
    self.btn_install_mirrors = Gtk.Button(label=reflector_label)
    self.btn_install_mirrors.connect("clicked", functools.partial(maintenance.on_click_install_arch_mirrors, self))
    rate_mirrors_label = (
        _("Remove rate-mirrors") if fn.path.exists("/usr/bin/rate-mirrors") else _("Install rate-mirrors")
    )
    self.btn_install_rate_mirrors = Gtk.Button(label=rate_mirrors_label)
    self.btn_install_rate_mirrors.connect(
        "clicked", functools.partial(maintenance.on_click_install_arch_mirrors2, self)
    )
    lbl_install_mirror_tools.set_margin_start(10)
    lbl_install_mirror_tools.set_margin_end(10)
    lbl_install_mirror_tools.set_hexpand(True)
    hbox_install_mirror_tools.append(lbl_install_mirror_tools)
    self.btn_install_rate_mirrors.set_margin_start(10)
    self.btn_install_rate_mirrors.set_margin_end(10)
    hbox_install_mirror_tools.append(self.btn_install_rate_mirrors)
    self.btn_install_mirrors.set_margin_start(10)
    self.btn_install_mirrors.set_margin_end(10)
    hbox_install_mirror_tools.append(self.btn_install_mirrors)

    if not fn.path.exists("/usr/bin/reflector"):
        self.btn_run_reflector.set_sensitive(False)
        self.btn_toggle_reflector_timer.set_sensitive(False)
    if not fn.path.exists("/usr/bin/rate-mirrors"):
        self.btn_run_rate_mirrors.set_sensitive(False)

    # ── Pacman tab rows ──────────────────────────────────────────
    hbox_reset_pacman_conf = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_reset_pacman_conf = Gtk.Label(xalign=0)
    lbl_reset_pacman_conf.set_text(_("Get the original ATT /etc/pacman.conf"))
    btn_reset_pacman = Gtk.Button(label=_("Reset pacman.conf"))
    btn_reset_pacman.connect(
        "clicked",
        lambda _w: maintenance.on_click_fix_pacman_conf(self, _w, on_success=lambda: pacman_gui.refresh_switches(self)),
    )
    lbl_reset_pacman_conf.set_margin_start(10)
    lbl_reset_pacman_conf.set_margin_end(10)
    lbl_reset_pacman_conf.set_hexpand(True)
    hbox_reset_pacman_conf.append(lbl_reset_pacman_conf)
    btn_reset_pacman.set_margin_start(10)
    btn_reset_pacman.set_margin_end(10)
    hbox_reset_pacman_conf.append(btn_reset_pacman)

    hbox_parallel_downloads = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_parallel_downloads = Gtk.Label(xalign=0)
    lbl_parallel_downloads.set_text(_("Choose the number of parallel downloads for pacman"))
    self.parallel_downloads = Gtk.DropDown.new_from_strings([])
    numbers = [str(i) for i in range(1, 31)]

    btn_apply_parallel_downloads = Gtk.Button(label=_("Apply"))
    btn_apply_parallel_downloads.connect("clicked", functools.partial(pacman.on_click_apply_parallel_downloads, self))

    if fn.check_content("ParallelDownloads", fn.pacman):
        for number in numbers:
            self.parallel_downloads.get_model().append(number)
        act_number = pacman.pop_parallel_downloads(self)
        self.parallel_downloads.set_selected(act_number)
    else:
        btn_apply_parallel_downloads.set_sensitive(False)

    lbl_parallel_downloads.set_margin_start(10)
    lbl_parallel_downloads.set_margin_end(10)
    lbl_parallel_downloads.set_hexpand(True)
    hbox_parallel_downloads.append(lbl_parallel_downloads)
    self.parallel_downloads.set_margin_start(10)
    self.parallel_downloads.set_margin_end(10)
    hbox_parallel_downloads.append(self.parallel_downloads)
    btn_apply_parallel_downloads.set_margin_start(10)
    btn_apply_parallel_downloads.set_margin_end(10)
    hbox_parallel_downloads.append(btn_apply_parallel_downloads)

    # ── Cursors tab rows ─────────────────────────────────────────
    hbox_bibata_cursors = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_install_bibata = Gtk.Button(label=_("Install Bibata cursors"))
    btn_install_bibata.connect("clicked", functools.partial(maintenance.on_click_install_bibata_cursors, self))
    btn_install_bibata.set_margin_start(10)
    btn_install_bibata.set_margin_end(10)
    btn_remove_bibata = Gtk.Button(label=_("Remove Bibata cursors"))
    btn_remove_bibata.connect("clicked", functools.partial(maintenance.on_click_remove_bibata_cursors, self))
    btn_remove_bibata.set_margin_end(10)
    hbox_bibata_cursors.append(btn_install_bibata)
    hbox_bibata_cursors.append(btn_remove_bibata)

    hbox_cursor_theme = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_cursor_theme = Gtk.Label(xalign=0)
    lbl_cursor_theme.set_text(_("Choose your cursor theme for installed desktops and SDDM"))
    self.cursor_themes = Gtk.DropDown.new_from_strings([])
    maintenance.pop_gtk_cursor_names(self.cursor_themes)
    self.cursor_theme_preview = Gtk.Picture()
    self.cursor_theme_preview.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
    self.cursor_theme_preview.set_size_request(24, 24)
    self.cursor_theme_preview.set_halign(Gtk.Align.END)
    self.cursor_theme_preview.set_valign(Gtk.Align.CENTER)
    self.cursor_themes.connect(
        "notify::selected",
        lambda *_args: _update_cursor_preview(self, fn, Gdk),
    )
    _update_cursor_preview(self, fn, Gdk)
    btn_apply_cursor = Gtk.Button(label=_("Apply"))
    btn_apply_cursor.connect("clicked", functools.partial(maintenance.on_click_apply_global_cursor, self))
    lbl_cursor_theme.set_margin_start(10)
    lbl_cursor_theme.set_margin_end(10)
    lbl_cursor_theme.set_hexpand(True)
    hbox_cursor_theme.append(lbl_cursor_theme)
    self.cursor_theme_preview.set_margin_start(10)
    self.cursor_theme_preview.set_margin_end(10)
    hbox_cursor_theme.append(self.cursor_theme_preview)
    self.cursor_themes.set_margin_start(10)
    self.cursor_themes.set_margin_end(10)
    hbox_cursor_theme.append(self.cursor_themes)
    btn_apply_cursor.set_margin_start(10)
    btn_apply_cursor.set_margin_end(10)
    hbox_cursor_theme.append(btn_apply_cursor)

    hbox_cursor_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    cursor_info_label = Gtk.Label(xalign=0, wrap=True)
    cursor_info_label.set_text(
        _("Applies cursor theme globally to: System & user xcursor, GTK2/3/4, XFCE, GNOME (gsettings),"
        " KDE Plasma, and SDDM login screen. Affects all applications and SDDM login screen.")
    )
    cursor_info_label.set_margin_start(40)
    cursor_info_label.set_margin_end(10)
    cursor_info_label.set_margin_top(0)
    cursor_info_label.set_margin_bottom(5)
    hbox_cursor_info.append(cursor_info_label)

    # ── Boot / Initramfs tab rows ────────────────────────────────
    hbox_boot_status_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_boot_status_title = Gtk.Label(xalign=0)
    lbl_boot_status_title.set_markup(_("<b>Current state</b>"))
    lbl_boot_status_title.set_margin_start(10)
    lbl_boot_status_title.set_margin_top(5)
    lbl_boot_status_title.set_margin_bottom(5)
    hbox_boot_status_title.append(lbl_boot_status_title)

    hbox_hooks = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_hooks_key = Gtk.Label(xalign=0)
    lbl_hooks_key.set_text(_("HOOKS:"))
    self.lbl_hooks_value = Gtk.Label(xalign=0, wrap=True, selectable=True)
    self.lbl_hooks_value.set_hexpand(True)
    lbl_hooks_key.set_margin_start(10)
    lbl_hooks_key.set_margin_end(10)
    self.lbl_hooks_value.set_margin_end(10)
    hbox_hooks.append(lbl_hooks_key)
    hbox_hooks.append(self.lbl_hooks_value)

    hbox_resume = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_resume_key = Gtk.Label(xalign=0)
    lbl_resume_key.set_text(_("resume hook:"))
    self.lbl_resume_value = Gtk.Label(xalign=0)
    self.lbl_resume_value.set_hexpand(True)
    lbl_resume_key.set_margin_start(10)
    lbl_resume_key.set_margin_end(10)
    self.lbl_resume_value.set_margin_end(10)
    hbox_resume.append(lbl_resume_key)
    hbox_resume.append(self.lbl_resume_value)

    hbox_swap = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_swap_key = Gtk.Label(xalign=0)
    lbl_swap_key.set_text(_("Real swap:"))
    self.lbl_swap_value = Gtk.Label(xalign=0, wrap=True)
    self.lbl_swap_value.set_hexpand(True)
    lbl_swap_key.set_margin_start(10)
    lbl_swap_key.set_margin_end(10)
    self.lbl_swap_value.set_margin_end(10)
    hbox_swap.append(lbl_swap_key)
    hbox_swap.append(self.lbl_swap_value)

    hbox_boot_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    boot_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    boot_sep.set_hexpand(True)
    boot_sep.set_margin_top(10)
    boot_sep.set_margin_bottom(10)
    boot_sep.set_margin_start(10)
    boot_sep.set_margin_end(10)
    hbox_boot_sep.append(boot_sep)

    hbox_remove_resume = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_remove_resume = Gtk.Label(xalign=0, wrap=True)
    lbl_remove_resume.set_text(
        _("Remove the 'resume' hook from /etc/mkinitcpio.conf — suppresses the "
        "'no resume device' boot warning on systems without a hibernation swap partition. "
        "Backs up to /etc/mkinitcpio.conf.bak and rebuilds initramfs.")
    )
    self.btn_remove_resume = Gtk.Button(label=_("Remove resume hook"))
    self.btn_remove_resume.connect(
        "clicked",
        lambda _w: maintenance.on_click_remove_resume_hook(
            self, _w, on_success=lambda: _refresh_boot_status(self, fn, maintenance)
        ),
    )
    lbl_remove_resume.set_margin_start(10)
    lbl_remove_resume.set_margin_end(10)
    lbl_remove_resume.set_hexpand(True)
    hbox_remove_resume.append(lbl_remove_resume)
    self.btn_remove_resume.set_margin_start(10)
    self.btn_remove_resume.set_margin_end(10)
    hbox_remove_resume.append(self.btn_remove_resume)

    hbox_regen_initramfs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_regen_initramfs = Gtk.Label(xalign=0, wrap=True)
    lbl_regen_initramfs.set_text(
        _("Regenerate all initramfs images (mkinitcpio -P). Run after manual HOOKS changes "
        "or when troubleshooting boot.")
    )
    btn_regen_initramfs = Gtk.Button(label=_("Regenerate initramfs"))
    btn_regen_initramfs.connect("clicked", functools.partial(maintenance.on_click_regenerate_initramfs, self))
    lbl_regen_initramfs.set_margin_start(10)
    lbl_regen_initramfs.set_margin_end(10)
    lbl_regen_initramfs.set_hexpand(True)
    hbox_regen_initramfs.append(lbl_regen_initramfs)
    btn_regen_initramfs.set_margin_start(10)
    btn_regen_initramfs.set_margin_end(10)
    hbox_regen_initramfs.append(btn_regen_initramfs)

    # ── Pack tabs ────────────────────────────────────────────────
    vbox_system.append(hbox_update_system)
    vbox_system.append(hbox_clean_cache)
    vbox_system.append(hbox_remove_lock)
    vbox_system.append(hbox_probe)

    vbox_mirrors.append(hbox_install_mirror_tools)
    vbox_mirrors.append(hbox_run_mirror_tools)
    vbox_mirrors.append(hbox_reflector_timer)
    vbox_mirrors.append(hbox_mainstream_servers)

    vbox_keys.append(hbox_keyring)
    vbox_keys.append(hbox_fix_keys)
    vbox_keys.append(hbox_gpg_conf)
    vbox_keys.append(hbox_gpg_conf_local)

    vbox_pacman.append(hbox_reset_pacman_conf)
    vbox_pacman.append(hbox_parallel_downloads)

    vbox_cursors.append(hbox_bibata_cursors)
    vbox_cursors.append(hbox_cursor_theme)
    vbox_cursors.append(hbox_cursor_info)

    vbox_initramfs.append(hbox_boot_status_title)
    vbox_initramfs.append(hbox_hooks)
    vbox_initramfs.append(hbox_resume)
    vbox_initramfs.append(hbox_swap)
    vbox_initramfs.append(hbox_boot_sep)
    vbox_initramfs.append(hbox_remove_resume)
    vbox_initramfs.append(hbox_regen_initramfs)

    stack.add_titled(vbox_system, "system", _("System"))
    stack.add_titled(vbox_mirrors, "mirrors", _("Mirrors"))
    stack.add_titled(vbox_keys, "keys", _("Keys & GPG"))
    stack.add_titled(vbox_pacman, "pacman", _("Pacman"))
    stack.add_titled(vbox_cursors, "cursors", _("Cursors"))
    stack.add_titled(vbox_initramfs, "initramfs", _("Boot / Initramfs"))

    vboxstack_maintenance.append(hbox_title)
    vboxstack_maintenance.append(hbox_separator)
    vboxstack_maintenance.append(stack_switcher)
    vboxstack_maintenance.append(stack)

    _refresh_boot_status(self, fn, maintenance)
    vboxstack_maintenance.connect("map", lambda _w: _refresh_boot_status(self, fn, maintenance))

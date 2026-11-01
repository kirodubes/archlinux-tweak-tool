import plymouth
from att_i18n import _, ngettext


def gui(self, Gtk, vboxstack_plymouth, fn):
    """Create the Plymouth boot splash configuration GUI."""
    _default_theme = {
        "omarchy": "omarchy",
        "cachyos": "cachyos-bootanimation",
        "prismlinux": "prismlinux-theme",
    }.get(fn.distr)

    _is_dracut = plymouth.is_dracut()
    _rebuild_cmd = fn.get_initramfs_rebuild_cmd()
    _rebuild_label = "kernel-install add" if _rebuild_cmd.startswith("for ") else _rebuild_cmd

    _plymouth_initialized = [False]

    # ── title ─────────────────────────────────────────────────────────────

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_title_label = Gtk.Label(xalign=0)
    hbox_title_label.set_text("Plymouth")
    hbox_title_label.set_name("title")
    hbox_title_label.set_margin_start(10)
    hbox_title_label.set_margin_end(10)
    hbox_title.append(hbox_title_label)

    hbox_sep_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hsep_top = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_top.set_hexpand(True)
    hsep_top.set_vexpand(False)
    hbox_sep_top.append(hsep_top)

    # ── section: Install Plymouth ──────────────────────────────────────────

    hbox_section_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_install = Gtk.Label(xalign=0)
    lbl_section_install.set_markup(_("<b>Install / Remove Plymouth</b>"))
    lbl_section_install.set_margin_start(10)
    lbl_section_install.set_margin_top(6)
    hbox_section_install.append(lbl_section_install)

    hbox_install_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_install_desc.set_margin_start(10)
    hbox_install_desc.set_margin_top(4)
    lbl_install_desc = Gtk.Label(xalign=0)
    lbl_install_desc.set_markup(
        _("Install adds the plymouth hook to <tt>/etc/mkinitcpio.conf</tt> and rebuilds initramfs.\n"
        "Remove strips the hook, optionally cleans <tt>quiet splash</tt> from the kernel cmdline,\n"
        "optionally removes <tt>plymouth-theme-*</tt> packages, and rebuilds initramfs.\n"
        "Every step is shown in the terminal — prompts ask before destructive cleanup.")
    )
    hbox_install_desc.append(lbl_install_desc)

    hbox_install_plymouth = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_install_plymouth.set_margin_start(10)
    hbox_install_plymouth.set_margin_top(8)
    btn_install_plymouth = Gtk.Button(label=_("Install Plymouth"))
    btn_install_plymouth.set_size_request(160, 30)
    btn_remove_plymouth = Gtk.Button(label=_("Remove Plymouth"))
    btn_remove_plymouth.set_size_request(160, 30)
    btn_remove_plymouth.set_margin_start(10)
    btn_remove_plymouth.set_visible(False)
    lbl_plymouth_installed = Gtk.Label(xalign=0)
    lbl_plymouth_installed.set_markup(_("<b>Installed</b>"))
    lbl_plymouth_installed.set_margin_start(10)
    lbl_plymouth_installed.set_visible(False)
    hbox_install_plymouth.append(btn_install_plymouth)
    hbox_install_plymouth.append(btn_remove_plymouth)
    hbox_install_plymouth.append(lbl_plymouth_installed)

    # ── section: Bootloader Integration ───────────────────────────────────

    hbox_sep_bootloader = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sep_bootloader.set_margin_top(10)
    hsep_bootloader = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_bootloader.set_hexpand(True)
    hsep_bootloader.set_vexpand(False)
    hbox_sep_bootloader.append(hsep_bootloader)

    hbox_section_bootloader = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_bootloader = Gtk.Label(xalign=0)
    lbl_section_bootloader.set_markup(_("<b>Bootloader Integration</b>"))
    lbl_section_bootloader.set_margin_start(10)
    lbl_section_bootloader.set_margin_top(6)
    hbox_section_bootloader.append(lbl_section_bootloader)

    _bootloader = plymouth.detect_bootloader()

    hbox_bootloader_detected = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bootloader_detected.set_margin_start(10)
    hbox_bootloader_detected.set_margin_top(4)
    lbl_bootloader_title = Gtk.Label(xalign=0)
    lbl_bootloader_title.set_markup(_("Detected bootloader"))
    lbl_bootloader_title.set_size_request(180, -1)
    lbl_bootloader_detected = Gtk.Label(xalign=0)
    lbl_bootloader_detected.set_text(_bootloader)
    hbox_bootloader_detected.append(lbl_bootloader_title)
    hbox_bootloader_detected.append(lbl_bootloader_detected)

    # systemd-boot splash check

    _use_cmdline = plymouth.check_kernel_cmdline_exists()

    hbox_sdboot_cmdline_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sdboot_cmdline_status.set_margin_start(10)
    hbox_sdboot_cmdline_status.set_margin_top(6)
    lbl_sdboot_cmdline_status = Gtk.Label(xalign=0)
    hbox_sdboot_cmdline_status.append(lbl_sdboot_cmdline_status)

    hbox_sdboot_entries_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sdboot_entries_status.set_margin_start(10)
    hbox_sdboot_entries_status.set_margin_top(4)
    lbl_sdboot_entries_status = Gtk.Label(xalign=0)
    hbox_sdboot_entries_status.append(lbl_sdboot_entries_status)

    hbox_sdboot_fix = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sdboot_fix.set_margin_start(10)
    hbox_sdboot_fix.set_margin_top(6)
    btn_sdboot_fix = Gtk.Button(label=_("Add quiet splash to cmdline + entries"))
    btn_sdboot_fix.set_size_request(260, 30)
    hbox_sdboot_fix.append(btn_sdboot_fix)

    if _bootloader == "systemd-boot":
        _cmdline_ok = plymouth.check_kernel_cmdline_splash() if _use_cmdline else True
        _sdboot_missing, _unused = plymouth.check_systemd_boot_splash()
        _entries_ok = not bool(_sdboot_missing)
        _all_ok = _cmdline_ok and _entries_ok

        if _use_cmdline:
            if _cmdline_ok:
                lbl_sdboot_cmdline_status.set_markup(
                    _("<b>OK:</b> <tt>/etc/kernel/cmdline</tt> contains <tt>quiet splash</tt>.")
                )
            else:
                lbl_sdboot_cmdline_status.set_markup(
                    _('<span foreground="#FFA500"><b>Warning:</b></span>'
                    " <tt>/etc/kernel/cmdline</tt> is missing <tt>quiet splash</tt>.")
                )
        if _entries_ok:
            lbl_sdboot_entries_status.set_markup(_("<b>OK:</b> all boot entries contain <tt>quiet splash</tt>."))
        else:
            _n = len(_sdboot_missing)
            lbl_sdboot_entries_status.set_markup(
                ngettext(
                    '<span foreground="#FFA500"><b>Warning:</b></span> {count} boot entry missing <tt>quiet splash</tt>.',
                    '<span foreground="#FFA500"><b>Warning:</b></span> {count} boot entries missing <tt>quiet splash</tt>.',
                    _n,
                ).format(count=_n)
            )
        hbox_sdboot_cmdline_status.set_visible(_use_cmdline)
        hbox_sdboot_entries_status.set_visible(True)
        hbox_sdboot_fix.set_visible(not _all_ok)
    else:
        hbox_sdboot_cmdline_status.set_visible(False)
        hbox_sdboot_entries_status.set_visible(False)
        hbox_sdboot_fix.set_visible(False)

    # GRUB splash check

    hbox_grub_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_grub_status.set_margin_start(10)
    hbox_grub_status.set_margin_top(6)
    lbl_grub_status = Gtk.Label(xalign=0)

    hbox_grub_fix = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_grub_fix.set_margin_start(10)
    hbox_grub_fix.set_margin_top(4)
    btn_grub_fix = Gtk.Button(label=_("Add quiet splash and run grub-mkconfig"))
    btn_grub_fix.set_size_request(280, 30)
    hbox_grub_fix.append(btn_grub_fix)

    if _bootloader == "grub":
        if plymouth.check_grub_splash():
            lbl_grub_status.set_markup(_("<b>OK:</b> <tt>GRUB_CMDLINE_LINUX_DEFAULT</tt> contains <tt>quiet splash</tt>."))
            btn_grub_fix.set_sensitive(False)
        else:
            lbl_grub_status.set_markup(
                _('<span foreground="#FFA500"><b>Warning:</b></span>'
                " <tt>GRUB_CMDLINE_LINUX_DEFAULT</tt> in <tt>/etc/default/grub</tt>"
                " is missing <tt>quiet splash</tt>.")
            )
        hbox_grub_status.append(lbl_grub_status)
        hbox_grub_status.set_visible(True)
        hbox_grub_fix.set_visible(not plymouth.check_grub_splash())
    else:
        hbox_grub_status.set_visible(False)
        hbox_grub_fix.set_visible(False)

    # limine / refind info

    hbox_bootloader_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bootloader_info.set_margin_start(10)
    hbox_bootloader_info.set_margin_top(6)
    lbl_bootloader_info = Gtk.Label(xalign=0)

    if _bootloader == "limine":
        lbl_bootloader_info.set_markup(
            _("Add <tt>quiet splash</tt> to the <tt>cmdline</tt>\nin your limine configuration file <tt>limine.conf</tt>")
        )
        hbox_bootloader_info.append(lbl_bootloader_info)
        hbox_bootloader_info.set_visible(True)
    elif _bootloader == "refind":
        lbl_bootloader_info.set_markup(
            _("Add <tt>quiet splash</tt> to the <tt>options</tt> line\n"
            "in your rEFInd stanza (<tt>/boot/EFI/refind/refind.conf</tt>).")
        )
        hbox_bootloader_info.append(lbl_bootloader_info)
        hbox_bootloader_info.set_visible(True)
    else:
        hbox_bootloader_info.set_visible(False)

    # hooks order warning

    hbox_hooks_warn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_hooks_warn.set_margin_start(10)
    hbox_hooks_warn.set_margin_top(6)
    lbl_hooks_warn = Gtk.Label(xalign=0)
    lbl_hooks_warn.set_markup(
        _('<span foreground="#FFA500"><b>Warning:</b></span>'
        " In <tt>/etc/mkinitcpio.conf</tt>, <tt>encrypt</tt>/<tt>lvm2</tt> appears before"
        " <tt>plymouth</tt>.\n"
        "Move <tt>plymouth</tt> before <tt>encrypt</tt>/<tt>sd-encrypt</tt>/<tt>lvm2</tt>"
        " so the splash screen renders correctly.")
    )
    hbox_hooks_warn.append(lbl_hooks_warn)
    hbox_hooks_warn.set_visible(not _is_dracut and not plymouth.check_hooks_order())

    # ── section: Early KMS ────────────────────────────────────────────────────

    hbox_sep_earlykms = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sep_earlykms.set_margin_top(10)
    hsep_earlykms = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_earlykms.set_hexpand(True)
    hsep_earlykms.set_vexpand(False)
    hbox_sep_earlykms.append(hsep_earlykms)

    hbox_section_earlykms = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_earlykms = Gtk.Label(xalign=0)
    lbl_section_earlykms.set_markup(_("<b>Early KMS</b>"))
    lbl_section_earlykms.set_margin_start(10)
    lbl_section_earlykms.set_margin_top(6)
    hbox_section_earlykms.append(lbl_section_earlykms)

    _in_vm = plymouth.is_virtual_machine()
    _gpu = None if _in_vm else plymouth.detect_gpu()
    _kms_module = plymouth.get_kms_module(_gpu)
    _gpu_name = None if _in_vm else plymouth.get_gpu_name()

    hbox_kms_detected = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_kms_detected.set_margin_start(10)
    hbox_kms_detected.set_margin_top(4)
    lbl_kms_detected_title = Gtk.Label(xalign=0)
    lbl_kms_detected_title.set_markup(_("Detected GPU"))
    lbl_kms_detected_title.set_size_request(120, -1)
    lbl_kms_detected = Gtk.Label(xalign=0)
    lbl_kms_detected.set_text(_gpu_name or _("Not detected"))
    hbox_kms_detected.append(lbl_kms_detected_title)
    hbox_kms_detected.append(lbl_kms_detected)

    hbox_kms_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_kms_status.set_margin_start(10)
    hbox_kms_status.set_margin_top(4)
    lbl_kms_status = Gtk.Label(xalign=0)
    hbox_kms_status.append(lbl_kms_status)

    hbox_kms_fix = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_kms_fix.set_margin_start(10)
    hbox_kms_fix.set_margin_top(6)
    btn_kms_fix = Gtk.Button(
        label=_("Add {module} to MODULES and rebuild initramfs").format(module=_kms_module or "kms module")
    )
    btn_kms_fix.set_size_request(340, 30)
    hbox_kms_fix.append(btn_kms_fix)

    hbox_kms_nvidia_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_kms_nvidia_info.set_margin_start(10)
    hbox_kms_nvidia_info.set_margin_top(4)
    lbl_kms_nvidia_info = Gtk.Label(xalign=0)
    lbl_kms_nvidia_info.set_markup(
        _("NVIDIA early KMS setup varies by driver (open vs proprietary).\n"
        "See the <tt>plymouth</tt> section of the Arch Wiki for your driver.")
    )
    hbox_kms_nvidia_info.append(lbl_kms_nvidia_info)

    if _is_dracut and _gpu in ("amd", "intel", "nvidia"):
        lbl_kms_nvidia_info.set_markup(
            _(
                "Dracut auto-detects KMS modules in most cases.\n"
                'For forced loading add e.g. <tt>force_drivers+=" amdgpu "</tt> to a file in\n'
                "<tt>/etc/dracut.conf.d/</tt> and run <tt>{command}</tt>."
            ).format(command=_rebuild_cmd)
        )
        hbox_kms_status.set_visible(False)
        hbox_kms_fix.set_visible(False)
        hbox_kms_nvidia_info.set_visible(True)
        hbox_sep_earlykms.set_visible(True)
        hbox_section_earlykms.set_visible(True)
        hbox_kms_detected.set_visible(True)
    elif _gpu in ("amd", "intel"):
        _kms_ok = plymouth.check_early_kms(_kms_module)
        if _kms_ok:
            lbl_kms_status.set_markup(
                _("<b>OK:</b> <tt>{module}</tt> is already in <tt>MODULES</tt> — early KMS active.").format(
                    module=_kms_module
                )
            )
        else:
            lbl_kms_status.set_markup(
                _(
                    '<span foreground="#FFA500"><b>Warning:</b></span>'
                    " <tt>{module}</tt> not in <tt>MODULES</tt> in <tt>/etc/mkinitcpio.conf</tt>."
                ).format(module=_kms_module)
            )
        hbox_kms_status.set_visible(True)
        hbox_kms_fix.set_visible(not _kms_ok)
        hbox_kms_nvidia_info.set_visible(False)
        hbox_sep_earlykms.set_visible(True)
        hbox_section_earlykms.set_visible(True)
        hbox_kms_detected.set_visible(True)
    elif _gpu == "nvidia":
        hbox_kms_status.set_visible(False)
        hbox_kms_fix.set_visible(False)
        hbox_kms_nvidia_info.set_visible(True)
        hbox_sep_earlykms.set_visible(True)
        hbox_section_earlykms.set_visible(True)
        hbox_kms_detected.set_visible(True)
    else:
        hbox_sep_earlykms.set_visible(False)
        hbox_section_earlykms.set_visible(False)
        hbox_kms_detected.set_visible(False)
        hbox_kms_status.set_visible(False)
        hbox_kms_fix.set_visible(False)
        hbox_kms_nvidia_info.set_visible(False)

    # ── section: Installed themes ──────────────────────────────────────────

    hbox_sep_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sep_install.set_margin_top(10)
    hsep_install = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_install.set_hexpand(True)
    hsep_install.set_vexpand(False)
    hbox_sep_install.append(hsep_install)

    hbox_section_installed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_installed = Gtk.Label(xalign=0)
    lbl_section_installed.set_markup(_("<b>Installed themes</b>"))
    lbl_section_installed.set_margin_start(10)
    lbl_section_installed.set_margin_top(6)
    hbox_section_installed.append(lbl_section_installed)

    # initramfs plymouth-module warning (dracut or mkinitcpio)

    if _is_dracut:
        _hook_ok = plymouth.check_dracut_plymouth_enabled()
        _hook_warn_markup = _(
            '<span foreground="#FFA500"><b>Warning:</b></span>'
            " plymouth dracut module not active — themes will not render at boot."
        )
        _hook_btn_label = _("Enable plymouth dracut module")
    else:
        _mkinitcpio_lines = fn.get_lines("/etc/mkinitcpio.conf") or []
        _hook_ok = any("plymouth" in line for line in _mkinitcpio_lines if line.strip().startswith("HOOKS="))
        _hook_warn_markup = _(
            '<span foreground="#FFA500"><b>Warning:</b></span>'
            " plymouth hook not found in /etc/mkinitcpio.conf — themes will not render at boot."
        )
        _hook_btn_label = _("Add plymouth hook to mkinitcpio.conf")

    hbox_hook_warn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_hook_warn.set_margin_start(10)
    hbox_hook_warn.set_margin_top(4)
    lbl_hook_warn = Gtk.Label(xalign=0)
    lbl_hook_warn.set_markup(_hook_warn_markup)
    hbox_hook_warn.append(lbl_hook_warn)
    hbox_hook_warn.set_visible(not _hook_ok)

    hbox_fix_hook = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fix_hook.set_margin_start(10)
    hbox_fix_hook.set_margin_top(4)
    btn_fix_hook = Gtk.Button(label=_hook_btn_label)
    btn_fix_hook.set_size_request(280, 30)
    hbox_fix_hook.append(btn_fix_hook)
    hbox_fix_hook.set_visible(not _hook_ok)

    hbox_current = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_current.set_margin_start(10)
    hbox_current.set_margin_top(6)
    lbl_current_title = Gtk.Label(xalign=0)
    lbl_current_title.set_markup(_("<b>Active theme</b>"))
    lbl_current_title.set_size_request(120, -1)
    lbl_current = Gtk.Label(xalign=0)
    lbl_current.set_text("")
    hbox_current.append(lbl_current_title)
    hbox_current.append(lbl_current)

    hbox_select = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_select.set_margin_start(10)
    hbox_select.set_margin_top(6)
    lbl_select = Gtk.Label(xalign=0)
    lbl_select.set_markup(_("Select theme"))
    lbl_select.set_size_request(120, -1)
    dd_installed = Gtk.ComboBoxText()
    hbox_select.append(lbl_select)
    hbox_select.append(dd_installed)

    hbox_apply = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_apply.set_margin_start(10)
    hbox_apply.set_margin_top(6)
    btn_apply = Gtk.Button(label=_("Apply theme"))
    btn_apply.set_size_request(140, 30)
    hbox_apply.append(btn_apply)

    hbox_apply_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_apply_desc.set_margin_start(10)
    hbox_apply_desc.set_margin_top(4)
    lbl_apply_desc = Gtk.Label(xalign=0)
    lbl_apply_desc.set_markup(
        _(
            "Applying a theme sets it with <tt>plymouth-set-default-theme</tt> then\n"
            "rebuilds the initramfs with <tt>{command}</tt>. This takes a few seconds."
        ).format(command=_rebuild_label)
    )
    hbox_apply_desc.append(lbl_apply_desc)

    hbox_reset = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_reset.set_margin_start(10)
    hbox_reset.set_margin_top(6)
    btn_reset = Gtk.Button(label=_("Reset to {distro} default").format(distro=fn.distr.capitalize()))
    btn_reset.set_size_request(200, 30)
    hbox_reset.append(btn_reset)
    hbox_reset.set_visible(_default_theme is not None)

    # ── section: Available themes ──────────────────────────────────────────

    hbox_sep_installed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sep_installed.set_margin_top(10)
    hsep_installed = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_installed.set_hexpand(True)
    hsep_installed.set_vexpand(False)
    hbox_sep_installed.append(hsep_installed)

    hbox_section_available = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_available = Gtk.Label(xalign=0)
    lbl_section_available.set_markup(_("<b>Available themes</b>"))
    lbl_section_available.set_margin_start(10)
    lbl_section_available.set_margin_top(6)
    lbl_section_available.set_hexpand(True)
    hbox_section_available.append(lbl_section_available)
    btn_refresh_avail = Gtk.Button(label=_("Refresh list"))
    btn_refresh_avail.set_size_request(100, 28)
    btn_refresh_avail.set_margin_end(10)
    btn_refresh_avail.set_margin_top(4)
    hbox_section_available.append(btn_refresh_avail)

    hbox_avail_select = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_avail_select.set_margin_start(10)
    hbox_avail_select.set_margin_top(6)
    lbl_avail_select = Gtk.Label(xalign=0)
    lbl_avail_select.set_markup(_("Select package"))
    lbl_avail_select.set_size_request(120, -1)
    dd_available = Gtk.ComboBoxText()
    hbox_avail_select.append(lbl_avail_select)
    hbox_avail_select.append(dd_available)

    hbox_install_theme = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_install_theme.set_margin_start(10)
    hbox_install_theme.set_margin_top(6)
    btn_install_theme = Gtk.Button(label=_("Install theme"))
    btn_install_theme.set_size_request(140, 30)
    hbox_install_theme.append(btn_install_theme)

    hbox_install_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_install_note.set_margin_start(10)
    hbox_install_note.set_margin_top(4)
    lbl_install_note = Gtk.Label(xalign=0)
    lbl_install_note.set_markup(
        _('<span foreground="#FFA500"><b>Note:</b></span>'
        " Installing a theme does not activate it."
        " Go to <b>Select theme</b> above and click <b>Apply theme</b>.")
    )
    hbox_install_note.append(lbl_install_note)

    aur_helper = fn.get_aur_helper()
    repo_active = fn.check_nemesis_repo_active() or fn.check_chaotic_aur_active()
    if not aur_helper and not repo_active:
        btn_install_theme.set_sensitive(False)
        lbl_no_aur = Gtk.Label(xalign=0)
        lbl_no_aur.set_markup(_("<i>No AUR helper (paru/yay) or active repo found</i>"))
        lbl_no_aur.set_margin_start(10)
        hbox_install_theme.append(lbl_no_aur)

    # ── populate dropdowns ─────────────────────────────────────────────────

    def populate_installed():
        dd_installed.remove_all()
        themes = plymouth.list_themes()
        current = plymouth.get_current_theme()
        for t in themes:
            dd_installed.append_text(t)
        if current in themes:
            dd_installed.set_active(themes.index(current))
        elif themes:
            dd_installed.set_active(0)

    def populate_available():
        dd_available.remove_all()
        pkgs = plymouth.list_available_packages()
        for p in pkgs:
            dd_available.append_text(p)
        if pkgs:
            dd_available.set_active(0)
        btn_install_theme.set_sensitive(bool(pkgs) and (aur_helper is not None or repo_active))

    def _refresh_plymouth(_widget):
        if _plymouth_initialized[0]:
            return
        _plymouth_initialized[0] = True
        installed = fn.check_package_installed("plymouth")
        lbl_plymouth_installed.set_visible(installed)
        btn_install_plymouth.set_visible(not installed)
        btn_remove_plymouth.set_visible(installed)
        if not installed:
            return

        def _load_initial_data():
            themes = plymouth.list_themes()
            current = plymouth.get_current_theme()
            pkgs = plymouth.list_available_packages()

            def _apply():
                dd_installed.remove_all()
                for t in themes:
                    dd_installed.append_text(t)
                if current in themes:
                    dd_installed.set_active(themes.index(current))
                elif themes:
                    dd_installed.set_active(0)
                fn.log_info(f"Plymouth: {len(themes)} installed theme(s)")
                lbl_current.set_text(current)
                dd_available.remove_all()
                for p in pkgs:
                    dd_available.append_text(p)
                if pkgs:
                    dd_available.set_active(0)
                fn.log_info(f"Plymouth: {len(pkgs)} AUR theme(s) available")
                btn_install_theme.set_sensitive(bool(pkgs) and (aur_helper is not None or repo_active))
                return False

            fn.GLib.idle_add(_apply)

        fn.threading.Thread(target=_load_initial_data, daemon=True).start()

    # ── callbacks ──────────────────────────────────────────────────────────

    def on_install_plymouth_clicked(_widget):
        fn.log_subsection("Installing Plymouth — full setup")
        fn.show_in_app_notification(self, _("Installing Plymouth..."))
        btn_install_plymouth.set_sensitive(False)

        if _is_dracut:
            script = (
                "set -euo pipefail\n"
                'trap \'echo ""; read -p "Press Enter to close..."\' EXIT\n'
                "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)\n"
                'echo "${CYAN}Step 1/2 — Installing plymouth...${RESET}"\n'
                "pacman -S --noconfirm plymouth\n"
                'echo ""\n'
                f'echo "${{CYAN}}Step 2/2 — Rebuilding initramfs ({_rebuild_label})...${{RESET}}"\n'
                f"{_rebuild_cmd}\n"
                'echo ""\n'
                'echo "${GREEN}Plymouth installation complete.${RESET}"\n'
            )
        else:
            script = (
                "set -euo pipefail\n"
                'trap \'echo ""; read -p "Press Enter to close..."\' EXIT\n'
                "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)\n"
                'echo "${CYAN}Step 1/3 — Installing plymouth...${RESET}"\n'
                "pacman -S --noconfirm plymouth\n"
                'echo ""\n'
                'echo "${CYAN}Step 2/3 — Adding plymouth hook to /etc/mkinitcpio.conf...${RESET}"\n'
                "if grep -qP '(?:^|\\s)plymouth(?:\\s|$)' /etc/mkinitcpio.conf; then\n"
                "    echo '  plymouth hook already present — skipping'\n"
                "else\n"
                "    cp /etc/mkinitcpio.conf /etc/mkinitcpio.conf-bak\n"
                "    if grep -qP '\\bkms\\b' /etc/mkinitcpio.conf; then\n"
                "        sed -i 's/\\bkms\\b/kms plymouth/' /etc/mkinitcpio.conf\n"
                "        echo '  plymouth hook added after kms'\n"
                "    else\n"
                "        sed -i 's/\\budev\\b/udev plymouth/' /etc/mkinitcpio.conf\n"
                "        echo '  plymouth hook added after udev (kms not in HOOKS)'\n"
                "    fi\n"
                "fi\n"
                'echo ""\n'
                f'echo "${{CYAN}}Step 3/3 — Rebuilding initramfs ({_rebuild_label})...${{RESET}}"\n'
                f"{_rebuild_cmd}\n"
                'echo ""\n'
                'echo "${GREEN}Plymouth installation complete.${RESET}"\n'
            )

        def run_install():
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.invalidate_pkg_cache()
            fn.GLib.idle_add(on_install_plymouth_done)

        fn.threading.Thread(target=run_install, daemon=True).start()

    def on_install_plymouth_done():
        btn_install_plymouth.set_sensitive(True)
        if fn.check_package_installed("plymouth"):
            fn.log_success("Plymouth installed — refreshing theme manager")
            lbl_plymouth_installed.set_visible(True)
            btn_install_plymouth.set_visible(False)
            btn_remove_plymouth.set_visible(True)
            if _is_dracut:
                module_ok = plymouth.check_dracut_plymouth_enabled()
            else:
                lines = fn.get_lines("/etc/mkinitcpio.conf") or []
                module_ok = any("plymouth" in line for line in lines if line.strip().startswith("HOOKS="))
            hbox_hook_warn.set_visible(not module_ok)
            hbox_fix_hook.set_visible(not module_ok)
            lbl_current.set_text(plymouth.get_current_theme())
            populate_installed()
            populate_available()
        else:
            fn.log_warn("Plymouth package not found after install — check terminal output")

    def on_remove_plymouth_clicked(_widget):
        fn.log_subsection("Removing Plymouth — full cleanup")
        fn.show_in_app_notification(self, _("Removing Plymouth..."))
        btn_remove_plymouth.set_sensitive(False)

        bootloader = plymouth.detect_bootloader()
        sd_entries = plymouth.find_systemd_boot_entries() if bootloader == "systemd-boot" else []
        has_cmdline_file = plymouth.check_kernel_cmdline_exists()

        # Step 1 — initramfs config strip
        if _is_dracut:
            step1_header = "Step 1/5 — Remove plymouth dracut config"
            step1_body = (
                "if [ -f /etc/dracut.conf.d/att-plymouth.conf ]; then\n"
                "    rm /etc/dracut.conf.d/att-plymouth.conf\n"
                '    echo "  removed: /etc/dracut.conf.d/att-plymouth.conf"\n'
                "else\n"
                '    echo "  /etc/dracut.conf.d/att-plymouth.conf not present — nothing to remove"\n'
                "fi\n"
            )
        else:
            step1_header = "Step 1/5 — Strip plymouth hook from /etc/mkinitcpio.conf"
            step1_body = (
                "if grep -qP '(?:^|\\s)plymouth(?:\\s|$)' /etc/mkinitcpio.conf; then\n"
                "    cp /etc/mkinitcpio.conf /etc/mkinitcpio.conf-bak\n"
                "    before=$(grep -E '^HOOKS=' /etc/mkinitcpio.conf)\n"
                "    sed -i -E 's/\\bplymouth\\b//; s/  +/ /g; s/\\( /(/; s/ \\)/)/' /etc/mkinitcpio.conf\n"
                "    after=$(grep -E '^HOOKS=' /etc/mkinitcpio.conf)\n"
                '    echo "  before: $before"\n'
                '    echo "  after:  $after"\n'
                '    echo "  backup: /etc/mkinitcpio.conf-bak"\n'
                "else\n"
                '    echo "  plymouth hook not present — nothing to strip"\n'
                "fi\n"
            )

        # Step 4 — bootloader cmdline strip (prompted)
        if bootloader == "systemd-boot":
            step4_header = "Step 4/5 — Strip 'quiet splash' from kernel cmdline (systemd-boot)"
            cmdline_strip = ""
            if has_cmdline_file:
                cmdline_strip = (
                    "        cp /etc/kernel/cmdline /etc/kernel/cmdline-bak\n"
                    "        before=$(cat /etc/kernel/cmdline)\n"
                    '        new=$(awk \'{out=""; for(i=1;i<=NF;i++) if($i!="quiet" && $i!="splash")'
                    ' out=(out==""?$i:out" "$i); print out}\' /etc/kernel/cmdline)\n'
                    '        echo "$new" > /etc/kernel/cmdline\n'
                    '        echo "  /etc/kernel/cmdline:"\n'
                    '        echo "    before: $before"\n'
                    '        echo "    after:  $new"\n'
                )
            entries_strip = ""
            if sd_entries:
                quoted = " ".join("'" + e.replace("'", "'\\''") + "'" for e in sd_entries)
                entries_strip = (
                    f"        for entry in {quoted}; do\n"
                    '            if [ -f "$entry" ]; then\n'
                    '                cp "$entry" "$entry-bak"\n'
                    '                before=$(grep -E "^options" "$entry" || true)\n'
                    "                awk '/^options / {out=$1; for(i=2;i<=NF;i++)"
                    ' if($i!="quiet" && $i!="splash") out=out" "$i; print out; next} {print}\''
                    ' "$entry" > "$entry.tmp" && mv "$entry.tmp" "$entry"\n'
                    '                after=$(grep -E "^options" "$entry" || true)\n'
                    '                echo "  $entry:"\n'
                    '                echo "    before: $before"\n'
                    '                echo "    after:  $after"\n'
                    "            fi\n"
                    "        done\n"
                )
            step4_body = (
                '    read -rp "  Strip now? [Y/n] (Recommended: Y — splash is dead without plymouth) " ans\n'
                '    case "${ans,,}" in\n'
                "        n|no)\n"
                '            echo "  skipped"\n'
                "            ;;\n"
                "        *)\n"
                + cmdline_strip
                + entries_strip
                + "            ;;\n"
                "    esac\n"
            )
        elif bootloader == "grub":
            step4_header = "Step 4/5 — Strip 'quiet splash' from kernel cmdline (GRUB)"
            step4_body = (
                '    read -rp "  Strip now? [Y/n] (Recommended: Y — splash is dead without plymouth) " ans\n'
                '    case "${ans,,}" in\n'
                "        n|no)\n"
                '            echo "  skipped"\n'
                "            ;;\n"
                "        *)\n"
                "            cp /etc/default/grub /etc/default/grub-bak\n"
                "            before=$(grep -E '^GRUB_CMDLINE_LINUX_DEFAULT=' /etc/default/grub)\n"
                "            current=$(awk -F'=' '/^GRUB_CMDLINE_LINUX_DEFAULT=/"
                ' {sub(/^[^=]+=/, ""); print; exit}\' /etc/default/grub)\n'
                '            current="${current#[\\"\\\']}"\n'
                '            current="${current%[\\"\\\']}"\n'
                '            new=$(echo "$current" | awk \'{out=""; for(i=1;i<=NF;i++)'
                ' if($i!="quiet" && $i!="splash") out=(out==""?$i:out" "$i); print out}\')\n'
                '            sed -i "s|^GRUB_CMDLINE_LINUX_DEFAULT=.*'
                '|GRUB_CMDLINE_LINUX_DEFAULT=\\"$new\\"|" /etc/default/grub\n'
                '            echo "  before: $before"\n'
                '            echo "  after:  GRUB_CMDLINE_LINUX_DEFAULT=\\"$new\\""\n'
                '            echo "  backup: /etc/default/grub-bak"\n'
                '            echo ""\n'
                '            echo "${CYAN}  Regenerating grub.cfg...${RESET}"\n'
                "            grub-mkconfig -o /boot/grub/grub.cfg\n"
                "            ;;\n"
                "    esac\n"
            )
        else:
            step4_header = f"Step 4/5 — Bootloader '{bootloader}' — cmdline strip not automated"
            step4_body = (
                "    echo \"  If your bootloader's kernel cmdline contains 'quiet splash',\"\n"
                '    echo "  remove them manually."\n'
            )

        script = (
            "set -euo pipefail\n"
            "trap 'echo \"\"; read -p \"Press Enter to close...\"' EXIT\n"
            "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2); YELLOW=$(tput setaf 3)\n"
            f'echo "${{CYAN}}{step1_header}...${{RESET}}"\n'
            f"{step1_body}"
            'echo ""\n'
            'echo "${CYAN}Step 2/5 — Check for plymouth-theme-* packages...${RESET}"\n'
            "themes=$(pacman -Qq | grep '^plymouth-theme-' || true)\n"
            'if [ -n "$themes" ]; then\n'
            '    echo "  Found:"\n'
            "    echo \"$themes\" | sed 's/^/    /'\n"
            '    echo ""\n'
            '    echo "  Note: these depend on plymouth — removing plymouth requires removing them too."\n'
            '    read -rp "  Remove these packages? [Y/n] (Recommended: Y — they break without plymouth) " ans\n'
            '    case "${ans,,}" in\n'
            "        n|no)\n"
            '            echo "${YELLOW}  Keeping themes — aborting plymouth removal '
            '(would break dependencies).${RESET}"\n'
            '            echo "${YELLOW}  Re-run and answer Y, or remove plymouth manually '
            'with pacman -Rc plymouth.${RESET}"\n'
            "            exit 0\n"
            "            ;;\n"
            "        *)\n"
            "            pacman -R --noconfirm $themes\n"
            "            ;;\n"
            "    esac\n"
            "else\n"
            '    echo "  None installed"\n'
            "fi\n"
            'echo ""\n'
            'echo "${CYAN}Step 3/5 — Remove plymouth package...${RESET}"\n'
            "pacman -R --noconfirm plymouth\n"
            'echo ""\n'
            f'echo "${{CYAN}}{step4_header}...${{RESET}}"\n'
            f"{step4_body}"
            'echo ""\n'
            f'echo "${{CYAN}}Step 5/5 — Rebuild initramfs ({_rebuild_label})...${{RESET}}"\n'
            f"{_rebuild_cmd}\n"
            'echo ""\n'
            'echo "${GREEN}Plymouth removal complete — reboot to apply.${RESET}"\n'
        )

        def run_remove():
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.invalidate_pkg_cache()
            fn.GLib.idle_add(on_remove_plymouth_done)

        fn.threading.Thread(target=run_remove, daemon=True).start()

    def on_remove_plymouth_done():
        btn_remove_plymouth.set_sensitive(True)
        still_installed = fn.check_package_installed("plymouth")
        if not still_installed:
            fn.log_success("Plymouth removed")
            lbl_plymouth_installed.set_visible(False)
            btn_install_plymouth.set_visible(True)
            btn_remove_plymouth.set_visible(False)
            hbox_hook_warn.set_visible(False)
            hbox_fix_hook.set_visible(False)
        else:
            fn.log_warn("Plymouth still installed — check terminal output")

    def on_apply_clicked(_widget):
        selected = dd_installed.get_active_text()
        if not selected:
            fn.log_warn("No Plymouth theme selected")
            return
        fn.log_subsection(f"Applying Plymouth theme: {selected}")
        fn.show_in_app_notification(self, _("Applying Plymouth theme: {name}").format(name=selected))
        script = (
            "set -euo pipefail\n"
            'trap \'echo ""; read -p "Press Enter to close..."\' EXIT\n'
            "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)\n"
            f'echo "${{CYAN}}Step 1/2 — Setting Plymouth theme to {selected}...${{RESET}}"\n'
            f"plymouth-set-default-theme {selected}\n"
            'echo ""\n'
            f'echo "${{CYAN}}Step 2/2 — Rebuilding initramfs ({_rebuild_label})...${{RESET}}"\n'
            f"{_rebuild_cmd}\n"
            'echo ""\n'
            f'echo "${{GREEN}}Plymouth theme applied: {selected}${{RESET}}"\n'
        )

        def run_apply():
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.invalidate_pkg_cache()
            if fn.distr == "omarchy":
                settings = fn.read_att_settings()
                settings["omarchy_plymouth_customized"] = True
                fn.write_att_settings(settings)
                fn.log_info("ATT Omarchy Plymouth marker saved to att_settings.json")
            fn.GLib.idle_add(refresh_after_apply)

        fn.threading.Thread(target=run_apply, daemon=True).start()

    def refresh_after_apply():
        new_theme = plymouth.get_current_theme()
        lbl_current.set_text(new_theme)
        fn.log_success(f"Plymouth theme now: {new_theme}")
        populate_installed()

    def on_install_theme_clicked(_widget):
        selected = dd_available.get_active_text()
        if not selected:
            fn.log_warn("No Plymouth package selected")
            return
        fn.log_subsection(f"Installing Plymouth theme package: {selected}")
        fn.show_in_app_notification(self, _("Installing: {name}").format(name=selected))

        def run_install():
            if aur_helper:
                process = fn.launch_aur_install_in_terminal(aur_helper, selected)
            else:
                process = fn.launch_pacman_install_in_terminal(selected)
            if process:
                process.wait()
                fn.invalidate_pkg_cache()
            fn.GLib.idle_add(refresh_after_install)

        fn.threading.Thread(target=run_install, daemon=True).start()

    def refresh_after_install():
        populate_installed()
        populate_available()
        fn.log_success("Plymouth theme list refreshed")

    def on_reset_clicked(_widget):
        fn.log_subsection(f"Resetting Plymouth theme to {fn.distr.capitalize()} default")
        fn.show_in_app_notification(self, _("Resetting Plymouth theme to {name}...").format(name=_default_theme))
        themes = plymouth.list_themes()
        if _default_theme in themes:
            dd_installed.set_active(themes.index(_default_theme))
        script = (
            "set -euo pipefail\n"
            'trap \'echo ""; read -p "Press Enter to close..."\' EXIT\n'
            "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)\n"
            f'echo "${{CYAN}}Step 1/2 — Setting Plymouth theme to {_default_theme}...${{RESET}}"\n'
            f"plymouth-set-default-theme {_default_theme}\n"
            'echo ""\n'
            f'echo "${{CYAN}}Step 2/2 — Rebuilding initramfs ({_rebuild_label})...${{RESET}}"\n'
            f"{_rebuild_cmd}\n"
            'echo ""\n'
            f'echo "${{GREEN}}Plymouth theme reset to: {_default_theme}${{RESET}}"\n'
        )

        def run_reset():
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.invalidate_pkg_cache()
            fn.GLib.idle_add(refresh_after_apply)

        fn.threading.Thread(target=run_reset, daemon=True).start()

    def on_refresh_avail_clicked(_widget):
        fn.log_subsection("Refreshing Plymouth available themes...")
        fn.show_in_app_notification(self, _("Refreshing available themes..."))
        btn_refresh_avail.set_sensitive(False)

        def _fetch():
            pkgs = plymouth.list_available_packages()
            themes = plymouth.list_themes()
            current = plymouth.get_current_theme()

            def _update():
                dd_available.remove_all()
                for p in pkgs:
                    dd_available.append_text(p)
                if pkgs:
                    dd_available.set_active(0)
                btn_install_theme.set_sensitive(bool(pkgs) and (aur_helper is not None or repo_active))
                dd_installed.remove_all()
                for t in themes:
                    dd_installed.append_text(t)
                if current in themes:
                    dd_installed.set_active(themes.index(current))
                elif themes:
                    dd_installed.set_active(0)
                lbl_current.set_text(current)
                btn_refresh_avail.set_sensitive(True)
                fn.log_success("Plymouth theme list refreshed")

            fn.GLib.idle_add(_update)

        fn.threading.Thread(target=_fetch, daemon=True).start()

    def on_sdboot_fix_clicked(_widget):
        fn.log_subsection("Adding quiet splash to cmdline + entries")
        fn.show_in_app_notification(self, _("Adding quiet splash to cmdline + entries..."))
        btn_sdboot_fix.set_sensitive(False)

        def run_both():
            if _use_cmdline:
                try:
                    content = open(plymouth.KERNEL_CMDLINE).read().rstrip()
                    tokens = content.split()
                    if "quiet" not in tokens:
                        content += " quiet"
                    if "splash" not in tokens:
                        content += " splash"
                    open(plymouth.KERNEL_CMDLINE, "w").write(content.strip() + "\n")
                    fn.log_info(f"Patched: {plymouth.KERNEL_CMDLINE}")
                except OSError as e:
                    fn.log_error(f"Could not patch {plymouth.KERNEL_CMDLINE}: {e}")
            missing, _unused = plymouth.check_systemd_boot_splash()
            for path in missing:
                try:
                    lines = open(path).readlines()
                    new_lines = []
                    for line in lines:
                        if line.strip().startswith("options"):
                            stripped = line.rstrip()
                            tokens = stripped.split()
                            if "quiet" not in tokens:
                                stripped += " quiet"
                            if "splash" not in tokens:
                                stripped += " splash"
                            new_lines.append(stripped + "\n")
                        else:
                            new_lines.append(line)
                    open(path, "w").writelines(new_lines)
                    fn.log_info(f"Patched: {path}")
                except OSError as e:
                    fn.log_error(f"Could not patch {path}: {e}")
            fn.GLib.idle_add(refresh_sdboot_status)

        fn.threading.Thread(target=run_both, daemon=True).start()

    def refresh_sdboot_status():
        cmdline_ok = plymouth.check_kernel_cmdline_splash() if _use_cmdline else True
        new_missing, _unused = plymouth.check_systemd_boot_splash()
        entries_ok = not bool(new_missing)
        all_ok = cmdline_ok and entries_ok
        if _use_cmdline:
            if cmdline_ok:
                lbl_sdboot_cmdline_status.set_markup(
                    _("<b>OK:</b> <tt>/etc/kernel/cmdline</tt> contains <tt>quiet splash</tt>.")
                )
            else:
                lbl_sdboot_cmdline_status.set_markup(
                    _('<span foreground="#FFA500"><b>Warning:</b></span>'
                    " <tt>/etc/kernel/cmdline</tt> is missing <tt>quiet splash</tt>.")
                )
        if entries_ok:
            lbl_sdboot_entries_status.set_markup(_("<b>OK:</b> all boot entries contain <tt>quiet splash</tt>."))
        else:
            n = len(new_missing)
            lbl_sdboot_entries_status.set_markup(
                ngettext(
                    '<span foreground="#FFA500"><b>Warning:</b></span> {count} boot entry missing <tt>quiet splash</tt>.',
                    '<span foreground="#FFA500"><b>Warning:</b></span> {count} boot entries missing <tt>quiet splash</tt>.',
                    n,
                ).format(count=n)
            )
        if all_ok:
            hbox_sdboot_fix.set_visible(False)
        else:
            btn_sdboot_fix.set_sensitive(True)
        fn.log_success("systemd-boot splash status refreshed")

    def on_fix_hook_clicked(_widget):
        if _is_dracut:
            fn.log_subsection("Enabling plymouth dracut module")
            fn.show_in_app_notification(self, _("Writing dracut conf and rebuilding initramfs..."))
            btn_fix_hook.set_sensitive(False)
            script = (
                "set -euo pipefail\n"
                'trap \'echo ""; read -p "Press Enter to close..."\' EXIT\n'
                "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)\n"
                'echo "${CYAN}Step 1/2 — Writing /etc/dracut.conf.d/att-plymouth.conf...${RESET}"\n'
                "mkdir -p /etc/dracut.conf.d\n"
                "echo 'add_dracutmodules+=\" plymouth \"' > /etc/dracut.conf.d/att-plymouth.conf\n"
                "echo '  module enabled'\n"
                'echo ""\n'
                f'echo "${{CYAN}}Step 2/2 — Rebuilding initramfs ({_rebuild_label})...${{RESET}}"\n'
                f"{_rebuild_cmd}\n"
                'echo ""\n'
                'echo "${GREEN}Done.${RESET}"\n'
            )
        else:
            fn.log_subsection("Adding plymouth hook to /etc/mkinitcpio.conf")
            fn.show_in_app_notification(self, _("Adding plymouth hook and rebuilding initramfs..."))
            btn_fix_hook.set_sensitive(False)
            script = (
                "set -euo pipefail\n"
                'trap \'echo ""; read -p "Press Enter to close..."\' EXIT\n'
                "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)\n"
                'echo "${CYAN}Step 1/2 — Adding plymouth hook to /etc/mkinitcpio.conf...${RESET}"\n'
                "if grep -qP '(?:^|\\s)plymouth(?:\\s|$)' /etc/mkinitcpio.conf; then\n"
                "    echo '  plymouth hook already present — skipping'\n"
                "else\n"
                "    cp /etc/mkinitcpio.conf /etc/mkinitcpio.conf-bak\n"
                "    if grep -qP '\\bkms\\b' /etc/mkinitcpio.conf; then\n"
                "        sed -i 's/\\bkms\\b/kms plymouth/' /etc/mkinitcpio.conf\n"
                "        echo '  plymouth hook added after kms'\n"
                "    else\n"
                "        sed -i 's/\\budev\\b/udev plymouth/' /etc/mkinitcpio.conf\n"
                "        echo '  plymouth hook added after udev (kms not in HOOKS)'\n"
                "    fi\n"
                "fi\n"
                'echo ""\n'
                f'echo "${{CYAN}}Step 2/2 — Rebuilding initramfs ({_rebuild_label})...${{RESET}}"\n'
                f"{_rebuild_cmd}\n"
                'echo ""\n'
                'echo "${GREEN}Done.${RESET}"\n'
            )

        def run_fix_hook():
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.GLib.idle_add(refresh_hook_status)

        fn.threading.Thread(target=run_fix_hook, daemon=True).start()

    def refresh_hook_status():
        if _is_dracut:
            hook_present = plymouth.check_dracut_plymouth_enabled()
            success_msg = "plymouth dracut module enabled"
            warn_msg = "plymouth dracut module still not active — check terminal output"
        else:
            lines = fn.get_lines("/etc/mkinitcpio.conf") or []
            hook_present = any("plymouth" in line for line in lines if line.strip().startswith("HOOKS="))
            success_msg = "plymouth hook added to /etc/mkinitcpio.conf"
            warn_msg = "plymouth hook still not found — check terminal output"
        hbox_hook_warn.set_visible(not hook_present)
        hbox_fix_hook.set_visible(not hook_present)
        if hook_present:
            fn.log_success(success_msg)
        else:
            btn_fix_hook.set_sensitive(True)
            fn.log_warn(warn_msg)

    def on_kms_fix_clicked(_widget):
        fn.log_subsection(f"Adding {_kms_module} to MODULES for early KMS")
        fn.show_in_app_notification(self, _("Adding {module} to MODULES...").format(module=_kms_module))
        btn_kms_fix.set_sensitive(False)
        script = (
            "set -euo pipefail\n"
            'trap \'echo ""; read -p "Press Enter to close..."\' EXIT\n'
            "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)\n"
            f'echo "${{CYAN}}Step 1/2 — Adding {_kms_module} to MODULES in /etc/mkinitcpio.conf...${{RESET}}"\n'
            "cp /etc/mkinitcpio.conf /etc/mkinitcpio.conf-bak\n"
            f"sed -i '/^MODULES=/{{ /\\b{_kms_module}\\b/! s/)/ {_kms_module})/ }}' /etc/mkinitcpio.conf\n"
            "echo '  module added'\n"
            'echo ""\n'
            f'echo "${{CYAN}}Step 2/2 — Rebuilding initramfs ({_rebuild_label})...${{RESET}}"\n'
            f"{_rebuild_cmd}\n"
            'echo ""\n'
            f'echo "${{GREEN}}{_kms_module} added — early KMS is now active.${{RESET}}"\n'
        )

        def run_kms():
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.GLib.idle_add(refresh_kms_status)

        fn.threading.Thread(target=run_kms, daemon=True).start()

    def refresh_kms_status():
        kms_ok = plymouth.check_early_kms(_kms_module)
        if kms_ok:
            lbl_kms_status.set_markup(
                _("<b>OK:</b> <tt>{module}</tt> is already in <tt>MODULES</tt> — early KMS active.").format(
                    module=_kms_module
                )
            )
            hbox_kms_fix.set_visible(False)
            fn.log_success(f"Early KMS enabled: {_kms_module} added to MODULES")
        else:
            btn_kms_fix.set_sensitive(True)
            fn.log_warn(f"{_kms_module} still not found in MODULES — check terminal output")

    def on_grub_fix_clicked(_widget):
        fn.log_subsection("Adding quiet splash to GRUB config")
        fn.show_in_app_notification(self, _("Patching GRUB config and regenerating..."))
        btn_grub_fix.set_sensitive(False)
        script = r"""set -euo pipefail
trap 'echo ""; read -p "Press Enter to close..."' EXIT
RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)

echo "${CYAN}Step 1/2 — Patching /etc/default/grub...${RESET}"

current=$(awk -F'=' '/^GRUB_CMDLINE_LINUX_DEFAULT=/ {sub(/^[^=]+=/, ""); print; exit}' /etc/default/grub)
current="${current#[\"\']}"
current="${current%[\"\']}"

new="$current"
case " $new " in *" quiet "*) ;; *) new="quiet $new" ;; esac
case " $new " in *" splash "*) ;; *) new="$new splash" ;; esac

if [ "$new" = "$current" ]; then
    echo "  quiet splash already present — skipping"
else
    cp /etc/default/grub /etc/default/grub-bak
    sed -i "s|^GRUB_CMDLINE_LINUX_DEFAULT=.*|GRUB_CMDLINE_LINUX_DEFAULT=\"$new\"|" /etc/default/grub
    echo "  updated: $new"
fi

echo ""
echo "${CYAN}Step 2/2 — Regenerating GRUB config...${RESET}"
grub-mkconfig -o /boot/grub/grub.cfg

echo ""
echo "${GREEN}Done.${RESET}"
"""

        def run_grub():
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.invalidate_pkg_cache()
            fn.GLib.idle_add(refresh_grub_status)

        fn.threading.Thread(target=run_grub, daemon=True).start()

    def refresh_grub_status():
        if plymouth.check_grub_splash():
            lbl_grub_status.set_markup(_("<b>OK:</b> <tt>GRUB_CMDLINE_LINUX_DEFAULT</tt> contains <tt>quiet splash</tt>."))
            hbox_grub_fix.set_visible(False)
        else:
            btn_grub_fix.set_sensitive(True)
        fn.log_success("GRUB splash status refreshed")

    btn_install_plymouth.connect("clicked", on_install_plymouth_clicked)
    btn_remove_plymouth.connect("clicked", on_remove_plymouth_clicked)
    btn_fix_hook.connect("clicked", on_fix_hook_clicked)
    btn_sdboot_fix.connect("clicked", on_sdboot_fix_clicked)
    btn_grub_fix.connect("clicked", on_grub_fix_clicked)
    btn_apply.connect("clicked", on_apply_clicked)
    btn_install_theme.connect("clicked", on_install_theme_clicked)
    btn_reset.connect("clicked", on_reset_clicked)
    btn_refresh_avail.connect("clicked", on_refresh_avail_clicked)
    if _kms_module:
        btn_kms_fix.connect("clicked", on_kms_fix_clicked)

    # ── layout ─────────────────────────────────────────────────────────────

    vboxstack_plymouth.append(hbox_title)
    vboxstack_plymouth.append(hbox_sep_top)
    vboxstack_plymouth.append(hbox_section_install)
    vboxstack_plymouth.append(hbox_install_desc)
    vboxstack_plymouth.append(hbox_install_plymouth)
    vboxstack_plymouth.append(hbox_sep_bootloader)
    vboxstack_plymouth.append(hbox_section_bootloader)
    vboxstack_plymouth.append(hbox_bootloader_detected)
    vboxstack_plymouth.append(hbox_sdboot_cmdline_status)
    vboxstack_plymouth.append(hbox_sdboot_entries_status)
    vboxstack_plymouth.append(hbox_sdboot_fix)
    vboxstack_plymouth.append(hbox_grub_status)
    vboxstack_plymouth.append(hbox_grub_fix)
    vboxstack_plymouth.append(hbox_bootloader_info)
    vboxstack_plymouth.append(hbox_hooks_warn)
    vboxstack_plymouth.append(hbox_sep_earlykms)
    vboxstack_plymouth.append(hbox_section_earlykms)
    vboxstack_plymouth.append(hbox_kms_detected)
    vboxstack_plymouth.append(hbox_kms_status)
    vboxstack_plymouth.append(hbox_kms_fix)
    vboxstack_plymouth.append(hbox_kms_nvidia_info)
    vboxstack_plymouth.append(hbox_sep_install)
    vboxstack_plymouth.append(hbox_section_installed)
    vboxstack_plymouth.append(hbox_hook_warn)
    vboxstack_plymouth.append(hbox_fix_hook)
    vboxstack_plymouth.append(hbox_current)
    vboxstack_plymouth.append(hbox_select)
    vboxstack_plymouth.append(hbox_apply)
    vboxstack_plymouth.append(hbox_apply_desc)
    vboxstack_plymouth.append(hbox_reset)
    vboxstack_plymouth.append(hbox_sep_installed)
    vboxstack_plymouth.append(hbox_section_available)
    vboxstack_plymouth.append(hbox_avail_select)
    vboxstack_plymouth.append(hbox_install_theme)
    vboxstack_plymouth.append(hbox_install_note)

    _refresh_plymouth(None)

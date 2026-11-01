# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools


def gui(self, Gtk, Pango, vboxstack_sddm, sddm, fn):
    """Create the SDDM login manager configuration GUI."""
    simplicity_pkg, simplicity_id = sddm.simplicity_theme()
    _pkg = fn.check_packages_installed(["sddm", "sddm-git", simplicity_pkg])

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    if fn.check_content("sddm", fn.display_manager_service):
        lbl_title.set_text("Sddm (active)")
    else:
        lbl_title.set_text("Sddm (inactive)")
    lbl_title.set_name("title")
    lbl_title.set_margin_start(10)
    hbox_title.append(lbl_title)

    hbox_sep_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hsep_top = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_top.set_hexpand(True)
    hsep_top.set_vexpand(False)
    hbox_sep_top.append(hsep_top)

    if _pkg["sddm"] or _pkg["sddm-git"]:
        hbox_section_config = _build_section_title(Gtk, "Configuration Setup")

        hbox_config_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_config_info = Gtk.Label(xalign=0)
        lbl_config_info.set_text(
            "We recommend to use the default sddm configuration setup\n"
            "Sddm configuration split into two files: /etc/sddm.conf "
            "and /etc/sddm.conf.d/kde_settings.conf\n"
            "/etc/sddm.conf.d/kde_settings.conf contains all the parameters - We will backup your files\n"
            "You can also restore your own original configuration if you want to - auto restart ATT\n"
        )
        lbl_config_info.set_margin_start(10)
        hbox_config_info.append(lbl_config_info)

        hbox_config_btns = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hbox_config_btns.set_margin_start(130)
        hbox_config_btns.set_margin_end(130)
        btn_apply_att_config = Gtk.Button(label="Apply the Sddm configuration from ATT - auto restart ATT")
        btn_apply_att_config.connect("clicked", functools.partial(sddm.on_click_sddm_reset_original_att, self))
        hbox_config_btns.append(btn_apply_att_config)
        btn_apply_original_config = Gtk.Button(label="Apply your original Sddm configuration - auto restart ATT")
        btn_apply_original_config.connect("clicked", functools.partial(sddm.on_click_sddm_reset_original, self))
        hbox_config_btns.append(btn_apply_original_config)

        hbox_sep_config = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hsep_config = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        hsep_config.set_hexpand(True)
        hbox_sep_config.append(hsep_config)

        vboxstack_sddm.append(hbox_title)
        vboxstack_sddm.append(hbox_sep_top)
        vboxstack_sddm.append(hbox_section_config)
        vboxstack_sddm.append(hbox_config_info)
        vboxstack_sddm.append(hbox_config_btns)
        vboxstack_sddm.append(hbox_sep_config)

        if fn.path.isfile(fn.sddm_default_d2):
            simplicity_installed = _pkg[simplicity_pkg]
            if fn.is_kirotux():
                fn.log_info(f"KiroTux: SDDM page manages {simplicity_pkg} ({simplicity_id})")

            hbox_section_login = _build_section_title(Gtk, "Login Settings")

            hbox_auto = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox_auto_lbl = Gtk.Label(xalign=0)
            hbox_auto_lbl.set_text("Auto login enabled or disabled")
            hbox_auto_lbl.set_margin_start(10)
            hbox_auto_lbl.set_hexpand(True)
            self.autologin_sddm = Gtk.Switch()
            self.autologin_sddm.set_active(sddm.get_autologin_state())
            self.autologin_sddm.connect("notify::active", functools.partial(sddm.on_autologin_sddm_activated, self))
            self.autologin_sddm.set_margin_end(10)
            hbox_auto.append(hbox_auto_lbl)
            hbox_auto.append(self.autologin_sddm)

            hbox_session = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            lbl_session = Gtk.Label(xalign=0)
            lbl_session.set_text("Autologin into this desktop")
            lbl_session.set_margin_start(10)
            lbl_session.set_hexpand(True)
            self.sessions_sddm = Gtk.DropDown.new_from_strings([])
            sddm.pop_box(self, self.sessions_sddm)
            self.sessions_sddm.set_margin_end(10)
            self.sessions_sddm.connect(
                "notify::selected",
                functools.partial(sddm.on_sddm_setting_changed, self, "Session changed"),
            )
            hbox_session.append(lbl_session)
            hbox_session.append(self.sessions_sddm)

            hbox_theme = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            lbl_theme = Gtk.Label(xalign=0)
            lbl_theme.set_text("Theme")
            lbl_theme.set_margin_start(10)
            lbl_theme.set_hexpand(True)
            self.theme_sddm = Gtk.DropDown.new_from_strings([])
            sddm.pop_theme_box(self, self.theme_sddm)
            self.theme_sddm.set_margin_end(10)
            self.theme_sddm.connect(
                "notify::selected",
                functools.partial(sddm.on_sddm_setting_changed, self, "Theme changed"),
            )
            self.theme_sddm.connect(
                "notify::selected",
                lambda *_: sddm._update_sddm_theme_preview(self),
            )
            hbox_theme.append(lbl_theme)
            hbox_theme.append(self.theme_sddm)

            hbox_theme_preview = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.sddm_theme_preview = Gtk.Picture()
            self.sddm_theme_preview.set_margin_start(10)
            self.sddm_theme_preview.set_margin_end(10)
            self.sddm_theme_preview.set_margin_top(4)
            self.sddm_theme_preview.set_margin_bottom(4)
            self.sddm_theme_preview.set_can_shrink(True)
            self.sddm_theme_preview.set_content_fit(Gtk.ContentFit.CONTAIN)
            self.sddm_theme_preview.set_size_request(-1, 150)
            self.sddm_theme_preview.set_hexpand(True)
            hbox_theme_preview.append(self.sddm_theme_preview)
            sddm._update_sddm_theme_preview(self)

            hbox_section_cursor = _build_section_title(Gtk, "Cursor Settings")

            hbox_bibata = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            btn_install_bibata = Gtk.Button(label="Install Bibata cursors")
            btn_install_bibata.connect("clicked", functools.partial(sddm.on_click_install_bibata_cursor, self))
            btn_install_bibata.set_margin_start(10)
            btn_install_bibata.set_margin_end(10)
            btn_remove_bibata = Gtk.Button(label="Remove Bibata cursors")
            btn_remove_bibata.connect("clicked", functools.partial(sddm.on_click_remove_bibata_cursor, self))
            btn_remove_bibata.set_margin_end(10)
            hbox_bibata.append(btn_install_bibata)
            hbox_bibata.append(btn_remove_bibata)

            hbox_bibata_extra = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            btn_install_bibata_extra = Gtk.Button(label="Install Bibata extra cursors")
            btn_install_bibata_extra.connect("clicked", functools.partial(sddm.on_click_install_bibatar_cursor, self))
            btn_install_bibata_extra.set_margin_start(10)
            btn_install_bibata_extra.set_margin_end(10)
            btn_remove_bibata_extra = Gtk.Button(label="Remove Bibata extra cursors")
            btn_remove_bibata_extra.connect("clicked", functools.partial(sddm.on_click_remove_bibatar_cursor, self))
            btn_remove_bibata_extra.set_margin_end(10)
            hbox_bibata_extra.append(btn_install_bibata_extra)
            hbox_bibata_extra.append(btn_remove_bibata_extra)

            hbox_cursor_hint = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            lbl_cursor_hint = Gtk.Label(xalign=0)
            lbl_cursor_hint.set_text("Select your cursor theme for the login screen e.g. Bibata-Modern-Ice")
            lbl_cursor_hint.set_margin_start(10)
            hbox_cursor_hint.append(lbl_cursor_hint)

            hbox_cursor = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            lbl_cursor = Gtk.Label(xalign=0)
            lbl_cursor.set_text("Cursor theme only for SDDM (global cursor setting in maintenance)")
            lbl_cursor.set_margin_start(10)
            lbl_cursor.set_hexpand(True)
            self.sddm_cursor_themes = Gtk.DropDown.new_from_strings([])
            sddm.pop_gtk_cursor_names(self.sddm_cursor_themes)
            self.sddm_cursor_themes.set_margin_end(10)
            self.sddm_cursor_preview = Gtk.Picture()
            self.sddm_cursor_preview.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
            self.sddm_cursor_preview.set_size_request(24, 24)
            self.sddm_cursor_preview.set_halign(Gtk.Align.END)
            self.sddm_cursor_preview.set_valign(Gtk.Align.CENTER)
            self.sddm_cursor_preview.set_margin_end(4)
            self.sddm_cursor_themes.connect(
                "notify::selected",
                functools.partial(sddm.on_sddm_setting_changed, self, "Cursor theme changed"),
            )
            self.sddm_cursor_themes.connect(
                "notify::selected",
                lambda *_: sddm._update_sddm_cursor_preview(self),
            )
            sddm._update_sddm_cursor_preview(self)
            hbox_cursor.append(lbl_cursor)
            hbox_cursor.append(self.sddm_cursor_preview)
            hbox_cursor.append(self.sddm_cursor_themes)

            hbox_apply = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            btn_apply_settings = Gtk.Button()
            btn_apply_lbl = Gtk.Label()
            btn_apply_lbl.set_markup("<b>Apply the above mentioned settings</b>")
            btn_apply_settings.set_child(btn_apply_lbl)
            btn_apply_settings.connect("clicked", functools.partial(sddm.on_click_sddm_apply, self))
            btn_apply_settings.set_margin_start(10)
            btn_apply_settings.set_hexpand(True)
            sddm_git_active = _pkg["sddm-git"] and fn.check_service_enabled("sddm")
            btn_enable_sddm = Gtk.Button(label="Install and enable sddm-git (when not yet active)")
            btn_enable_sddm.connect("clicked", functools.partial(sddm.on_click_sddm_enable, self))
            btn_enable_sddm.set_margin_end(10)
            btn_enable_sddm.set_visible(not sddm_git_active)
            hbox_apply.append(btn_apply_settings)
            hbox_apply.append(btn_enable_sddm)

            hbox_section_wallpaper = _build_section_title(Gtk, f"Wallpaper for {simplicity_id} theme")

            hbox_wp_lbl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            lbl_wp_desc = Gtk.Label(xalign=0)
            lbl_wp_desc.set_text("Set background wallpaper for the Simplicity Sddm theme")
            lbl_wp_desc.set_margin_start(10)
            lbl_wp_desc.set_hexpand(True)
            hbox_wp_lbl.append(lbl_wp_desc)
            self.btn_install_simplicity = Gtk.Button(label="Install Simplicity theme")
            self.btn_install_simplicity.connect("clicked", functools.partial(sddm.on_click_install_simplicity, self))
            self.btn_install_simplicity.set_margin_end(10)
            self.btn_install_simplicity.set_visible(not simplicity_installed)
            hbox_wp_lbl.append(self.btn_install_simplicity)
            self.btn_remove_simplicity = Gtk.Button(label="Remove Simplicity theme")
            self.btn_remove_simplicity.connect("clicked", functools.partial(sddm.on_click_remove_simplicity, self))
            self.btn_remove_simplicity.set_margin_end(10)
            # KiroTux has no other login theme, so removing its own would leave the grey SDDM fallback
            self.btn_remove_simplicity.set_visible(simplicity_installed and not fn.is_kirotux())
            hbox_wp_lbl.append(self.btn_remove_simplicity)

            hbox_wp_folder = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.btn_simplicity_browse = Gtk.Button(label="Select folder")
            self.btn_simplicity_browse.connect("clicked", functools.partial(sddm.on_browse_sddm_folder, self))
            self.btn_simplicity_browse.set_margin_start(10)
            self.btn_simplicity_browse.set_margin_end(10)
            self.btn_simplicity_browse.set_sensitive(simplicity_installed)
            default_wp_folder = "/usr/share/archlinux-tweak-tool/wallpapers"
            self.sddm_folder_entry = Gtk.Entry()
            self.sddm_folder_entry.set_hexpand(True)
            self.sddm_folder_entry.set_text(default_wp_folder)
            self.sddm_folder_entry.set_sensitive(simplicity_installed)
            self.btn_simplicity_load = Gtk.Button(label="Load")
            self.btn_simplicity_load.connect("clicked", functools.partial(sddm.on_load_sddm_folder, self))
            self.btn_simplicity_load.set_margin_start(10)
            self.btn_simplicity_load.set_margin_end(10)
            self.btn_simplicity_load.set_sensitive(simplicity_installed)
            self.btn_simplicity_stop = Gtk.Button(label="Stop")
            self.btn_simplicity_stop.connect("clicked", functools.partial(sddm.on_stop_sddm_loading, self))
            self.btn_simplicity_stop.set_margin_end(10)
            self.btn_simplicity_stop.set_sensitive(simplicity_installed)
            hbox_wp_folder.append(self.btn_simplicity_browse)
            hbox_wp_folder.append(self.sddm_folder_entry)
            hbox_wp_folder.append(self.btn_simplicity_load)
            hbox_wp_folder.append(self.btn_simplicity_stop)

            self.sddm_thumb_flow = Gtk.FlowBox()
            self.sddm_thumb_flow.set_valign(Gtk.Align.START)
            self.sddm_thumb_flow.set_max_children_per_line(20)
            self.sddm_thumb_flow.set_selection_mode(Gtk.SelectionMode.NONE)
            self.sddm_thumb_flow.set_homogeneous(True)
            wp_scroll = Gtk.ScrolledWindow()
            wp_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            wp_scroll.set_hexpand(True)
            wp_scroll.set_size_request(-1, 280)
            wp_scroll.set_margin_start(10)
            wp_scroll.set_margin_end(10)
            wp_scroll.set_child(self.sddm_thumb_flow)
            hbox_wp_scroll = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox_wp_scroll.append(wp_scroll)

            hbox_wp_selected = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.sddm_wallpaper_lbl = Gtk.Label(xalign=0)
            self.sddm_wallpaper_lbl.set_text("No wallpaper selected")
            self.sddm_wallpaper_lbl.set_margin_start(10)
            self.sddm_wallpaper_lbl.set_hexpand(True)
            self.sddm_wallpaper_lbl.set_ellipsize(Pango.EllipsizeMode.START)
            hbox_wp_selected.append(self.sddm_wallpaper_lbl)

            hbox_wp_preview = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.sddm_wallpaper_preview = Gtk.Picture()
            self.sddm_wallpaper_preview.set_margin_start(10)
            self.sddm_wallpaper_preview.set_margin_end(10)
            self.sddm_wallpaper_preview.set_margin_top(4)
            self.sddm_wallpaper_preview.set_margin_bottom(4)
            self.sddm_wallpaper_preview.set_can_shrink(True)
            self.sddm_wallpaper_preview.set_content_fit(Gtk.ContentFit.CONTAIN)
            self.sddm_wallpaper_preview.set_size_request(-1, 150)
            self.sddm_wallpaper_preview.set_hexpand(True)
            hbox_wp_preview.append(self.sddm_wallpaper_preview)
            default_sddm_wallpaper = sddm.theme_background(fn.path.join("/usr/share/sddm/themes", simplicity_id))
            fallback_wallpaper = "/usr/share/archlinux-tweak-tool/data/wallpaper/wallpaper.jpg"
            if fn.path.isfile(default_sddm_wallpaper):
                self.sddm_wallpaper_lbl.set_text(default_sddm_wallpaper)
                self.sddm_wallpaper_preview.set_filename(default_sddm_wallpaper)
            elif fn.path.isfile(fallback_wallpaper):
                self.sddm_wallpaper_preview.set_filename(fallback_wallpaper)
            else:
                hbox_wp_preview.set_visible(False)

            hbox_wp_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.btn_simplicity_apply = Gtk.Button(label="Apply wallpaper")
            self.btn_simplicity_apply.connect("clicked", functools.partial(sddm.on_set_sddm_wallpaper, self))
            self.btn_simplicity_apply.set_margin_start(10)
            self.btn_simplicity_apply.set_margin_end(10)
            self.btn_simplicity_apply.set_sensitive(simplicity_installed)
            self.btn_simplicity_restore = Gtk.Button(label="Restore default")
            self.btn_simplicity_restore.connect("clicked", functools.partial(sddm.on_restore_sddm_wallpaper, self))
            self.btn_simplicity_restore.set_margin_end(10)
            self.btn_simplicity_restore.set_sensitive(simplicity_installed)
            btn_fix_sddm_conf = Gtk.Button(label="Fix SDDM config")
            btn_fix_sddm_conf.set_margin_end(10)
            btn_fix_sddm_conf.connect("clicked", functools.partial(sddm.on_click_fix_sddm_conf, self))
            hbox_wp_btns_spacer = Gtk.Box()
            hbox_wp_btns_spacer.set_hexpand(True)
            hbox_wp_btns.append(self.btn_simplicity_apply)
            hbox_wp_btns.append(self.btn_simplicity_restore)
            hbox_wp_btns.append(hbox_wp_btns_spacer)
            hbox_wp_btns.append(btn_fix_sddm_conf)

            vboxstack_sddm.append(hbox_section_login)
            vboxstack_sddm.append(hbox_auto)
            vboxstack_sddm.append(hbox_session)
            vboxstack_sddm.append(hbox_theme)
            vboxstack_sddm.append(hbox_theme_preview)
            vboxstack_sddm.append(hbox_section_cursor)
            vboxstack_sddm.append(hbox_bibata)
            vboxstack_sddm.append(hbox_bibata_extra)
            vboxstack_sddm.append(hbox_cursor_hint)
            vboxstack_sddm.append(hbox_cursor)
            vboxstack_sddm.append(hbox_apply)

            # ── Available themes ───────────────────────────────────────────
            hbox_section_available = _build_section_title(Gtk, "Available SDDM Themes")

            hbox_refresh_avail = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox_refresh_avail.set_margin_start(10)
            hbox_refresh_avail.set_margin_top(4)
            btn_refresh_avail = Gtk.Button(label="Refresh list")
            btn_refresh_avail.set_size_request(100, 28)
            hbox_refresh_avail.append(btn_refresh_avail)

            hbox_avail_select = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox_avail_select.set_margin_start(10)
            hbox_avail_select.set_margin_top(4)
            hbox_avail_select.set_margin_bottom(6)
            lbl_avail_select = Gtk.Label(xalign=0)
            lbl_avail_select.set_text("Select package")
            lbl_avail_select.set_size_request(120, -1)
            lbl_avail_select.set_hexpand(True)
            dd_avail_sddm = Gtk.DropDown.new_from_strings([])
            btn_install_sddm_theme = Gtk.Button(label="Install theme")
            btn_install_sddm_theme.set_size_request(140, 30)
            btn_install_sddm_theme.set_margin_end(10)
            hbox_avail_select.append(lbl_avail_select)
            hbox_avail_select.append(dd_avail_sddm)
            hbox_avail_select.append(btn_install_sddm_theme)

            aur_helper = fn.get_aur_helper()
            repo_active = fn.check_nemesis_repo_active() or fn.check_chaotic_aur_active()
            if not aur_helper and not repo_active:
                btn_install_sddm_theme.set_sensitive(False)

            hbox_aur_toggle = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox_aur_toggle.set_margin_start(10)
            hbox_aur_toggle.set_margin_top(4)
            lbl_aur_toggle = Gtk.Label(xalign=0)
            lbl_aur_toggle.set_text("Include AUR packages")
            lbl_aur_toggle.set_hexpand(True)
            switch_aur = Gtk.Switch()
            switch_aur.set_active(bool(aur_helper))
            switch_aur.set_sensitive(bool(aur_helper))
            switch_aur.set_margin_end(10)
            hbox_aur_toggle.append(lbl_aur_toggle)
            hbox_aur_toggle.append(switch_aur)

            hbox_sort_toggle = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox_sort_toggle.set_margin_start(10)
            hbox_sort_toggle.set_margin_top(4)
            lbl_sort_toggle = Gtk.Label(xalign=0)
            lbl_sort_toggle.set_text("Sort by recently updated (AUR)")
            lbl_sort_toggle.set_hexpand(True)
            switch_sort_date = Gtk.Switch()
            switch_sort_date.set_active(False)
            switch_sort_date.set_margin_end(10)
            hbox_sort_toggle.append(lbl_sort_toggle)
            hbox_sort_toggle.append(switch_sort_date)

            _aur_modified = {}
            _current_avail_pkgs = []

            def _populate_avail_sddm(pkgs=None):
                nonlocal _current_avail_pkgs
                if pkgs is None:
                    pkgs = sddm.list_available_sddm_packages(use_aur=switch_aur.get_active())
                _current_avail_pkgs = pkgs
                if switch_sort_date.get_active() and _aur_modified:
                    display = sorted(pkgs, key=lambda p: _aur_modified.get(p, 0), reverse=True)
                else:
                    display = pkgs
                _m = dd_avail_sddm.get_model()
                _m.splice(0, _m.get_n_items(), [])
                for p in display:
                    _m.append(p)
                if display:
                    dd_avail_sddm.set_selected(0)
                btn_install_sddm_theme.set_sensitive(bool(display) and (aur_helper is not None or repo_active))

            def _on_install_sddm_theme_clicked(_widget):
                _item = dd_avail_sddm.get_selected_item()
                selected = _item.get_string() if _item else None
                if not selected:
                    fn.log_warn("No SDDM theme package selected")
                    return
                fn.log_subsection(f"Installing SDDM theme: {selected}")
                fn.show_in_app_notification(self, f"Installing: {selected}")

                def _run():
                    if aur_helper:
                        process = fn.launch_aur_install_in_terminal(aur_helper, selected)
                    else:
                        process = fn.launch_pacman_install_in_terminal(selected)
                    if process:
                        process.wait()
                        fn.invalidate_pkg_cache()
                    fn.GLib.idle_add(_after_install)

                def _after_install():
                    sddm.pop_theme_box(self, self.theme_sddm)
                    sddm._update_sddm_theme_preview(self)
                    pkgs = sddm.list_available_sddm_packages(force=True)
                    _populate_avail_sddm(pkgs)
                    _populate_remove_sddm()
                    fn.log_success(f"SDDM theme installed: {selected}")

                fn.threading.Thread(target=_run, daemon=True).start()

            hbox_remove_sddm_select = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox_remove_sddm_select.set_margin_start(10)
            hbox_remove_sddm_select.set_margin_top(4)
            hbox_remove_sddm_select.set_margin_bottom(6)
            lbl_remove_select = Gtk.Label(xalign=0)
            lbl_remove_select.set_text("Remove installed")
            lbl_remove_select.set_size_request(120, -1)
            lbl_remove_select.set_hexpand(True)
            dd_remove_sddm = Gtk.DropDown.new_from_strings([])
            btn_remove_sddm_theme = Gtk.Button(label="Remove theme")
            btn_remove_sddm_theme.set_size_request(140, 30)
            btn_remove_sddm_theme.set_margin_end(10)
            hbox_remove_sddm_select.append(lbl_remove_select)
            hbox_remove_sddm_select.append(dd_remove_sddm)
            hbox_remove_sddm_select.append(btn_remove_sddm_theme)

            def _populate_remove_sddm():
                _m = dd_remove_sddm.get_model()
                _m.splice(0, _m.get_n_items(), [])
                themes = sddm.list_installed_sddm_themes()
                for t in themes:
                    _m.append(t)
                if themes:
                    dd_remove_sddm.set_selected(0)
                btn_remove_sddm_theme.set_sensitive(bool(themes))

            def _on_refresh_avail_clicked(_widget):
                fn.log_subsection("Refreshing SDDM available themes...")
                fn.show_in_app_notification(self, "Refreshing available themes...")

                def _run():
                    pkgs = sddm.list_available_sddm_packages(force=True, use_aur=switch_aur.get_active())
                    fn.GLib.idle_add(lambda: _populate_avail_sddm(pkgs))
                    fn.GLib.idle_add(_populate_remove_sddm)
                    fn.GLib.idle_add(lambda: fn.log_success(f"Found {len(pkgs)} available SDDM themes"))

                fn.threading.Thread(target=_run, daemon=True).start()

            def _on_aur_toggle_changed(_widget, _param):
                fn.log_info(f"SDDM AUR toggle: {switch_aur.get_active()}")

                def _run():
                    pkgs = sddm.list_available_sddm_packages(force=True, use_aur=switch_aur.get_active())
                    fn.GLib.idle_add(lambda: _populate_avail_sddm(pkgs))

                fn.threading.Thread(target=_run, daemon=True).start()

            def _on_sort_toggle_changed(_widget, _param):
                fn.log_info(f"SDDM sort by date: {switch_sort_date.get_active()}")
                if switch_sort_date.get_active() and not _aur_modified:
                    fn.show_in_app_notification(self, "Fetching AUR package dates...")

                    def _run():
                        nonlocal _aur_modified
                        _aur_modified = sddm.fetch_aur_pkg_modified(_current_avail_pkgs)
                        fn.GLib.idle_add(lambda: _populate_avail_sddm(_current_avail_pkgs))

                    fn.threading.Thread(target=_run, daemon=True).start()
                    return
                _populate_avail_sddm(_current_avail_pkgs)

            def _on_remove_sddm_theme_clicked(_widget):
                _item = dd_remove_sddm.get_selected_item()
                theme = _item.get_string() if _item else None
                if not theme:
                    fn.log_warn("No installed SDDM theme selected for removal")
                    return
                theme_dir = fn.path.join(sddm._SDDM_THEME_DIR, theme)
                try:
                    pkg = fn.subprocess.run(
                        ["pacman", "-Qqo", theme_dir], capture_output=True, text=True
                    ).stdout.strip()
                except Exception:
                    pkg = ""
                if not pkg:
                    fn.log_warn(f"Could not find package owning {theme_dir} — cannot remove")
                    fn.show_in_app_notification(self, f"No package found for theme: {theme}")
                    return
                fn.log_subsection(f"Removing SDDM theme: {pkg}")
                fn.show_in_app_notification(self, f"Removing: {pkg}")

                def _run():
                    process = fn.launch_pacman_remove_in_terminal(pkg)
                    if process:
                        process.wait()
                        fn.invalidate_pkg_cache()
                    fn.GLib.idle_add(_after_remove)

                def _after_remove():
                    sddm.pop_theme_box(self, self.theme_sddm)
                    sddm._update_sddm_theme_preview(self)
                    pkgs = sddm.list_available_sddm_packages(force=True)
                    _populate_avail_sddm(pkgs)
                    _populate_remove_sddm()
                    fn.log_success(f"SDDM theme removed: {pkg}")

                fn.threading.Thread(target=_run, daemon=True).start()

            btn_install_sddm_theme.connect("clicked", _on_install_sddm_theme_clicked)
            btn_refresh_avail.connect("clicked", _on_refresh_avail_clicked)
            btn_remove_sddm_theme.connect("clicked", _on_remove_sddm_theme_clicked)
            switch_aur.connect("notify::active", _on_aur_toggle_changed)
            switch_sort_date.connect("notify::active", _on_sort_toggle_changed)

            vboxstack_sddm.append(hbox_section_available)
            vboxstack_sddm.append(hbox_refresh_avail)
            vboxstack_sddm.append(hbox_aur_toggle)
            vboxstack_sddm.append(hbox_sort_toggle)
            vboxstack_sddm.append(hbox_avail_select)
            vboxstack_sddm.append(hbox_remove_sddm_select)
            vboxstack_sddm.append(hbox_section_wallpaper)
            vboxstack_sddm.append(hbox_wp_lbl)
            vboxstack_sddm.append(hbox_wp_folder)
            vboxstack_sddm.append(hbox_wp_selected)
            vboxstack_sddm.append(hbox_wp_preview)
            vboxstack_sddm.append(hbox_wp_btns)
            vboxstack_sddm.append(hbox_wp_scroll)

            def _load_avail_bg():
                try:
                    pkgs = sddm.list_available_sddm_packages(use_aur=switch_aur.get_active())
                    fn.GLib.idle_add(lambda: _populate_avail_sddm(pkgs))
                    fn.GLib.idle_add(_populate_remove_sddm)
                except Exception as e:
                    fn.log_error(f"SDDM available themes load failed: {e}")

            fn.threading.Thread(target=_load_avail_bg, daemon=True).start()

            if simplicity_installed and fn.path.isdir(default_wp_folder):
                fn.GLib.idle_add(
                    lambda: sddm._populate_sddm_thumbs(self, default_wp_folder),
                    priority=fn.GLib.PRIORITY_LOW,
                )

    else:
        hbox_not_installed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_not_installed = Gtk.Label(xalign=0)
        lbl_not_installed.set_text("Sddm is not installed")
        lbl_not_installed.set_name("title")
        lbl_not_installed.set_margin_start(10)
        hbox_not_installed.append(lbl_not_installed)

        hbox_sep_not_installed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hsep_not_installed = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        hsep_not_installed.set_hexpand(True)
        hbox_sep_not_installed.append(hsep_not_installed)

        message = Gtk.Label()
        message.set_markup("<b>Sddm does not seem to be installed</b>")
        message.set_margin_start(10)

        install_sddm = Gtk.Button(label="Install sddm-git and enable it")
        install_sddm.connect("clicked", functools.partial(sddm.on_click_att_sddm_clicked, self))
        install_sddm.set_margin_start(10)
        install_sddm.set_margin_end(10)

        vboxstack_sddm.append(hbox_title)
        vboxstack_sddm.append(hbox_sep_top)
        vboxstack_sddm.append(hbox_not_installed)
        vboxstack_sddm.append(hbox_sep_not_installed)
        vboxstack_sddm.append(message)
        vboxstack_sddm.append(install_sddm)


def _build_section_title(Gtk, title, btn=None):
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox.set_margin_top(14)
    hbox.set_margin_bottom(6)

    lbl = Gtk.Label(xalign=0)
    lbl.set_markup(f"<b><big>{title}</big></b>")
    lbl.set_margin_start(10)

    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    sep.set_margin_start(8)

    hbox.append(lbl)
    hbox.append(sep)
    if btn:
        btn.set_margin_end(10)
        hbox.append(btn)
    return hbox

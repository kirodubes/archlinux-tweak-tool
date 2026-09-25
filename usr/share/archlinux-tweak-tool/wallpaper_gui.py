# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools


def _refresh(self, fn):
    variety_installed = fn.check_package_installed("variety")
    autostarts = fn.path.isfile(fn.path.join(fn.home, ".config", "autostart", "variety.desktop"))
    self.lbl_variety_installed.set_visible(variety_installed)
    self.btn_variety_next.set_sensitive(variety_installed)
    self.btn_variety_prev.set_sensitive(variety_installed)
    self.btn_save_variety_config.set_sensitive(variety_installed)
    self.btn_open_variety_settings.set_sensitive(variety_installed)
    self.btn_open_variety_selector.set_sensitive(variety_installed)
    self.btn_restore_variety_backup.set_sensitive(fn.path.isdir(fn.path.join(fn.home, ".config", "variety-bak")))
    self.btn_add_variety_autostart.set_sensitive(variety_installed and not autostarts)
    self.btn_remove_variety_autostart.set_sensitive(autostarts)


def gui(self, Gtk, Pango, vboxstack_wallpaper, wallpaper, fn, base_dir):
    """Create the Wallpaper GUI (variety controls, ATT config, wallpaper picker)."""
    fn.log_tip("Store your wallpapers in ~/Templates/wallpapers — variety picks them up automatically")
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox.set_margin_start(10)
    vbox.set_margin_end(10)

    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text("Wallpaper")
    lbl_title.set_name("title")
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hbox_separator.append(hseparator)
    hbox_title.append(lbl_title)

    # ---- Variety section ----
    hbox_section_variety = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_variety = Gtk.Label(xalign=0)
    lbl_section_variety.set_markup("<b>Variety</b>")
    hbox_section_variety.append(lbl_section_variety)

    hbox_variety_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.btn_install_variety = Gtk.Button(label="Install/launch variety")
    self.btn_install_variety.connect("clicked", functools.partial(wallpaper.on_install_or_launch_variety, self))

    self.btn_remove_variety = Gtk.Button(label="Remove variety")
    self.btn_remove_variety.connect("clicked", functools.partial(wallpaper.on_remove_variety, self))

    self.lbl_variety_installed = Gtk.Label(xalign=0)
    self.lbl_variety_installed.set_markup("<b>Installed</b>")
    self.lbl_variety_installed.set_margin_start(6)
    self.lbl_variety_installed.set_visible(False)

    hbox_variety_btns.append(self.btn_install_variety)
    hbox_variety_btns.append(self.btn_remove_variety)
    hbox_variety_btns.append(self.lbl_variety_installed)

    hbox_variety_nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.btn_variety_next = Gtk.Button(label="Next wallpaper")
    self.btn_variety_next.connect("clicked", functools.partial(wallpaper.on_variety_next, self))

    self.btn_variety_prev = Gtk.Button(label="Previous wallpaper")
    self.btn_variety_prev.connect("clicked", functools.partial(wallpaper.on_variety_prev, self))

    hbox_variety_nav.append(self.btn_variety_prev)
    hbox_variety_nav.append(self.btn_variety_next)

    hbox_section_autostart = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_autostart = Gtk.Label(xalign=0)
    lbl_section_autostart.set_markup("<b>Autostart</b>")
    lbl_section_autostart.set_margin_top(8)
    hbox_section_autostart.append(lbl_section_autostart)

    hbox_autostart_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.btn_add_variety_autostart = Gtk.Button(label="Add to autostart")
    self.btn_add_variety_autostart.connect("clicked", functools.partial(wallpaper.on_add_variety_autostart, self))

    self.btn_remove_variety_autostart = Gtk.Button(label="Remove from autostart")
    self.btn_remove_variety_autostart.connect("clicked", functools.partial(wallpaper.on_remove_variety_autostart, self))

    hbox_autostart_btns.append(self.btn_add_variety_autostart)
    hbox_autostart_btns.append(self.btn_remove_variety_autostart)

    # ---- ATT Configuration section ----
    hbox_section_config = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_config = Gtk.Label(xalign=0)
    lbl_section_config.set_markup("<b>ATT Configuration</b>")
    lbl_section_config.set_margin_top(16)
    hbox_section_config.append(lbl_section_config)

    hbox_config_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_config_info = Gtk.Label(xalign=0)
    lbl_config_info.set_markup(
        "<i>Store your wallpapers in ~/Templates/wallpapers — variety picks them up automatically</i>"
    )
    lbl_config_info.set_margin_start(2)
    hbox_config_info.append(lbl_config_info)

    hbox_config_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.btn_save_variety_config = Gtk.Button(label="Save ATT variety config")
    self.btn_save_variety_config.connect("clicked", functools.partial(wallpaper.on_save_variety_config, self))

    self.btn_open_variety_settings = Gtk.Button(label="Open variety settings")
    self.btn_open_variety_settings.connect("clicked", functools.partial(wallpaper.on_open_variety_settings, self))

    self.btn_open_variety_selector = Gtk.Button(label="Open Selector")
    self.btn_open_variety_selector.connect("clicked", functools.partial(wallpaper.on_open_variety_selector, self))

    self.btn_restore_variety_backup = Gtk.Button(label="Restore backup")
    self.btn_restore_variety_backup.connect("clicked", functools.partial(wallpaper.on_restore_variety_backup, self))
    self.btn_restore_variety_backup.set_sensitive(False)

    hbox_config_btns.append(self.btn_open_variety_settings)
    hbox_config_btns.append(self.btn_open_variety_selector)
    hbox_config_btns.append(self.btn_save_variety_config)
    hbox_config_btns.append(self.btn_restore_variety_backup)

    # ---- ATT Wallpaper Picker section (hidden on full DEs that manage wallpaper themselves) ----
    box_picker = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box_picker.set_visible(wallpaper.should_show_picker())

    hbox_section_picker = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_picker = Gtk.Label(xalign=0)
    lbl_section_picker.set_markup("<b>ATT Wallpaper Picker</b>")
    lbl_section_picker.set_margin_top(16)
    hbox_section_picker.append(lbl_section_picker)

    # Folder row
    hbox_folder = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_browse = Gtk.Button(label="Browse")
    btn_browse.connect("clicked", functools.partial(wallpaper.on_browse_wallpaper_folder, self))

    self.wallpaper_folder_entry = Gtk.Entry()
    self.wallpaper_folder_entry.set_hexpand(True)
    self.wallpaper_folder_entry.set_text("/usr/share/archlinux-tweak-tool/walls")

    btn_load = Gtk.Button(label="Load")
    btn_load.connect("clicked", functools.partial(wallpaper.on_load_wallpaper_folder, self))

    btn_stop = Gtk.Button(label="Stop")
    btn_stop.connect("clicked", functools.partial(wallpaper.on_stop_wallpaper_loading, self))

    hbox_folder.append(btn_browse)
    hbox_folder.append(self.wallpaper_folder_entry)
    hbox_folder.append(btn_load)
    hbox_folder.append(btn_stop)

    # Thumbnail FlowBox
    self.wallpaper_thumb_flow = Gtk.FlowBox()
    self.wallpaper_thumb_flow.set_valign(Gtk.Align.START)
    self.wallpaper_thumb_flow.set_max_children_per_line(20)
    self.wallpaper_thumb_flow.set_selection_mode(Gtk.SelectionMode.NONE)
    self.wallpaper_thumb_flow.set_homogeneous(True)

    wp_scroll = Gtk.ScrolledWindow()
    wp_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    wp_scroll.set_hexpand(True)
    wp_scroll.set_size_request(-1, 300)
    wp_scroll.set_child(self.wallpaper_thumb_flow)

    # Preview
    hbox_preview = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.wallpaper_preview = Gtk.Picture()
    self.wallpaper_preview.set_can_shrink(True)
    self.wallpaper_preview.set_content_fit(Gtk.ContentFit.CONTAIN)
    self.wallpaper_preview.set_size_request(-1, 180)
    self.wallpaper_preview.set_hexpand(True)
    hbox_preview.append(self.wallpaper_preview)

    hbox_path = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.wallpaper_path_lbl = Gtk.Label(xalign=0)
    self.wallpaper_path_lbl.set_text("No wallpaper selected")
    self.wallpaper_path_lbl.set_hexpand(True)
    self.wallpaper_path_lbl.set_ellipsize(Pango.EllipsizeMode.START)
    hbox_path.append(self.wallpaper_path_lbl)

    # Options + Apply row
    hbox_apply = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_scale = Gtk.Label(xalign=0)
    lbl_scale.set_text("Scale:")
    self.wallpaper_scale_combo = Gtk.DropDown.new_from_strings(["Fill", "Fit", "Center", "Tile", "Stretch"])
    self.wallpaper_scale_combo.set_selected(0)
    _on_wayland = bool(wallpaper._get_user_env(["WAYLAND_DISPLAY"])["WAYLAND_DISPLAY"])

    btn_apply = Gtk.Button(label="Apply wallpaper")
    btn_apply.connect("clicked", functools.partial(wallpaper.on_apply_wallpaper, self))

    hbox_apply_spacer = Gtk.Box()
    hbox_apply_spacer.set_hexpand(True)
    hbox_apply.append(lbl_scale)
    hbox_apply.append(self.wallpaper_scale_combo)
    hbox_apply.append(hbox_apply_spacer)
    hbox_apply.append(btn_apply)

    # Persistence tip for WM/feh users
    hbox_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_note = Gtk.Label(xalign=0)
    lbl_note.set_markup("<i>Tip: source ~/.fehbg in your WM autostart to restore wallpaper on login</i>")
    lbl_note.set_margin_top(4)
    hbox_note.append(lbl_note)
    if _on_wayland:
        hbox_note.set_visible(False)

    box_picker.append(hbox_section_picker)
    box_picker.append(hbox_folder)
    box_picker.append(wp_scroll)
    box_picker.append(hbox_preview)
    box_picker.append(hbox_path)
    box_picker.append(hbox_apply)
    box_picker.append(hbox_note)

    # Pack
    vbox.append(hbox_section_variety)
    vbox.append(hbox_variety_btns)
    vbox.append(hbox_variety_nav)
    vbox.append(hbox_section_autostart)
    vbox.append(hbox_autostart_btns)
    vbox.append(hbox_section_config)
    vbox.append(hbox_config_info)
    vbox.append(hbox_config_btns)
    vbox.append(box_picker)

    vboxstack_wallpaper.append(hbox_title)
    vboxstack_wallpaper.append(hbox_separator)
    vboxstack_wallpaper.append(vbox)

    vboxstack_wallpaper.connect("map", lambda _w: _refresh(self, fn))
    _refresh(self, fn)

    bundled = "/usr/share/archlinux-tweak-tool/walls"
    if fn.path.isdir(bundled):
        fn.GLib.idle_add(
            lambda: wallpaper._populate_wallpaper_thumbs(self, bundled),
            priority=fn.GLib.PRIORITY_LOW,
        )

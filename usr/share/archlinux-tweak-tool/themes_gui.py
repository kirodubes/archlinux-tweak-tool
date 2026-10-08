# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
# pylint:disable=C0103,

import functools
import desktopr_gui
import themes


def _att_preview_picture(Gtk, GdkPixbuf, Gdk, base_dir, filename, scale=1.0, out_pics=None):
    """Return a scaled preview image wrapped in a Frame; append (pic, scale) to out_pics if given."""
    img_load = int(desktopr_gui.IMAGE_PREVIEW_LOAD * scale)
    img_min = int(desktopr_gui.IMAGE_PREVIEW_MIN * scale)
    pic = Gtk.Picture()
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            base_dir + "/images/" + filename,
            img_load,
            img_load,
        )
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        pic.set_paintable(texture)
    except Exception:
        pass
    pic.set_can_shrink(True)
    pic.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
    pic.set_size_request(img_min, img_min)
    pic.set_hexpand(True)
    pic.set_vexpand(False)
    pic.set_halign(Gtk.Align.CENTER)
    pic.set_valign(Gtk.Align.CENTER)
    frame = Gtk.Frame(label="Preview")
    frame.set_child(pic)
    frame.set_hexpand(True)
    frame.set_vexpand(True)
    frame.set_margin_start(10)
    frame.set_margin_end(10)
    frame.set_margin_top(10)
    frame.set_margin_bottom(10)
    if out_pics is not None:
        out_pics.append((pic, scale))
    return frame


def make_swatch(Gtk, hex_color):
    """Return a small DrawingArea filled with the theme's accent colour; shared with the Celestial page."""
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    def _draw(_area, cr, width, height, *_data):
        cr.set_source_rgb(r, g, b)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        # 1px border so light swatches don't wash out against a light background
        cr.set_source_rgba(0, 0, 0, 0.35)
        cr.set_line_width(1)
        cr.rectangle(0.5, 0.5, width - 1, height - 1)
        cr.stroke()

    area = Gtk.DrawingArea()
    area.set_content_width(16)
    area.set_content_height(16)
    area.set_valign(Gtk.Align.CENTER)
    area.set_draw_func(_draw)
    return area


def build_env_theme_row(Gtk, self, names_attr, dropdown_attr, on_apply):
    """Build the /etc/environment GTK-theme row (label, dropdown, Apply) and store its widgets on self."""
    hbox_env_dropdown = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_env_dropdown.set_halign(Gtk.Align.CENTER)
    hbox_env_dropdown.set_margin_start(10)
    hbox_env_dropdown.set_margin_end(10)
    hbox_env_dropdown.set_margin_bottom(10)
    hbox_env_dropdown.set_tooltip_text(
        "Optional override: GTK_THEME forces this one theme on every GTK app for every user, "
        "and partly restyles libadwaita apps.\n"
        "Leave it on None to let each user's own theme settings decide."
    )

    lbl_env_dropdown = Gtk.Label()
    lbl_env_dropdown.set_markup(
        '<span foreground="#FFA500">Set the system-wide GTK theme in /etc/environment</span>'
    )
    lbl_env_dropdown.set_margin_start(10)
    lbl_env_dropdown.set_margin_end(10)
    hbox_env_dropdown.append(lbl_env_dropdown)

    dropdown = Gtk.DropDown.new_from_strings([themes.ENV_NONE_LABEL])
    setattr(self, dropdown_attr, dropdown)
    themes.refresh_env_theme_row(self, names_attr, dropdown_attr)
    dropdown.set_margin_start(10)
    dropdown.set_margin_end(10)
    hbox_env_dropdown.append(dropdown)

    button_apply_env_theme = Gtk.Button(label="Apply")
    button_apply_env_theme.connect("clicked", functools.partial(on_apply, self))
    button_apply_env_theme.set_margin_start(10)
    button_apply_env_theme.set_margin_end(10)
    hbox_env_dropdown.append(button_apply_env_theme)

    return hbox_env_dropdown


def gui(self, Gtk, GdkPixbuf, vboxstack_themes, _themes_module, fn, base_dir):
    """Create the Themes GUI (arc theme checkboxes, presets, install/remove actions)."""
    from gi.repository import Gdk

    fn.log_info(f"{len(themes._all_tokens())} arc themes available to install")

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text("Arc themes")
    lbl_title.set_name("title")
    hbox_title.append(lbl_title)

    hbox_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_separator.append(hseparator)

    hbox_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_info_label = Gtk.Label(xalign=0)
    hbox_info_label.set_markup(
        'Select the packages you want to install or remove, then click the appropriate button.\n\
Ensure that the <b>Nemesis repository is enabled</b> — see the "Pacman" tab for details.'
    )

    hbox_info_label.set_margin_start(10)
    hbox_info_label.set_margin_end(10)
    hbox_info.append(hbox_info_label)

    is_plasma = "kde" in fn.desktop.lower() or "plasma" in fn.desktop.lower()
    is_kiro = fn.get_distro_label() == "Kiro"

    hbox_plasma_qt = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_plasma_qt.set_halign(Gtk.Align.CENTER)
    button_toggle_plasma_qt = Gtk.Button()
    themes.style_toggle_button(button_toggle_plasma_qt, themes.PLASMA_QT_TOGGLE_LABEL)
    button_toggle_plasma_qt.connect("clicked", functools.partial(themes.on_click_toggle_plasma_qt, self))
    button_toggle_plasma_qt.set_margin_start(10)
    button_toggle_plasma_qt.set_margin_end(10)
    hbox_plasma_qt.append(button_toggle_plasma_qt)

    hbox_gtk_theme_hint = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_gtk_theme_hint.set_halign(Gtk.Align.CENTER)
    lbl_gtk_theme_hint = Gtk.Label()
    lbl_gtk_theme_hint.set_markup(
        '<span size="large">The GTK theme is set per user — pick it in your desktop\'s appearance settings.\n'
        "The setting below is an optional system-wide override; leave it on None normally.</span>"
    )
    lbl_gtk_theme_hint.set_justify(Gtk.Justification.CENTER)
    hbox_gtk_theme_hint.append(lbl_gtk_theme_hint)

    hbox_env_reminder = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_env_reminder.set_halign(Gtk.Align.CENTER)
    lbl_env_reminder = Gtk.Label()
    lbl_env_reminder.set_markup(
        '<span size="large">Remember to check /etc/environment — themes are sometimes set there.</span>'
    )
    lbl_env_reminder.set_justify(Gtk.Justification.CENTER)
    hbox_env_reminder.append(lbl_env_reminder)

    hbox_env_edit = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_env_edit.set_halign(Gtk.Align.CENTER)
    button_edit_env = Gtk.Button(label="Edit /etc/environment in terminal")
    button_edit_env.connect("clicked", functools.partial(themes.on_click_edit_environment, self))
    button_edit_env.set_margin_start(10)
    button_edit_env.set_margin_end(10)
    hbox_env_edit.append(button_edit_env)

    hbox_env_dropdown = build_env_theme_row(
        Gtk, self, "_env_gtk_theme_names", "env_theme_dropdown", themes.on_click_apply_env_theme
    )

    hbox_plasma_warning = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    if is_plasma:
        lbl_plasma_warning = Gtk.Label(xalign=0)
        lbl_plasma_warning.set_markup("<b>⚠ On Plasma these themes will not work</b>")
        lbl_plasma_warning.set_margin_start(10)
        lbl_plasma_warning.set_margin_end(10)
        hbox_plasma_warning.append(lbl_plasma_warning)
        hbox_plasma_warning.add_css_class("warning")

    self.arc_checkboxes = {}
    vbox_families = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    vbox_families.set_hexpand(True)

    for family_label, family_themes in themes.THEME_FAMILIES:
        lbl_family = Gtk.Label(xalign=0)
        lbl_family.set_markup(f"<b>{family_label}</b>")
        lbl_family.set_margin_start(10)
        lbl_family.set_margin_top(6)
        vbox_families.append(lbl_family)

        flowbox_family = Gtk.FlowBox()
        flowbox_family.set_valign(Gtk.Align.START)
        flowbox_family.set_max_children_per_line(6)
        flowbox_family.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox_family.set_hexpand(True)
        flowbox_family.set_margin_start(10)
        flowbox_family.set_margin_end(10)

        for token, hex_color, _is_dark in family_themes:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row.append(make_swatch(Gtk, hex_color))
            checkbox = Gtk.CheckButton(label="kiro-arc-" + token)
            self.arc_checkboxes[token] = checkbox
            row.append(checkbox)
            flowbox_family.append(row)

        vbox_families.append(flowbox_family)

    hbox_presets = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    hbox_presets.set_hexpand(True)
    lbl_preset_hint = Gtk.Label()
    lbl_preset_hint.set_text("Choose what to select with a button")
    lbl_preset_hint.set_margin_start(10)
    lbl_preset_hint.set_margin_end(10)
    lbl_preset_hint.set_hexpand(True)
    lbl_preset_hint.set_xalign(0)
    hbox_presets.append(lbl_preset_hint)

    btn_all_selection_themes = Gtk.Button(label="All")
    btn_all_selection_themes.connect("clicked", functools.partial(themes.on_click_att_theming_all_selection, self))
    btn_dark_selection_themes = Gtk.Button(label="Dark")
    btn_dark_selection_themes.connect("clicked", functools.partial(themes.on_click_att_theming_dark_selection, self))
    btn_none_selection_themes = Gtk.Button(label="None")
    btn_none_selection_themes.connect("clicked", functools.partial(themes.on_click_att_theming_none_selection, self))
    for btn_preset in (btn_all_selection_themes, btn_dark_selection_themes, btn_none_selection_themes):
        btn_preset.set_margin_start(10)
        btn_preset.set_margin_end(10)
        hbox_presets.append(btn_preset)

    hbox_family_presets = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    hbox_family_presets.set_halign(Gtk.Align.CENTER)
    for family_label, _family_themes in themes.THEME_FAMILIES:
        btn_family = Gtk.Button(label=family_label)
        btn_family.connect("clicked", functools.partial(themes.on_click_att_family_selection, self, family_label))
        btn_family.set_margin_start(6)
        btn_family.set_margin_end(6)
        hbox_family_presets.append(btn_family)

    hbox_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_install_themes = Gtk.Button(label="Install the selected themes")
    button_install_themes.connect("clicked", functools.partial(themes.on_install_att_themes_clicked, self))
    button_remove_themes = Gtk.Button(label="Uninstall the selected themes")
    button_remove_themes.connect("clicked", functools.partial(themes.on_remove_att_themes_clicked, self))
    button_find_themes = Gtk.Button(label="Show the installed themes")
    button_find_themes.connect("clicked", functools.partial(themes.on_find_att_themes_clicked, self))

    button_find_themes.set_margin_start(10)
    button_find_themes.set_margin_end(10)
    hbox_actions.append(button_find_themes)
    button_install_themes.set_margin_start(10)
    button_install_themes.set_margin_end(10)
    hbox_actions.append(button_install_themes)
    hbox_actions.set_halign(Gtk.Align.CENTER)

    hbox_remove = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_remove.set_halign(Gtk.Align.CENTER)
    button_remove_themes.set_margin_start(10)
    button_remove_themes.set_margin_end(10)
    hbox_remove.append(button_remove_themes)

    _themes_pics = []

    vboxstack_themes.append(hbox_title)
    vboxstack_themes.append(hbox_separator)

    if is_kiro:
        hbox_gtk_theme_hint.set_margin_start(10)
        hbox_gtk_theme_hint.set_margin_end(10)
        hbox_gtk_theme_hint.set_margin_top(10)
        hbox_gtk_theme_hint.set_margin_bottom(10)
        vboxstack_themes.append(hbox_gtk_theme_hint)

        if is_plasma:
            hbox_plasma_qt.set_margin_start(10)
            hbox_plasma_qt.set_margin_end(10)
            hbox_plasma_qt.set_margin_bottom(10)
            vboxstack_themes.append(hbox_plasma_qt)
    else:
        hbox_env_reminder.set_margin_start(10)
        hbox_env_reminder.set_margin_end(10)
        hbox_env_reminder.set_margin_top(10)
        hbox_env_reminder.set_margin_bottom(10)
        vboxstack_themes.append(hbox_env_reminder)

    vboxstack_themes.append(hbox_env_dropdown)

    # Manual escape hatch on every distro — if the automated write misbehaves, edit the file by hand.
    hbox_env_edit.set_margin_start(10)
    hbox_env_edit.set_margin_end(10)
    hbox_env_edit.set_margin_bottom(10)
    vboxstack_themes.append(hbox_env_edit)

    hbox_info.set_margin_start(10)
    hbox_info.set_margin_end(10)
    vboxstack_themes.append(hbox_info)
    if hbox_plasma_warning.get_first_child() is not None:
        hbox_plasma_warning.set_margin_start(10)
        hbox_plasma_warning.set_margin_end(10)
        vboxstack_themes.append(hbox_plasma_warning)
    vbox_families.set_margin_start(10)
    vbox_families.set_margin_end(10)
    vboxstack_themes.append(vbox_families)
    vboxstack_themes.append(
        _att_preview_picture(Gtk, GdkPixbuf, Gdk, base_dir, "arcthemes.jpg", scale=1, out_pics=_themes_pics)
    )
    hbox_presets.set_margin_start(10)
    hbox_presets.set_margin_end(10)
    vboxstack_themes.append(hbox_presets)
    hbox_family_presets.set_margin_start(10)
    hbox_family_presets.set_margin_end(10)
    hbox_family_presets.set_margin_bottom(10)
    vboxstack_themes.append(hbox_family_presets)
    vboxstack_themes.append(hbox_actions)
    vboxstack_themes.append(hbox_remove)

    return _themes_pics

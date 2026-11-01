# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
import celestial
from att_i18n import _
import themes
import themes_gui


def _refresh_repo_state(self, fn):
    """Show the repo warning, grey the theme Install button, and resync the forge row."""
    available = celestial.repo_available()
    self.celestial_repo_warning.set_visible(not available)
    self.celestial_install_btn.set_sensitive(available)
    self.celestial_install_btn.set_tooltip_text(
        "" if available else _("Enable nemesis_repo on the Pacman page to install celestial themes")
    )
    # Owns the forge button's own Install/Launch state, which does not follow the repo
    # once the generator is installed.
    celestial.refresh_forge_state(self)


def gui(self, Gtk, vboxstack_celestial, fn):
    """Create the Celestial GUI (celestial theme checkboxes grouped by colour family)."""
    fn.log_info(f"{celestial.available_count()} celestial themes available to install")

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text(_("Celestial themes"))
    lbl_title.set_name("title")
    hbox_title.append(lbl_title)

    hbox_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_separator.append(hseparator)

    hbox_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_info = Gtk.Label(xalign=0)
    lbl_info.set_markup(
        _(
            "Select the packages you want to install or remove, then click the appropriate button.\n"
            "Every celestial theme ships a base, a <b>Dark</b> and a <b>Light</b> variant in three DPI tiers.\n"
            'Ensure that the <b>Nemesis repository is enabled</b> — see the "Pacman" tab for details.'
        )
    )
    lbl_info.set_margin_start(10)
    lbl_info.set_margin_end(10)
    hbox_info.append(lbl_info)

    hbox_repo_warning = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.celestial_repo_warning = Gtk.Label(xalign=0)
    self.celestial_repo_warning.set_margin_start(20)
    self.celestial_repo_warning.set_margin_end(20)
    self.celestial_repo_warning.set_margin_top(10)
    self.celestial_repo_warning.set_wrap(True)
    self.celestial_repo_warning.set_markup(
        '<span foreground="#FFA500"><b>nemesis_repo is not enabled — every celestial package lives there. '
        "Enable it on the Pacman page first.</b></span>"
    )
    self.celestial_repo_warning.set_visible(False)
    hbox_repo_warning.append(self.celestial_repo_warning)

    hbox_env_dropdown = themes_gui.build_env_theme_row(
        Gtk, self, "_celestial_env_theme_names", "celestial_env_dropdown", celestial.on_click_apply_env_theme
    )

    hbox_env_hint = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_env_hint.set_halign(Gtk.Align.CENTER)
    lbl_env_hint = Gtk.Label()
    lbl_env_hint.set_markup(
        '<span size="large">Install themes first — the dropdown lists what is present in /usr/share/themes.</span>'
    )
    lbl_env_hint.set_justify(Gtk.Justification.CENTER)
    hbox_env_hint.append(lbl_env_hint)

    hbox_env_edit = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_env_edit.set_halign(Gtk.Align.CENTER)
    button_edit_env = Gtk.Button(label=_("Edit /etc/environment in terminal"))
    button_edit_env.connect("clicked", functools.partial(themes.on_click_edit_environment, self))
    button_edit_env.set_margin_start(10)
    button_edit_env.set_margin_end(10)
    hbox_env_edit.append(button_edit_env)

    self.celestial_checkboxes = {}
    vbox_families = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    vbox_families.set_hexpand(True)
    vbox_families.set_margin_start(10)
    vbox_families.set_margin_end(10)

    for family_label, family_themes in celestial.CELESTIAL_FAMILIES:
        lbl_family = Gtk.Label(xalign=0)
        lbl_family.set_markup("<b>{label}</b>".format(label=_(family_label)))
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

        for token, hex_color in family_themes:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row.append(themes_gui.make_swatch(Gtk, hex_color))
            checkbox = Gtk.CheckButton(label="celestial-" + token)
            self.celestial_checkboxes[token] = checkbox
            row.append(checkbox)
            flowbox_family.append(row)

        vbox_families.append(flowbox_family)

    hbox_presets = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    hbox_presets.set_hexpand(True)
    hbox_presets.set_margin_start(10)
    hbox_presets.set_margin_end(10)
    lbl_preset_hint = Gtk.Label()
    lbl_preset_hint.set_text(_("Choose what to select with a button"))
    lbl_preset_hint.set_margin_start(10)
    lbl_preset_hint.set_margin_end(10)
    lbl_preset_hint.set_hexpand(True)
    lbl_preset_hint.set_xalign(0)
    hbox_presets.append(lbl_preset_hint)

    btn_all_selection = Gtk.Button(label=_("All"))
    btn_all_selection.connect("clicked", functools.partial(celestial.on_click_all_selection, self))
    btn_none_selection = Gtk.Button(label=_("None"))
    btn_none_selection.connect("clicked", functools.partial(celestial.on_click_none_selection, self))
    for btn_preset in (btn_all_selection, btn_none_selection):
        btn_preset.set_margin_start(10)
        btn_preset.set_margin_end(10)
        hbox_presets.append(btn_preset)

    hbox_family_presets = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    hbox_family_presets.set_halign(Gtk.Align.CENTER)
    hbox_family_presets.set_margin_start(10)
    hbox_family_presets.set_margin_end(10)
    hbox_family_presets.set_margin_bottom(10)
    for family_label, _family_themes in celestial.CELESTIAL_FAMILIES:
        btn_family = Gtk.Button(label=_(family_label))
        btn_family.connect("clicked", functools.partial(celestial.on_click_family_selection, self, family_label))
        btn_family.set_margin_start(6)
        btn_family.set_margin_end(6)
        hbox_family_presets.append(btn_family)

    hbox_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_actions.set_halign(Gtk.Align.CENTER)
    button_find_themes = Gtk.Button(label=_("Show the installed themes"))
    button_find_themes.connect("clicked", functools.partial(celestial.on_find_clicked, self))
    button_find_themes.set_margin_start(10)
    button_find_themes.set_margin_end(10)
    hbox_actions.append(button_find_themes)
    button_install_themes = Gtk.Button(label=_("Install the selected themes"))
    button_install_themes.connect("clicked", functools.partial(celestial.on_install_clicked, self))
    button_install_themes.set_margin_start(10)
    button_install_themes.set_margin_end(10)
    self.celestial_install_btn = button_install_themes
    hbox_actions.append(button_install_themes)

    hbox_forge_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    forge_separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    forge_separator.set_hexpand(True)
    forge_separator.set_margin_top(10)
    hbox_forge_separator.append(forge_separator)

    hbox_forge_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_forge_title = Gtk.Label(xalign=0)
    lbl_forge_title.set_markup(_("<b>Theme generator — celestial-theme-forge</b>"))
    lbl_forge_title.set_margin_start(10)
    lbl_forge_title.set_margin_top(6)
    hbox_forge_title.append(lbl_forge_title)

    hbox_forge_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_forge_info = Gtk.Label(xalign=0)
    lbl_forge_info.set_markup(
        _(
            "This is <b>not a theme</b> — it is the tool that <b>builds</b> the themes above.\n"
            "It rebuilds the Celestial GTK theme in any accent colour you name, so you are not limited to the\n"
            "list on this page. You only need it if you want a colour that is not shipped yet.\n\n"
            "It installs two commands: <b>celestial-theme-forge</b> (the generator) and <b>theme-forge-picker</b>\n"
            "(a small GTK4 picker with a screen eyedropper — xcolor on X11, hyprpicker on Wayland). Your own\n"
            "colours are remembered in <b>custom-colors.def</b> and generated alongside the curated ones.\n\n"
            "It pulls in build tools (git, python, sassc, inkscape, imagemagick) and it needs a checkout of the\n"
            "celestial theme sources to build against. The result is a theme folder you install yourself —\n"
            "generating a colour here does not add it to the checkboxes above.\n\n"
            "Removing the forge uses a plain removal, so the build tools and any themes it already generated stay."
        )
    )
    lbl_forge_info.set_margin_start(10)
    lbl_forge_info.set_margin_end(10)
    hbox_forge_info.append(lbl_forge_info)

    # LinkButton's default handler would xdg-open as root and fail — the callback
    # returns True so fn.open_url_as_user() does it as the real user instead.
    hbox_upstream = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_upstream.set_margin_start(10)
    hbox_upstream.set_margin_end(10)
    btn_upstream = Gtk.LinkButton.new_with_label(
        celestial.UPSTREAM_URL,
        _("Celestial is made by zquestz — open the upstream project on GitHub"),
    )
    btn_upstream.connect("activate-link", functools.partial(celestial.on_open_upstream, self))
    hbox_upstream.append(btn_upstream)

    hbox_forge_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_forge_actions.set_halign(Gtk.Align.CENTER)
    hbox_forge_actions.set_margin_top(10)
    hbox_forge_actions.set_margin_bottom(10)
    lbl_forge_status = Gtk.Label(xalign=0)
    lbl_forge_status.set_margin_start(10)
    lbl_forge_status.set_margin_end(10)
    self.lbl_celestial_forge = lbl_forge_status
    hbox_forge_actions.append(lbl_forge_status)
    # Label and sensitivity are set by celestial.refresh_forge_state() — Launch once installed.
    button_forge = Gtk.Button(label=_("Install the generator"))
    button_forge.connect("clicked", functools.partial(celestial.on_forge_button_clicked, self))
    button_forge.set_margin_start(10)
    button_forge.set_margin_end(10)
    self.celestial_forge_install_btn = button_forge
    hbox_forge_actions.append(button_forge)
    button_remove_forge = Gtk.Button(label=_("Remove the generator"))
    button_remove_forge.connect("clicked", functools.partial(celestial.on_remove_forge_clicked, self))
    button_remove_forge.set_margin_start(10)
    button_remove_forge.set_margin_end(10)
    self.celestial_forge_remove_btn = button_remove_forge
    hbox_forge_actions.append(button_remove_forge)

    hbox_remove = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_remove.set_halign(Gtk.Align.CENTER)
    button_remove_themes = Gtk.Button(label=_("Uninstall the selected themes"))
    button_remove_themes.connect("clicked", functools.partial(celestial.on_remove_clicked, self))
    button_remove_themes.set_margin_start(10)
    button_remove_themes.set_margin_end(10)
    hbox_remove.append(button_remove_themes)

    vboxstack_celestial.append(hbox_title)
    vboxstack_celestial.append(hbox_separator)
    hbox_env_hint.set_margin_start(10)
    hbox_env_hint.set_margin_end(10)
    hbox_env_hint.set_margin_top(10)
    hbox_env_hint.set_margin_bottom(10)
    vboxstack_celestial.append(hbox_env_hint)
    vboxstack_celestial.append(hbox_env_dropdown)
    hbox_env_edit.set_margin_start(10)
    hbox_env_edit.set_margin_end(10)
    hbox_env_edit.set_margin_bottom(10)
    vboxstack_celestial.append(hbox_env_edit)
    vboxstack_celestial.append(hbox_info)
    vboxstack_celestial.append(hbox_repo_warning)
    vboxstack_celestial.append(vbox_families)
    vboxstack_celestial.append(hbox_presets)
    vboxstack_celestial.append(hbox_family_presets)
    vboxstack_celestial.append(hbox_actions)
    vboxstack_celestial.append(hbox_remove)
    vboxstack_celestial.append(hbox_forge_separator)
    vboxstack_celestial.append(hbox_forge_title)
    vboxstack_celestial.append(hbox_forge_info)
    vboxstack_celestial.append(hbox_upstream)
    vboxstack_celestial.append(hbox_forge_actions)

    # Called immediately AND on every map: the repo can be toggled on the Pacman page
    # after this deferred page was built, and the forge can be installed elsewhere.
    _refresh_repo_state(self, fn)
    vboxstack_celestial.connect("map", lambda _widget: _refresh_repo_state(self, fn))

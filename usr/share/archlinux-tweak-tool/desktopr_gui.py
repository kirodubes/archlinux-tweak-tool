# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools

from att_i18n import _

# Desktop preview: decode at this max edge (sharp when scaled); minimum widget size (GTK size_request).
IMAGE_PREVIEW_LOAD = 855
IMAGE_PREVIEW_MIN = 456


def gui(self, Gtk, GdkPixbuf, vboxstack_desktop, desktopr, fn, base_dir):
    from gi.repository import Gdk

    self.base_dir = base_dir

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    buttonbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    checkbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    vboxprog = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

    dropbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)

    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text(_("Desktop"))
    lbl_title.set_name("title")
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_separator.append(hseparator)
    hbox_title.append(lbl_title)

    # =======================================
    #               DROPDOWN
    # =======================================
    label_warning = Gtk.Label(xalign=0.5)
    label_warning.set_markup(
        "<big>{}</big>".format(
            _("Make sure the {repo1} and {repo2} are both enabled - see Pacman tab").format(
                repo1="chaotic-aur", repo2="nemesis repo"
            )
        )
    )
    label = Gtk.Label(xalign=0.5)
    label.set_text("\n" + _("Select a desktop"))
    label.set_halign(Gtk.Align.CENTER)

    self.d_combo = Gtk.DropDown.new_from_strings(list(desktopr.desktops))
    self.d_combo.set_name("desktop_combo")
    self.d_combo.set_size_request(220, 0)
    self.d_combo.set_selected(0)
    self.d_combo.connect("notify::selected", functools.partial(desktopr.on_d_combo_changed, self))
    # removed in GTK4: set_wrap_width

    dropbox.append(label_warning)

    dropbox.append(label)

    combo_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    combo_hbox.set_margin_top(10)
    combo_hbox.set_halign(Gtk.Align.CENTER)
    self.d_combo.set_halign(Gtk.Align.CENTER)
    combo_hbox.append(self.d_combo)
    dropbox.append(combo_hbox)

    self.label_installed_desktops = Gtk.Label(xalign=0.5)
    self.label_installed_desktops.set_halign(Gtk.Align.CENTER)
    self.label_installed_desktops.set_justify(Gtk.Justification.CENTER)
    self.label_installed_desktops.set_wrap(True)
    self.label_installed_desktops.set_hexpand(True)
    self.label_installed_desktops.set_margin_top(6)
    dropbox.append(self.label_installed_desktops)
    desktopr.refresh_installed_desktops(self)

    # =======================================
    #               BUTTONS
    # =======================================

    self.button_install = Gtk.Button(label=_("Install desktop"))

    self.button_install.connect("clicked", functools.partial(desktopr.on_install_clicked, self))

    self.button_install.set_hexpand(False)
    self.button_install.set_vexpand(False)
    update_button_state(self, fn)
    buttonbox.set_halign(Gtk.Align.CENTER)
    buttonbox.append(self.button_install)

    # =======================================
    #               UNINSTALL BUTTON
    # =======================================

    uninstall_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.button_uninstall = Gtk.Button(label=_("Remove desktop"))
    self.button_uninstall.connect("clicked", functools.partial(desktopr.on_uninstall_clicked, self))
    self.button_uninstall.set_hexpand(False)
    self.button_uninstall.set_vexpand(False)
    uninstall_hbox.set_halign(Gtk.Align.CENTER)
    uninstall_hbox.append(self.button_uninstall)

    # =======================================
    #               CHECKBOX
    # =======================================

    self.ch1 = Gtk.CheckButton(label=_("Clear package cache before installation"))
    checkbox.append(self.ch1)

    # =======================================
    #               TEXTVIEW
    # =======================================
    noice = Gtk.Label(xalign=0.5)
    noice.set_halign(Gtk.Align.CENTER)
    noice.set_justify(Gtk.Justification.CENTER)
    noice.set_markup(
        _(
            "When installing a desktop we back up only the configs it will overwrite\n"
            "Backup is in ~/.config-att folder\n"
            "Uninstalling a desktop leaves its ~/.config subfolder intact\n"
            "Remove it yourself if no longer needed\n"
        )
    )
    noice.set_wrap(True)
    vboxprog.append(noice)

    # =======================================
    #               FRAME PREVIEW
    # =======================================
    try:
        pixbuf3 = GdkPixbuf.Pixbuf.new_from_file_at_size(
            base_dir + "/desktop_data/" + fn.get_combo_text(self.d_combo) + ".jpg",
            IMAGE_PREVIEW_LOAD,
            IMAGE_PREVIEW_LOAD,
        )
        texture = Gdk.Texture.new_for_pixbuf(pixbuf3)
        self.image_DE.set_paintable(texture)
    except Exception:
        pass
    self.image_DE.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
    # size_request = minimum allocation; Picture inside ScrolledWindow often got 0×0 and hid the image.
    self.image_DE.set_size_request(IMAGE_PREVIEW_MIN, IMAGE_PREVIEW_MIN)
    self.image_DE.set_hexpand(True)
    self.image_DE.set_vexpand(False)
    self.image_DE.set_halign(Gtk.Align.CENTER)
    self.image_DE.set_valign(Gtk.Align.CENTER)

    frame = Gtk.Frame(label=_("Preview"))
    frame.set_child(self.image_DE)

    # =======================================
    #        ONE-WAY INSTALL WARNING LABEL
    # =======================================

    self.hbox_oneway_warning = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.hbox_oneway_warning.set_halign(Gtk.Align.CENTER)
    self.hbox_oneway_warning.set_margin_top(4)
    self.lbl_oneway_warning = Gtk.Label()
    self.lbl_oneway_warning.set_halign(Gtk.Align.CENTER)
    self.hbox_oneway_warning.append(self.lbl_oneway_warning)
    self.hbox_oneway_warning.set_visible(False)

    # =======================================
    #        PLASMA META PACKAGE TIP
    # =======================================

    self.hbox_plasma_tip = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.hbox_plasma_tip.set_halign(Gtk.Align.CENTER)
    self.hbox_plasma_tip.set_margin_top(4)
    self.lbl_plasma_tip = Gtk.Label()
    self.lbl_plasma_tip.set_halign(Gtk.Align.CENTER)
    self.lbl_plasma_tip.set_wrap(True)
    self.hbox_plasma_tip.append(self.lbl_plasma_tip)
    self.hbox_plasma_tip.set_visible(False)

    # =======================================
    #           BACKUP NOTICE LABEL
    # =======================================

    self.hbox_backup_notice = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.hbox_backup_notice.set_halign(Gtk.Align.CENTER)
    self.hbox_backup_notice.set_margin_top(4)
    self.lbl_backup_notice = Gtk.Label()
    self.lbl_backup_notice.set_markup(
        '<span foreground="#FFD700"><b>{}</b></span>'.format(
            _("Backing up the configs this desktop will overwrite to ~/.config-att ...")
        )
    )
    self.lbl_backup_notice.set_halign(Gtk.Align.CENTER)
    self.hbox_backup_notice.append(self.lbl_backup_notice)
    self.hbox_backup_notice.set_visible(False)

    # =======================================
    #               PACK TO BOXES
    # =======================================
    vbox.append(dropbox)
    frame.set_hexpand(True)
    frame.set_vexpand(False)
    frame.set_margin_start(0)
    frame.set_margin_end(0)
    vbox.append(frame)
    vbox.append(checkbox)
    vbox.append(self.hbox_oneway_warning)
    vbox.append(self.hbox_plasma_tip)
    vbox.append(buttonbox)
    vbox.append(uninstall_hbox)
    vbox.append(vboxprog)
    vbox.append(self.hbox_backup_notice)

    vbox.set_hexpand(True)
    vbox.set_vexpand(True)
    vbox.set_margin_start(10)
    vbox.set_margin_end(10)

    hbox_dev_test = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_dev_test.set_halign(Gtk.Align.CENTER)
    hbox_dev_test.set_margin_top(10)
    btn_install_all = Gtk.Button()
    lbl_install_all = Gtk.Label()
    lbl_install_all.set_markup('<span foreground="#FFD700">{}</span>'.format(_("Install all desktops")))
    btn_install_all.set_child(lbl_install_all)
    btn_install_all.connect("clicked", lambda _w: desktopr.install_all_desktops(self))
    btn_install_all_twms = Gtk.Button()
    lbl_install_all_twms = Gtk.Label()
    lbl_install_all_twms.set_markup('<span foreground="#FFD700">{}</span>'.format(_("Install all twms")))
    btn_install_all_twms.set_child(lbl_install_all_twms)
    btn_install_all_twms.connect("clicked", lambda _w: desktopr.install_all_twms(self))
    btn_remove_all = Gtk.Button(label=_("Remove all desktops"))
    btn_remove_all.connect("clicked", lambda _w: desktopr.remove_all_desktops(self))
    hbox_dev_test.append(btn_install_all)
    hbox_dev_test.append(btn_install_all_twms)
    hbox_dev_test.append(btn_remove_all)

    # =======================================
    #               PACK TO WINDOW
    # =======================================
    vboxstack_desktop.append(hbox_title)
    vboxstack_desktop.append(hbox_separator)
    vboxstack_desktop.append(vbox)
    if fn.DEV:
        vboxstack_desktop.append(hbox_dev_test)

    nemesis_active = fn.check_nemesis_repo_active()
    chaotic_active = fn.check_chaotic_aur_active()
    fn.log_info(
        f"Desktop — nemesis_repo: {'enabled' if nemesis_active else 'NOT enabled'}, "
        f"chaotic-aur: {'enabled' if chaotic_active else 'NOT enabled'}"
    )


def update_button_state(self, fn):
    if not hasattr(self, "d_combo"):
        return
    import desktopr
    from gi.repository import GLib

    selected = fn.get_combo_text(self.d_combo)
    nemesis_active = fn.check_nemesis_repo_active()
    can_install = nemesis_active or not desktopr.desktop_needs_nemesis(selected)
    self.button_install.set_sensitive(can_install)
    if can_install:
        self.button_install.set_tooltip_text("")
    else:
        self.button_install.set_tooltip_text(
            _("Enable {repo1} and {repo2} in the Pacman tab to install this desktop").format(
                repo1="nemesis_repo", repo2="chaotic-aur"
            )
        )

    if hasattr(self, "button_uninstall"):
        if selected in desktopr.ONE_WAY_DESKTOPS:
            de_name = desktopr.desktop_display_name(selected)
            self.button_uninstall.set_sensitive(False)
            self.button_uninstall.set_tooltip_text(
                _("{name} cannot be safely removed — reinstall the system to switch desktop environments").format(
                    name=de_name
                )
            )
        else:
            self.button_uninstall.set_sensitive(True)
            self.button_uninstall.set_tooltip_text("")

    if hasattr(self, "hbox_oneway_warning"):
        if selected in desktopr.ONE_WAY_DESKTOPS:
            de_name = desktopr.desktop_display_name(selected)
            self.lbl_oneway_warning.set_markup(
                '<span foreground="#FFA500"><b>{}</b></span>'.format(
                    _("WARNING: Installing {name} is a one-way operation — removal requires a system reinstall").format(
                        name=de_name
                    )
                )
            )
            self.hbox_oneway_warning.set_visible(True)
            fn.log_warn(f"{de_name} selected — installing is a one-way operation; removal requires a full system reinstall")
            fn.show_in_app_notification(
                self,
                _("WARNING: Installing {name} is a one-way operation — removal requires a system reinstall").format(
                    name=de_name
                ),
            )
        else:
            self.hbox_oneway_warning.set_visible(False)

    if hasattr(self, "hbox_plasma_tip"):
        if selected == "plasma" and not fn.check_package_installed(desktopr.PLASMA_META_PKG):
            self.lbl_plasma_tip.set_markup(
                '<span foreground="#7FDBFF">{}</span>'.format(GLib.markup_escape_text(desktopr.plasma_meta_tip()))
            )
            self.hbox_plasma_tip.set_visible(True)
        else:
            self.hbox_plasma_tip.set_visible(False)

# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
from att_i18n import _


def gui(self, Gtk, vboxstack_user, user, fn):
    """Create the User Management GUI (create user form, delete user controls)."""
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text(_("User management"))
    lbl_title.set_name("title")
    hbox_title.append(lbl_title)

    hbox_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_separator.append(hseparator)

    hbox_create_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_create_user = Gtk.Label(xalign=0)
    lbl_create_user.set_markup(_("<b>Create user</b>"))
    hbox_create_title.append(lbl_create_user)

    sep_text = "                       "

    label_name = Gtk.Label(xalign=0)
    label_name.set_text(_("    Name"))
    name_sep = Gtk.Label(xalign=0)
    name_sep.set_text(sep_text)

    label_username = Gtk.Label(xalign=0)
    label_username.set_text(_("    Username"))
    uname_sep = Gtk.Label(xalign=0)
    uname_sep.set_text(sep_text)

    label_account_type = Gtk.Label(xalign=0)
    label_account_type.set_text(_("    Account type"))
    account_sep = Gtk.Label(xalign=0)
    account_sep.set_text(sep_text)

    label_password = Gtk.Label(xalign=0)
    label_password.set_text(_("    Password"))
    pwd_sep = Gtk.Label(xalign=0)
    pwd_sep.set_text(sep_text)

    label_confirm_password = Gtk.Label(xalign=0)
    label_confirm_password.set_text(_("    Confirm password"))
    conf_pwd_sep = Gtk.Label(xalign=0)
    conf_pwd_sep.set_text(sep_text)

    self.entry_username = Gtk.Entry()
    self.entry_name = Gtk.Entry()
    self.entry_password = Gtk.Entry()
    self.entry_password.set_visibility(False)
    self.entry_confirm_password = Gtk.Entry()
    self.entry_confirm_password.set_visibility(False)

    self.combo_account_type = Gtk.DropDown.new_from_strings(list(fn.account_list))
    self.combo_account_type.set_selected(1)

    grid = Gtk.Grid()
    grid.attach(label_username, 0, 0, 2, 1)
    grid.attach_next_to(uname_sep, label_username, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach_next_to(self.entry_username, uname_sep, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach(label_name, 0, 2, 2, 1)
    grid.attach_next_to(name_sep, label_name, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach_next_to(self.entry_name, name_sep, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach(label_account_type, 0, 4, 2, 1)
    grid.attach_next_to(account_sep, label_account_type, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach_next_to(self.combo_account_type, account_sep, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach(label_password, 0, 6, 2, 1)
    grid.attach_next_to(pwd_sep, label_password, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach_next_to(self.entry_password, pwd_sep, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach(label_confirm_password, 0, 8, 2, 1)
    grid.attach_next_to(conf_pwd_sep, label_confirm_password, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach_next_to(self.entry_confirm_password, conf_pwd_sep, Gtk.PositionType.RIGHT, 1, 1)

    hbox_admin_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_information = Gtk.Label(xalign=0)
    lbl_information.set_markup(
        _("The following groups are used for an administrator:\n"
        "audio, video, network, storage, rfkill, wheel, autologin, sambashare")
    )
    hbox_admin_info.append(lbl_information)

    hbox_apply = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    apply_settings = Gtk.Button(label=_("Apply settings"))
    apply_settings.connect("clicked", functools.partial(user.on_click_user_apply, self))
    hbox_apply.append(apply_settings)

    hbox_delete_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_delete_user = Gtk.Label(xalign=0)
    lbl_delete_user.set_markup(_("<b>Delete user</b>"))
    hbox_delete_title.append(lbl_delete_user)

    hbox_delete_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator2.set_hexpand(True)
    hseparator2.set_vexpand(False)
    hbox_delete_separator.append(hseparator2)

    hbox_delete_warning = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_warning = Gtk.Label(xalign=0)
    lbl_warning.set_markup(_("<b>Beware - you could delete your own user account</b>"))
    lbl_warning.set_margin_start(10)
    lbl_warning.set_margin_end(10)
    hbox_delete_warning.append(lbl_warning)

    hbox_user_select = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_remove_selected = Gtk.Label(xalign=0)
    lbl_remove_selected.set_text(_("Remove the selected user"))
    button_delete_user = Gtk.Button(label=_("Remove the selected user"))
    button_delete_user.connect("clicked", functools.partial(user.on_click_delete_user, self))
    button_delete_all_user = Gtk.Button(label=_("Remove the selected user and the home folder"))
    button_delete_all_user.connect("clicked", functools.partial(user.on_click_delete_all_user, self))
    self.cbt_users = Gtk.DropDown.new_from_strings([])
    user.pop_cbt_users(self, self.cbt_users)
    lbl_remove_selected.set_margin_start(10)
    lbl_remove_selected.set_margin_end(10)
    hbox_user_select.append(lbl_remove_selected)
    self.cbt_users.set_margin_start(10)
    self.cbt_users.set_margin_end(10)
    hbox_user_select.append(self.cbt_users)

    hbox_delete_all = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_delete_all_user.set_margin_start(10)
    button_delete_all_user.set_margin_end(10)
    hbox_delete_all.append(button_delete_all_user)

    hbox_delete_only = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_delete_user.set_margin_start(10)
    button_delete_user.set_margin_end(10)
    hbox_delete_only.append(button_delete_user)

    hbox_visudo = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    visudo_message = Gtk.Label(xalign=0)
    visudo_message.set_markup(
        _("On <b>pure Arch Linux</b> remember to 'EDITOR=nano visudo' and uncomment "
        "the line '%wheel ALL=(ALL:ALL) ALL'\n"
        "if you want your users to have administrator rights")
    )
    hbox_visudo.append(visudo_message)

    vboxstack_user.append(hbox_title)
    vboxstack_user.append(hbox_separator)
    vboxstack_user.append(hbox_create_title)
    vboxstack_user.append(grid)
    vboxstack_user.append(hbox_admin_info)
    vboxstack_user.append(hbox_apply)
    vboxstack_user.append(hbox_delete_title)
    vboxstack_user.append(hbox_delete_separator)
    vboxstack_user.append(hbox_delete_warning)
    vboxstack_user.append(hbox_user_select)
    vboxstack_user.append(hbox_delete_all)
    vboxstack_user.append(hbox_delete_only)
    if fn.distr == "arch":
        vboxstack_user.append(hbox_visudo)

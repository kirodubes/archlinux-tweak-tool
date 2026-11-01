# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
# pylint:disable=C0301,I1101,W0104

import functions as fn

from functions import GLib
from att_i18n import _


def create_user(self):
    """Create a new user"""
    fn.log_subsection("Create New User Account")
    username = self.entry_username.get_text()
    name = self.entry_name.get_text()
    atype = fn.get_combo_text(self.combo_account_type)
    password = self.entry_password.get_text()
    confirm_password = self.entry_confirm_password.get_text()
    if len(username) > 0 and len(name) > 0 and len(password) > 0 and len(confirm_password) > 0:
        if password == confirm_password:
            fn.debug_print(f"Creating user account: {username} ({name})")
            user_password = "echo " + username + ":" + password
            try:
                fn.debug_print("Ensuring sambashare group exists")
                command = "groupadd -r sambashare"
                fn.subprocess.Popen(
                    command.split(" "),
                    shell=False,
                    stdout=fn.subprocess.PIPE,
                    stderr=fn.subprocess.STDOUT,
                ).wait()
            except Exception as error:
                fn.log_warn(f"Sambashare group error: {error}")

            try:
                if atype == "Administrator":
                    fn.debug_print(f"Adding {username} to administrative groups")
                    useradd = (
                        'useradd -m -G audio,video,network,storage,rfkill,wheel,sambashare -c "'
                        + name
                        + '" -s /bin/bash '
                        + username
                    )
                    fn.system(useradd)
                    fn.system(user_password + " | " + "chpasswd -c SHA512")
                else:
                    fn.debug_print(f"Creating standard user {username}")
                    useradd = (
                        'useradd -m -G audio,video,network,storage,rfkill,sambashare -c "'
                        + name
                        + '" -s /bin/bash '
                        + username
                    )
                    fn.system(useradd)
                    fn.system(user_password + " | " + "chpasswd -c SHA512")
                fn.log_success(f"User account {username} created successfully")
                GLib.idle_add(fn.show_in_app_notification, self, _("User has been created"))
            except Exception as error:
                fn.log_error(f"Failed to create user account: {error}")
                fn.messagebox(self, _("Error"), _("Failed to create user: {error}").format(error=error))
        else:
            fn.log_warn("Password mismatch")
            fn.show_in_app_notification(self, _("Passwords are not the same"))
            fn.messagebox(self, _("Message"), _("Passwords are not the same"))
    else:
        fn.log_warn("Missing required fields")
        fn.show_in_app_notification(self, _("First fill in all the fields"))
        fn.messagebox(self, _("Message"), _("First fill in all the fields"))


def _do_delete_user(self):
    """Delete user, retain home folder"""
    fn.log_subsection("Delete User Account")
    username = fn.get_combo_text(self.cbt_users)
    if username is not None:
        try:
            fn.debug_print(f"Removing user account: {username}")
            fn.system("userdel " + username)
            fn.log_success(f"User {username} deleted - home folder retained")
            GLib.idle_add(fn.show_in_app_notification, self, _("User has been deleted"))
        except Exception as error:
            fn.log_error(f"Failed to delete user: {error}")
            fn.messagebox(self, _("Error"), _("Failed to delete user: {error}").format(error=error))


def _do_delete_all_user(self):
    """Delete user and home folder"""
    fn.log_subsection("Delete User Account and Home Folder")
    username = fn.get_combo_text(self.cbt_users)
    if username is not None:
        try:
            fn.debug_print(f"Removing user account and home folder: {username}")
            fn.system("userdel -r -f " + username)
            fn.log_success(f"User {username} and home folder deleted")
            GLib.idle_add(fn.show_in_app_notification, self, _("User and home folder has been deleted"))
        except Exception as error:
            fn.log_error(f"Failed to delete user and home folder: {error}")
            fn.messagebox(self, _("Error"), _("Failed to delete user: {error}").format(error=error))


def pop_cbt_users(self, combo):
    """Populate dropdown with system users (uid >= 1000)"""
    model = combo.get_model()
    model.splice(0, model.get_n_items(), [])
    users = fn.list_users("/etc/passwd")
    for user in users:
        self.cbt_users.get_model().append(user)
        self.cbt_users.set_selected(0)


# ── User callbacks ──────────────────────────────────────────────────


def on_click_user_apply(self, _widget):
    """Run user creation in a background thread and refresh the users dropdown."""
    fn.log_subsection("Create User")

    def _run():
        create_user(self)
        GLib.idle_add(pop_cbt_users, self, self.cbt_users)

    fn.threading.Thread(target=_run, daemon=True).start()


def on_click_delete_user(self, _widget):
    """Delete the selected user account, retaining the home folder."""
    fn.log_subsection("Delete User")
    _do_delete_user(self)
    pop_cbt_users(self, self.cbt_users)


def on_click_delete_all_user(self, _widget):
    """Delete the selected user account and home folder."""
    fn.log_subsection("Delete All Users")
    _do_delete_all_user(self)
    pop_cbt_users(self, self.cbt_users)

# ============================================================
# Author: Erik Dubois
# ============================================================
# Backup page — logic. Personal-file backup with Pika Backup / Vorta.

import functions as fn
from functions import GLib
from att_i18n import _

# ── Backup app registry ──────────────────────────────────────────────
# Each entry drives one row (label + Launch/Install + Remove) and its
# handlers, in display order.
#   key      : unique slug → label widget attr (lbl_backup_<key>)
#   label    : display name
#   packages : space-separated install set (passed verbatim to pacman)
#   launch   : binary launched as the real user when already installed
# Both packages live in the Arch extra repo — no special repo needed.
BACKUP_APPS = [
    {"key": "pika", "label": "Pika Backup", "packages": "pika-backup", "launch": "pika-backup"},
    {"key": "vorta", "label": "Vorta", "packages": "vorta", "launch": "vorta"},
]


def _label_markup(app, installed):
    if installed:
        return _("{name} <b>installed</b>").format(name=app["label"])
    return app["label"]


def _launch(app):
    fn.subprocess.Popen(
        "sudo -E -u " + fn.sudo_username + " " + app["launch"] + " &",
        shell=True,
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.STDOUT,
        env=fn.get_terminal_env(),
    )


def install_or_launch(self, app, _widget=None):
    """Launch the app if installed, otherwise install its package then launch."""
    primary = app["packages"].split()[0]
    if fn.check_package_installed(primary):
        fn.log_subsection(f"Launching {app['label']}...")
        _launch(app)
        fn.show_in_app_notification(self, _("{name} launched").format(name=app["label"]))
        return

    fn.log_subsection(f"Installing {app['label']}...")
    process = fn.launch_pacman_install_in_terminal(app["packages"])
    GLib.idle_add(fn.show_in_app_notification, self, _("{name} installation started").format(name=app["label"]))

    def wait_install():
        if process is None:
            return
        process.communicate()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed(primary):
            fn.log_success(f"{app['label']} installed")
            label = getattr(self, f"lbl_backup_{app['key']}", None)
            if label:
                GLib.idle_add(label.set_markup, _label_markup(app, True))
            GLib.idle_add(fn.show_in_app_notification, self, _("{name} installed").format(name=app["label"]))
            _launch(app)
        else:
            fn.log_warn(f"{app['label']} install did not complete")
            fn.check_missing_repo_error(self, "", primary)

    fn.threading.Thread(target=wait_install, daemon=True).start()


def remove(self, app, _widget=None):
    """Remove the app's package set plus its now-unused deps (safe -Rns), then refresh its label."""
    primary = app["packages"].split()[0]
    fn.log_subsection(f"Removing {app['label']}...")
    process = fn.launch_pacman_remove_recursive_in_terminal(app["packages"])
    GLib.idle_add(fn.show_in_app_notification, self, _("{name} removal started").format(name=app["label"]))

    def wait_remove():
        if process is None:
            return
        process.communicate()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed(primary):
            fn.log_success(f"{app['label']} removed")
            label = getattr(self, f"lbl_backup_{app['key']}", None)
            if label:
                GLib.idle_add(label.set_markup, _label_markup(app, False))
            GLib.idle_add(fn.show_in_app_notification, self, _("{name} removed").format(name=app["label"]))

    fn.threading.Thread(target=wait_remove, daemon=True).start()

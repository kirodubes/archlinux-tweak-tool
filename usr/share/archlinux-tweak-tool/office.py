# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
from functions import GLib
from att_i18n import N_, _

# ── Office app registry ──────────────────────────────────────────────
# Each entry drives one row (label + Launch/Install + Remove) and its
# handlers. Keyed by tab title, in display order.
#   key      : unique slug → label widget attr (lbl_office_<key>)
#   label    : display name
#   packages : space-separated install set (passed verbatim to pacman)
#   launch   : binary launched as the real user when already installed
#   repo     : "chaotic-aur" if the set needs that repo enabled, else None
#   remove   : packages to remove (defaults to the install set; set
#              explicitly to avoid removing shared library deps)
OFFICE_APPS = {
    N_("Suites"): [
        {"key": "libreoffice", "label": "LibreOffice", "packages": "libreoffice-fresh", "launch": "libreoffice"},
        {
            "key": "onlyoffice",
            "label": "OnlyOffice",
            "packages": "onlyoffice-bin",
            "launch": "onlyoffice-desktopeditors",
            "repo": "chaotic-aur",
        },
        {
            "key": "wps",
            "label": "WPS Office",
            "packages": "wps-office wps-office-fonts wps-office-mime ttf-wps-fonts libtiff5",
            "remove": "wps-office wps-office-fonts wps-office-mime ttf-wps-fonts",
            "launch": "wps",
            "repo": "chaotic-aur",
        },
    ],
    N_("Mail"): [
        {"key": "thunderbird", "label": "Thunderbird", "packages": "thunderbird", "launch": "thunderbird"},
        {"key": "betterbird", "label": "Betterbird", "packages": "betterbird-bin", "launch": "betterbird",
         "repo": "chaotic-aur"},
        {"key": "geary", "label": "Geary", "packages": "geary", "launch": "geary"},
        {"key": "evolution", "label": "Evolution", "packages": "evolution", "launch": "evolution"},
        {"key": "clawsmail", "label": "Claws Mail", "packages": "claws-mail", "launch": "claws-mail"},
        {"key": "kmail", "label": "KMail", "packages": "kmail", "launch": "kmail"},
    ],
    N_("Editors"): [
        {"key": "geany", "label": "Geany", "packages": "geany", "launch": "geany"},
        {"key": "kate", "label": "Kate", "packages": "kate", "launch": "kate"},
        {"key": "mousepad", "label": "Mousepad", "packages": "mousepad", "launch": "mousepad"},
        {"key": "gedit", "label": "Gedit", "packages": "gedit", "launch": "gedit"},
        {"key": "gnometext", "label": "GNOME Text Editor", "packages": "gnome-text-editor",
         "launch": "gnome-text-editor"},
        {"key": "featherpad", "label": "FeatherPad", "packages": "featherpad", "launch": "featherpad"},
    ],
    N_("PDF & Notes"): [
        {"key": "okular", "label": "Okular", "packages": "okular", "launch": "okular"},
        {"key": "evince", "label": "Evince", "packages": "evince", "launch": "evince"},
        {"key": "qpdfview", "label": "qpdfview", "packages": "qpdfview", "launch": "qpdfview",
         "repo": "chaotic-aur"},
        {"key": "pdfarranger", "label": "PDF Arranger", "packages": "pdfarranger", "launch": "pdfarranger"},
        {"key": "xournalpp", "label": "Xournal++", "packages": "xournalpp", "launch": "xournalpp"},
        {"key": "cherrytree", "label": "CherryTree", "packages": "cherrytree", "launch": "cherrytree"},
        {"key": "obsidian", "label": "Obsidian", "packages": "obsidian", "launch": "obsidian"},
    ],
    N_("Scanning"): [
        {"key": "simplescan", "label": "Simple Scan", "packages": "simple-scan", "launch": "simple-scan"},
        {"key": "gscan2pdf", "label": "gscan2pdf", "packages": "gscan2pdf", "launch": "gscan2pdf"},
    ],
}


def all_apps():
    """Flatten the registry to a single list of app dicts."""
    return [app for apps in OFFICE_APPS.values() for app in apps]


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
    """Launch the app if installed, otherwise install its package set then launch."""
    primary = app["packages"].split()[0]
    if fn.check_package_installed(primary):
        fn.log_subsection(f"Launching {app['label']}...")
        _launch(app)
        fn.show_in_app_notification(self, _("{name} launched").format(name=app["label"]))
        return

    if app.get("repo") == "chaotic-aur" and not fn.check_chaotic_aur_active():
        fn.log_warn(f"{app['label']} needs the chaotic-aur repo — not enabled")
        fn.show_in_app_notification(
            self,
            _("{name} needs the {repo} repo — enable it on the Pacman page").format(name=app["label"], repo="chaotic-aur"),
        )
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
            label = getattr(self, f"lbl_office_{app['key']}", None)
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
    # -Rns: also clears dependencies nothing else needs (e.g. WPS's libtiff5);
    # pacman refuses to remove deps still required elsewhere, so it stays safe.
    process = fn.launch_pacman_remove_recursive_in_terminal(app.get("remove", app["packages"]))
    GLib.idle_add(fn.show_in_app_notification, self, _("{name} removal started").format(name=app["label"]))

    def wait_remove():
        if process is None:
            return
        process.communicate()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed(primary):
            fn.log_success(f"{app['label']} removed")
            label = getattr(self, f"lbl_office_{app['key']}", None)
            if label:
                GLib.idle_add(label.set_markup, _label_markup(app, False))
            GLib.idle_add(fn.show_in_app_notification, self, _("{name} removed").format(name=app["label"]))

    fn.threading.Thread(target=wait_remove, daemon=True).start()

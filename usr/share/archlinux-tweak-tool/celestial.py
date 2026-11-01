# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
from att_i18n import N_, _, ngettext
import themes
from functions import GLib


# Celestial palette — single source of truth for the Celestial page.
# Each accent is the theme's own @define-color theme_selected_bg_color, read out of
# the gtk-3.0/gtk.css inside the matching celestial-* package in nemesis_repo.
# Regenerate after adding colours with celestial-theme-forge.
# Each family: (family_label, [(token, accent_hex), ...]).
# token -> package "celestial-<token>", swatch "#<hex>".
# No dark flag here (unlike the arc themes): every package ships the base, -Dark and
# -Light variants in three DPI tiers, so a "select the dark ones" preset is meaningless.
CELESTIAL_FAMILIES = [
    (N_("Blues"), [
        ("aqua", "66a8cb"),
        ("archlinux-blue", "1793d1"),
        ("arcolinux-blue", "6790eb"),
        ("azul", "3498db"),
        ("azure", "456bff"),
        ("azure-dodger-blue", "1e9cff"),
        ("blue-sky", "7684a8"),
        ("botticelli", "82a4b3"),
        ("carolina-blue", "6ba4e7"),
        ("denim", "385fb8"),
        ("dodger-blue", "2a8dff"),
        ("havelock", "6ba4e7"),
        ("light-blue-surfn", "94c2e4"),
        ("medium-blue", "4a71c4"),
        ("neon-blue", "4e60ff"),
        ("nice-blue", "147eb8"),
        ("night-owl", "527c8b"),
        ("polo", "688bc6"),
        ("sky-blue", "7ec1ff"),
        ("soft-blue", "5481e5"),
    ]),
    (N_("Indigos"), [
        ("cornflower-blue", "3250a7"),
        ("dawn", "566282"),
        ("slateblue", "394bd9"),
        ("tory", "596bb0"),
    ]),
    (N_("Purples"), [
        ("blueberry", "52428f"),
        ("bright-lilac", "cd58ff"),
        ("darkish", "28293d"),
        ("dracul", "7e82a0"),
        ("orchid", "ff7def"),
        ("purpley", "8d2dc9"),
        ("red-violet", "901265"),
        ("twilight", "44397d"),
        ("vampire", "555a69"),
    ]),
    (N_("Greens"), [
        ("emerald", "1fa732"),
        ("evopop", "1685a6"),
        ("fern", "65b058"),
        ("mantis", "6aa847"),
        ("niagara", "42edcc"),
        ("pueril", "97bb72"),
        ("sea", "2eb398"),
    ]),
    (N_("Reds"), [
        ("aliz", "f0544c"),
        ("blood", "cf0808"),
        ("crimson", "dc143c"),
        ("hibiscus", "d52f61"),
        ("mandarin", "ea553f"),
        ("mandy", "c93648"),
        ("punch", "c03645"),
    ]),
    (N_("Oranges"), [
        ("casablanca", "fdb95b"),
        ("fire", "f68516"),
        ("jasmine", "fcde83"),
        ("numix", "ffa726"),
        ("red-orange", "fe5100"),
        ("rusty-orange", "e56b1a"),
        ("tacao", "efa369"),
        ("tangerine", "ff9500"),
    ]),
    (N_("Pinks"), [
        ("carnation", "fe6d88"),
        ("froly", "fd7980"),
        ("light-salmon", "ffa38d"),
        ("pink", "ce6ca2"),
        ("warm-pink", "fd3e84"),
    ]),
    (N_("Greys"), [
        ("light-blue-grey", "b8a8bc"),
        ("pale-grey", "e1e3e7"),
        ("paper", "90a4ae"),
        ("slate-grey", "636a78"),
        ("smoke", "a1a1a1"),
    ]),
]


def _pkg(token):
    return "celestial-" + token


def _all_tokens():
    return [token for _label, entries in CELESTIAL_FAMILIES for token, _hex in entries]


def available_count():
    """Return how many celestial themes the page can install."""
    return len(_all_tokens())


def repo_available():
    """Return True when nemesis_repo is enabled — every celestial package is shipped there only."""
    return fn.check_nemesis_repo_active()


def _warn_repo_missing(self):
    """Log and notify that nemesis_repo is off; return True when the caller must stop."""
    if repo_available():
        return False
    fn.log_warn("nemesis_repo is not enabled — celestial packages cannot be installed")
    fn.show_in_app_notification(self, _("nemesis_repo is not enabled — enable it on the Pacman page"))
    return True


def install_themes(self):
    """Install the selected celestial themes with detailed logging."""
    themes_to_install = [_pkg(t) for t in _all_tokens() if self.celestial_checkboxes[t].get_active()]

    if not themes_to_install:
        fn.log_warn("No celestial themes selected for installation")
        fn.show_in_app_notification(self, _("No themes selected for installation"))
        return

    if _warn_repo_missing(self):
        return

    packages_str = " ".join(themes_to_install)
    fn.log_info(f"Installing {len(themes_to_install)} Celestial theme(s): {', '.join(themes_to_install)}")
    process = fn.launch_pacman_install_in_terminal(packages_str)
    fn.show_in_app_notification(self, ngettext("Installing {count} theme...", "Installing {count} themes...", len(themes_to_install)).format(
            count=len(themes_to_install)
        ))
    # The new theme folders only exist once pacman is done, so the dropdown is rebuilt from here.
    fn.wait_and_notify(
        process,
        self,
        _("Celestial themes installation complete"),
        on_done=lambda: themes.refresh_env_theme_dropdowns(self),
    )


def remove_themes(self):
    """Remove the selected celestial themes with detailed logging."""
    themes_to_remove = [_pkg(t) for t in _all_tokens() if self.celestial_checkboxes[t].get_active()]

    if not themes_to_remove:
        fn.log_warn("No celestial themes selected for removal")
        fn.show_in_app_notification(self, _("No themes selected for removal"))
        return

    packages_str = " ".join(themes_to_remove)
    fn.log_info(f"Removing {len(themes_to_remove)} Celestial theme(s): {', '.join(themes_to_remove)}")
    process = fn.launch_pacman_remove_in_terminal(packages_str)
    fn.show_in_app_notification(self, ngettext("Removing {count} theme...", "Removing {count} themes...", len(themes_to_remove)).format(
            count=len(themes_to_remove)
        ))
    fn.wait_and_notify(
        process,
        self,
        _("Celestial themes removal complete"),
        on_done=lambda: themes.refresh_env_theme_dropdowns(self),
    )


def find_themes(self):
    """Check which celestial themes are installed and tick their checkboxes (one bulk query)."""
    installed = fn.check_packages_installed([_pkg(t) for t in _all_tokens()])
    for token in _all_tokens():
        self.celestial_checkboxes[token].set_active(installed.get(_pkg(token), False))


def set_checkboxes_all(self):
    """Select all celestial theme checkboxes."""
    for token in _all_tokens():
        self.celestial_checkboxes[token].set_active(True)


def set_checkboxes_none(self):
    """Deselect all celestial theme checkboxes."""
    for token in _all_tokens():
        self.celestial_checkboxes[token].set_active(False)


def select_family(self, family_label):
    """Tick the checkboxes for one colour family and clear the rest."""
    for label, entries in CELESTIAL_FAMILIES:
        for token, _hex in entries:
            self.celestial_checkboxes[token].set_active(label == family_label)


# ── Celestial callbacks ──────────────────────────────────────────────


def on_install_clicked(self, _widget):
    """Install the checked celestial theme packages."""
    fn.log_subsection("Install Celestial Themes")
    fn.debug_print("Installing selected Celestial themes")
    install_themes(self)


def on_remove_clicked(self, _widget):
    """Remove the checked celestial theme packages."""
    fn.log_subsection("Remove Celestial Themes")
    fn.debug_print("Removing selected Celestial themes")
    remove_themes(self)


def on_find_clicked(self, _widget):
    """Scan installed packages and tick matching celestial theme checkboxes."""
    fn.log_subsection("Scan for Installed Celestial Themes")
    fn.debug_print("Checking which Celestial themes are installed")
    find_themes(self)
    fn.log_success("Celestial theme scan complete")


def on_click_all_selection(self, _widget):
    """Select all celestial theme checkboxes via preset."""
    fn.log_subsection("Select All Celestial Themes")
    set_checkboxes_all(self)
    fn.log_success("All celestial themes selected")


def on_click_none_selection(self, _widget):
    """Deselect all celestial theme checkboxes via preset."""
    fn.log_subsection("Clear Celestial Theme Selection")
    set_checkboxes_none(self)
    fn.log_success("All celestial themes deselected")


def on_click_family_selection(self, family_label, _widget):
    """Select one colour family of celestial themes via preset."""
    fn.log_subsection(f"Select {family_label} Celestial Themes")
    select_family(self, family_label)
    fn.log_success(f"{family_label} celestial themes selected")


def on_click_apply_env_theme(self, _widget):
    """Apply the Celestial-page dropdown selection to /etc/environment."""
    themes.apply_env_theme_from(self, self.celestial_env_dropdown, self._celestial_env_theme_names)


# ── celestial-theme-forge (the generator, not a theme) ───────────────

FORGE_PKG = "celestial-theme-forge"
# The package ships two commands; this is the GTK4 picker, the one worth a button.
FORGE_LAUNCH = "theme-forge-picker"
# Upstream Celestial GTK theme by zquestz — the sources every celestial-* package is recoloured from.
UPSTREAM_URL = "https://github.com/zquestz/celestial-gtk-theme"


def on_open_upstream(self, _widget):
    """Open the upstream celestial-gtk-theme project in the real user's browser."""
    fn.log_subsection("Open the upstream celestial-gtk-theme project")
    fn.open_url_as_user(UPSTREAM_URL)
    fn.show_in_app_notification(self, _("Opening the celestial-gtk-theme project page"))
    return True  # suppress GTK's default xdg-open, which fails from root


def forge_installed():
    """Return True when the celestial-theme-forge generator is installed."""
    return fn.check_package_installed(FORGE_PKG)


def _forge_label_markup(installed):
    if installed:
        return _("{name} <b>installed</b>").format(name=FORGE_PKG)
    return _("{name} <b>not installed</b>").format(name=FORGE_PKG)


def refresh_forge_state(self):
    """Sync the forge status label and its buttons — Launch when installed, Install when not."""
    installed = forge_installed()
    label = getattr(self, "lbl_celestial_forge", None)
    if label:
        label.set_markup(_forge_label_markup(installed))

    button = getattr(self, "celestial_forge_install_btn", None)
    if button:
        button.set_label(_("Launch {name}").format(name=FORGE_LAUNCH) if installed else _("Install the generator"))
        # Launching an installed generator never needs the repo — only installing does.
        usable = installed or repo_available()
        button.set_sensitive(usable)
        button.set_tooltip_text(
            "" if usable else _("Enable nemesis_repo on the Pacman page to install the generator")
        )

    remove_button = getattr(self, "celestial_forge_remove_btn", None)
    if remove_button:
        remove_button.set_sensitive(installed)
        remove_button.set_tooltip_text("" if installed else _("The generator is not installed"))


def _launch_forge():
    fn.subprocess.Popen(
        "sudo -E -u " + fn.sudo_username + " " + FORGE_LAUNCH + " &",
        shell=True,
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.STDOUT,
        env=fn.get_terminal_env(),
    )


def on_forge_button_clicked(self, _widget):
    """Launch the picker when the generator is installed, otherwise install the generator."""
    if forge_installed():
        fn.log_subsection(f"Launching {FORGE_LAUNCH}")
        _launch_forge()
        fn.show_in_app_notification(self, _("{name} launched").format(name=FORGE_LAUNCH))
        return

    fn.log_subsection(f"Install {FORGE_PKG}")
    if _warn_repo_missing(self):
        return

    process = fn.launch_pacman_install_in_terminal(FORGE_PKG)
    GLib.idle_add(fn.show_in_app_notification, self, _("{name} installation started").format(name=FORGE_PKG))

    def wait_install():
        if process is None:
            return
        process.communicate()
        fn.invalidate_pkg_cache()
        if forge_installed():
            fn.log_success(f"{FORGE_PKG} installed — run theme-forge-picker to pick a colour")
            GLib.idle_add(fn.show_in_app_notification, self, _("{name} installed").format(name=FORGE_PKG))
        else:
            fn.log_warn(f"{FORGE_PKG} install did not complete")
            fn.check_missing_repo_error(self, "", FORGE_PKG)
        GLib.idle_add(refresh_forge_state, self)

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_forge_clicked(self, _widget):
    """Remove the celestial-theme-forge generator, leaving any themes it built in place."""
    fn.log_subsection(f"Remove {FORGE_PKG}")
    if not forge_installed():
        fn.log_info(f"{FORGE_PKG} is not installed")
        fn.show_in_app_notification(self, _("{name} is not installed").format(name=FORGE_PKG))
        return

    # Plain -R, not -Rns: the forge's dependencies (git, python, inkscape, imagemagick,
    # sassc) are general-purpose tools a user very likely wants to keep.
    process = fn.launch_pacman_remove_in_terminal(FORGE_PKG)
    GLib.idle_add(fn.show_in_app_notification, self, _("{name} removal started").format(name=FORGE_PKG))

    def wait_remove():
        if process is None:
            return
        process.communicate()
        fn.invalidate_pkg_cache()
        if not forge_installed():
            fn.log_success(f"{FORGE_PKG} removed — themes it already generated are untouched")
            GLib.idle_add(fn.show_in_app_notification, self, _("{name} removed").format(name=FORGE_PKG))
        GLib.idle_add(refresh_forge_state, self)

    fn.threading.Thread(target=wait_remove, daemon=True).start()

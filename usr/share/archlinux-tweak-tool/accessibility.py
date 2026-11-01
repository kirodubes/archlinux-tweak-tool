# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
from functions import GLib
from att_i18n import N_, _

# ── Assistive-tool registry ──────────────────────────────────────────
# Each entry drives one install/launch/remove row, mirroring office.py.
# All packages live in the official [extra] repo, so no AUR helper is
# needed for this section.
#   key      : unique slug → label widget attr (lbl_acc_<key>)
#   label    : display name
#   packages : space-separated install set (passed verbatim to pacman)
#   launch   : binary launched as the real user when already installed
ACCESSIBILITY_APPS = [
    {"key": "orca", "label": N_("Orca (screen reader)"), "packages": "orca", "launch": "orca"},
    {"key": "onboard", "label": N_("Onboard (on-screen keyboard)"), "packages": "onboard", "launch": "onboard"},
    {"key": "kmag", "label": N_("KMag (screen magnifier)"), "packages": "kmag", "launch": "kmag"},
]

# High-contrast / large-text GTK themes ship in this single package; we
# install it here and send the user to the Themer page to apply it,
# rather than switching themes live across the 13 supported WMs.
HIGH_CONTRAST_PKG = "gnome-themes-extra"

# ── AccessX (X11 keyboard accessibility) ─────────────────────────────
# Toggled live via xkbset against the running X session. xkbset is an
# AUR package, so the GUI guards the switches when no helper is present.
#   query : token in `xkbset q` output whose "= On/Off" we read back
#   on/off: shell run as the real user on their DISPLAY
XKBSET_PKG = "xkbset"

ACCESSX = [
    {
        "key": "sticky",
        "label": N_("Sticky Keys"),
        "query": "Sticky-Keys",
        "on": "xkbset sticky -twokey -latchlock; xkbset exp 1 =sticky",
        "off": "xkbset -sticky",
    },
    {
        "key": "slow",
        "label": N_("Slow Keys"),
        "query": "Slow-Keys",
        "on": "xkbset slowkeys 300; xkbset exp 1 =slowkeys",
        "off": "xkbset -slowkeys",
    },
    {
        "key": "bounce",
        "label": N_("Bounce Keys"),
        "query": "Bounce-Keys",
        "on": "xkbset bouncekeys 300; xkbset exp 1 =bouncekeys",
        "off": "xkbset -bouncekeys",
    },
    {
        "key": "mouse",
        "label": N_("Mouse Keys"),
        "query": "Mouse-Keys",
        "on": "xkbset mousekeys; xkbset exp 1 =mousekeys",
        "off": "xkbset -mousekeys",
    },
]

_AUTOSTART_DESKTOP = fn.home + "/.config/autostart/att-accessx.desktop"


# ── Assistive-tool install / launch / remove ─────────────────────────


def _label_markup(app, installed):
    if installed:
        return _("{name} <b>installed</b>").format(name=_(app["label"]))
    return _(app["label"])


def _launch(app):
    fn.subprocess.Popen(
        "sudo -E -u " + fn.sudo_username + " " + app["launch"] + " &",
        shell=True,
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.STDOUT,
        env=fn.get_terminal_env(),
    )


def install_or_launch(self, app, _widget=None):
    """Launch the assistive tool if installed, otherwise install it then launch."""
    primary = app["packages"].split()[0]
    if fn.check_package_installed(primary):
        fn.log_subsection(f"Launching {app['label']}...")
        _launch(app)
        fn.show_in_app_notification(self, _("{name} launched").format(name=_(app["label"])))
        return

    fn.log_subsection(f"Installing {app['label']}...")
    process = fn.launch_pacman_install_in_terminal(app["packages"])
    GLib.idle_add(fn.show_in_app_notification, self, _("{name} installation started").format(name=_(app["label"])))

    def wait_install():
        if process is None:
            return
        process.communicate()
        fn.invalidate_pkg_cache()
        if fn.check_package_installed(primary):
            fn.log_success(f"{app['label']} installed")
            label = getattr(self, f"lbl_acc_{app['key']}", None)
            if label:
                GLib.idle_add(label.set_markup, _label_markup(app, True))
            GLib.idle_add(fn.show_in_app_notification, self, _("{name} installed").format(name=_(app["label"])))
            _launch(app)
        else:
            fn.log_warn(f"{app['label']} install did not complete")
            fn.check_missing_repo_error(self, "", primary)

    fn.threading.Thread(target=wait_install, daemon=True).start()


def remove(self, app, _widget=None):
    """Remove the assistive tool's package set, then refresh its label."""
    primary = app["packages"].split()[0]
    fn.log_subsection(f"Removing {app['label']}...")
    process = fn.launch_pacman_remove_recursive_in_terminal(app["packages"])
    GLib.idle_add(fn.show_in_app_notification, self, _("{name} removal started").format(name=_(app["label"])))

    def wait_remove():
        if process is None:
            return
        process.communicate()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed(primary):
            fn.log_success(f"{app['label']} removed")
            label = getattr(self, f"lbl_acc_{app['key']}", None)
            if label:
                GLib.idle_add(label.set_markup, _label_markup(app, False))
            GLib.idle_add(fn.show_in_app_notification, self, _("{name} removed").format(name=_(app["label"])))

    fn.threading.Thread(target=wait_remove, daemon=True).start()


# ── High contrast / large text ───────────────────────────────────────


def high_contrast_installed():
    return fn.check_package_installed(HIGH_CONTRAST_PKG)


def install_high_contrast(self, _widget=None):
    """Install the high-contrast/large-text theme package, then refresh its label."""
    fn.log_subsection("Installing high-contrast themes (gnome-themes-extra)...")
    process = fn.launch_pacman_install_in_terminal(HIGH_CONTRAST_PKG)
    GLib.idle_add(fn.show_in_app_notification, self, _("High-contrast themes installation started"))

    def wait_install():
        if process is None:
            return
        process.communicate()
        fn.invalidate_pkg_cache()
        if high_contrast_installed():
            fn.log_success("High-contrast themes installed — apply them on the Themer page")
            GLib.idle_add(fn.show_in_app_notification, self, _("High-contrast themes installed — open Themer to apply"))
            refresh = getattr(self, "refresh_high_contrast_lbl", None)
            if refresh:
                GLib.idle_add(refresh)
        else:
            fn.log_warn("High-contrast theme install did not complete")

    fn.threading.Thread(target=wait_install, daemon=True).start()


# ── AccessX live apply + persistence ─────────────────────────────────


def _run_as_user(command):
    """Run a shell command as the real user on their X session; return CompletedProcess."""
    return fn.subprocess.run(
        ["sudo", "-E", "-u", fn.sudo_username, "bash", "-c", command],
        capture_output=True,
        text=True,
        env=fn.get_terminal_env(),
    )


def read_accessx_state():
    """Return {key: bool} for each AccessX feature, parsed from `xkbset q`.

    All features default to False when xkbset is missing or the query fails.
    """
    state = {feature["key"]: False for feature in ACCESSX}
    if not fn.check_package_installed(XKBSET_PKG):
        return state
    result = _run_as_user("xkbset q")
    if result.returncode != 0:
        return state
    # Match the EXACT control key on the left of "=" — `xkbset q` has decoy lines
    # (e.g. "Mouse-Keys Acceleration = On", "Beep if Slow/Bounce-Keys ... = On")
    # that a substring match would wrongly read as the feature being on.
    by_query = {feature["query"]: feature["key"] for feature in ACCESSX}
    for line in result.stdout.splitlines():
        if "=" not in line:
            continue
        key_part, _sep, value = line.partition("=")
        feature_key = by_query.get(key_part.strip())
        if feature_key is not None:
            state[feature_key] = value.strip().lower().startswith("on")
    return state


def apply_accessx(feature, enabled):
    """Apply one AccessX feature live to the running X session, then persist."""
    command = feature["on"] if enabled else feature["off"]
    _run_as_user(command)
    fn.log_info(f"AccessX {feature['label']}: {'on' if enabled else 'off'} (live)")
    _persist()


def _persist():
    """Rewrite the autostart entry from the current live state so toggles survive login."""
    state = read_accessx_state()
    commands = [feature["on"] for feature in ACCESSX if state.get(feature["key"])]
    if not commands:
        if fn.path.isfile(_AUTOSTART_DESKTOP):
            fn.os.remove(_AUTOSTART_DESKTOP)
            fn.log_info("AccessX autostart entry removed (no features enabled)")
        return
    fn.os.makedirs(fn.path.dirname(_AUTOSTART_DESKTOP), exist_ok=True)
    exec_line = "; ".join(commands)
    contents = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=ATT Keyboard Accessibility\n"
        f"Exec=bash -c \"{exec_line}\"\n"
        "X-GNOME-Autostart-enabled=true\n"
        "NoDisplay=true\n"
    )
    with open(_AUTOSTART_DESKTOP, "w", encoding="utf-8") as f:
        f.write(contents)
    fn.permissions(_AUTOSTART_DESKTOP)
    fn.log_info(f"AccessX persisted to {_AUTOSTART_DESKTOP}")


def xkbset_installed():
    return fn.check_package_installed(XKBSET_PKG)


def remove_xkbset(self, _widget=None):
    """Remove xkbset (the keyboard-accessibility backend) and its autostart entry."""
    fn.log_subsection("Removing xkbset (keyboard accessibility)...")
    process = fn.launch_pacman_remove_recursive_in_terminal(XKBSET_PKG)
    GLib.idle_add(fn.show_in_app_notification, self, _("{name} removal started").format(name="xkbset"))

    def wait_remove():
        if process is None:
            return
        process.communicate()
        fn.invalidate_pkg_cache()
        if not fn.check_package_installed(XKBSET_PKG):
            # Drop the autostart entry so its now-dead xkbset lines don't run at next login.
            if fn.path.isfile(_AUTOSTART_DESKTOP):
                fn.os.remove(_AUTOSTART_DESKTOP)
                fn.log_info("AccessX autostart entry removed with xkbset")
            fn.log_success("xkbset removed")
            GLib.idle_add(
                fn.show_in_app_notification,
                self,
                _("{name} removed — keyboard accessibility toggles disabled").format(name="xkbset"),
            )
            refresh = getattr(self, "refresh_xkbset_state", None)
            if refresh:
                GLib.idle_add(refresh)
        else:
            fn.log_warn("xkbset removal did not complete")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def ensure_xkbset(self):
    """Install xkbset via the AUR helper if missing; return True when available."""
    if fn.check_package_installed(XKBSET_PKG):
        return True
    helper = fn.get_aur_helper()
    if helper is None:
        fn.log_warn("xkbset is required for keyboard accessibility but no AUR helper is installed")
        return False
    fn.log_subsection(f"Installing {XKBSET_PKG} via {helper}...")
    GLib.idle_add(fn.show_in_app_notification, self, _("Installing {name} (keyboard accessibility)...").format(name="xkbset"))
    process = fn.launch_aur_install_in_terminal(helper, XKBSET_PKG)
    if process is None:
        return False
    process.communicate()
    fn.invalidate_pkg_cache()
    return fn.check_package_installed(XKBSET_PKG)

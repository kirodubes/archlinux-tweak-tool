# ============================================================
# Authors: Erik Dubois
# ============================================================

import functions as fn
from att_i18n import _

PACKAGE = "kiro-iso-builder"
ARCHISO_PACKAGE = "archiso"
# Resolve relative to this module so it works both from source and when installed.
BUILD_ARCH_ISO_SCRIPT = fn.path.join(fn.path.dirname(fn.path.abspath(__file__)), "data", "bin", "build-arch-iso")


def _refresh_kib_lbl(self):
    if fn.check_package_installed(PACKAGE):
        self.kib_status_lbl.set_markup(_("{name} is <b>installed</b>").format(name=PACKAGE))
    else:
        self.kib_status_lbl.set_markup(_("{name} is <b>not installed</b>").format(name=PACKAGE))


def _refresh_launch_btn(self):
    self.btn_launch_kib.set_sensitive(fn.check_package_installed(PACKAGE))


def on_install_kib_clicked(self, _widget):
    """Install kiro-iso-builder from the Nemesis repo via terminal."""
    if fn.check_package_installed(PACKAGE):
        fn.log_info(f"{PACKAGE} is already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("{name} is already installed").format(name=PACKAGE))
        return
    fn.log_subsection(f"Installing {PACKAGE}...")
    process = fn.launch_pacman_install_in_terminal(PACKAGE)
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Opening terminal to install {name}").format(name=PACKAGE))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success(f"{PACKAGE} installed")
            fn.GLib.idle_add(_refresh_kib_lbl, self)
            fn.GLib.idle_add(_refresh_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("{name} installed").format(name=PACKAGE))
        except Exception as e:
            fn.log_error(f"Error installing {PACKAGE}: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_kib_clicked(self, _widget):
    """Remove kiro-iso-builder via terminal."""
    if not fn.check_package_installed(PACKAGE):
        fn.log_info(f"{PACKAGE} is not installed — nothing to remove")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("{name} is not installed").format(name=PACKAGE))
        return
    fn.log_subsection(f"Removing {PACKAGE}...")
    process = fn.launch_pacman_remove_in_terminal(PACKAGE)
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Opening terminal to remove {name}").format(name=PACKAGE))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success(f"{PACKAGE} removed")
            fn.GLib.idle_add(_refresh_kib_lbl, self)
            fn.GLib.idle_add(_refresh_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("{name} removed").format(name=PACKAGE))
        except Exception as e:
            fn.log_error(f"Error removing {PACKAGE}: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def on_launch_kib_clicked(self, _widget):
    """Launch Kiro ISO Builder as the real user (it elevates internally)."""
    if not fn.check_package_installed(PACKAGE):
        fn.log_info(f"{PACKAGE} not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("{name} not installed").format(name=PACKAGE))
        return
    fn.log_subsection("Launching Kiro ISO Builder...")
    fn.subprocess.Popen(
        "sudo -E -u " + fn.sudo_username + " env HOME=" + fn.home + " " + PACKAGE + " &",
        shell=True,
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.STDOUT,
    )
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("{name} launched").format(name="Kiro ISO Builder"))


def _refresh_archiso_lbl(self):
    if fn.check_package_installed(ARCHISO_PACKAGE):
        self.archiso_status_lbl.set_markup(_("{name} is <b>installed</b>").format(name=ARCHISO_PACKAGE))
    else:
        self.archiso_status_lbl.set_markup(
            _("{name} is <b>not installed</b> — it will be installed first").format(name=ARCHISO_PACKAGE)
        )


def on_build_arch_iso_clicked(self, _widget):
    """Build a vanilla Arch ISO via archiso's releng profile, in a terminal."""
    fn.log_subsection("Building a vanilla Arch ISO...")
    fn.show_in_app_notification(self, _("Opening terminal to build the Arch ISO"))
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", f"{BUILD_ARCH_ISO_SCRIPT} {fn.sudo_username}"],
        shell=False,
    )

    def wait_and_refresh():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Arch ISO build terminal closed")
            fn.GLib.idle_add(_refresh_archiso_lbl, self)
        except Exception as e:
            fn.log_error(f"Error during Arch ISO build: {e}")

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()

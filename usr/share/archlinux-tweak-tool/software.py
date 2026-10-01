# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
import functions_backup as fb
import pacman_functions
from gi.repository import GLib


def on_click_software_pamac(self, _widget):
    """Launch pamac-manager or install pamac-aur if not present."""
    try:
        if fn.path.exists("/usr/bin/pamac-manager"):
            fn.log_subsection("Launching pamac-manager...")
            fn.subprocess.Popen(
                "sudo -E -u " + fn.sudo_username + " pamac-manager &",
                shell=True,
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "Pamac launched")
        else:
            fn.log_subsection("Installing pamac-aur...")
            process = fn.launch_pacman_install_in_terminal("pamac-aur")
            GLib.idle_add(fn.show_in_app_notification, self, "pamac-aur installation started")

            def wait_install():
                try:
                    import time

                    fn.debug_print("Waiting for pamac-aur installation to complete...")
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.debug_print("Installation process completed")
                    time.sleep(1)
                    if fn.path.exists("/usr/bin/pamac-manager"):
                        fn.log_success("pamac-aur installed successfully")
                        GLib.idle_add(
                            self.lbl_software_pamac.set_markup, "Pamac - GUI package manager <b>installed</b>"
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "pamac-aur installed")
                        time.sleep(1)
                        fn.log_subsection("Launching pamac-manager...")
                        fn.subprocess.Popen(
                            "sudo -E -u " + fn.sudo_username + " pamac-manager &",
                            shell=True,
                            stdout=fn.subprocess.PIPE,
                            stderr=fn.subprocess.STDOUT,
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "Pamac launched")
                    else:
                        fn.log_warn("pamac-aur binary NOT found, installation may have failed")
                        fn.check_missing_repo_error(self, "", "pamac-aur")
                except Exception as e:
                    fn.log_error(f"Error during installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with pamac: {error}")


def on_click_software_octopi(self, _widget):
    """Launch octopi or install it if not present."""
    try:
        if fn.path.exists("/usr/bin/octopi"):
            fn.log_subsection("Launching octopi...")
            fn.subprocess.Popen(
                "sudo -E -u " + fn.sudo_username + " octopi &",
                shell=True,
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "Octopi launched")
        else:
            fn.log_subsection("Installing octopi...")
            process = fn.launch_pacman_install_in_terminal("octopi")
            GLib.idle_add(fn.show_in_app_notification, self, "octopi installation started")

            def wait_install():
                try:
                    import time

                    fn.debug_print("Waiting for octopi installation to complete...")
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.debug_print("Installation process completed")
                    time.sleep(1)
                    fn.invalidate_pkg_cache()
                    if fn.path.exists("/usr/bin/octopi"):
                        fn.log_success("octopi installed successfully")
                        GLib.idle_add(
                            self.lbl_software_octopi.set_markup, "Octopi - GUI package manager <b>installed</b>"
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "octopi installed")
                        fn.log_subsection("Launching octopi...")
                        fn.subprocess.Popen(
                            "sudo -E -u " + fn.sudo_username + " octopi &",
                            shell=True,
                            stdout=fn.subprocess.PIPE,
                            stderr=fn.subprocess.STDOUT,
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "Octopi launched")
                    else:
                        fn.log_warn("octopi binary NOT found, installation may have failed")
                        GLib.idle_add(fn.check_missing_repo_error, self, "", "octopi")
                except Exception as e:
                    fn.log_error(f"Error during installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with octopi: {error}")


def on_click_software_bazaar(self, _widget):
    """Launch bazaar or install it if not present."""
    try:
        if fn.path.exists("/usr/bin/bazaar"):
            fn.log_subsection("Launching bazaar...")
            fn.subprocess.Popen(
                "sudo -E -u " + fn.sudo_username + " bazaar &",
                shell=True,
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
                env=fn.get_terminal_env(),
            )
            GLib.idle_add(fn.show_in_app_notification, self, "Bazaar launched")
        else:
            fn.log_subsection("Installing bazaar...")
            process = fn.launch_pacman_install_in_terminal("bazaar")
            GLib.idle_add(fn.show_in_app_notification, self, "bazaar installation started")

            def wait_install():
                try:
                    import time

                    fn.debug_print("Waiting for bazaar installation to complete...")
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.debug_print("Installation process completed")
                    time.sleep(1)
                    if fn.path.exists("/usr/bin/bazaar"):
                        fn.log_success("bazaar installed successfully")
                        GLib.idle_add(self.lbl_software_bazaar.set_markup, "Bazaar <b>installed</b>")
                        if fn.path.exists("/usr/bin/flatpak"):
                            fn.log_info("flatpak pulled in as dependency")
                            GLib.idle_add(
                                self.lbl_software_flatpak.set_markup, "Flatpak - Manage Flatpak apps <b>installed</b>"
                            )
                        GLib.idle_add(fn.show_in_app_notification, self, "bazaar installed")
                        time.sleep(1)
                        fn.log_subsection("Launching bazaar...")
                        fn.subprocess.Popen(
                            "sudo -E -u " + fn.sudo_username + " bazaar &",
                            shell=True,
                            stdout=fn.subprocess.PIPE,
                            stderr=fn.subprocess.STDOUT,
                            env=fn.get_terminal_env(),
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "Bazaar launched")
                    else:
                        fn.log_warn("bazaar binary NOT found, installation may have failed")
                        fn.check_missing_repo_error(self, "", "bazaar")
                except Exception as e:
                    fn.log_error(f"Error during installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with bazaar: {error}")


def on_click_software_shelly(self, _widget):
    """Launch shelly or install it if not present."""
    try:
        if fn.path.exists("/usr/bin/shelly-ui"):
            fn.log_subsection("Launching shelly...")
            fn.subprocess.Popen(
                "sudo -E -u " + fn.sudo_username + " shelly-ui &",
                shell=True,
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
                env=fn.get_terminal_env(),
            )
            GLib.idle_add(fn.show_in_app_notification, self, "Shelly launched")
        else:
            fn.log_subsection("Installing shelly...")
            process = fn.launch_pacman_install_in_terminal("shelly")
            GLib.idle_add(fn.show_in_app_notification, self, "shelly installation started")

            def wait_install():
                try:
                    import time

                    fn.debug_print("Waiting for shelly installation to complete...")
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.debug_print("Installation process completed")
                    time.sleep(1)
                    if fn.path.exists("/usr/bin/shelly-ui"):
                        fn.log_success("shelly installed successfully")
                        GLib.idle_add(
                            self.lbl_software_shelly.set_markup, "Shelly - Modern package manager <b>installed</b>"
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "shelly installed")
                        time.sleep(1)
                        fn.log_subsection("Launching shelly...")
                        fn.subprocess.Popen(
                            "sudo -E -u " + fn.sudo_username + " shelly-ui &",
                            shell=True,
                            stdout=fn.subprocess.PIPE,
                            stderr=fn.subprocess.STDOUT,
                            env=fn.get_terminal_env(),
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "Shelly launched")
                    else:
                        fn.log_warn("shelly binary NOT found, installation may have failed")
                        fn.check_missing_repo_error(self, "", "shelly")
                except Exception as e:
                    fn.log_error(f"Error during installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with shelly: {error}")


def on_click_software_gnome(self, _widget):
    """Launch gnome-software or install it if not present."""
    try:
        if fn.path.exists("/usr/bin/gnome-software"):
            fn.log_subsection("Launching gnome-software...")
            import pwd

            uid = pwd.getpwnam(fn.sudo_username).pw_uid
            fn.subprocess.Popen(
                "sudo -E -u "
                + fn.sudo_username
                + " HOME=/home/"
                + fn.sudo_username
                + " XDG_RUNTIME_DIR=/run/user/"
                + str(uid)
                + " DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/"
                + str(uid)
                + "/bus"
                + " gnome-software &",
                shell=True,
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "GNOME Software launched")
        else:
            fn.log_subsection("Installing gnome-software...")
            process = fn.launch_pacman_install_in_terminal("gnome-software")
            GLib.idle_add(fn.show_in_app_notification, self, "gnome-software installation started")

            def wait_install():
                try:
                    import time
                    import pwd

                    fn.debug_print("Waiting for gnome-software installation to complete...")
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.debug_print("Installation process completed")
                    time.sleep(1)
                    if fn.path.exists("/usr/bin/gnome-software"):
                        fn.log_success("gnome-software installed successfully")
                        GLib.idle_add(
                            self.lbl_software_gnome.set_markup, "GNOME Software - GUI package manager <b>installed</b>"
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "gnome-software installed")
                        time.sleep(1)
                        fn.log_subsection("Launching gnome-software...")
                        uid = pwd.getpwnam(fn.sudo_username).pw_uid
                        fn.subprocess.Popen(
                            "sudo -E -u "
                            + fn.sudo_username
                            + " HOME=/home/"
                            + fn.sudo_username
                            + " XDG_RUNTIME_DIR=/run/user/"
                            + str(uid)
                            + " DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/"
                            + str(uid)
                            + "/bus"
                            + " gnome-software &",
                            shell=True,
                            stdout=fn.subprocess.PIPE,
                            stderr=fn.subprocess.STDOUT,
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "gnome-software launched")
                    else:
                        fn.log_warn("gnome-software binary NOT found, installation may have failed")
                        fn.check_missing_repo_error(self, "", "gnome-software")
                except Exception as e:
                    fn.log_error(f"Error during installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with gnome-software: {error}")


def on_click_software_discover(self, _widget):
    """Install KDE Discover and launch it, or launch if already installed."""
    try:
        if not fn.path.exists("/usr/bin/plasma-discover"):
            fn.log_subsection("Installing discover...")
            process = fn.launch_pacman_install_in_terminal("discover packagekit-qt6")
            GLib.idle_add(fn.show_in_app_notification, self, "discover installation started")

            def wait_install():
                try:
                    import time
                    import pwd

                    fn.debug_print("Waiting for discover installation to complete...")
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.debug_print("Installation process completed")
                    time.sleep(1)
                    if fn.path.exists("/usr/bin/plasma-discover"):
                        fn.log_success("discover installed successfully")
                        GLib.idle_add(
                            self.lbl_software_discover.set_markup,
                            "KDE Discover - KDE software center (pulls KDE deps) <b>installed</b>",
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "plasma-discover installed")
                        fn.log_subsection("Launching plasma-discover...")
                        uid = pwd.getpwnam(fn.sudo_username).pw_uid
                        fn.subprocess.Popen(
                            "DISPLAY=:0 sudo -E -u "
                            + fn.sudo_username
                            + " HOME=/home/"
                            + fn.sudo_username
                            + " XDG_RUNTIME_DIR=/run/user/"
                            + str(uid)
                            + " DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/"
                            + str(uid)
                            + "/bus"
                            + " plasma-discover",
                            shell=True,
                            stdout=fn.subprocess.DEVNULL,
                            stderr=fn.subprocess.DEVNULL,
                        )
                    else:
                        fn.log_warn("discover binary NOT found, installation may have failed")
                except Exception as e:
                    fn.log_error(f"Error during installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
        else:
            fn.log_subsection("Launching plasma-discover...")
            import pwd

            uid = pwd.getpwnam(fn.sudo_username).pw_uid
            fn.subprocess.Popen(
                "DISPLAY=:0 sudo -E -u "
                + fn.sudo_username
                + " HOME=/home/"
                + fn.sudo_username
                + " XDG_RUNTIME_DIR=/run/user/"
                + str(uid)
                + " DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/"
                + str(uid)
                + "/bus"
                + " plasma-discover",
                shell=True,
                stdout=fn.subprocess.DEVNULL,
                stderr=fn.subprocess.DEVNULL,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "KDE Discover launched")
    except Exception as error:
        fn.log_error(f"Error with discover: {error}")


def on_click_software_pachub(self, _widget):
    """Launch PacHub or install it from AUR if not present."""
    try:
        if fn.path.exists("/usr/bin/pachub"):
            fn.log_subsection("Launching PacHub...")
            fn.subprocess.Popen(
                "sudo -E -u " + fn.sudo_username + " pachub &",
                shell=True,
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "PacHub launched")
            return
        aur_helper = fn.get_aur_helper()
        if aur_helper is None:
            fn.log_warn("No AUR helper found — install yay, paru, trizen or pikaur first")
            GLib.idle_add(
                fn.show_in_app_notification,
                self,
                "No AUR helper found — install yay, paru, trizen or pikaur first",
            )
            return
        fn.log_subsection("Installing pachub from AUR...")
        process = fn.launch_aur_install_in_terminal(aur_helper, "pachub")
        GLib.idle_add(fn.show_in_app_notification, self, "pachub installation started")
        fn.wait_install_and_update(
            process,
            "/usr/bin/pachub",
            self.lbl_software_pachub,
            "PacHub - Pacman/AUR GUI (GTK4) <b>installed</b>",
            self,
            "pachub installation complete",
            "pachub",
        )
    except Exception as error:
        fn.log_error(f"Error with PacHub: {error}")


def on_click_software_yay(self, _widget):
    """Install yay-git from chaotic-AUR or build from AUR if unavailable."""
    try:
        if fn.path.exists("/usr/bin/yay"):
            fn.log_subsection("yay-git already installed")
            GLib.idle_add(fn.show_in_app_notification, self, "yay-git already installed")
            return
        fn.log_subsection("Installing yay-git...")
        if not fn.check_chaotic_aur_active():
            fn.log_info("chaotic-AUR not active — asking user to build from AUR")
            if fn.show_confirm_dialog(
                self,
                "chaotic-AUR is not enabled",
                "Build <b>yay-git</b> from AUR instead?\n(git clone + makepkg — takes a few minutes)",
            ):
                process = pacman_functions.install_yay_git(self)
            else:
                fn.log_info("User declined AUR build for yay-git")
                return
        else:
            process = fn.launch_pacman_install_in_terminal("yay-git")
            GLib.idle_add(fn.show_in_app_notification, self, "yay-git installation started")
        fn.wait_install_and_update(
            process,
            "/usr/bin/yay",
            self.lbl_software_yay,
            "Yay-git - AUR helper (Go-based) <b>installed</b>",
            self,
            "yay-git installed",
            "yay-git",
        )
    except Exception as error:
        fn.log_error(f"Error with yay-git: {error}")


def on_click_software_paru(self, _widget):
    """Install paru-git from chaotic-AUR or build from AUR if unavailable."""
    try:
        if fn.path.exists("/usr/bin/paru"):
            fn.log_subsection("paru-git already installed")
            GLib.idle_add(fn.show_in_app_notification, self, "paru-git already installed")
            return
        fn.log_subsection("Installing paru-git...")
        if not fn.check_chaotic_aur_active():
            fn.log_info("chaotic-AUR not active — asking user to build from AUR")
            if fn.show_confirm_dialog(
                self,
                "chaotic-AUR is not enabled",
                "Build <b>paru-git</b> from AUR instead?\n(git clone + makepkg — takes a few minutes)",
            ):
                process = pacman_functions.install_paru_git(self)
            else:
                fn.log_info("User declined AUR build for paru-git")
                return
        else:
            process = fn.launch_pacman_install_in_terminal("paru-git")
            GLib.idle_add(fn.show_in_app_notification, self, "paru-git installation started")
        fn.wait_install_and_update(
            process,
            "/usr/bin/paru",
            self.lbl_software_paru,
            "Paru-git - AUR helper (Rust-based) <b>installed</b>",
            self,
            "paru-git installed",
            "paru-git",
        )
    except Exception as error:
        fn.log_error(f"Error with paru-git: {error}")


def on_click_software_trizen(self, _widget):
    """Install the trizen AUR helper."""
    try:
        if fn.path.exists("/usr/bin/trizen"):
            fn.log_subsection("trizen already installed")
            GLib.idle_add(fn.show_in_app_notification, self, "trizen already installed")
            return
        fn.log_subsection("Installing trizen...")
        process = fn.launch_pacman_install_in_terminal("trizen")
        GLib.idle_add(fn.show_in_app_notification, self, "trizen installation started")
        fn.wait_install_and_update(
            process,
            "/usr/bin/trizen",
            self.lbl_software_trizen,
            "Trizen - AUR helper (Perl-based) <b>installed</b>",
            self,
            "trizen installed",
            "trizen",
        )
    except Exception as error:
        fn.log_error(f"Error with trizen: {error}")


def on_click_software_pikaur(self, _widget):
    """Install the pikaur-git AUR helper."""
    try:
        if fn.path.exists("/usr/bin/pikaur"):
            fn.log_subsection("pikaur-git already installed")
            GLib.idle_add(fn.show_in_app_notification, self, "pikaur-git already installed")
            return
        fn.log_subsection("Installing pikaur-git...")
        process = fn.launch_pacman_install_in_terminal("pikaur-git")
        GLib.idle_add(fn.show_in_app_notification, self, "pikaur-git installation started")
        fn.wait_install_and_update(
            process,
            "/usr/bin/pikaur",
            self.lbl_software_pikaur,
            "Pikaur-git - AUR helper (Python-based) <b>installed</b>",
            self,
            "pikaur-git installed",
            "pikaur-git",
        )
    except Exception as error:
        fn.log_error(f"Error with pikaur-git: {error}")


def on_click_software_yay_remove(self, _widget):
    """Remove the yay-git AUR helper."""
    try:
        fn.log_subsection("Removing yay-git...")
        process = fn.launch_pacman_remove_recursive_in_terminal("yay-git", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "yay-git removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/yay",
            self.lbl_software_yay,
            "Yay-git - AUR helper (Go-based)",
            self,
            "yay-git removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with yay-git removal: {error}")


def on_click_software_paru_remove(self, _widget):
    """Remove the paru-git AUR helper."""
    try:
        fn.log_subsection("Removing paru-git...")
        process = fn.launch_pacman_remove_recursive_in_terminal("paru-git", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "paru-git removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/paru",
            self.lbl_software_paru,
            "Paru-git - AUR helper (Rust-based)",
            self,
            "paru-git removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with paru-git removal: {error}")


def on_click_software_trizen_remove(self, _widget):
    """Remove the trizen AUR helper."""
    try:
        fn.log_subsection("Removing trizen...")
        process = fn.launch_pacman_remove_recursive_in_terminal("trizen", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "trizen removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/trizen",
            self.lbl_software_trizen,
            "Trizen - AUR helper (Perl-based)",
            self,
            "trizen removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with trizen removal: {error}")


def on_click_software_pikaur_remove(self, _widget):
    """Remove the pikaur-git AUR helper."""
    try:
        fn.log_subsection("Removing pikaur-git...")
        process = fn.launch_pacman_remove_recursive_in_terminal("pikaur-git", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "pikaur-git removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/pikaur",
            self.lbl_software_pikaur,
            "Pikaur-git - AUR helper (Python-based)",
            self,
            "pikaur-git removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with pikaur-git removal: {error}")


def on_click_software_pacui_open(self, _widget):
    """Launch pacui TUI or install it from chaotic-AUR if not present."""
    try:
        if fn.path.exists("/usr/bin/pacui"):
            fn.log_subsection("Launching pacui...")
            fn.subprocess.Popen(
                "sudo -E -u " + fn.sudo_username + " alacritty -e pacui &",
                shell=True,
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "pacui launched")
            return
        fn.log_subsection("Installing pacui...")
        if not fn.check_chaotic_aur_active():
            fn.log_info("chaotic-AUR not active — pacui is available on chaotic-AUR")
            GLib.idle_add(fn.show_in_app_notification, self, "Enable chaotic-AUR in the Pacman tab first")
            return
        fn.log_info("pacui is available on the chaotic-AUR repository")
        GLib.idle_add(fn.show_in_app_notification, self, "pacui is on chaotic-AUR — installing...")
        process = fn.launch_pacman_install_in_terminal("pacui")
        fn.wait_install_and_update(
            process,
            "/usr/bin/pacui",
            self.lbl_software_pacui,
            "Pacui - TUI pacman wrapper <b>installed</b>",
            self,
            "pacui installed",
            "pacui",
        )
    except Exception as error:
        fn.log_error(f"Error with pacui: {error}")


def on_click_software_pacui_remove(self, _widget):
    """Remove the pacui TUI package manager."""
    try:
        fn.log_subsection("Removing pacui...")
        process = fn.launch_pacman_remove_recursive_in_terminal("pacui", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "pacui removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/pacui",
            self.lbl_software_pacui,
            "Pacui - TUI pacman wrapper",
            self,
            "pacui removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with pacui removal: {error}")


def on_click_software_flatpak(self, _widget):
    """Install flatpak and show installed apps, or open terminal list if already installed."""
    try:
        if not fn.path.exists("/usr/bin/flatpak"):
            fn.log_subsection("Installing flatpak...")
            script = (
                "pacman -S --noconfirm flatpak; echo ''; "
                "echo '=== Installation complete ===' && "
                "echo 'You can close this window' && "
                "read -p 'Press Enter to close...'"
            )
            fn.debug_print(f"Terminal cmd: {script}")
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "flatpak installation started")

            def wait_install():
                try:
                    import time

                    fn.debug_print("Waiting for flatpak installation to complete...")
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.debug_print("Installation process completed")
                    time.sleep(1)
                    if fn.path.exists("/usr/bin/flatpak"):
                        fn.log_success("flatpak installed successfully")
                        GLib.idle_add(
                            self.lbl_software_flatpak.set_markup, "Flatpak - Manage Flatpak apps <b>installed</b>"
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "flatpak installed")
                        time.sleep(1)
                        fn.log_subsection("Launching flatpak...")
                        flatpak_script = (
                            "echo '=== Installed Flatpak apps ===' && "
                            "sudo -u " + fn.sudo_username + " flatpak list && "
                            "echo '' && "
                            "echo 'To install an app: flatpak install flathub <app-id>'"
                        )
                        fn.debug_print(f"Terminal cmd: {flatpak_script}")
                        fn.subprocess.Popen(
                            ["alacritty", "--hold", "-e", "bash", "-c", flatpak_script],
                            stdout=fn.subprocess.PIPE,
                            stderr=fn.subprocess.STDOUT,
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "flatpak launched")
                    else:
                        fn.log_warn("flatpak binary NOT found, installation may have failed")
                except Exception as e:
                    fn.log_error(f"Error during flatpak installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
        else:
            fn.log_subsection("Launching flatpak...")
            script = (
                "echo '=== Installed Flatpak apps ===' && "
                "sudo -u " + fn.sudo_username + " flatpak list && "
                "echo '' && "
                "echo 'To install an app: flatpak install flathub <app-id>'"
            )
            fn.debug_print(f"Terminal cmd: {script}")
            fn.subprocess.Popen(
                ["alacritty", "--hold", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "flatpak launched")
    except Exception as error:
        fn.log_error(f"Error with flatpak: {error}")


def on_click_software_flatpak_remove(self, _widget):
    """Remove the flatpak package."""
    try:
        fn.log_subsection("Removing flatpak...")
        process = fn.launch_pacman_remove_recursive_in_terminal("flatpak", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "flatpak removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/flatpak",
            self.lbl_software_flatpak,
            "Flatpak - Manage Flatpak apps",
            self,
            "flatpak removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with flatpak removal: {error}")


def on_click_software_snapd(self, _widget):
    """Install snapd via AUR helper or show installed snaps if already present."""
    try:
        if not fn.path.exists("/usr/bin/snap"):
            aur_helper = fn.get_aur_helper()
            if aur_helper is None:
                fn.log_warn("No AUR helper found — install yay, paru, trizen or pikaur first")
                GLib.idle_add(
                    fn.show_in_app_notification, self, "No AUR helper found - install yay, paru, trizen or pikaur first"
                )
                return
            fn.log_subsection("Installing snapd...")
            username = fn.sudo_username
            script = (
                "echo '=== Installing build dependencies ===' && "
                "sudo pacman -S --noconfirm --needed base-devel && "
                "echo '' && "
                f"echo '=== Building and installing snapd from AUR ===' && "
                f"sudo -H -u {username} {aur_helper} -S --noconfirm snapd; "
                "echo ''; echo '=== Done ==='; read -p 'Press Enter to close...'"
            )
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "snapd installation started")

            def wait_install():
                try:
                    import time

                    fn.debug_print("Waiting for snapd installation to complete...")
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.debug_print("Installation process completed")
                    time.sleep(1)
                    if fn.path.exists("/usr/bin/snap"):
                        fn.log_success("snapd installed successfully")
                        GLib.idle_add(self.lbl_software_snapd.set_markup, "Snapd - Manage Snap apps <b>installed</b>")
                        GLib.idle_add(fn.show_in_app_notification, self, "snapd installed")
                    else:
                        fn.log_warn("snapd binary NOT found, installation may have failed")
                except Exception as e:
                    fn.log_error(f"Error during snapd installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
        else:
            fn.log_subsection("Launching snapd...")
            script = (
                "echo '=== Installed Snap apps ===' && "
                "sudo -u " + fn.sudo_username + " snap list && "
                "echo '' && "
                "echo 'To install an app: snap install <app-name>'"
            )
            fn.debug_print(f"Terminal cmd: {script}")
            fn.subprocess.Popen(
                ["alacritty", "--hold", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "snapd launched")
    except Exception as error:
        fn.log_error(f"Error with snapd: {error}")


def on_click_software_snapd_remove(self, _widget):
    """Remove the snapd package."""
    try:
        fn.log_subsection("Removing snapd...")
        process = fn.launch_pacman_remove_recursive_in_terminal("snapd", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "snapd removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/snap",
            self.lbl_software_snapd,
            "Snapd - Manage Snap apps",
            self,
            "snapd removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with snapd removal: {error}")


def on_click_software_appimagelauncher(self, _widget):
    """Launch app-manager or install appmanager via AUR helper if not present."""
    try:
        if not fn.path.exists("/usr/bin/app-manager"):
            aur_helper = fn.get_aur_helper()
            if aur_helper is None:
                fn.log_warn("No AUR helper found — install yay, paru, trizen or pikaur first")
                GLib.idle_add(
                    fn.show_in_app_notification, self, "No AUR helper found - install yay, paru, trizen or pikaur first"
                )
                return
            fn.log_subsection("Installing appmanager...")
            process = fn.launch_aur_install_in_terminal(aur_helper, "appmanager")
            GLib.idle_add(fn.show_in_app_notification, self, "appmanager installation started")

            def wait_install():
                try:
                    import time
                    import pwd

                    fn.debug_print("Waiting for appmanager installation to complete...")
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.debug_print("Installation process completed")
                    time.sleep(1)
                    if fn.path.exists("/usr/bin/app-manager"):
                        fn.log_success("appmanager installed successfully")
                        GLib.idle_add(
                            self.lbl_software_appimagelauncher.set_markup,
                            "App-manager - Manage AppImages <b>installed</b>",
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "appmanager installed")
                        time.sleep(1)
                        fn.log_subsection("Launching app-manager...")
                        uid = pwd.getpwnam(fn.sudo_username).pw_uid
                        fn.subprocess.Popen(
                            "sudo -E -u "
                            + fn.sudo_username
                            + " HOME=/home/"
                            + fn.sudo_username
                            + " XDG_RUNTIME_DIR=/run/user/"
                            + str(uid)
                            + " DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/"
                            + str(uid)
                            + "/bus"
                            + " app-manager &",
                            shell=True,
                            stdout=fn.subprocess.PIPE,
                            stderr=fn.subprocess.STDOUT,
                        )
                        GLib.idle_add(fn.show_in_app_notification, self, "app-manager launched")
                    else:
                        fn.log_warn("appmanager binary NOT found, installation may have failed")
                except Exception as e:
                    fn.log_error(f"Error during installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            return
        fn.log_subsection("Launching app-manager...")
        import pwd

        uid = pwd.getpwnam(fn.sudo_username).pw_uid
        fn.subprocess.Popen(
            "sudo -E -u "
            + fn.sudo_username
            + " HOME=/home/"
            + fn.sudo_username
            + " XDG_RUNTIME_DIR=/run/user/"
            + str(uid)
            + " DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/"
            + str(uid)
            + "/bus"
            + " app-manager &",
            shell=True,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "App-manager launched")
    except Exception as error:
        fn.log_error(f"Error with app-manager: {error}")


def on_click_software_appimagelauncher_remove(self, _widget):
    """Remove the appmanager package."""
    try:
        fn.log_subsection("Removing appmanager...")
        process = fn.launch_pacman_remove_recursive_in_terminal("appmanager", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "appmanager removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/app-manager",
            self.lbl_software_appimagelauncher,
            "App-manager - Manage AppImages",
            self,
            "appmanager removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with appmanager removal: {error}")


def on_click_software_pacseek(self, _widget):
    """Launch pacseek TUI or install it from chaotic-AUR if not present."""
    try:
        if fn.path.exists("/usr/bin/pacseek"):
            fn.log_subsection("Launching pacseek...")
            fn.subprocess.Popen(
                ["alacritty", "-e", "sudo", "-u", fn.sudo_username, "pacseek"],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            GLib.idle_add(fn.show_in_app_notification, self, "pacseek launched")
            return
        fn.log_subsection("Installing pacseek...")
        if not fn.check_chaotic_aur_active():
            fn.log_info("chaotic-AUR not active — pacseek is available on chaotic-AUR")
            GLib.idle_add(fn.show_in_app_notification, self, "Enable chaotic-AUR in the Pacman tab first")
            return
        fn.log_info("pacseek is available on the chaotic-AUR repository")
        GLib.idle_add(fn.show_in_app_notification, self, "pacseek is on chaotic-AUR — installing...")
        process = fn.launch_pacman_install_in_terminal("pacseek")
        fn.wait_install_and_update(
            process,
            "/usr/bin/pacseek",
            self.lbl_software_pacseek,
            "Pacseek - TUI package searcher <b>installed</b>",
            self,
            "pacseek installed",
            "pacseek",
        )
    except Exception as error:
        fn.log_error(f"Error with pacseek: {error}")


def on_click_software_pacseek_remove(self, _widget):
    """Remove the pacseek TUI package searcher."""
    try:
        fn.log_subsection("Removing pacseek...")
        process = fn.launch_pacman_remove_recursive_in_terminal("pacseek", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "pacseek removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/pacseek",
            self.lbl_software_pacseek,
            "Pacseek - TUI package searcher",
            self,
            "pacseek removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with pacseek removal: {error}")


def on_click_software_pamac_remove(self, _widget):
    """Remove the pamac-aur GUI package manager."""
    try:
        fn.log_subsection("Removing pamac-aur...")
        process = fn.launch_pacman_remove_recursive_in_terminal("pamac-aur", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "pamac-aur removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/pamac-manager",
            self.lbl_software_pamac,
            "Pamac - GUI package manager",
            self,
            "pamac-aur removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with pamac removal: {error}")


def on_click_software_octopi_remove(self, _widget):
    """Remove the octopi Qt GUI package manager."""
    try:
        fn.log_subsection("Removing octopi...")
        process = fn.launch_pacman_remove_recursive_in_terminal("octopi", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "octopi removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/octopi",
            self.lbl_software_octopi,
            "Octopi - GUI package manager",
            self,
            "octopi removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with octopi removal: {error}")


def on_click_software_bazaar_remove(self, _widget):
    """Remove the bazaar package manager."""
    try:
        fn.log_subsection("Removing bazaar...")
        process = fn.launch_pacman_remove_recursive_in_terminal("bazaar", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "bazaar removal started")
        fn.wait_remove_and_update(
            process, "/usr/bin/bazaar", self.lbl_software_bazaar, "Bazaar", self, "bazaar removal complete"
        )
    except Exception as error:
        fn.log_error(f"Error with bazaar removal: {error}")


def on_click_software_shelly_remove(self, _widget):
    """Remove the shelly package manager."""
    try:
        fn.log_subsection("Removing shelly...")
        process = fn.launch_pacman_remove_recursive_in_terminal("shelly", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "shelly removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/shelly-ui",
            self.lbl_software_shelly,
            "Shelly - Modern package manager",
            self,
            "shelly removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with shelly removal: {error}")


def on_click_software_gnome_remove(self, _widget):
    """Remove the gnome-software GTK software center."""
    try:
        fn.log_subsection("Removing gnome-software...")
        process = fn.launch_pacman_remove_recursive_in_terminal("gnome-software", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "gnome-software removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/gnome-software",
            self.lbl_software_gnome,
            "GNOME Software - GUI package manager",
            self,
            "gnome-software removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with gnome-software removal: {error}")


def on_click_software_discover_remove(self, _widget):
    """Remove the KDE Discover software center."""
    try:
        fn.log_subsection("Removing discover...")
        process = fn.launch_pacman_remove_recursive_in_terminal("discover", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "plasma-discover removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/plasma-discover",
            self.lbl_software_discover,
            "KDE Discover - GUI package manager",
            self,
            "plasma-discover removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with discover removal: {error}")


def on_click_software_pachub_remove(self, _widget):
    """Remove the PacHub package."""
    try:
        fn.log_subsection("Removing pachub...")
        process = fn.launch_pacman_remove_recursive_in_terminal("pachub", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "pachub removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/pachub",
            self.lbl_software_pachub,
            "PacHub - Pacman/AUR GUI (GTK4)",
            self,
            "pachub removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with pachub removal: {error}")


def on_click_software_archlinux_logout(self, _widget):
    """Install archlinux-logout from the nemesis/chaotic-AUR repository."""
    try:
        fn.log_subsection("Installing archlinux-logout...")
        if not fn.check_chaotic_aur_active():
            fn.log_info("chaotic-AUR not active — archlinux-logout needs Chaotic-AUR and nemesis repo")
            GLib.idle_add(fn.show_in_app_notification, self, "Enable nemesis/chaotic-AUR in the Pacman tab first")
            return
        fn.log_info("archlinux-logout is available on the nemesis/chaotic-AUR repository")
        GLib.idle_add(fn.show_in_app_notification, self, "archlinux-logout is on nemesis/chaotic-AUR — installing...")
        process = fn.launch_pacman_install_in_terminal("archlinux-logout")
        fn.wait_install_and_update(
            process,
            "/usr/bin/archlinux-logout",
            self.lbl_software_archlinux_logout,
            "ArchLinux Logout - Session logout tool <b>installed</b>",
            self,
            "archlinux-logout installed",
            "archlinux-logout",
        )
    except Exception as error:
        fn.log_error(f"Error with archlinux-logout: {error}")


def on_click_software_archlinux_logout_remove(self, _widget):
    """Remove the archlinux-logout package."""
    try:
        fn.log_subsection("Removing archlinux-logout...")
        process = fn.launch_pacman_remove_recursive_in_terminal("archlinux-logout", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "archlinux-logout removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/bin/archlinux-logout",
            self.lbl_software_archlinux_logout,
            "ArchLinux Logout - Session logout tool",
            self,
            "archlinux-logout removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with archlinux-logout removal: {error}")


def on_click_software_powermenu(self, _widget):
    """Install kiro-powermenu and copy the skel config if missing."""
    try:
        if fn.path.exists("/usr/local/bin/edu-powermenu"):
            fn.log_info("edu-powermenu is already installed")
            fn.show_in_app_notification(self, "edu-powermenu is already installed")
            return
        fn.log_subsection("Installing kiro-powermenu...")
        process = fn.launch_pacman_install_in_terminal("kiro-powermenu")
        GLib.idle_add(fn.show_in_app_notification, self, "kiro-powermenu installation started")

        def wait_install():
            try:
                import time

                fn.debug_print("Waiting for kiro-powermenu installation to complete...")
                process.wait()
                fn.invalidate_pkg_cache()
                fn.debug_print("Installation process completed")
                time.sleep(1)
                if fn.path.exists("/usr/local/bin/edu-powermenu"):
                    fn.log_success("kiro-powermenu installed successfully")
                    skel_src = "/etc/skel/.config/powermenu"
                    user_dst = fn.path.join(fn.home, ".config", "powermenu")
                    if fn.path.exists(skel_src) and not fn.path.exists(user_dst):
                        fn.log_info(f"Copying powermenu config to {user_dst}")
                        fn.shutil.copytree(skel_src, user_dst)
                        fn.permissions(user_dst)
                        fn.log_success("powermenu config installed with user permissions")
                    GLib.idle_add(
                        self.lbl_software_powermenu.set_markup, "powermenu - Power menu for twms <b>installed</b>"
                    )
                    GLib.idle_add(fn.show_in_app_notification, self, "kiro-powermenu installed")
                else:
                    fn.log_warn("edu-powermenu binary NOT found, installation may have failed")
                    fn.check_missing_repo_error(self, "", "kiro-powermenu")
            except Exception as e:
                fn.log_error(f"Error during installation: {e}")

        fn.threading.Thread(target=wait_install, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Error with edu-powermenu: {error}")


def on_click_software_powermenu_remove(self, _widget):
    """Remove the kiro-powermenu package."""
    try:
        fn.log_subsection("Removing kiro-powermenu...")
        process = fn.launch_pacman_remove_recursive_in_terminal("kiro-powermenu", keep_config=True)
        GLib.idle_add(fn.show_in_app_notification, self, "kiro-powermenu removal started")
        fn.wait_remove_and_update(
            process,
            "/usr/local/bin/edu-powermenu",
            self.lbl_software_powermenu,
            "powermenu - Power menu for twms",
            self,
            "kiro-powermenu removal complete",
        )
    except Exception as error:
        fn.log_error(f"Error with edu-powermenu removal: {error}")


def on_click_apply_att_nanorc(self, _widget):
    """Backup /etc/nanorc and apply the ATT nanorc config."""
    fn.log_subsection("Apply ATT nanorc")
    fb.backup_nanorc()
    try:
        fn.shutil.copy(fn.nanorc_att, fn.nanorc)
        fn.log_success("ATT nanorc applied to /etc/nanorc")
        fn.show_in_app_notification(self, "ATT nanorc applied to /etc/nanorc")
        self.lbl_software_nano.set_markup("Apply ATT nanorc to /etc/nanorc (backup created first) <b>applied</b>")
        self.btn_software_nano_restore.set_sensitive(True)
    except Exception as error:
        fn.log_error(f"Failed to apply ATT nanorc: {error}")
        fn.show_in_app_notification(self, "Failed to apply ATT nanorc")


def on_click_restore_nanorc(self, _widget):
    """Restore /etc/nanorc from the ATT backup."""
    fn.log_subsection("Restore nanorc backup")
    fb.restore_nanorc(self)
    self.lbl_software_nano.set_markup("Apply ATT nanorc to /etc/nanorc (backup created first)")


def on_click_launch_alacritty_tweak_tool(self, _widget):
    """Launch Alacritty Tweak Tool as real user."""
    if fn.path.exists("/usr/bin/alacritty-tweak-tool"):
        fn.log_subsection("Launching Alacritty Tweak Tool...")
        fn.subprocess.Popen(
            "sudo -E -u " + fn.sudo_username + " env HOME=" + fn.home + " alacritty-tweak-tool &",
            shell=True,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Alacritty Tweak Tool launched")
    else:
        fn.log_info("alacritty-tweak-tool not installed")
        GLib.idle_add(fn.show_in_app_notification, self, "alacritty-tweak-tool not found")

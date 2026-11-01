# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
import zsh_theme
from gi.repository import GLib
from att_i18n import _


def tobash_apply(self, _widget):
    """Switch the default shell to bash."""
    fn.log_subsection("Apply Bash")
    fn.debug_print(f"  Current shell : {fn.get_shell()}")
    fn.debug_print("  Target shell  : bash")
    fn.change_shell(self, "bash")


def _refresh_bash_completion_label(self):
    if fn.check_package_installed("bash-completion"):
        fn.GLib.idle_add(self.bash_completion_lbl.set_markup, _("Bash and bash-completion are already <b>installed</b>"))
    else:
        fn.GLib.idle_add(
            self.bash_completion_lbl.set_markup, _("Bash is already installed and bash-completion is not installed")
        )


def on_install_bash_completion_clicked(self, _widget):
    """Install bash and bash-completion packages."""
    fn.log_subsection("Installing bash and bash-completion...")
    process = fn.launch_pacman_install_in_terminal("bash bash-completion")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Installation started"))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Installation completed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("bash and bash-completion installed"))
            _refresh_bash_completion_label(self)
        except Exception as e:
            fn.log_error(f"Error: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_bash_completion_clicked(self, _widget):
    """Remove the bash-completion package."""
    fn.log_subsection("Removing bash-completion...")
    process = fn.launch_pacman_remove_in_terminal("bash-completion")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Removal started"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("bash-completion removed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("bash-completion removed"))
            _refresh_bash_completion_label(self)
        except Exception as e:
            fn.log_error(f"Error: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def on_install_att_bashrc_clicked(self, _widget):
    """Copy the ATT bashrc to ~/.bashrc."""
    fn.log_subsection("Apply ATT Bash Configuration")
    fn.debug_print(f"  Source : {fn.bashrc_kiro}")
    fn.debug_print(f"  Target : {fn.bash_config}")
    fn.debug_print(f"  Exists : {fn.path.isfile(fn.bashrc_kiro)}")
    try:
        if fn.path.isfile(fn.bashrc_kiro):
            fn.log_info_concise(f"  From: {fn.bashrc_kiro}")
            fn.log_info_concise(f"  To:   {fn.bash_config}")
            fn.shutil.copy(fn.bashrc_kiro, fn.bash_config)
            fn.debug_print("  Result : copied successfully")
            fn.permissions(fn.home + "/.bashrc")
            fn.debug_print(f"  Perms  : permissions set on {fn.bash_config}")
            fn.log_success("ATT bash configuration applied — log out and back in to apply")
            GLib.idle_add(fn.show_in_app_notification, self, _("ATT ~/.bashrc applied — log out and back in to apply"))
        else:
            fn.debug_print("  Result : source file not found - nothing copied")
            fn.log_warn("ATT bashrc not found - add .bashrc to data/")
    except Exception as error:
        fn.debug_print(f"  Result : FAILED - {error}")
        fn.log_error(f"Failed to apply ATT bash configuration: {error}")
        fn.messagebox(self, _("Error"), _("Failed to apply bash configuration: {error}").format(error=error))


def on_bash_reset_clicked(self, _widget):
    """Restore the original ~/.bashrc from the ATT backup."""
    fn.log_subsection("Restore Original Bash Configuration")
    backup = fn.bash_config + "-bak"
    fn.debug_print(f"  Source : {backup}")
    fn.debug_print(f"  Target : {fn.bash_config}")
    fn.debug_print(f"  Exists : {fn.path.isfile(backup)}")
    try:
        if fn.path.isfile(backup):
            fn.log_info_concise(f"  From: {backup}")
            fn.log_info_concise(f"  To:   {fn.bash_config}")
            fn.shutil.copy(backup, fn.bash_config)
            fn.debug_print("  Result : copied successfully")
            fn.permissions(fn.home + "/.bashrc")
            fn.debug_print(f"  Perms  : permissions set on {fn.bash_config}")
        else:
            fn.debug_print("  Result : no backup found - nothing restored")
        fn.log_success("Original bash configuration restored — log out and back in to apply")
        GLib.idle_add(fn.show_in_app_notification, self, _("~/.bashrc restored — log out and back in to apply"))
    except Exception as error:
        fn.debug_print(f"  Result : FAILED - {error}")
        fn.log_error(f"Failed to restore bash configuration: {error}")
        fn.messagebox(
            self, _("Error"), _("Failed to restore bash configuration: {error}").format(error=error)
        )


def _install_kiro_fish_payload():
    """Write the kiro-config.fish loader + parts to /usr/share/kiro/fish when the package is absent.

    The stub config.fish sources /usr/share/kiro/fish/kiro-config.fish. On Kiro that path is
    owned by the kiro-fish-config package, so we leave it to pacman; on other Arch distros ATT
    ships the payload itself so the stub's source line resolves.
    """
    if fn.check_package_installed("kiro-fish-config"):
        fn.log_info_concise("  kiro-fish-config installed — leaving /usr/share/kiro/fish to the package")
        return
    if not fn.path.isdir(fn.kiro_fish_payload_src):
        fn.log_warn("Kiro fish payload not found in ATT data — skipping /usr/share/kiro/fish")
        return
    fn.log_info_concise(f"  From: {fn.kiro_fish_payload_src}")
    fn.log_info_concise(f"  To:   {fn.kiro_fish_payload_dst}")
    fn.shutil.copytree(fn.kiro_fish_payload_src, fn.kiro_fish_payload_dst, dirs_exist_ok=True)
    fn.log_success("Kiro fish payload written to /usr/share/kiro/fish")


def on_install_att_fish_config_clicked(self, _widget):
    """Copy the ATT config.fish stub to ~/.config/fish and write the Kiro payload if needed."""
    fn.log_subsection("Apply ATT Fish Configuration")
    fn.debug_print(f"  Source : {fn.fish_config_kiro}")
    fn.debug_print(f"  Target : {fn.fish_config}")
    fn.debug_print(f"  Exists : {fn.path.isfile(fn.fish_config_kiro)}")
    try:
        if fn.path.isfile(fn.fish_config_kiro):
            fn.os.makedirs(fn.os.path.dirname(fn.fish_config), exist_ok=True)
            if fn.path.isfile(fn.fish_config):
                fn.log_info_concise(f"  From: {fn.fish_config}")
                fn.log_info_concise(f"  To:   {fn.fish_config}-bak")
                fn.shutil.copy(fn.fish_config, fn.fish_config + "-bak")
            fn.log_info_concise(f"  From: {fn.fish_config_kiro}")
            fn.log_info_concise(f"  To:   {fn.fish_config}")
            fn.shutil.copy(fn.fish_config_kiro, fn.fish_config)
            fn.debug_print("  Result : copied successfully")
            fn.permissions(fn.os.path.dirname(fn.fish_config))
            fn.debug_print(f"  Perms  : permissions set on {fn.os.path.dirname(fn.fish_config)}")
            _install_kiro_fish_payload()
            fn.log_success("ATT fish configuration applied — log out and back in to apply")
            fn.GLib.idle_add(
                fn.show_in_app_notification, self, _("ATT config.fish applied — log out and back in to apply")
            )
        else:
            fn.debug_print("  Result : source file not found - nothing copied")
            fn.log_warn("ATT config.fish source not found")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("ATT config.fish source not found"))
    except Exception as error:
        fn.debug_print(f"  Result : FAILED - {error}")
        fn.log_error(f"Failed to apply ATT fish configuration: {error}")
        fn.messagebox(
            self, _("Error"), _("Failed to apply fish configuration: {error}").format(error=error)
        )


def on_fish_reset_clicked(self, _widget):
    """Restore the original config.fish from the ATT backup."""
    fn.log_subsection("Restore Original Fish Configuration")
    backup = fn.fish_config + "-bak"
    fn.debug_print(f"  Source : {backup}")
    fn.debug_print(f"  Target : {fn.fish_config}")
    fn.debug_print(f"  Exists : {fn.path.isfile(backup)}")
    try:
        if fn.path.isfile(backup):
            fn.log_info_concise(f"  From: {backup}")
            fn.log_info_concise(f"  To:   {fn.fish_config}")
            fn.shutil.copy(backup, fn.fish_config)
            fn.debug_print("  Result : copied successfully")
            fn.permissions(fn.fish_config)
            fn.debug_print(f"  Perms  : permissions set on {fn.fish_config}")
        else:
            fn.debug_print("  Result : no backup found - nothing restored")
        fn.log_success("Original fish configuration restored — log out and back in to apply")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("config.fish restored — log out and back in to apply"))
    except Exception as error:
        fn.debug_print(f"  Result : FAILED - {error}")
        fn.log_error(f"Failed to restore fish configuration: {error}")
        fn.messagebox(
            self, _("Error"), _("Failed to restore fish configuration: {error}").format(error=error)
        )


def on_install_only_fish_clicked(self, _widget):
    """Install the fish shell package."""
    fn.log_subsection("Install Fish")
    fn.debug_print("  Package  : fish")
    fn.debug_print(f"  Installed: {fn.check_package_installed('fish')}")
    if fn.check_package_installed("fish"):
        fn.log_info("Fish is already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("Fish is already installed"))
        return
    process = fn.launch_pacman_install_in_terminal("fish")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Installing fish..."))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Fish installed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("Fish installed — page updated"))
            fn.GLib.idle_add(self.fish_status_lbl.set_markup, _("Fish is <b>installed</b>"))
            fn.GLib.idle_add(self.fish_config_section.set_sensitive, True)
        except Exception as error:
            fn.log_error(f"Error installing fish: {error}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_fish_all(self, _widget):
    """Remove the fish shell package."""
    fn.log_subsection("Remove All Fish Packages")
    fn.debug_print("  Package  : fish")
    fn.debug_print(f"  Installed: {fn.check_package_installed('fish')}")
    if not fn.check_package_installed("fish"):
        fn.log_info("fish is not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("Fish is not installed"))
        return
    process = fn.launch_pacman_remove_in_terminal("fish")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Removing fish - terminal opened"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Fish removed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("Fish removed"))
        except Exception as error:
            fn.log_error(f"Failed to remove fish: {error}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def on_remove_only_fish_clicked(self, _widget):
    """Remove the fish shell package and disable the config section."""
    fn.log_subsection("Remove Fish")
    fn.debug_print("  Package  : fish")
    fn.debug_print(f"  Installed: {fn.check_package_installed('fish')}")
    if not fn.check_package_installed("fish"):
        fn.log_info("fish is not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("Fish is not installed"))
        return
    process = fn.launch_pacman_remove_in_terminal("fish")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Removing fish - terminal opened"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Fish removed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("Fish removed"))
            fn.GLib.idle_add(self.fish_status_lbl.set_markup, _("Fish is <b>not installed</b>"))
            fn.GLib.idle_add(self.fish_config_section.set_sensitive, False)
        except Exception as error:
            fn.log_error(f"Failed to remove fish: {error}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def tofish_apply(self, _widget):
    """Switch the default shell to fish."""
    fn.log_subsection("Apply Fish")
    fn.debug_print(f"  Current shell : {fn.get_shell()}")
    fn.debug_print("  Target shell  : fish")
    fn.change_shell(self, "fish")


def tooltip_callback(self, _widget, x, _y, _keyboard_mode, tooltip, text):
    """Set tooltip text for a widget."""
    tooltip.set_text(text)
    return True


def on_install_att_zshrc_clicked(self, _widget):
    """Copy the ATT zshrc to ~/.zshrc."""
    fn.log_subsection("Apply ATT Zsh Configuration")
    fn.debug_print(f"  Source : {fn.zshrc_kiro}")
    fn.debug_print(f"  Target : {fn.zsh_config}")
    fn.debug_print(f"  Exists : {fn.path.isfile(fn.zshrc_kiro)}")
    try:
        if fn.path.isfile(fn.zshrc_kiro):
            fn.log_info_concise(f"  From: {fn.zshrc_kiro}")
            fn.log_info_concise(f"  To:   {fn.zsh_config}")
            fn.shutil.copy(fn.zshrc_kiro, fn.zsh_config)
            fn.debug_print("  Result : copied successfully")
            fn.permissions(fn.home + "/.zshrc")
            fn.debug_print(f"  Perms  : permissions set on {fn.zsh_config}")
            fn.log_success("ATT zsh configuration applied — log out and back in to apply")
            GLib.idle_add(fn.show_in_app_notification, self, _("ATT ~/.zshrc applied — log out and back in to apply"))
        else:
            fn.debug_print("  Result : source file not found - nothing copied")
    except Exception as error:
        fn.debug_print(f"  Result : FAILED - {error}")
        fn.log_error(f"Failed to apply ATT zsh configuration: {error}")
        fn.messagebox(
            self, _("Error"), _("Failed to apply zsh configuration: {error}").format(error=error)
        )


def on_zshrc_reset_clicked(self, _widget):
    """Restore the original ~/.zshrc from the ATT backup."""
    fn.log_subsection("Restore Original Zsh Configuration")
    backup = fn.zsh_config + "-bak"
    fn.debug_print(f"  Source : {backup}")
    fn.debug_print(f"  Target : {fn.zsh_config}")
    fn.debug_print(f"  Exists : {fn.path.isfile(backup)}")
    try:
        if fn.path.isfile(backup):
            fn.log_info_concise(f"  From: {backup}")
            fn.log_info_concise(f"  To:   {fn.zsh_config}")
            fn.shutil.copy(backup, fn.zsh_config)
            fn.debug_print("  Result : copied successfully")
            fn.permissions(fn.home + "/.zshrc")
            fn.debug_print(f"  Perms  : permissions set on {fn.zsh_config}")
        else:
            fn.debug_print("  Result : no backup found - nothing restored")
        fn.log_success("Original zsh configuration restored — log out and back in to apply")
        GLib.idle_add(
            fn.show_in_app_notification,
            self,
            _("~/.zshrc restored — log out and back in to apply"),
        )
    except Exception as error:
        fn.debug_print(f"  Result : FAILED - {error}")
        fn.log_error(f"Failed to restore zsh configuration: {error}")
        fn.messagebox(
            self, _("Error"), _("Failed to restore zsh configuration: {error}").format(error=error)
        )


def on_zsh_apply_theme(self, _widget):
    """Apply the selected oh-my-zsh theme to ~/.zshrc."""
    fn.log_subsection("Apply Zsh Theme")
    theme = fn.get_combo_text(self.zsh_themes)
    fn.debug_print(f"  Theme  : {theme}")
    fn.debug_print(f"  Target : {fn.zsh_config}")
    zsh_theme.set_config(self, theme)
    fn.log_success(f"Zsh theme set to {theme} - open a new terminal to activate")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Zsh theme set to {name}").format(name=theme))


def tozsh_apply(self, _widget):
    """Switch the default shell to zsh."""
    fn.log_subsection("Apply Zsh")
    fn.debug_print(f"  Current shell : {fn.get_shell()}")
    fn.debug_print("  Target shell  : zsh")
    fn.change_shell(self, "zsh")


def install_oh_my_zsh(self, _widget):
    """Install the oh-my-zsh-git package via AUR helper."""
    if fn.check_package_installed("oh-my-zsh-git"):
        fn.debug_print("oh-my-zsh-git already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("oh-my-zsh-git already installed"))
        return
    aur_helper = fn.get_aur_helper()
    if aur_helper is None:
        fn.log_error("No AUR helper found (yay/paru). Install one first.")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("No AUR helper found — install yay or paru first"))
        return
    fn.log_subsection("Installing oh-my-zsh-git...")
    fn.debug_print(f"AUR helper: {aur_helper}")
    process = fn.launch_aur_install_in_terminal(aur_helper, "oh-my-zsh-git")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("oh-my-zsh-git installation started"))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("oh-my-zsh-git installed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("oh-my-zsh-git installed"))
            fn.GLib.idle_add(_refresh_zsh_omz_lbl, self)
            fn.GLib.idle_add(_refresh_termset_sensitive, self)
            fn.GLib.idle_add(_refresh_zsh_themes_dropdown, self)
        except Exception as e:
            fn.log_error(f"Error: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_extra_shell_applications_clicked(self, _widget):
    """Install the selected extra shell tools."""
    fn.log_subsection("Install Extra Shell Applications")
    pairs = [
        ("expac", self.expac),
        ("ripgrep", self.ripgrep),
        ("yay-git", self.yay),
        ("paru-git", self.paru),
        ("bat", self.bat),
        ("downgrade", self.downgrade),
        ("hw-probe", self.hw_probe),
        ("rate-mirrors", self.rate_mirrors),
        ("most", self.most),
        ("fzf", self.fzf),
    ]
    selected = [pkg for pkg, cb in pairs if cb.get_active()]
    if not selected:
        fn.log_info("No packages selected")
        fn.show_in_app_notification(self, _("No packages selected"))
        return

    chaotic_only = {"yay-git", "paru-git", "downgrade", "rate-mirrors"}
    needs_chaotic = [pkg for pkg in selected if pkg in chaotic_only]
    if needs_chaotic and not fn.check_chaotic_aur_active():
        msg = f"{', '.join(needs_chaotic)} require chaotic-aur — enable it in pacman.conf first"
        fn.log_warn(msg)
        fn.show_in_app_notification(self, _("Enable chaotic-aur first: {packages}").format(packages=", ".join(needs_chaotic)))
        return

    fn.log_info(f"Installing: {' '.join(selected)}")
    fn.show_in_app_notification(self, _("Opening terminal..."))

    def wait_and_refresh(process):
        if process is not None:
            process.wait()
        fn.invalidate_pkg_cache()
        for pkg, cb in pairs:
            installed = fn.check_package_installed(pkg)
            fn.GLib.idle_add(cb.set_active, installed)
            fn.log_item(f"  {pkg:<20} {'OK' if installed else 'NOT INSTALLED'}")
        fn.GLib.idle_add(fn.log_success, "Extra shell applications done")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("Extra shell applications installed"))

    process = fn.launch_pacman_install_in_terminal(" ".join(selected))
    fn.threading.Thread(target=wait_and_refresh, args=(process,), daemon=True).start()


def on_extra_shell_applications_remove_clicked(self, _widget):
    """Remove the selected extra shell tools."""
    fn.log_subsection("Remove Extra Shell Applications")
    pairs = [
        ("expac", self.expac),
        ("ripgrep", self.ripgrep),
        ("yay-git", self.yay),
        ("paru-git", self.paru),
        ("bat", self.bat),
        ("downgrade", self.downgrade),
        ("hw-probe", self.hw_probe),
        ("rate-mirrors", self.rate_mirrors),
        ("most", self.most),
        ("fzf", self.fzf),
    ]
    selected = [pkg for pkg, cb in pairs if cb.get_active()]
    if not selected:
        fn.log_info("No packages selected")
        fn.show_in_app_notification(self, _("No packages selected"))
        return

    fn.log_info(f"Removing: {' '.join(selected)}")
    fn.show_in_app_notification(self, _("Opening terminal..."))

    def wait_and_refresh(process):
        if process is not None:
            process.wait()
        fn.invalidate_pkg_cache()
        for pkg, cb in pairs:
            installed = fn.check_package_installed(pkg)
            fn.GLib.idle_add(cb.set_active, installed)
            fn.log_item(f"  {pkg:<20} {'OK' if installed else 'NOT INSTALLED'}")
        fn.GLib.idle_add(self.select_all.set_active, False)
        fn.GLib.idle_add(fn.log_success, "Extra shell applications removal done")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("Extra shell applications removed"))

    pkgs = " ".join(selected)
    script = f"sudo pacman -Rdd --noconfirm {pkgs}; echo ''; read -p 'Press Enter to close'"
    fn.debug_print(f"Terminal cmd: {script}")
    process = fn.subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
    fn.threading.Thread(target=wait_and_refresh, args=(process,), daemon=True).start()


def on_select_all_toggle(self, _widget, active):
    """Select or deselect all extra shell tool checkboxes."""
    fn.log_info(f"Select all tools: {'on' if self.select_all.get_active() else 'off'}")
    if self.select_all.get_active():
        self.expac.set_active(True)
        self.ripgrep.set_active(True)
        self.yay.set_active(True)
        self.paru.set_active(True)
        self.bat.set_active(True)
        self.downgrade.set_active(True)
        self.hw_probe.set_active(True)
        self.rate_mirrors.set_active(True)
        self.most.set_active(True)
        self.fzf.set_active(True)


def on_install_zsh_clicked(self, _widget):
    """Install the zsh package."""
    fn.log_subsection("Install Zsh")
    if fn.check_package_installed("zsh"):
        fn.log_info("zsh is already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh is already installed"))
        return
    process = fn.launch_pacman_install_in_terminal("zsh")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Installing zsh..."))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            if fn.check_package_installed("zsh"):
                fn.log_success("zsh installed")
                fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh installed — page updated"))
                fn.GLib.idle_add(self.zsh_status_lbl.set_markup, _("Zsh is <b>installed</b>"))
                fn.GLib.idle_add(self.zsh_config_section.set_sensitive, True)
            else:
                fn.log_warn("zsh installation did not complete")
                fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh installation failed or was cancelled"))
        except Exception as e:
            fn.log_error(f"Error installing zsh: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_zsh_clicked(self, _widget):
    """Remove the zsh package."""
    fn.log_subsection("Remove Zsh")
    if not fn.check_package_installed("zsh"):
        fn.log_info("zsh is not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("Zsh is not installed"))
        return
    process = fn.launch_pacman_remove_in_terminal("zsh")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Removing zsh - terminal opened"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            if not fn.check_package_installed("zsh"):
                fn.log_success("Zsh removed")
                fn.GLib.idle_add(fn.show_in_app_notification, self, _("Zsh removed"))
                fn.GLib.idle_add(self.zsh_status_lbl.set_markup, _("Zsh is <b>not installed</b>"))
                fn.GLib.idle_add(self.zsh_config_section.set_sensitive, False)
            else:
                fn.log_warn("Zsh removal did not complete")
                fn.GLib.idle_add(fn.show_in_app_notification, self, _("Zsh removal failed or was cancelled"))
        except Exception as e:
            fn.log_error(f"Error removing zsh: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def _refresh_zsh_completions_lbl(self):
    if fn.check_package_installed("zsh-completions"):
        self.zsh_completions_lbl.set_markup(_("Zsh-completion is already <b>installed</b>"))
    else:
        self.zsh_completions_lbl.set_markup(_("Zsh-completion is <b>not</b> installed"))


def _refresh_zsh_syntax_lbl(self):
    if fn.check_package_installed("zsh-syntax-highlighting"):
        self.zsh_syntax_lbl.set_markup(_("Zsh-syntax-highlighting is already <b>installed</b>"))
    else:
        self.zsh_syntax_lbl.set_markup(_("Zsh-syntax-highlighting is not installed"))


def _refresh_zsh_omz_lbl(self):
    if fn.check_package_installed("oh-my-zsh-git"):
        self.zsh_omz_lbl.set_markup(_("Oh-my-zsh-git is already <b>installed</b>"))
    else:
        self.zsh_omz_lbl.set_markup(_("Oh-my-zsh-git is not installed"))


def _refresh_termset_sensitive(self):
    installed = fn.check_package_installed("oh-my-zsh-git")
    self.termset.set_sensitive(installed)
    self.zsh_themes.set_sensitive(installed)


def _refresh_zsh_themes_dropdown(self):
    if fn.check_package_installed("oh-my-zsh-git"):
        zsh_theme.get_themes(self.zsh_themes)
    else:
        self.zsh_themes.set_model(fn.Gtk.StringList.new([]))


def on_install_zsh_completions_clicked(self, _widget):
    """Install the zsh-completions package."""
    if fn.check_package_installed("zsh-completions"):
        fn.debug_print("zsh-completions already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-completions already installed"))
        return
    fn.log_subsection("Installing zsh-completions...")
    process = fn.launch_pacman_install_in_terminal("zsh-completions")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-completions installation started"))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("zsh-completions installed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-completions installed"))
            fn.GLib.idle_add(_refresh_zsh_completions_lbl, self)
        except Exception as e:
            fn.log_error(f"Error: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_zsh_completions_clicked(self, _widget):
    """Remove the zsh-completions package."""
    if not fn.check_package_installed("zsh-completions"):
        fn.log_info("zsh-completions is not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-completions is not installed"))
        return
    fn.log_subsection("Removing zsh-completions...")
    process = fn.launch_pacman_remove_in_terminal("zsh-completions")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Removal started"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("zsh-completions removed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-completions removed"))
            fn.GLib.idle_add(_refresh_zsh_completions_lbl, self)
        except Exception as e:
            fn.log_error(f"Error: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def on_install_zsh_syntax_highlighting_clicked(self, _widget):
    """Install the zsh-syntax-highlighting package."""
    if fn.check_package_installed("zsh-syntax-highlighting"):
        fn.debug_print("zsh-syntax-highlighting already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-syntax-highlighting already installed"))
        return
    fn.log_subsection("Installing zsh-syntax-highlighting...")
    process = fn.launch_pacman_install_in_terminal("zsh-syntax-highlighting")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-syntax-highlighting installation started"))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("zsh-syntax-highlighting installed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-syntax-highlighting installed"))
            fn.GLib.idle_add(_refresh_zsh_syntax_lbl, self)
        except Exception as e:
            fn.log_error(f"Error: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_zsh_syntax_highlighting_clicked(self, _widget):
    """Remove the zsh-syntax-highlighting package."""
    if not fn.check_package_installed("zsh-syntax-highlighting"):
        fn.log_info("zsh-syntax-highlighting is not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-syntax-highlighting is not installed"))
        return
    fn.log_subsection("Removing zsh-syntax-highlighting...")
    process = fn.launch_pacman_remove_in_terminal("zsh-syntax-highlighting")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Removal started"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("zsh-syntax-highlighting removed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("zsh-syntax-highlighting removed"))
            fn.GLib.idle_add(_refresh_zsh_syntax_lbl, self)
        except Exception as e:
            fn.log_error(f"Error: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def remove_oh_my_zsh(self, _widget):
    """Remove the oh-my-zsh-git package."""
    if not fn.check_package_installed("oh-my-zsh-git"):
        fn.log_info("oh-my-zsh-git is not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("oh-my-zsh-git is not installed"))
        return
    fn.log_subsection("Removing oh-my-zsh-git...")
    process = fn.launch_pacman_remove_in_terminal("oh-my-zsh-git")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Removal started"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("oh-my-zsh-git removed")
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("oh-my-zsh-git removed"))
            fn.GLib.idle_add(_refresh_zsh_omz_lbl, self)
            fn.GLib.idle_add(_refresh_termset_sensitive, self)
            fn.GLib.idle_add(_refresh_zsh_themes_dropdown, self)
        except Exception as e:
            fn.log_error(f"Error: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def _refresh_alacritty_lbl(self):
    if fn.check_package_installed("alacritty"):
        self.alacritty_status_lbl.set_markup(_("Alacritty is <b>installed</b>"))
    else:
        self.alacritty_status_lbl.set_markup(_("Alacritty is <b>not installed</b>"))


def _refresh_att_lbl(self):
    if fn.check_package_installed("alacritty-tweak-tool"):
        self.att_status_lbl.set_markup(_("alacritty-tweak-tool is <b>installed</b>"))
    else:
        self.att_status_lbl.set_markup(_("alacritty-tweak-tool is <b>not installed</b>"))


def _refresh_att_launch_btn(self):
    self.btn_launch_att.set_sensitive(fn.check_package_installed("alacritty-tweak-tool"))


def on_install_alacritty_clicked(self, _widget):
    """Install alacritty via terminal."""
    if fn.check_package_installed("alacritty"):
        fn.log_info("alacritty is already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("alacritty is already installed"))
        return
    fn.log_subsection("Installing alacritty...")
    process = fn.launch_pacman_install_in_terminal("alacritty")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Opening terminal to install alacritty"))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("alacritty installed")
            fn.GLib.idle_add(_refresh_alacritty_lbl, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("alacritty installed"))
        except Exception as e:
            fn.log_error(f"Error installing alacritty: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_alacritty_clicked(self, _widget):
    """Remove alacritty via terminal."""
    if not fn.check_package_installed("alacritty"):
        fn.log_info("alacritty is not installed — nothing to remove")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("alacritty is not installed"))
        return
    fn.log_subsection("Removing alacritty...")
    process = fn.launch_pacman_remove_in_terminal("alacritty")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Opening terminal to remove alacritty"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("alacritty removed")
            fn.GLib.idle_add(_refresh_alacritty_lbl, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("alacritty removed"))
        except Exception as e:
            fn.log_error(f"Error removing alacritty: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def on_install_alacritty_tweak_tool_clicked(self, _widget):
    """Install alacritty-tweak-tool from nemesis repo via terminal."""
    if fn.check_package_installed("alacritty-tweak-tool"):
        fn.log_info("alacritty-tweak-tool is already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("alacritty-tweak-tool is already installed"))
        return
    fn.log_subsection("Installing alacritty-tweak-tool...")
    process = fn.launch_pacman_install_in_terminal("alacritty-tweak-tool")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Opening terminal to install alacritty-tweak-tool"))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("alacritty-tweak-tool installed")
            fn.GLib.idle_add(_refresh_att_lbl, self)
            fn.GLib.idle_add(_refresh_att_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("alacritty-tweak-tool installed"))
        except Exception as e:
            fn.log_error(f"Error installing alacritty-tweak-tool: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_alacritty_tweak_tool_clicked(self, _widget):
    """Remove alacritty-tweak-tool via terminal."""
    if not fn.check_package_installed("alacritty-tweak-tool"):
        fn.log_info("alacritty-tweak-tool is not installed — nothing to remove")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("alacritty-tweak-tool is not installed"))
        return
    fn.log_subsection("Removing alacritty-tweak-tool...")
    process = fn.launch_pacman_remove_in_terminal("alacritty-tweak-tool")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Opening terminal to remove alacritty-tweak-tool"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("alacritty-tweak-tool removed")
            fn.GLib.idle_add(_refresh_att_lbl, self)
            fn.GLib.idle_add(_refresh_att_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("alacritty-tweak-tool removed"))
        except Exception as e:
            fn.log_error(f"Error removing alacritty-tweak-tool: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def on_click_launch_att_from_shells(self, _widget):
    """Launch Alacritty Tweak Tool as real user from the Shells page."""
    if fn.check_package_installed("alacritty-tweak-tool"):
        fn.log_subsection("Launching Alacritty Tweak Tool...")
        fn.subprocess.Popen(
            "sudo -E -u " + fn.sudo_username + " env HOME=" + fn.home + " alacritty-tweak-tool &",
            shell=True,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        GLib.idle_add(fn.show_in_app_notification, self, _("Alacritty Tweak Tool launched"))
    else:
        fn.log_info("alacritty-tweak-tool not installed")
        GLib.idle_add(fn.show_in_app_notification, self, _("alacritty-tweak-tool not installed"))


def _refresh_ftt_lbl(self):
    if fn.check_package_installed("fish-tweak-tool"):
        self.ftt_status_lbl.set_markup(_("fish-tweak-tool is <b>installed</b>"))
    else:
        self.ftt_status_lbl.set_markup(_("fish-tweak-tool is <b>not installed</b>"))


def _refresh_ftt_launch_btn(self):
    self.btn_launch_ftt.set_sensitive(fn.check_package_installed("fish-tweak-tool"))


def on_install_fish_tweak_tool_clicked(self, _widget):
    """Install fish-tweak-tool from nemesis repo via terminal."""
    if fn.check_package_installed("fish-tweak-tool"):
        fn.log_info("fish-tweak-tool is already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("fish-tweak-tool is already installed"))
        return
    fn.log_subsection("Installing fish-tweak-tool...")
    process = fn.launch_pacman_install_in_terminal("fish-tweak-tool")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Opening terminal to install fish-tweak-tool"))

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("fish-tweak-tool installed")
            fn.GLib.idle_add(_refresh_ftt_lbl, self)
            fn.GLib.idle_add(_refresh_ftt_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("fish-tweak-tool installed"))
        except Exception as e:
            fn.log_error(f"Error installing fish-tweak-tool: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_fish_tweak_tool_clicked(self, _widget):
    """Remove fish-tweak-tool via terminal."""
    if not fn.check_package_installed("fish-tweak-tool"):
        fn.log_info("fish-tweak-tool is not installed — nothing to remove")
        fn.GLib.idle_add(fn.show_in_app_notification, self, _("fish-tweak-tool is not installed"))
        return
    fn.log_subsection("Removing fish-tweak-tool...")
    process = fn.launch_pacman_remove_in_terminal("fish-tweak-tool")
    fn.GLib.idle_add(fn.show_in_app_notification, self, _("Opening terminal to remove fish-tweak-tool"))

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("fish-tweak-tool removed")
            fn.GLib.idle_add(_refresh_ftt_lbl, self)
            fn.GLib.idle_add(_refresh_ftt_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("fish-tweak-tool removed"))
        except Exception as e:
            fn.log_error(f"Error removing fish-tweak-tool: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def on_click_launch_ftt_from_shells(self, _widget):
    """Launch Fish Tweak Tool as real user from the Shells page."""
    if fn.check_package_installed("fish-tweak-tool"):
        fn.log_subsection("Launching Fish Tweak Tool...")
        fn.subprocess.Popen(
            "sudo -E -u " + fn.sudo_username + " env HOME=" + fn.home + " fish-tweak-tool &",
            shell=True,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        GLib.idle_add(fn.show_in_app_notification, self, _("Fish Tweak Tool launched"))
    else:
        fn.log_info("fish-tweak-tool not installed")
        GLib.idle_add(fn.show_in_app_notification, self, _("fish-tweak-tool not installed"))

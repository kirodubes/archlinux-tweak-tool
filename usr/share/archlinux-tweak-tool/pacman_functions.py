# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
from att_i18n import _


def append_repo(self, text):
    """Append text to /etc/pacman.conf, invalidate cache, and notify."""
    if hasattr(self, "initializing") and self.initializing:
        with open(fn.pacman, "a", encoding="utf-8") as myfile:
            myfile.write("\n\n")
            myfile.write(text)
        fn.invalidate_pacman_conf_cache()
        return
    fn.debug_print(f"Appending repository to {fn.pacman}")
    try:
        with open(fn.pacman, "a", encoding="utf-8") as myfile:
            myfile.write("\n\n")
            myfile.write(text)
        fn.invalidate_pacman_conf_cache()
        fn.log_success("Repository appended successfully")
        fn.show_in_app_notification(self, _("Settings Saved Successfully"))
    except Exception as error:
        fn.log_error(f"Failed to append repository: {error}")
        fn.show_in_app_notification(self, _("Failed to save settings"))


def insert_repo(self, text):
    """Insert text before the [custom] block in /etc/pacman.conf."""
    fn.debug_print(f"Inserting repository into {fn.pacman}")
    try:
        with open(fn.pacman, "r", encoding="utf-8") as f:
            lines = f.readlines()
            f.close()
        pos = fn.get_position(lines, "[custom]")
        num = pos + 3

        lines.insert(num, "\n" + text + "\n")

        with open(fn.pacman, "w", encoding="utf-8") as f:
            f.writelines(lines)
        fn.invalidate_pacman_conf_cache()
        fn.log_success("Repository inserted successfully")
    except Exception as error:
        fn.log_error(f"Failed to insert repository: {error}")


def check_repo(value):
    """Return True if the repo header is present and uncommented in pacman.conf."""
    for line in fn.get_pacman_conf_lines():
        if value in line:
            if "#" + value in line:
                return False
            else:
                return True
    return False


def repo_exist(value):
    """Return True if the repo header appears anywhere in pacman.conf."""
    for line in fn.get_pacman_conf_lines():
        if value in line:
            return True
    return False


def pacman_on(repo, lines, i, line):
    """Uncomment the repo header and its Include/Server lines."""
    if repo in line:
        lines[i] = line.replace("#", "")
        if (i + 1) < len(lines):
            lines[i + 1] = lines[i + 1].replace("#", "")
        if (i + 2) < len(lines) and "Server" in lines[i + 2]:
            lines[i + 2] = lines[i + 2].replace("#", "")


def mirror_on(mirror, lines, i, line):
    """Uncomment the mirror header and its Include/Server lines."""
    if mirror in line:
        lines[i] = line.replace("#", "")
        if (i + 1) < len(lines):
            lines[i + 1] = lines[i + 1].replace("#", "")
        if (i + 2) < len(lines) and "Server" in lines[i + 2]:
            lines[i + 2] = lines[i + 2].replace("#", "")


def pacman_off(repo, lines, i, line):
    """Comment out the repo header and its Include/Server lines."""
    if repo in line:
        if "#" not in lines[i]:
            lines[i] = line.replace(lines[i], "#" + lines[i])
        if (i + 1) < len(lines):
            if "#" not in lines[i + 1]:
                lines[i + 1] = lines[i + 1].replace(lines[i + 1], "#" + lines[i + 1])
        if (i + 2) < len(lines) and "Server" in lines[i + 2]:
            if "#" not in lines[i + 2]:
                lines[i + 2] = lines[i + 2].replace(lines[i + 2], "#" + lines[i + 2])


def mirror_off(mirror, lines, i, line):
    """Comment out the mirror header line."""
    if mirror in line:
        if "#" not in lines[i]:
            lines[i] = line.replace(lines[i], "#" + lines[i])


def spin_on(repo, lines, i, line):
    """Uncomment the repo header and the single Include line below it."""
    if repo in line:
        lines[i] = line.replace("#", "")
        if (i + 1) < len(lines):
            lines[i + 1] = lines[i + 1].replace("#", "")


def spin_off(repo, lines, i, line):
    """Comment out the repo header and the single Include line below it."""
    if repo in line:
        if "#" not in lines[i]:
            lines[i] = line.replace(lines[i], "#" + lines[i])
        if (i + 1) < len(lines):
            if "#" not in lines[i + 1]:
                lines[i + 1] = lines[i + 1].replace(lines[i + 1], "#" + lines[i + 1])


def toggle_test_repos(self, state, widget):
    """Enable or disable a named repo section in pacman.conf."""
    if hasattr(self, "initializing") and self.initializing:
        return
    action = "Enable" if state is True else "Disable"
    fn.log_subsection(f"{action} Repository: {widget}")

    if not fn.os.path.isfile(fn.pacman + "-bak"):
        fn.debug_print(f"Creating backup: {fn.pacman}-bak")
        fn.log_info_concise(f"  From: {fn.pacman}")
        fn.log_info_concise(f"  To:   {fn.pacman}-bak")
        fn.shutil.copy(fn.pacman, fn.pacman + "-bak")

    lines = ""
    if state is True:
        with open(fn.pacman, "r", encoding="utf-8") as f:
            lines = f.readlines()
        try:
            fn.debug_print(f"Enabling {widget} repository")
            for i in range(0, len(lines)):
                line = lines[i]
                if widget == "chaotics":
                    spin_on("[chaotic-aur]", lines, i, line)
                if widget == "nemesis":
                    spin_on("[nemesis_repo]", lines, i, line)
                if widget == "cachyos":
                    pacman_on("[cachyos]", lines, i, line)
                if widget == "testing":
                    pacman_on("[core-testing]", lines, i, line)
                if widget == "core":
                    pacman_on("[core]", lines, i, line)
                if widget == "extra":
                    pacman_on("[extra]", lines, i, line)
                if widget == "community-testing":
                    pacman_on("[extra-testing]", lines, i, line)
                if widget == "community":
                    pacman_on("[extra-testing]", lines, i, line)
                if widget == "multilib-testing":
                    pacman_on("[multilib-testing]", lines, i, line)
                if widget == "multilib":
                    pacman_on("[multilib]", lines, i, line)

            with open(fn.pacman, "w", encoding="utf-8") as f:
                f.writelines(lines)
            fn.invalidate_pacman_conf_cache()
            fn.log_success(f"Repository {widget} enabled successfully")
        except Exception as error:
            fn.log_error(f"Failed to enable {widget}: {error}")
            fn.messagebox(
                self,
                _("ERROR!!"),
                _("An error has occurred enabling repository {widget}").format(widget=widget),
            )
    else:
        with open(fn.pacman, "r", encoding="utf-8") as f:
            lines = f.readlines()
        try:
            fn.debug_print(f"Disabling {widget} repository")
            for i in range(0, len(lines)):
                line = lines[i]
                if widget == "chaotics":
                    spin_off("[chaotic-aur]", lines, i, line)
                if widget == "nemesis":
                    spin_off("[nemesis_repo]", lines, i, line)
                if widget == "cachyos":
                    pacman_off("[cachyos]", lines, i, line)
                if widget == "testing":
                    pacman_off("[core-testing]", lines, i, line)
                if widget == "core":
                    pacman_off("[core]", lines, i, line)
                if widget == "extra":
                    pacman_off("[extra]", lines, i, line)
                if widget == "community-testing":
                    pacman_off("[extra-testing]", lines, i, line)
                if widget == "community":
                    pacman_off("[extra-testing]", lines, i, line)
                if widget == "multilib-testing":
                    pacman_off("[multilib-testing]", lines, i, line)
                if widget == "multilib":
                    pacman_off("[multilib]", lines, i, line)

            with open(fn.pacman, "w", encoding="utf-8") as f:
                f.writelines(lines)
            fn.invalidate_pacman_conf_cache()
            fn.log_success(f"Repository {widget} disabled successfully")
        except Exception as error:
            fn.log_error(f"Failed to disable {widget}: {error}")
            fn.messagebox(
                self,
                _("ERROR!!"),
                _("An error has occurred disabling repository {widget}").format(widget=widget),
            )


# ── AUR helper management ──────────────────────────────────────────────


def check_aur_helper():
    """Check which AUR helper is installed (yay or paru)."""
    if fn.path.exists("/usr/bin/yay"):
        return "yay"
    elif fn.path.exists("/usr/bin/paru"):
        return "paru"
    return None


def install_yay_pacman(self):
    """Install yay-git from chaotic-aur repository."""
    fn.log_subsection("Install yay from Chaotic-AUR")
    fn.debug_print("Installing yay-git from chaotic-aur repository")
    fn.show_in_app_notification(self, _("Opening terminal to install yay-git"))
    return fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", "sudo pacman -S yay-git; read -p 'Press enter to close'"],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )


def install_yay_git(self):
    """Install yay-git from source in a terminal window. Returns the Popen process."""
    fn.log_subsection("Install yay from Source")
    fn.show_in_app_notification(self, _("Opening terminal to build yay-git"))
    build_script = "/usr/share/archlinux-tweak-tool/data/bin/build-yay-git"
    fn.log_success("Build terminal opened")
    return fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", f"{build_script} {fn.sudo_username}"],
        shell=False,
    )


def install_paru_pacman(self):
    """Install paru-git from chaotic-aur repository."""
    fn.log_subsection("Install paru from Chaotic-AUR")
    fn.debug_print("Installing paru-git from chaotic-aur repository")
    fn.show_in_app_notification(self, _("Opening terminal to install paru-git"))
    return fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", "sudo pacman -S paru-git; read -p 'Press enter to close'"],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )


def install_paru_git(self):
    """Install paru-git from source in a terminal window. Returns the Popen process."""
    fn.log_subsection("Install paru from Source")
    fn.show_in_app_notification(self, _("Opening terminal to build paru-git"))
    build_script = "/usr/share/archlinux-tweak-tool/data/bin/build-paru-git"
    fn.log_success("Build terminal opened")
    return fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", f"{build_script} {fn.sudo_username}"],
        shell=False,
    )


def ensure_nemesis_packages(self):
    """Open setup terminal to install kiro-keyring and kiro-mirrorlist if missing."""
    has_keyring = True
    has_mirrorlist = True
    try:
        fn.subprocess.check_output(["pacman", "-Q", "kiro-keyring"], stderr=fn.subprocess.DEVNULL)
    except fn.subprocess.CalledProcessError:
        has_keyring = False
    try:
        fn.subprocess.check_output(["pacman", "-Q", "kiro-mirrorlist"], stderr=fn.subprocess.DEVNULL)
    except fn.subprocess.CalledProcessError:
        has_mirrorlist = False

    if has_keyring and has_mirrorlist:
        return None

    fn.log_subsection("Nemesis: keyring/mirrorlist missing — running setup")
    fn.show_in_app_notification(self, _("Installing Nemesis keyring and mirrorlist..."))
    setup_script = "/usr/share/archlinux-tweak-tool/data/bin/setup-nemesis"
    return fn.subprocess.Popen(
        ["alacritty", "-e", "sudo", "bash", setup_script],
    )


def ensure_chaotic_packages(self):
    """Open setup terminal to install chaotic-keyring and chaotic-mirrorlist if missing."""
    has_keyring = True
    has_mirrorlist = True
    try:
        fn.subprocess.check_output(["pacman", "-Q", "chaotic-keyring"], stderr=fn.subprocess.DEVNULL)
    except fn.subprocess.CalledProcessError:
        has_keyring = False
    try:
        fn.subprocess.check_output(["pacman", "-Q", "chaotic-mirrorlist"], stderr=fn.subprocess.DEVNULL)
    except fn.subprocess.CalledProcessError:
        has_mirrorlist = False

    if has_keyring and has_mirrorlist:
        return None

    fn.log_subsection("Chaotic-AUR: keyring/mirrorlist missing — running setup")
    fn.show_in_app_notification(self, _("Installing Chaotic-AUR keyring and mirrorlist..."))
    setup_script = "/usr/share/archlinux-tweak-tool/data/bin/setup-chaotic-aur"
    return fn.subprocess.Popen(
        ["alacritty", "-e", "sudo", "bash", setup_script],
    )


def ensure_cachyos_packages(self):
    """Open setup terminal to install cachyos-keyring and cachyos-mirrorlist if missing."""
    has_keyring = True
    has_mirrorlist = True
    try:
        fn.subprocess.check_output(["pacman", "-Q", "cachyos-keyring"], stderr=fn.subprocess.DEVNULL)
    except fn.subprocess.CalledProcessError:
        has_keyring = False
    try:
        fn.subprocess.check_output(["pacman", "-Q", "cachyos-mirrorlist"], stderr=fn.subprocess.DEVNULL)
    except fn.subprocess.CalledProcessError:
        has_mirrorlist = False

    if has_keyring and has_mirrorlist:
        return None

    fn.log_subsection("CachyOS: keyring/mirrorlist missing — running setup")
    fn.show_in_app_notification(self, _("Installing CachyOS keyring and mirrorlist..."))
    setup_script = "/usr/share/archlinux-tweak-tool/data/bin/setup-cachyos"
    return fn.subprocess.Popen(
        ["alacritty", "-e", "sudo", "bash", setup_script],
    )


def _find_aur_package(binary):
    """Return the installed pacman package name for an AUR helper binary."""
    for pkg in [f"{binary}-git", f"{binary}-bin", binary]:
        try:
            fn.subprocess.check_output(["pacman", "-Q", pkg], stderr=fn.subprocess.DEVNULL)
            return pkg
        except fn.subprocess.CalledProcessError:
            continue
    return None


def remove_aur_helper(self, binary):
    """Remove yay or paru by checking known package name variants."""
    fn.log_subsection(f"Remove AUR Helper: {binary}")
    pkg = _find_aur_package(binary)
    if pkg is None:
        fn.log_error(f"Could not find installed package for {binary}")
        fn.show_in_app_notification(self, _("Could not find installed package for {binary}").format(binary=binary))
        return None
    fn.debug_print(f"Package to remove: {pkg}")
    fn.show_in_app_notification(self, _("Opening terminal to remove {pkg}").format(pkg=pkg))
    return fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", f"sudo pacman -R {pkg}; read -p 'Press enter to close'"],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
import os


def backup_gtk_config():
    fn.log_subsection("Backing up GTK + Qt theme config")
    fn.log_info("  ATT runs as root; copying user GTK 3/4 + Qt (Kvantum/qt5ct/qt6ct) config so apps respect your desktop theme")
    fn.debug_print("backup_gtk_config() START")
    fn.debug_print("=" * 75)

    if fn.path.isdir(fn.home + "/.config/gtk-3.0"):
        fn.debug_print(f"Found GTK-3.0 config at {fn.home}/.config/gtk-3.0")
        try:
            if not os.path.islink("/root/.config/gtk-3.0"):
                fn.debug_print("Removing existing /root/.config/gtk-3.0")
                fn.shutil.rmtree("/root/.config/gtk-3.0")
                src = fn.home + "/.config/gtk-3.0"
                dst = "/root/.config/gtk-3.0"
                fn.debug_print(f"  From: {src}")
                fn.debug_print(f"  To:   {dst}")
                fn.debug_print(f"  copytree: {src} → {dst}")
                fn.shutil.copytree(src, dst)
                fn.debug_print("✓ GTK-3.0 backup completed")
            else:
                fn.debug_print("/root/.config/gtk-3.0 is a symlink, skipping")
        except Exception as error:
            fn.debug_print(f"Error backing up gtk-3.0: {error}")
            fn.log_error(str(error))
    else:
        fn.debug_print(f"GTK-3.0 config not found at {fn.home}/.config/gtk-3.0")

    gtk4_src = fn.home + "/.config/gtk-4.0"
    gtk4_dst = "/root/.config/gtk-4.0"
    if fn.path.isdir(gtk4_src) and not os.path.islink(gtk4_dst):
        fn.debug_print(f"Found GTK-4.0 config at {gtk4_src}")
        try:
            os.makedirs(gtk4_dst, exist_ok=True)
            fn.debug_print(f"  From: {gtk4_src}")
            fn.debug_print(f"  To:   {gtk4_dst}")
            fn.shutil.copytree(gtk4_src, gtk4_dst, dirs_exist_ok=True)
            for dirpath, dirnames, filenames in os.walk(gtk4_dst):
                os.chmod(dirpath, 0o755)
                for fname in filenames:
                    os.chmod(os.path.join(dirpath, fname), 0o644)
            fn.debug_print("✓ GTK-4.0 backup completed")
        except Exception as error:
            fn.debug_print(f"Error backing up gtk-4.0: {error}")
            fn.log_error(str(error))
    elif os.path.islink(gtk4_dst):
        fn.debug_print("/root/.config/gtk-4.0 is a symlink, skipping")
    else:
        fn.debug_print(f"GTK-4.0 config not found at {gtk4_src}")

    if fn.path.isdir("/root/.config/xsettingsd/xsettingsd.conf"):
        fn.debug_print("Found xsettingsd config")
        try:
            if not os.path.islink("/root/.config/xsettingsd/"):
                fn.debug_print("Removing existing /root/.config/xsettingsd/")
                fn.shutil.rmtree("/root/.config/xsettingsd/")
                if fn.path.isdir(fn.home + "/.config/xsettingsd/"):
                    src = fn.home + "/.config/xsettingsd/"
                    dst = "/root/.config/xsettingsd/"
                    fn.log_info_concise(f"  From: {src}")
                    fn.log_info_concise(f"  To:   {dst}")
                    fn.debug_print(f"  copytree: {src} → {dst}")
                    fn.shutil.copytree(src, dst)
                    fn.debug_print("✓ xsettingsd backup completed")
            else:
                fn.debug_print("/root/.config/xsettingsd/ is a symlink, skipping")
        except Exception as error:
            fn.debug_print(f"Error backing up xsettingsd: {error}")
            fn.log_error(str(error))
    else:
        fn.debug_print("xsettingsd config not found")

    # Qt theming — Kvantum + qt5ct + qt6ct, so root-launched Qt apps follow the desktop theme.
    # Qt apps (e.g. Btrfs Assistant) theme via Kvantum, not GTK; root has no Qt config
    # of its own, so without this they fall back to the default Kvantum theme instead of
    # the user's ArcDark. qt6ct carries the icons and fonts for Qt6 apps. Mirrors the GTK-4.0 copy above.
    for qt_dir in ("Kvantum", "qt5ct", "qt6ct"):
        qt_src = fn.home + "/.config/" + qt_dir
        qt_dst = "/root/.config/" + qt_dir
        if fn.path.isdir(qt_src) and not os.path.islink(qt_dst):
            fn.debug_print(f"Found Qt config at {qt_src}")
            try:
                os.makedirs(qt_dst, exist_ok=True)
                fn.debug_print(f"  From: {qt_src}")
                fn.debug_print(f"  To:   {qt_dst}")
                fn.shutil.copytree(qt_src, qt_dst, dirs_exist_ok=True)
                for dirpath, dirnames, filenames in os.walk(qt_dst):
                    os.chmod(dirpath, 0o755)
                    for fname in filenames:
                        os.chmod(os.path.join(dirpath, fname), 0o644)
                fn.debug_print(f"✓ {qt_dir} backup completed")
            except Exception as error:
                fn.debug_print(f"Error backing up {qt_dir}: {error}")
                fn.log_error(str(error))
        elif os.path.islink(qt_dst):
            fn.debug_print(f"/root/.config/{qt_dir} is a symlink, skipping")
        else:
            fn.debug_print(f"Qt config not found at {qt_src}")

    fn.debug_print("=" * 75)
    fn.debug_print("backup_gtk_config() END")
    fn.debug_print("=" * 75)


def backup_system_configs():
    fn.log_subsection("Backing up system config files")
    fn.debug_print("backup_system_configs() START")
    fn.debug_print("=" * 75)

    if fn.path.isfile(fn.sddm_default_d1):
        if not fn.path.isfile(fn.sddm_default_d1_bak):
            try:
                fn.debug_print(f"Backing up {fn.sddm_default_d1} → {fn.sddm_default_d1_bak}")
                fn.log_info_concise(f"  From: {fn.sddm_default_d1}")
                fn.log_info_concise(f"  To:   {fn.sddm_default_d1_bak}")
                fn.shutil.copy(fn.sddm_default_d1, fn.sddm_default_d1_bak)
                fn.debug_print(f"✓ {fn.sddm_default_d1_bak} created")
            except Exception as error:
                fn.debug_print(f"Error backing up {fn.sddm_default_d1}: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print(f"{fn.sddm_default_d1_bak} already exists, skipping")
    else:
        fn.debug_print(f"{fn.sddm_default_d1} not found")

    if fn.path.isdir(fn.sddm_default_d2_dir):
        if not fn.path.isdir(fn.sddm_default_d2_dir_bak):
            try:
                fn.debug_print(f"Backing up {fn.sddm_default_d2_dir} → {fn.sddm_default_d2_dir_bak}")
                fn.log_info_concise(f"  From: {fn.sddm_default_d2_dir}")
                fn.log_info_concise(f"  To:   {fn.sddm_default_d2_dir_bak}")
                fn.shutil.copytree(fn.sddm_default_d2_dir, fn.sddm_default_d2_dir_bak)
                fn.debug_print(f"✓ {fn.sddm_default_d2_dir_bak} created")
            except Exception as error:
                fn.debug_print(f"Error backing up {fn.sddm_default_d2_dir}: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print(f"{fn.sddm_default_d2_dir_bak} already exists, skipping")
    else:
        fn.debug_print(f"{fn.sddm_default_d2_dir} not found")

    if fn.path.exists("/usr/share/icons/default/index.theme"):
        if not fn.path.isfile("/usr/share/icons/default/index.theme-bak"):
            try:
                fn.debug_print("Backing up /usr/share/icons/default/index.theme")
                fn.log_info_concise("  From: /usr/share/icons/default/index.theme")
                fn.log_info_concise("  To:   /usr/share/icons/default/index.theme-bak")
                fn.shutil.copy(
                    "/usr/share/icons/default/index.theme",
                    "/usr/share/icons/default/index.theme-bak",
                )
                fn.debug_print("✓ index.theme-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up index.theme: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("index.theme-bak already exists, skipping")
    else:
        fn.debug_print("/usr/share/icons/default/index.theme not found")

    if fn.path.exists("/etc/samba/smb.conf"):
        if not fn.path.isfile("/etc/samba/smb.conf-bak"):
            try:
                fn.debug_print("Backing up /etc/samba/smb.conf")
                fn.log_info_concise("  From: /etc/samba/smb.conf")
                fn.log_info_concise("  To:   /etc/samba/smb.conf-bak")
                fn.shutil.copy("/etc/samba/smb.conf", "/etc/samba/smb.conf-bak")
                fn.debug_print("✓ smb.conf-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up smb.conf: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("smb.conf-bak already exists, skipping")
    else:
        fn.debug_print("/etc/samba/smb.conf not found")

    if fn.path.exists("/etc/nsswitch.conf"):
        if not fn.path.isfile("/etc/nsswitch.conf-bak"):
            try:
                fn.debug_print("Backing up /etc/nsswitch.conf")
                fn.log_info_concise("  From: /etc/nsswitch.conf")
                fn.log_info_concise("  To:   /etc/nsswitch.conf-bak")
                fn.shutil.copy("/etc/nsswitch.conf", "/etc/nsswitch.conf-bak")
                fn.debug_print("✓ nsswitch.conf-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up nsswitch.conf: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("nsswitch.conf-bak already exists, skipping")
    else:
        fn.debug_print("/etc/nsswitch.conf not found")

    if fn.path.exists("/etc/makepkg.conf"):
        if not fn.path.isfile("/etc/makepkg.conf-bak"):
            try:
                fn.debug_print("Backing up /etc/makepkg.conf")
                fn.log_info_concise("  From: /etc/makepkg.conf")
                fn.log_info_concise("  To:   /etc/makepkg.conf-bak")
                fn.shutil.copy("/etc/makepkg.conf", "/etc/makepkg.conf-bak")
                fn.debug_print("✓ makepkg.conf-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up makepkg.conf: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("makepkg.conf-bak already exists, skipping")
    else:
        fn.debug_print("/etc/makepkg.conf not found")

    fn.debug_print("=" * 75)
    fn.debug_print("backup_system_configs() END")
    fn.debug_print("=" * 75)


def backup_user_configs():
    fn.log_subsection("Backing up user config files")
    fn.debug_print("backup_user_configs() START")
    fn.debug_print("=" * 75)

    # Fish shell config
    fish_config = fn.home + "/.config/fish/config.fish"
    if fn.path.isfile(fish_config) and not fn.path.isfile(fish_config + "-bak"):
        try:
            fn.debug_print(f"Backing up fish config: {fish_config}")
            fn.log_info_concise(f"  From: {fish_config}")
            fn.log_info_concise(f"  To:   {fish_config}-bak")
            fn.shutil.copy(fish_config, fish_config + "-bak")
            fn.permissions(fish_config + "-bak")
            fn.debug_print("✓ fish config.fish-bak created")
        except Exception as error:
            fn.debug_print(f"Error backing up fish config: {error}")
            fn.log_error(str(error))
    elif fn.path.isfile(fish_config + "-bak"):
        fn.debug_print("fish config.fish-bak already exists, skipping")
    else:
        fn.debug_print(f"fish config not found at {fish_config}")

    # Pacman mirrorlist
    if fn.path.isfile(fn.mirrorlist):
        if not fn.path.isfile(fn.mirrorlist + "-bak"):
            try:
                fn.debug_print(f"Backing up mirrorlist: {fn.mirrorlist}")
                fn.log_info_concise(f"  From: {fn.mirrorlist}")
                fn.log_info_concise(f"  To:   {fn.mirrorlist}-bak")
                fn.shutil.copy(fn.mirrorlist, fn.mirrorlist + "-bak")
                fn.debug_print("✓ mirrorlist-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up mirrorlist: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("mirrorlist-bak already exists, skipping")
    else:
        fn.debug_print(f"mirrorlist not found at {fn.mirrorlist}")

    # Hosts file
    if fn.path.isfile("/etc/hosts"):
        if not fn.path.isfile("/etc/hosts-bak"):
            try:
                fn.debug_print("Backing up /etc/hosts")
                fn.log_info_concise("  From: /etc/hosts")
                fn.log_info_concise("  To:   /etc/hosts-bak")
                fn.shutil.copy("/etc/hosts", "/etc/hosts-bak")
                fn.debug_print("✓ hosts-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up hosts: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("hosts-bak already exists, skipping")
    else:
        fn.debug_print("/etc/hosts not found")

    # Fastfetch config — backup only; ATT jsonc placement happens on install toggle
    if fn.path.isfile(fn.fastfetch_config):
        if not fn.path.isfile(fn.fastfetch_config + "-bak"):
            try:
                fn.debug_print(f"Backing up fastfetch config: {fn.fastfetch_config}")
                fn.log_info_concise(f"  From: {fn.fastfetch_config}")
                fn.log_info_concise(f"  To:   {fn.fastfetch_config}-bak")
                fn.shutil.copy(fn.fastfetch_config, fn.fastfetch_config + "-bak")
                fn.permissions(fn.fastfetch_config + "-bak")
                fn.debug_print("✓ fastfetch.json-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up fastfetch config: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("fastfetch.json-bak already exists, skipping")

    # Bash config
    if fn.path.isfile(fn.bash_config):
        if not fn.path.isfile(fn.bash_config + "-bak"):
            try:
                fn.debug_print(f"Backing up bashrc: {fn.bash_config}")
                fn.log_info_concise(f"  From: {fn.bash_config}")
                fn.log_info_concise(f"  To:   {fn.bash_config}-bak")
                fn.shutil.copy(fn.bash_config, fn.bash_config + "-bak")
                fn.permissions(fn.home + "/.bashrc-bak")
                fn.debug_print("✓ .bashrc-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up bashrc: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print(".bashrc-bak already exists, skipping")
    else:
        fn.debug_print(f"bashrc not found at {fn.bash_config}")

    # Zsh config
    if fn.path.isfile(fn.zsh_config):
        if not fn.path.isfile(fn.zsh_config + "-bak"):
            try:
                fn.debug_print(f"Backing up zshrc: {fn.zsh_config}")
                fn.log_info_concise(f"  From: {fn.zsh_config}")
                fn.log_info_concise(f"  To:   {fn.zsh_config}-bak")
                fn.shutil.copy(fn.zsh_config, fn.zsh_config + "-bak")
                fn.permissions(fn.home + "/.zshrc-bak")
                fn.debug_print("✓ .zshrc-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up zshrc: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print(".zshrc-bak already exists, skipping")
    else:
        fn.debug_print(f"zshrc not found at {fn.zsh_config}")

    # Pacman config
    if fn.path.isfile(fn.pacman):
        if not fn.path.isfile(fn.pacman + "-bak"):
            try:
                fn.debug_print(f"Backing up pacman config: {fn.pacman}")
                fn.log_info_concise(f"  From: {fn.pacman}")
                fn.log_info_concise(f"  To:   {fn.pacman}-bak")
                fn.shutil.copy(fn.pacman, fn.pacman + "-bak")
                fn.debug_print("✓ pacman.conf-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up pacman config: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("pacman.conf-bak already exists, skipping")
    else:
        fn.debug_print(f"pacman config not found at {fn.pacman}")

    # XFCE4 terminal config
    if fn.file_check(fn.xfce4_terminal_config):
        if not fn.path.isfile(fn.xfce4_terminal_config + "-bak"):
            try:
                fn.debug_print(f"Backing up xfce4 terminal config: {fn.xfce4_terminal_config}")
                fn.log_info_concise(f"  From: {fn.xfce4_terminal_config}")
                fn.log_info_concise(f"  To:   {fn.xfce4_terminal_config}-bak")
                fn.shutil.copy(fn.xfce4_terminal_config, fn.xfce4_terminal_config + "-bak")
                fn.permissions(fn.xfce4_terminal_config + "-bak")
                fn.debug_print("✓ terminalrc-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up xfce4 terminal config: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("terminalrc-bak already exists, skipping")
    else:
        fn.debug_print(f"xfce4 terminal config not found at {fn.xfce4_terminal_config}")

    # Alacritty config
    if fn.file_check(fn.alacritty_config):
        if not fn.path.isfile(fn.alacritty_config + "-bak"):
            try:
                fn.debug_print(f"Backing up alacritty config: {fn.alacritty_config}")
                fn.log_info_concise(f"  From: {fn.alacritty_config}")
                fn.log_info_concise(f"  To:   {fn.alacritty_config}-bak")
                fn.shutil.copy(fn.alacritty_config, fn.alacritty_config + "-bak")
                fn.permissions(fn.alacritty_config + "-bak")
                fn.debug_print("✓ alacritty.yml-bak created")
            except Exception as error:
                fn.debug_print(f"Error backing up alacritty config: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("alacritty.yml-bak already exists, skipping")
    else:
        fn.debug_print(f"alacritty config not found at {fn.alacritty_config}")

    # Variety config
    variety_conf = fn.path.join(fn.home, ".config", "variety", "variety.conf")
    variety_conf_bak = fn.path.join(fn.home, ".config", "variety", "variety.conf-bak")
    if fn.path.isfile(variety_conf) and not fn.path.isfile(variety_conf_bak):
        try:
            fn.debug_print(f"Backing up variety.conf: {variety_conf}")
            fn.log_info_concise(f"  From: {variety_conf}")
            fn.log_info_concise(f"  To:   {variety_conf_bak}")
            fn.shutil.copy2(variety_conf, variety_conf_bak)
            fn.permissions(variety_conf_bak)
            fn.debug_print("✓ variety.conf-bak created")
        except Exception as error:
            fn.debug_print(f"Error backing up variety.conf: {error}")
            fn.log_error(str(error))
    else:
        fn.debug_print("variety.conf-bak already exists or variety.conf not found, skipping")

    # Variety scripts folder
    variety_scripts = fn.path.join(fn.home, ".config", "variety", "scripts")
    variety_scripts_bak = fn.path.join(fn.home, ".config", "variety", "scripts-bak")
    if fn.path.isdir(variety_scripts) and not fn.path.isdir(variety_scripts_bak):
        try:
            fn.debug_print(f"Backing up variety scripts: {variety_scripts}")
            fn.log_info_concise(f"  From: {variety_scripts}")
            fn.log_info_concise(f"  To:   {variety_scripts_bak}")
            fn.shutil.copytree(variety_scripts, variety_scripts_bak)
            fn.permissions(variety_scripts_bak)
            fn.debug_print("✓ scripts-bak created")
        except Exception as error:
            fn.debug_print(f"Error backing up variety scripts: {error}")
            fn.log_error(str(error))
    else:
        fn.debug_print("scripts-bak already exists or scripts folder not found, skipping")

    fn.debug_print("=" * 75)
    fn.debug_print("backup_user_configs() END")
    fn.debug_print("=" * 75)


def backup_nanorc():
    fn.log_subsection("Backing up /etc/nanorc")
    if fn.path.isfile(fn.nanorc):
        if not fn.path.isfile(fn.nanorc_bak):
            try:
                fn.debug_print(f"  From: {fn.nanorc}")
                fn.debug_print(f"  To:   {fn.nanorc_bak}")
                fn.shutil.copy(fn.nanorc, fn.nanorc_bak)
                fn.log_success("nanorc backup created")
            except Exception as error:
                fn.log_error(f"Failed to back up nanorc: {error}")
        else:
            fn.log_info("nanorc-bak already exists, skipping")
    else:
        fn.log_warn("/etc/nanorc not found")


def restore_nanorc(self):
    fn.log_subsection("Restoring /etc/nanorc from backup")
    if fn.path.isfile(fn.nanorc_bak):
        try:
            fn.debug_print(f"  From: {fn.nanorc_bak}")
            fn.debug_print(f"  To:   {fn.nanorc}")
            fn.shutil.copy(fn.nanorc_bak, fn.nanorc)
            fn.log_success("nanorc restored from backup")
            fn.show_in_app_notification(self, "nanorc restored from backup")
        except Exception as error:
            fn.log_error(f"Failed to restore nanorc: {error}")
            fn.show_in_app_notification(self, "Failed to restore nanorc backup")
    else:
        fn.log_warn("No nanorc backup found")
        fn.show_in_app_notification(self, "No nanorc backup found")

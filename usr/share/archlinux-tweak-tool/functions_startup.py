# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn


def init_repos_and_sddm(self):
    """Initialize repository checks and SDDM configuration asynchronously"""
    self.initializing = True
    try:
        import pacman_functions as pmf
        import sddm

        # Check and display repository status
        arch_testing = pmf.check_repo("[core-testing]")
        arch_core = pmf.check_repo("[core]")
        arch_extra = pmf.check_repo("[extra]")
        arch_community = pmf.check_repo("[extra-testing]")
        arch_multilib_testing = pmf.check_repo("[multilib-testing]")
        arch_multilib = pmf.check_repo("[multilib]")
        nemesis_repo = pmf.check_repo("[nemesis_repo]")

        # Update repository toggle switches via GLib to stay async
        fn.GLib.idle_add(self.checkbutton2.set_active, arch_testing)
        fn.GLib.idle_add(self.checkbutton6.set_active, arch_core)
        fn.GLib.idle_add(self.checkbutton7.set_active, arch_extra)
        fn.GLib.idle_add(self.checkbutton5.set_active, arch_community)
        fn.GLib.idle_add(self.checkbutton3.set_active, arch_multilib_testing)
        fn.GLib.idle_add(self.checkbutton8.set_active, arch_multilib)

        self.opened = False
        fn.GLib.idle_add(self.nemesis_switch.set_active, nemesis_repo)
        self.opened = False

        # Disable desktop install button if nemesis_repo not available
        if not fn.check_nemesis_repo_active():
            fn.GLib.idle_add(self.button_install.set_sensitive, False)

        # Configure SDDM if present
        if fn.path.exists("/usr/bin/sddm"):
            try:
                if sddm.check_sddm(sddm.get_sddm_lines(fn.sddm_default_d2), "CursorTheme=") and sddm.check_sddm(
                    sddm.get_sddm_lines(fn.sddm_default_d2), "User="
                ):
                    if fn.path.isfile(fn.sddm_default_d2):
                        if "#" in sddm.check_sddm(sddm.get_sddm_lines(fn.sddm_default_d2), "User="):
                            fn.GLib.idle_add(self.autologin_sddm.set_active, False)
                            fn.GLib.idle_add(self.sessions_sddm.set_sensitive, False)
            except Exception:
                pass
    except Exception:
        pass
    finally:
        self.initializing = False


def setup_icon_theme():
    fn.log_subsection("Setting up icon/cursor theme defaults")
    fn.debug_print("setup_icon_theme() START")
    fn.debug_print("=" * 75)

    if fn.path.isfile("/usr/share/icons/default"):
        fn.debug_print("Found /usr/share/icons/default as file, removing")
        try:
            fn.unlink("/usr/share/icons/default")
            fn.debug_print("✓ /usr/share/icons/default removed")
        except Exception as error:
            fn.debug_print(f"Error removing /usr/share/icons/default: {error}")
            fn.log_error(str(error))

    if not fn.path.isdir("/usr/share/icons/default"):
        fn.debug_print("Creating /usr/share/icons/default directory")
        try:
            fn.makedirs("/usr/share/icons/default", 0o755)
            fn.debug_print("✓ /usr/share/icons/default created")
        except Exception as error:
            fn.debug_print(f"Error creating /usr/share/icons/default: {error}")
            fn.log_error(str(error))
    else:
        fn.debug_print("/usr/share/icons/default already exists")

    if not fn.path.isfile("/usr/share/icons/default/index.theme"):
        fn.debug_print("index.theme not found, checking for backup or default")
        if fn.path.isfile("/usr/share/icons/default/index.theme-bak"):
            fn.debug_print("Found index.theme-bak, restoring")
            try:
                fn.log_info_concise("  From: /usr/share/icons/default/index.theme-bak")
                fn.log_info_concise("  To:   /usr/share/icons/default/index.theme")
                fn.shutil.copy(
                    "/usr/share/icons/default/index.theme-bak",
                    "/usr/share/icons/default/index.theme",
                )
                fn.debug_print("✓ index.theme restored from backup")
            except Exception as error:
                fn.debug_print(f"Error restoring index.theme: {error}")
                fn.log_error(str(error))
        else:
            fn.debug_print("No backup found, installing default from ATT template")
            try:
                fn.log_info_concise("  From: /usr/share/archlinux-tweak-tool/data/cursor/index.theme")
                fn.log_info_concise("  To:   /usr/share/icons/default/index.theme")
                fn.shutil.copy(
                    "/usr/share/archlinux-tweak-tool/data/cursor/index.theme",
                    "/usr/share/icons/default/index.theme",
                )
                fn.debug_print("✓ Default index.theme installed")
            except Exception as error:
                fn.debug_print(f"Error installing default index.theme: {error}")
                fn.log_error(str(error))
    else:
        fn.debug_print("index.theme already exists, skipping")


def setup_fastfetch_config():
    fn.log_subsection("Setting up fastfetch config")
    fn.debug_print("setup_fastfetch_config() START")
    fn.debug_print("=" * 75)

    # KiroTux keeps fastfetch's own default (Arch logo); the Kiro config is only placed when picked on the page
    if fn.is_kirotux():
        fn.debug_print("KiroTux: leaving fastfetch at its default, no config placed")
    elif not fn.path.isfile(fn.fastfetch_config):
        fn.debug_print(f"fastfetch config not found at {fn.fastfetch_config}")
        fn.debug_print(f"Copying from template: {fn.fastfetch_kiro}")
        try:
            fn.log_info_concise(f"  From: {fn.fastfetch_kiro}")
            fn.log_info_concise(f"  To:   {fn.fastfetch_config}")
            fn.shutil.copy(fn.fastfetch_kiro, fn.fastfetch_config)
            fn.permissions(fn.fastfetch_config)
            fn.debug_print("✓ fastfetch config installed")
        except Exception as error:
            fn.debug_print(f"Error installing fastfetch config: {error}")
            fn.log_error(str(error))
    else:
        fn.debug_print(f"fastfetch config already exists at {fn.fastfetch_config}")

    fn.debug_print("=" * 75)
    fn.debug_print("setup_fastfetch_config() END")
    fn.debug_print("=" * 75)


def fix_permissions():
    fn.log_subsection("Checking file permissions")
    fn.debug_print("fix_permissions() START")
    fn.debug_print("=" * 75)

    fn.debug_print("Checking directory permissions")
    a1 = fn.stat(fn.home + "/.config/autostart")
    a2 = fn.stat(fn.home + "/.config/archlinux-tweak-tool")
    autostart_uid = a1.st_uid
    att_uid = a2.st_uid

    fn.debug_print(f"autostart owner UID: {autostart_uid}")
    fn.debug_print(f"archlinux-tweak-tool owner UID: {att_uid}")

    if fn.path.exists(fn.home + "/.config-att"):
        fn.debug_print(f"Found {fn.home}/.config-att, checking permissions")
        att_backup_uid = fn.stat(fn.home + "/.config-att").st_uid
        if att_backup_uid == 0:
            fn.debug_print("Fixing .config-att permissions (currently root-owned)")
            fn.debug_print(f"  chown -R {fn.sudo_username} {fn.home}/.config-att")
            fn.permissions(fn.home + "/.config-att")
            s = fn.stat(fn.home + "/.config-att")
            fn.debug_print(f"  result: uid={s.st_uid} gid={s.st_gid} mode={oct(s.st_mode)[-3:]}")
        else:
            fn.debug_print(".config-att permissions are correct (user-owned)")
    else:
        fn.debug_print(f"{fn.home}/.config-att not found, skipping")

    if autostart_uid == 0:
        fn.debug_print("Fixing autostart permissions (currently root-owned)")
        fn.debug_print(f"  chown -R {fn.sudo_username} {fn.home}/.config/autostart")
        fn.permissions(fn.home + "/.config/autostart")
        s = fn.stat(fn.home + "/.config/autostart")
        fn.debug_print(f"  result: uid={s.st_uid} gid={s.st_gid} mode={oct(s.st_mode)[-3:]}")
    else:
        fn.debug_print("autostart permissions are correct (user-owned)")

    if att_uid == 0:
        fn.debug_print("Fixing archlinux-tweak-tool permissions (currently root-owned)")
        fn.debug_print(f"  chown -R {fn.sudo_username} {fn.home}/.config/archlinux-tweak-tool")
        fn.permissions(fn.home + "/.config/archlinux-tweak-tool")
        s = fn.stat(fn.home + "/.config/archlinux-tweak-tool")
        fn.debug_print(f"  result: uid={s.st_uid} gid={s.st_gid} mode={oct(s.st_mode)[-3:]}")
    else:
        fn.debug_print("archlinux-tweak-tool permissions are correct (user-owned)")

    fn.debug_print("=" * 75)
    fn.debug_print("fix_permissions() END")
    fn.debug_print("=" * 75)

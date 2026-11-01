# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
from gi.repository import GLib
from att_i18n import _


def setup_sddm_config(self, sddm):
    fn.log_subsection("Setting up SDDM configuration")
    fn.debug_print("setup_sddm_config() START")
    fn.debug_print("=" * 75)

    if fn.path.isfile(fn.sddm_default_d2):
        fn.debug_print(f"Found SDDM config: {fn.sddm_default_d2}")
        session_exists = sddm.check_sddmk_session("Session=")
        fn.debug_print(f"Session= exists: {session_exists}")
        if session_exists is False:
            fn.debug_print("Inserting #Session= line")
            sddm.insert_session("#Session=")
            fn.debug_print("✓ #Session= inserted")
        else:
            fn.debug_print("Session= already configured, skipping")
    else:
        fn.debug_print(f"SDDM config not found: {fn.sddm_default_d2}")

    if fn.path.isfile(fn.sddm_default_d2):
        fn.debug_print(f"Checking User= in {fn.sddm_default_d2}")
        user_exists = sddm.check_sddmk_user("User=")
        fn.debug_print(f"User= exists: {user_exists}")
        if user_exists is False:
            fn.debug_print("Inserting #User= line")
            sddm.insert_user("#User=")
            fn.debug_print("✓ #User= inserted")
        else:
            fn.debug_print("User= already configured, skipping")
    else:
        fn.debug_print(f"SDDM config not found: {fn.sddm_default_d2}")

    if fn.path.exists("/usr/bin/sddm"):
        fn.debug_print("SDDM binary found at /usr/bin/sddm")
        config_complete = sddm.check_sddmk_complete()
        fn.debug_print(f"SDDM config complete: {config_complete}")
        if config_complete:
            fn.debug_print("SDDM configuration is complete, no changes needed")
        else:
            fn.debug_print("SDDM configuration incomplete, applying defaults")
            fn.debug_print("Creating SDDM directory")
            fn.create_sddm_k_dir()
            fn.debug_print(f"Copying {fn.sddm_default_d1_kiro} → {fn.sddm_default_d1}")
            fn.log_info_concise(f"  From: {fn.sddm_default_d1_kiro}")
            fn.log_info_concise(f"  To:   {fn.sddm_default_d1}")
            fn.shutil.copy(fn.sddm_default_d1_kiro, fn.sddm_default_d1)
            fn.debug_print("✓ SDDM KDE settings copied")
            fn.debug_print(f"Copying {fn.sddm_default_d2_kiro} → {fn.sddm_default_d2}")
            fn.log_info_concise(f"  From: {fn.sddm_default_d2_kiro}")
            fn.log_info_concise(f"  To:   {fn.sddm_default_d2}")
            fn.shutil.copy(fn.sddm_default_d2_kiro, fn.sddm_default_d2)
            sddm.set_default_theme()
            fn.debug_print("✓ SDDM config copied")
            fn.debug_print("Showing user notification")
            fn.debug_print("We changed your sddm configuration files so that ATT could start")
            fn.debug_print("Backups are at /etc/sddm.conf-bak and /etc/kde_settings.conf-bak")
            GLib.idle_add(
                fn.show_in_app_notification,
                self,
                _("We had to change your sddm configuration files"),
            )
            fn.debug_print("✓ User notified about SDDM changes")
    else:
        fn.debug_print("SDDM binary not found at /usr/bin/sddm, skipping configuration")

    fn.debug_print("=" * 75)
    fn.debug_print("setup_sddm_config() END")
    fn.debug_print("=" * 75)

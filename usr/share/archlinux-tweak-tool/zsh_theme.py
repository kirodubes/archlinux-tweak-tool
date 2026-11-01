# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
from att_i18n import _


def get_themes(combo):
    """get themes"""
    if fn.check_package_installed("oh-my-zsh-git"):
        try:
            lists = list(fn.listdir("/usr/share/oh-my-zsh/themes"))
            lists_sorted = sorted(lists)
            with open(fn.zsh_config, "r", encoding="utf-8", errors="ignore") as f:
                theme_list = f.readlines()
                f.close()
            pos = fn.get_position(theme_list, "ZSH_THEME=")
            if "ZSH_THEME=" not in theme_list[pos]:
                name = "random"
            else:
                name = theme_list[pos].split("=")[1].strip().strip('"')

            # Build theme list starting with "random"
            theme_items = ["random"]
            active = 0
            for x in range(len(lists_sorted)):
                theme_name = lists_sorted[x].split(".")[0].strip()
                theme_items.append(theme_name)
                if name in lists_sorted[x].replace(".zsh-theme", ""):
                    active = x + 1  # remember; arrays start at ZERO

            # Create StringList and populate dropdown
            string_list = fn.Gtk.StringList()
            string_list.splice(0, 0, theme_items)
            combo.set_model(string_list)
            combo.set_selected(active)
        except OSError:
            fn.debug_print(
                "ATT was unable to locate ~/.zshrc - a working ~/.zshrc has been placed in your home directory"
            )
            fn.debug_print("You may need to reload ATT to set the options in the zsh tab")
        except Exception as error:
            fn.log_error(str(error))


def set_config(self, theme):
    """set configuration"""
    try:
        with open(fn.zsh_config, "r", encoding="utf-8") as f:
            theme_list = f.readlines()
            f.close()

        pos = fn.get_position(theme_list, "ZSH_THEME=")

        theme_list[pos] = 'ZSH_THEME="' + theme + '"\n'

        with open(fn.zsh_config, "w", encoding="utf-8") as f:
            f.writelines(theme_list)
            f.close()

        fn.show_in_app_notification(self, _("Settings Saved Successfully"))

    except Exception as error:
        fn.log_error(str(error))
        fn.messagebox(self, _("Error!!"), _("Something went wrong setting this theme."))

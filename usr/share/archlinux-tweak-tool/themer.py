# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
# pylint:disable=C0301,R1705

import functions as fn
from att_i18n import _


def get_list(file_path):
    """Read all lines from a file and return them as a list."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        f.close()
    return lines


def get_value(lists, types):
    """Extract the value for a given config key from a line list."""
    try:
        pos = fn.get_position(lists, types)
        color = lists[pos].split("=")[-1].strip()

        return color
    except Exception as error:
        fn.log_error(str(error))


def move_file(self, state):
    """Swap the i3 config between polybar and bar variants."""
    if state:
        if fn.os.path.isfile(fn.home + "/.config/i3/config-polybar"):
            fn.subprocess.run(
                [
                    "mv",
                    fn.home + "/.config/i3/config",
                    fn.home + "/.config/i3/config-bar",
                ],
                check=True,
            )
            fn.subprocess.run(
                [
                    "mv",
                    fn.home + "/.config/i3/config-polybar",
                    fn.home + "/.config/i3/config",
                ],
                check=True,
            )
        else:
            fn.messagebox(
                self,
                _("OOPS!"),
                _(
                    "you dont seem to have <b>{name}</b> file in your <i>{path}</i> directory. "
                    "So we can not enable this feature."
                ).format(name="config-polybar", path="~/.config/i3"),
            )
            self.poly.set_active(False)
    else:
        fn.subprocess.run(
            [
                "mv",
                fn.home + "/.config/i3/config",
                fn.home + "/.config/i3/config-polybar",
            ],
            check=True,
        )
        fn.subprocess.run(
            ["mv", fn.home + "/.config/i3/config-bar", fn.home + "/.config/i3/config"],
            check=True,
        )


def toggle_polybar(self, lines, state):
    """Toggle polybar"""
    if state:
        if not check_polybar(lines):
            move_file(self, True)
    else:
        if check_polybar(lines):
            move_file(self, False)


def check_polybar(lines):
    """Return True if polybar is enabled (uncommented) in the i3 config."""
    try:
        pos = fn.get_position(lines, "~/.config/polybar/launch.sh")
        if "#" in lines[pos]:
            return False
        else:
            return True
    except Exception as error:
        fn.log_error(str(error))
        return False


# =================================================================
# =                  I3WM
# =================================================================


def get_i3_themes(combo, lines):
    """Populate combo with available i3 theme names and select the active one."""
    try:
        menu = [x for x in fn.os.listdir(fn.home + "/.config/i3") if ".theme" in x]
        sorted_menu = sorted(menu)
        theme_names = [x.replace(".theme", "") for x in sorted_menu]

        current_theme = fn.get_position(lines, "Theme name :")
        theme_name = lines[current_theme].split(":")[1].strip().lower().replace(" ", "-")

        active = 0
        for i, name in enumerate(theme_names):
            if theme_name in name:
                active = i

        combo.get_model().splice(0, combo.get_model().get_n_items(), theme_names)
        combo.set_selected(active)
    except Exception as error:
        fn.log_error(f"Failed to load i3 themes: {error}")


def set_i3_themes(lines, theme):
    """Write the selected i3 WM color block into the i3 config."""
    try:
        pos1 = fn.get_position(lines, "##START THEMING WM")
        pos2 = fn.get_position(lines, "##STOP THEMING WM")
        name = theme.lower().replace(" ", "-")
        with open(fn.home + "/.config/i3/" + name + ".theme", "r", encoding="utf-8") as f:
            theme_lines = f.readlines()
            f.close()
        pos3 = fn.get_position(theme_lines, "##START THEMING WM")
        pos4 = fn.get_position(theme_lines, "##STOP THEMING WM")
        lines[pos1 : pos2 + 1] = theme_lines[pos3 : pos4 + 1]
        with open(fn.i3wm_config, "w", encoding="utf-8") as f:
            f.writelines(lines)
            f.close()
    except Exception as error:
        fn.log_error(str(error))


def set_i3_themes_bar(lines, theme):
    """Write the selected i3 bar color block into the i3 config."""
    try:
        pos1 = fn.get_position(lines, "##START THEMING BAR")
        pos2 = fn.get_position(lines, "##STOP THEMING BAR")
        name = theme.lower().replace(" ", "-")
        with open(fn.home + "/.config/i3/" + name + ".theme", "r", encoding="utf-8") as f:
            theme_lines = f.readlines()
            f.close()

        pos3 = fn.get_position(theme_lines, "##START THEMING BAR")
        pos4 = fn.get_position(theme_lines, "##STOP THEMING BAR")

        lines[pos1 : pos2 + 1] = theme_lines[pos3 : pos4 + 1]

        with open(fn.i3wm_config, "w", encoding="utf-8") as f:
            f.writelines(lines)
            f.close()
    except Exception as error:
        fn.log_error(str(error))


# =================================================================
# =                  AWESOME
# =================================================================


def get_awesome_themes(lines):
    """Return a sorted list of Awesome WM theme names from the config."""
    theme_pos = fn.get_position(lines, "local themes = {")
    end_theme_pos = fn.get_position(lines, "local chosen_theme")

    coms = [x for x in lines[theme_pos:end_theme_pos] if '",' in x]
    theme_list = []
    for x in coms:
        theme_list.append(x.split('"')[1].strip())
    return_list = sorted(theme_list)
    return return_list


def set_awesome_theme(lines, val):
    """Write the selected Awesome theme index to the config."""
    theme_pos = fn.get_position(lines, "local chosen_theme")
    lst = lines[theme_pos].split("=")[1].replace("themes[", "").replace("]", "").strip()
    lines[theme_pos] = lines[theme_pos].replace("themes[" + lst + "]", "themes[" + val + "]")
    with open(fn.awesome_config, "w", encoding="utf-8") as f:
        f.writelines(lines)
        f.close()


# =================================================================
# =                  QTILE
# =================================================================


def get_qtile_themes(combo, lines):
    """Populate combo with qtile theme names and select the active one."""
    if fn.check_package_installed("kiro-qtile"):
        try:
            menu = [x for x in fn.os.listdir(fn.home + "/.config/qtile/themes/") if ".theme" in x]
            sorted_menu = sorted(menu)
            theme_names = [x.replace(".theme", "") for x in sorted_menu]

            current_theme = fn.get_position(lines, "Theme name :")
            theme_name = lines[current_theme].split(":")[1].strip().lower().replace(" ", "-")
            active = 0
            for i, name in enumerate(theme_names):
                if theme_name in name:
                    active = i

            combo.get_model().splice(0, combo.get_model().get_n_items(), theme_names)
            combo.set_selected(active)
        except Exception as error:
            fn.log_error(f"Failed to load qtile themes: {error}")


def set_qtile_themes(lines, theme):
    """Write the selected qtile color block into the qtile config."""
    if fn.check_package_installed("kiro-qtile"):
        try:
            pos1 = fn.get_position(lines, "# COLORS FOR THE BAR")
            pos2 = fn.get_position(lines, "colors = init_colors()")
            name = theme.lower().replace(" ", "-")
            with open(
                fn.home + "/.config/qtile/themes/" + name + ".theme",
                "r",
                encoding="utf-8",
            ) as f:
                theme_lines = f.readlines()
                f.close()
            pos3 = fn.get_position(theme_lines, "# COLORS FOR THE BAR")
            pos4 = fn.get_position(theme_lines, "colors = init_colors()")

            lines[pos1 : pos2 + 1] = theme_lines[pos3 : pos4 + 1]

            with open(fn.qtile_config, "w", encoding="utf-8") as f:
                f.writelines(lines)
                f.close()
        except Exception as error:
            fn.log_error(str(error))


# =================================================================
# =                  LEFTWM
# =================================================================


def get_leftwm_themes(combo, lines):
    """Populate combo with leftwm theme names and select the active one."""
    if fn.check_package_installed("kiro-leftwm"):
        try:
            menu = [x for x in fn.os.listdir(fn.home + "/.config/leftwm/themes/") if ".theme" in x]
            sorted_menu = sorted(menu)
            theme_names = [x.replace(".theme", "") for x in sorted_menu]

            current_theme = fn.get_position(lines, "Theme name :")
            theme_name = lines[current_theme].split(":")[1].strip().lower().replace(" ", "-")
            active = 0
            for i, name in enumerate(theme_names):
                if theme_name in name:
                    active = i

            combo.get_model().splice(0, combo.get_model().get_n_items(), theme_names)
            combo.set_selected(active)
        except Exception as error:
            fn.log_error(f"Failed to load leftwm themes: {error}")


def set_leftwm_themes(theme):
    """Update, install, and apply the given leftwm theme."""
    fn.subprocess.run(
        ["bash", "-c", "su - " + fn.sudo_username + ' -c "leftwm-theme update' + '"'],
        check=True,
        stdout=fn.subprocess.PIPE,
    )
    # install
    fn.subprocess.run(
        [
            "bash",
            "-c",
            "su - " + fn.sudo_username + ' -c "leftwm-theme install ' + theme + '"',
        ],
        check=True,
        stdout=fn.subprocess.PIPE,
    )
    # apply
    fn.subprocess.run(
        [
            "bash",
            "-c",
            "su - " + fn.sudo_username + ' -c "leftwm-theme apply ' + theme + '"',
        ],
        check=True,
        stdout=fn.subprocess.PIPE,
    )


def remove_leftwm_themes(theme):
    """Apply the candy fallback theme and remove the given leftwm theme."""
    fn.subprocess.run(
        ["bash", "-c", "su - " + fn.sudo_username + ' -c "leftwm-theme apply candy"'],
        check=True,
        stdout=fn.subprocess.PIPE,
    )
    # remove
    if not theme == "candy":
        fn.subprocess.run(
            [
                "bash",
                "-c",
                "su - " + fn.sudo_username + ' -c "leftwm-theme uninstall ' + theme + ' --noconfirm"',
            ],
            check=True,
            stdout=fn.subprocess.PIPE,
        )


def reset_leftwm_themes(theme):
    """Apply candy, remove the given theme, then reinstall and reapply it."""
    fn.subprocess.run(
        ["bash", "-c", "su - " + fn.sudo_username + ' -c "leftwm-theme apply candy"'],
        check=True,
        stdout=fn.subprocess.PIPE,
    )

    # remove
    if not theme == "candy":
        fn.subprocess.run(
            [
                "bash",
                "-c",
                "su - " + fn.sudo_username + ' -c "leftwm-theme uninstall ' + theme + ' --noconfirm"',
            ],
            check=True,
            stdout=fn.subprocess.PIPE,
        )

    # update
    fn.subprocess.run(
        ["bash", "-c", "su - " + fn.sudo_username + ' -c "leftwm-theme update' + '"'],
        check=True,
        stdout=fn.subprocess.PIPE,
    )

    # install
    fn.subprocess.run(
        [
            "bash",
            "-c",
            "su - " + fn.sudo_username + ' -c "leftwm-theme install ' + theme + '"',
        ],
        check=True,
        stdout=fn.subprocess.PIPE,
    )
    # apply
    fn.subprocess.run(
        [
            "bash",
            "-c",
            "su - " + fn.sudo_username + ' -c "leftwm-theme apply ' + theme + '"',
        ],
        check=True,
        stdout=fn.subprocess.PIPE,
    )


# ── Themer callbacks ─────────────────────────────────────────────────


def on_polybar_toggle(self, _widget, _pspec=None):
    """Toggle the polybar integration in the i3 config."""
    fn.log_subsection("Toggle Polybar")
    try:
        if self.poly.get_active():
            fn.debug_print("Enabling polybar")
            toggle_polybar(self, get_list(fn.i3wm_config), True)
            fn.log_success("Polybar enabled")
        else:
            fn.debug_print("Disabling polybar")
            toggle_polybar(self, get_list(fn.i3wm_config), False)
            if fn.check_if_process_is_running("polybar"):
                fn.debug_print("Stopping polybar process")
                fn.subprocess.run(["killall", "-q", "polybar"], check=True, shell=False)
            fn.log_success("Polybar disabled")
    except Exception as error:
        fn.log_error(f"Failed to toggle polybar: {error}")
        fn.messagebox(self, _("Error"), _("Failed to toggle polybar: {error}").format(error=error))


def awesome_apply_clicked(self, _widget):
    """Apply the selected Awesome WM theme to the config."""
    fn.log_subsection("Apply Awesome Theme")
    try:
        if not fn.path.isfile(fn.awesome_config + "-bak"):
            fn.debug_print(f"Creating backup: {fn.awesome_config}-bak")
            fn.log_info_concise(f"  From: {fn.awesome_config}")
            fn.log_info_concise(f"  To:   {fn.awesome_config}-bak")
            fn.shutil.copy(fn.awesome_config, fn.awesome_config + "-bak")
            fn.permissions(fn.awesome_config + "-bak")

        selected = self.awesome_combo.get_selected()
        if self.awesome_combo.get_selected_item() is None:
            return
        nid = str(selected + 1)
        fn.debug_print(f"Applying awesome theme: {nid}")
        set_awesome_theme(get_list(fn.awesome_config), nid)
        fn.log_success("Awesome theme applied successfully")
        fn.show_in_app_notification(self, _("Theme set successfully"))
    except Exception as error:
        fn.log_error(f"Failed to apply awesome theme: {error}")
        fn.messagebox(self, _("Error"), _("Failed to apply theme: {error}").format(error=error))


def awesome_reset_clicked(self, _widget):
    """Restore the Awesome config from backup and refresh the combo."""
    fn.log_subsection("Reset Awesome Theme")
    try:
        if fn.path.isfile(fn.awesome_config + "-bak"):
            fn.debug_print("Restoring awesome config from backup")
            fn.log_info_concise(f"  From: {fn.awesome_config}-bak")
            fn.log_info_concise(f"  To:   {fn.awesome_config}")
            fn.shutil.copy(fn.awesome_config + "-bak", fn.awesome_config)
            fn.permissions(fn.awesome_config)
            fn.log_success("Awesome configuration reset")
            fn.show_in_app_notification(self, _("Config reset successfully"))

            awesome_list = get_list(fn.awesome_config)
            awesome_lines = get_awesome_themes(awesome_list)

            aw_model = self.awesome_combo.get_model()
            aw_model.splice(0, aw_model.get_n_items(), awesome_lines)
            val = int(get_value(awesome_list, "local chosen_theme =").replace("themes[", "").replace("]", ""))
            self.awesome_combo.set_selected(val - 1)
        else:
            fn.log_warn("Backup configuration not found")
    except Exception as error:
        fn.log_error(f"Failed to reset awesome theme: {error}")
        fn.messagebox(self, _("Error"), _("Failed to reset theme: {error}").format(error=error))


def i3wm_apply_clicked(self, _widget):
    """Back up and apply the selected i3 WM theme."""
    fn.log_subsection("Apply I3WM Theme")
    try:
        if fn.path.isfile(fn.i3wm_config):
            fn.debug_print(f"Creating backup: {fn.i3wm_config}-bak")
            fn.log_info_concise(f"  From: {fn.i3wm_config}")
            fn.log_info_concise(f"  To:   {fn.i3wm_config}-bak")
            fn.shutil.copy(fn.i3wm_config, fn.i3wm_config + "-bak")
            fn.permissions(fn.i3wm_config + "-bak")

        fn.debug_print(f"Applying i3wm theme: {fn.get_combo_text(self.i3_combo)}")
        set_i3_themes(get_list(fn.i3wm_config), fn.get_combo_text(self.i3_combo))
        if not check_polybar(get_list(fn.i3wm_config)):
            fn.debug_print("Updating polybar configuration")
            set_i3_themes_bar(get_list(fn.i3wm_config), fn.get_combo_text(self.i3_combo))
        fn.log_success("I3WM theme applied successfully")
        fn.show_in_app_notification(self, _("Theme applied successfully"))
    except Exception as error:
        fn.log_error(f"Failed to apply i3wm theme: {error}")
        fn.messagebox(self, _("Error"), _("Failed to apply theme: {error}").format(error=error))


def i3wm_reset_clicked(self, _widget):
    """Restore the i3 config from backup and refresh the theme combo."""
    fn.log_subsection("Reset I3WM Theme")
    try:
        if fn.path.isfile(fn.i3wm_config + "-bak"):
            fn.debug_print("Restoring i3wm config from backup")
            fn.log_info_concise(f"  From: {fn.i3wm_config}-bak")
            fn.log_info_concise(f"  To:   {fn.i3wm_config}")
            fn.shutil.copy(fn.i3wm_config + "-bak", fn.i3wm_config)
            fn.permissions(fn.i3wm_config)
            fn.log_success("I3WM configuration reset")
            fn.show_in_app_notification(self, _("Config reset successfully"))

            i3_list = get_list(fn.i3wm_config)

            get_i3_themes(self.i3_combo, i3_list)
        else:
            fn.log_warn("Backup configuration not found")
    except Exception as error:
        fn.log_error(f"Failed to reset i3wm theme: {error}")
        fn.messagebox(self, _("Error"), _("Failed to reset theme: {error}").format(error=error))


def qtile_apply_clicked(self, _widget):
    """Back up and apply the selected qtile theme."""
    fn.log_subsection("Apply Qtile Theme")
    try:
        if fn.path.isfile(fn.qtile_config):
            fn.debug_print(f"Creating backup: {fn.qtile_config}-bak")
            fn.log_info_concise(f"  From: {fn.qtile_config}")
            fn.log_info_concise(f"  To:   {fn.qtile_config}-bak")
            fn.shutil.copy(fn.qtile_config, fn.qtile_config + "-bak")
            fn.permissions(fn.qtile_config + "-bak")

        fn.debug_print(f"Applying qtile theme: {fn.get_combo_text(self.qtile_combo)}")
        set_qtile_themes(get_list(fn.qtile_config), fn.get_combo_text(self.qtile_combo))
        fn.log_success("Qtile theme applied successfully")
        fn.show_in_app_notification(self, _("Theme applied successfully"))
    except Exception as error:
        fn.log_error(f"Failed to apply qtile theme: {error}")
        fn.messagebox(self, _("Error"), _("Failed to apply theme: {error}").format(error=error))


def qtile_reset_clicked(self, _widget):
    """Restore the qtile config from backup and refresh the theme combo."""
    fn.log_subsection("Reset Qtile Theme")
    try:
        if fn.path.isfile(fn.qtile_config + "-bak"):
            fn.debug_print("Restoring qtile config from backup")
            fn.log_info_concise(f"  From: {fn.qtile_config}-bak")
            fn.log_info_concise(f"  To:   {fn.qtile_config}")
            fn.shutil.copy(fn.qtile_config + "-bak", fn.qtile_config)
            fn.permissions(fn.qtile_config)
            fn.log_success("Qtile configuration reset")
            fn.show_in_app_notification(self, _("Config reset successfully"))

            qtile_list = get_list(fn.qtile_config)

            get_qtile_themes(self.qtile_combo, qtile_list)
        else:
            fn.log_warn("Backup configuration not found")
    except Exception as error:
        fn.log_error(f"Failed to reset qtile theme: {error}")
        fn.messagebox(self, _("Error"), _("Failed to reset theme: {error}").format(error=error))


def leftwm_apply_clicked(self, _widget):
    """Install and apply the selected leftwm theme."""
    fn.log_subsection("Apply Leftwm Theme")
    try:
        theme_name = fn.get_combo_text(self.leftwm_combo)
        fn.debug_print(f"Applying leftwm theme: {theme_name}")
        set_leftwm_themes(theme_name)
        fn.log_success(f"Leftwm theme {theme_name} applied successfully")
        fn.show_in_app_notification(
            self,
            _("Theme {name} applied successfully").format(name=theme_name),
        )
        self.status_leftwm.set_markup(_("<b>Theme is installed and applied</b>"))
    except Exception as error:
        fn.log_error(f"Failed to apply leftwm theme: {error}")
        fn.messagebox(self, _("Error"), _("Failed to apply theme: {error}").format(error=error))


def leftwm_reset_clicked(self, _widget):
    """Reset the selected leftwm theme to its defaults."""
    fn.log_subsection("Reset Leftwm Theme")
    try:
        theme_name = fn.get_combo_text(self.leftwm_combo)
        fn.debug_print("Reverting to candy as fallback")
        reset_leftwm_themes(theme_name)
        fn.debug_print(f"Resetting theme: {theme_name}")
        fn.log_success(f"Leftwm theme {theme_name} reset successfully")
        fn.show_in_app_notification(self, _("Theme {name} reset successfully").format(name=theme_name))
        self.status_leftwm.set_markup(_("<b>Theme is installed and applied</b>"))
    except Exception as error:
        fn.log_error(f"Failed to reset leftwm theme: {error}")
        fn.messagebox(self, _("Error"), _("Failed to reset theme: {error}").format(error=error))


def leftwm_remove_clicked(self, _widget):
    """Remove the selected leftwm theme and revert to candy."""
    fn.log_subsection("Remove Leftwm Theme")
    try:
        theme_name = fn.get_combo_text(self.leftwm_combo)
        fn.debug_print("Reverting to candy as fallback")
        remove_leftwm_themes(theme_name)
        fn.debug_print(f"Removing theme: {theme_name}")
        fn.log_success(f"Leftwm theme {theme_name} removed successfully")
        fn.show_in_app_notification(
            self,
            _("Theme {name} removed successfully").format(name=theme_name),
        )
    except Exception as error:
        fn.log_error(f"Failed to remove leftwm theme: {error}")
        fn.messagebox(self, _("Error"), _("Failed to remove theme: {error}").format(error=error))


def on_leftwm_combo_changed(self, _widget, _pspec=None):
    """Update the status label when the leftwm theme selection changes."""
    theme = fn.get_combo_text(self.leftwm_combo)
    fn.log_info(f"LeftWM theme selected: {theme}")
    link_theme = fn.path.basename(fn.os.readlink(fn.leftwm_config_theme_current))
    if fn.path_check(fn.leftwm_config_theme + theme):
        self.status_leftwm.set_markup(_("<b>Theme is installed</b>"))
    else:
        self.status_leftwm.set_markup(_("<b>Theme is NOT installed</b>"))

    if fn.path_check(fn.leftwm_config_theme + theme) and link_theme == theme:
        self.status_leftwm.set_markup(_("<b>Theme is installed and applied</b>"))

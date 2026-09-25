# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
import re
import json

# ====================================================================
#                       Fastfetch
# ====================================================================


def get_fastfetch():
    if not fn.path.isfile(fn.fastfetch_config):
        return {}
    try:
        with open(fn.fastfetch_config, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(r"^\s*//.*$", "", content, flags=re.MULTILINE)
        content = re.sub(r",(\s*[}\]])", r"\1", content)
        return json.loads(content)
    except Exception as e:
        fn.debug_print(f"Failed to parse fastfetch config: {e}")
        return {}


def get_position(lists, value):
    data = []
    suffixes = [" | lolcat", "\n", " | lolcat\n"]
    prefix = "#"

    for string in lists:
        for item in suffixes:
            if string in (value + item, prefix + value + item, value, prefix + value):
                data.append(string)

    if data:
        position = lists.index(data[0])
        return position
    else:
        return -1


def write_configs(util_enabled, lolcat_enabled):
    config = fn.get_config_file()
    if not config:
        return

    with open(config, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_state = "#fastfetch"
    if util_enabled:
        new_state = "fastfetch | lolcat" if lolcat_enabled else "fastfetch"

    reporting_section_start = -1
    for i, line in enumerate(lines):
        if "# reporting tools" in line.lower():
            reporting_section_start = i
            break

    if reporting_section_start == -1:
        if not util_enabled:
            return
        lines.append("\n# reporting tools\n")
        lines.append(new_state + "\n")
        with open(config, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return

    fastfetch_line = -1
    for i in range(reporting_section_start, len(lines)):
        if lines[i].strip().startswith(("fastfetch", "#fastfetch")):
            fastfetch_line = i
            break

    if fastfetch_line == -1:
        if not util_enabled:
            return
        lines.insert(reporting_section_start + 1, new_state + "\n")
    else:
        if lines[fastfetch_line].strip() != new_state:
            lines[fastfetch_line] = new_state + "\n"

    with open(config, "w", encoding="utf-8") as f:
        f.writelines(lines)


def get_term_rc():
    config_file = ""
    pos = -1
    try:
        config_file = fn.get_config_file()
    except Exception:
        config_file = ""
    if config_file != "":
        with open(config_file, "r", encoding="utf-8") as myfile:
            lines = myfile.readlines()
            pos = get_position(lines, "fastfetch")

    if pos >= 0 and lines[pos].startswith("#"):
        return False
    elif pos >= 0:
        return True
    else:
        return False


def apply_config(self):
    if fn.path.isfile(fn.fastfetch_config):
        with open(fn.fastfetch_config, "r", encoding="utf-8") as f:
            lines = f.readlines()

        key_to_checkbox = {
            '"os"': self.os,
            '"host"': self.host,
            '"kernel"': self.kernel,
            '"uptime"': self.uptime,
            '"packages"': self.packages,
            '"shell"': self.shell,
            '"display"': self.display,
            '"de"': self.de,
            '"wm"': self.wm,
            '"wmtheme"': self.wmtheme,
            '"theme"': self.themes,
            '"icons"': self.icons,
            '"font"': self.font,
            '"cursor"': self.cursor,
            '"terminal"': self.term,
            '"terminalfont"': self.termfont,
            '"cpu"': self.cpu,
            '"gpu"': self.gpu,
            '"memory"': self.mem,
            '"swap"': self.swap,
            '"disk"': self.disks,
            '"localIP"': self.l_ip,
            '"publicip"': self.p_ip,
            '"battery"': self.batt,
            '"poweradapter"': self.pwr,
            '"locale"': self.local,
            '"title"': self.title,
            '"underline"': self.title,
            '"colors"': self.cblocks,
        }

        for i, line in enumerate(lines):
            for key, checkbox in key_to_checkbox.items():
                if key.lower() in line.lower():
                    if checkbox.get_active() and line.strip().startswith("//"):
                        lines[i] = line.replace("//", "", 1)
                    elif not checkbox.get_active() and not line.strip().startswith("//"):
                        lines[i] = "//" + line

        with open(fn.fastfetch_config, "w", encoding="utf-8") as f:
            f.writelines(lines)

        fn.log_success("Fastfetch settings saved")
        fn.show_in_app_notification(self, "fastfetch settings saved successfully")


def get_checkboxes(self):
    config = get_fastfetch()
    modules = [m.lower() for m in config.get("modules", []) if isinstance(m, str)]

    self.title.set_active("title" in modules)
    self.os.set_active("os" in modules)
    self.host.set_active("host" in modules)
    self.kernel.set_active("kernel" in modules)
    self.uptime.set_active("uptime" in modules)
    self.packages.set_active("packages" in modules)
    self.shell.set_active("shell" in modules)
    self.display.set_active("display" in modules)
    self.de.set_active("de" in modules)
    self.wm.set_active("wm" in modules)
    self.wmtheme.set_active("wmtheme" in modules)
    self.themes.set_active("theme" in modules)
    self.icons.set_active("icons" in modules)
    self.font.set_active("font" in modules)
    self.cursor.set_active("cursor" in modules)
    self.term.set_active("terminal" in modules)
    self.termfont.set_active("terminalfont" in modules)
    self.cpu.set_active("cpu" in modules)
    self.gpu.set_active("gpu" in modules)
    self.mem.set_active("memory" in modules)
    self.swap.set_active("swap" in modules)
    self.disks.set_active("disk" in modules)
    self.l_ip.set_active("localip" in modules)
    self.p_ip.set_active("publicip" in modules)
    self.batt.set_active("battery" in modules)
    self.pwr.set_active("poweradapter" in modules)
    self.local.set_active("locale" in modules)
    self.cblocks.set_active("colors" in modules)


_PRESET_ALL = {
    "title": True,
    "os": True,
    "host": True,
    "kernel": True,
    "uptime": True,
    "packages": True,
    "shell": True,
    "display": True,
    "de": True,
    "wm": True,
    "wmtheme": True,
    "themes": True,
    "icons": True,
    "font": True,
    "cursor": True,
    "term": True,
    "termfont": True,
    "cpu": True,
    "gpu": True,
    "mem": True,
    "swap": True,
    "disks": True,
    "l_ip": True,
    "p_ip": False,
    "batt": True,
    "pwr": True,
    "local": True,
    "cblocks": True,
}

_PRESET_NORMAL = {
    "title": True,
    "os": True,
    "host": True,
    "kernel": True,
    "uptime": True,
    "packages": True,
    "shell": True,
    "display": True,
    "de": True,
    "wm": True,
    "wmtheme": True,
    "themes": True,
    "icons": True,
    "font": True,
    "cursor": True,
    "term": True,
    "termfont": True,
    "cpu": True,
    "gpu": True,
    "mem": True,
    "swap": True,
    "disks": True,
    "l_ip": False,
    "p_ip": False,
    "batt": True,
    "pwr": True,
    "local": False,
    "cblocks": False,
}

_PRESET_SMALL = {
    "title": True,
    "os": False,
    "host": False,
    "kernel": True,
    "uptime": True,
    "packages": True,
    "shell": True,
    "display": False,
    "de": True,
    "wm": True,
    "wmtheme": True,
    "themes": True,
    "icons": True,
    "font": True,
    "cursor": True,
    "term": True,
    "termfont": False,
    "cpu": True,
    "gpu": True,
    "mem": True,
    "swap": True,
    "disks": False,
    "l_ip": False,
    "p_ip": False,
    "batt": True,
    "pwr": True,
    "local": False,
    "cblocks": False,
}

_PRESET_NONE = {attr: False for attr in _PRESET_ALL}


def _apply_preset(self, states):
    for attr, state in states.items():
        getattr(self, attr).set_active(state)


def set_checkboxes_normal(self):
    _apply_preset(self, _PRESET_NORMAL)
    _ensure_separator_uncommented()


def set_checkboxes_small(self):
    _apply_preset(self, _PRESET_SMALL)
    _ensure_separator_uncommented()


def set_checkboxes_all(self):
    _apply_preset(self, _PRESET_ALL)
    _ensure_separator_uncommented()


def set_checkboxes_none(self):
    _apply_preset(self, _PRESET_NONE)
    _ensure_separator_commented()


def _ensure_separator_uncommented():
    if fn.path.isfile(fn.fastfetch_config):
        with open(fn.fastfetch_config, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if '"separator"' in line and line.strip().startswith("//"):
                lines[i] = line.lstrip("/")

        with open(fn.fastfetch_config, "w", encoding="utf-8") as f:
            f.writelines(lines)


def _ensure_separator_commented():
    if fn.path.isfile(fn.fastfetch_config):
        with open(fn.fastfetch_config, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if '"separator"' in line and not line.strip().startswith("//"):
                lines[i] = "//" + line

        with open(fn.fastfetch_config, "w", encoding="utf-8") as f:
            f.writelines(lines)


# ====================================================================
# FASTFETCH CALLBACKS
# ====================================================================


def set_fastfetch_ui_sensitive(self, state):
    for widget in [
        self.fast_lolcat,
        self.hbox_ff_warning,
        self.hbox_ff_checkboxes,
        self.fastfetch_image,
        self.hbox_ff_presets,
        self.hbox_ff_actions,
        self.btn_remove_fastfetch,
    ]:
        widget.set_sensitive(state)


def on_remove_fast(self, _widget):
    fn.log_subsection("Removing fastfetch")
    fn.show_in_app_notification(self, "Opening terminal to remove fastfetch...")
    result = fn.subprocess.run(["pacman", "-Q", "fastfetch-git"], capture_output=True)
    package = "fastfetch-git" if result.returncode == 0 else "fastfetch"
    process = fn.launch_pacman_remove_in_terminal(package)

    def wait_and_update():
        if process:
            process.wait()
        if not fn.path.exists("/usr/bin/fastfetch"):
            fn.log_success("Fastfetch removed")
            fn.GLib.idle_add(set_fastfetch_ui_sensitive, self, False)
            fn.GLib.idle_add(self.fast_util.set_active, False)

    fn.threading.Thread(target=wait_and_update, daemon=True).start()


def _pick_fastfetch_package():
    if fn.check_chaotic_aur_active() or fn.check_nemesis_repo_active():
        result = fn.subprocess.run(["pacman", "-Si", "fastfetch-git"], capture_output=True)
        if result.returncode == 0:
            fn.log_info("chaotic-AUR or nemesis repo detected — installing fastfetch-git")
            return "fastfetch-git"
    fn.log_info("fastfetch-git not available — installing fastfetch (stable)")
    return "fastfetch"


def on_install_fast(self, _widget):
    fn.log_subsection("Install Fastfetch")
    package = _pick_fastfetch_package()
    fn.show_in_app_notification(self, f"Installing {package}...")
    fn.install_package(self, package)


def on_apply_fast(self, _widget):
    fn.log_subsection("Apply Fastfetch configuration")
    if not self.fast_util.get_active():
        fn.log_info("Fastfetch was not enabled — enabling now")
        self.ff_initializing = True
        self.fast_util.set_active(True)
        self.ff_initializing = False
        write_configs(True, self.fast_lolcat.get_active())
    apply_config(self)
    fn.log_success("Fastfetch configuration applied")


def on_reset_fast_att(self, _widget):
    fn.debug_print("Reset fastfetch to ATT defaults")
    fn.debug_print(f"  Source : {fn.fastfetch_kiro}")
    fn.debug_print(f"  Target : {fn.fastfetch_config}")
    if fn.path.isfile(fn.fastfetch_kiro):
        fn.log_info_concise(f"  From: {fn.fastfetch_kiro}")
        fn.log_info_concise(f"  To:   {fn.fastfetch_config}")
        fn.shutil.copy(fn.fastfetch_kiro, fn.fastfetch_config)
        fn.permissions(fn.fastfetch_config)
        fn.debug_print("  Result : copied and permissions set")
        fn.log_success("Fastfetch ATT defaults applied")
        fn.show_in_app_notification(self, "ATT defaults applied")
        get_checkboxes(self)
    else:
        fn.debug_print("  Result : source file not found - nothing copied")


def on_reset_fast(self, _widget):
    fn.debug_print("Reset fastfetch from backup")
    fn.debug_print(f"  Source : {fn.fastfetch_config}-bak")
    fn.debug_print(f"  Target : {fn.fastfetch_config}")
    if fn.path.isfile(fn.fastfetch_config + "-bak"):
        fn.log_info_concise(f"  From: {fn.fastfetch_config}-bak")
        fn.log_info_concise(f"  To:   {fn.fastfetch_config}")
        fn.shutil.copy(fn.fastfetch_config + "-bak", fn.fastfetch_config)
        fn.permissions(fn.fastfetch_config)
        fn.debug_print("  Result : restored from backup")
        get_checkboxes(self)
        fn.log_success("fastfetch default settings applied")
        fn.show_in_app_notification(self, "Default settings applied")
    else:
        fn.debug_print("  Result : backup file not found - nothing restored")


def on_fast_util_toggled(self, switch, _gparam):
    if getattr(self, "ff_initializing", False):
        return
    util_state = switch.get_active()
    lolcat_state = self.fast_lolcat.get_active()
    label = "enabled" if util_state else "disabled"
    fn.log_subsection(f"Fastfetch {label}")
    fn.debug_print(f"  Config : {fn.get_config_file()}")

    if util_state and not fn.path.exists("/usr/bin/fastfetch"):
        package = _pick_fastfetch_package()
        fn.log_subsection(f"Installing {package}...")
        fn.show_in_app_notification(self, f"Opening terminal to install {package}...")
        process = fn.launch_pacman_install_in_terminal(package)

        def wait_and_enable():
            if process:
                process.communicate()
            if fn.path.exists("/usr/bin/fastfetch"):
                fn.log_success("fastfetch installed")
                if fn.path.isfile(fn.fastfetch_config):
                    if not fn.path.isfile(fn.fastfetch_config + "-bak"):
                        try:
                            fn.shutil.copy(fn.fastfetch_config, fn.fastfetch_config + "-bak")
                            fn.permissions(fn.fastfetch_config + "-bak")
                            fn.debug_print(f"  Backed up: {fn.fastfetch_config}-bak")
                        except Exception as error:
                            fn.log_error(str(error))
                elif fn.path.isfile(fn.fastfetch_kiro):
                    fn.shutil.copy(fn.fastfetch_kiro, fn.fastfetch_config)
                    fn.permissions(fn.fastfetch_config)
                    fn.debug_print(f"  ATT config placed: {fn.fastfetch_config}")
                fn.GLib.idle_add(set_fastfetch_ui_sensitive, self, True)
                fn.GLib.idle_add(write_configs, True, lolcat_state)
                fn.GLib.idle_add(fn.show_in_app_notification, self, "fastfetch installed")
            else:
                fn.log_warn("fastfetch not found after install — snapping switch back")

                def snap_back():
                    self.ff_initializing = True
                    self.fast_util.set_active(False)
                    self.ff_initializing = False
                    fn.log_warn("fastfetch installation failed or was cancelled")
                    fn.show_in_app_notification(self, "fastfetch installation failed or was cancelled")

                fn.GLib.idle_add(snap_back)

        fn.threading.Thread(target=wait_and_enable, daemon=True).start()
        return

    if not util_state:
        self.fast_lolcat.set_active(False)
        lolcat_state = False

    if not fn.get_config_file():
        fn.log_warn("No shell config files found — fastfetch cannot be added to your shell startup")
        fn.show_in_app_notification(self, "No shell config found")
        return
    write_configs(util_state, lolcat_state)
    self.fast_lolcat.set_sensitive(util_state)
    fn.log_success(f"Fastfetch {label} in shell config")
    fn.GLib.idle_add(fn.show_in_app_notification, self, f"Fastfetch {label}")


def on_fast_lolcat_toggled(self, switch, _gparam):
    if getattr(self, "ff_initializing", False):
        return
    lolcat_state = switch.get_active()
    util_state = self.fast_util.get_active()
    label = "enabled" if lolcat_state else "disabled"
    fn.log_subsection(f"Lolcat {label}")
    fn.debug_print(f"  Config : {fn.get_config_file()}")

    if lolcat_state and not fn.path.exists("/usr/bin/lolcat"):
        fn.log_subsection("Installing lolcat...")
        fn.show_in_app_notification(self, "Opening terminal to install lolcat...")
        process = fn.launch_pacman_install_in_terminal("lolcat")

        def wait_and_enable():
            if process:
                process.communicate()
            if fn.path.exists("/usr/bin/lolcat"):
                fn.log_success("lolcat installed")
                if util_state:
                    fn.GLib.idle_add(write_configs, util_state, True)
                fn.GLib.idle_add(fn.show_in_app_notification, self, "lolcat installed")
            else:
                fn.log_warn("lolcat installation failed or was cancelled")
                fn.GLib.idle_add(fn.show_in_app_notification, self, "lolcat installation failed or was cancelled")
                fn.GLib.idle_add(self.fast_lolcat.set_active, False)

        fn.threading.Thread(target=wait_and_enable, daemon=True).start()
        return

    if util_state:
        if not fn.get_config_file():
            fn.log_warn("No shell config files found — fastfetch cannot be added to your shell startup")
            fn.show_in_app_notification(self, "No shell config found")
            return
        write_configs(util_state, lolcat_state)
        fn.log_success(f"Lolcat {label} in shell config")
        fn.GLib.idle_add(fn.show_in_app_notification, self, f"Lolcat {label}")


def on_click_fastfetch_all_selection(self, _widget):
    fn.log_subsection("All Fastfetch switches selected")
    set_checkboxes_all(self)


def on_click_fastfetch_normal_selection(self, _widget):
    fn.log_subsection("Normal Fastfetch selection applied")
    set_checkboxes_normal(self)


def on_click_fastfetch_small_selection(self, _widget):
    fn.log_subsection("Small Fastfetch selection applied")
    set_checkboxes_small(self)


def on_click_fastfetch_none_selection(self, _widget):
    fn.log_subsection("No Fastfetch switches selected")
    set_checkboxes_none(self)


def _refresh_fftt_lbl(self):
    if fn.check_package_installed("fastfetch-tweak-tool"):
        self.fftt_status_lbl.set_markup("fastfetch-tweak-tool is <b>installed</b>")
    else:
        self.fftt_status_lbl.set_markup("fastfetch-tweak-tool is <b>not installed</b>")


def _refresh_fftt_launch_btn(self):
    self.btn_launch_fftt.set_sensitive(fn.check_package_installed("fastfetch-tweak-tool"))


def on_install_fastfetch_tweak_tool_clicked(self, _widget):
    """Install fastfetch-tweak-tool from nemesis repo via terminal."""
    if fn.check_package_installed("fastfetch-tweak-tool"):
        fn.log_info("fastfetch-tweak-tool is already installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "fastfetch-tweak-tool is already installed")
        return
    fn.log_subsection("Installing fastfetch-tweak-tool...")
    process = fn.launch_pacman_install_in_terminal("fastfetch-tweak-tool")
    fn.GLib.idle_add(fn.show_in_app_notification, self, "Opening terminal to install fastfetch-tweak-tool")

    def wait_install():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("fastfetch-tweak-tool installed")
            fn.GLib.idle_add(_refresh_fftt_lbl, self)
            fn.GLib.idle_add(_refresh_fftt_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, "fastfetch-tweak-tool installed")
        except Exception as e:
            fn.log_error(f"Error installing fastfetch-tweak-tool: {e}")

    fn.threading.Thread(target=wait_install, daemon=True).start()


def on_remove_fastfetch_tweak_tool_clicked(self, _widget):
    """Remove fastfetch-tweak-tool via terminal."""
    if not fn.check_package_installed("fastfetch-tweak-tool"):
        fn.log_info("fastfetch-tweak-tool is not installed — nothing to remove")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "fastfetch-tweak-tool is not installed")
        return
    fn.log_subsection("Removing fastfetch-tweak-tool...")
    process = fn.launch_pacman_remove_in_terminal("fastfetch-tweak-tool")
    fn.GLib.idle_add(fn.show_in_app_notification, self, "Opening terminal to remove fastfetch-tweak-tool")

    def wait_remove():
        try:
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("fastfetch-tweak-tool removed")
            fn.GLib.idle_add(_refresh_fftt_lbl, self)
            fn.GLib.idle_add(_refresh_fftt_launch_btn, self)
            fn.GLib.idle_add(fn.show_in_app_notification, self, "fastfetch-tweak-tool removed")
        except Exception as e:
            fn.log_error(f"Error removing fastfetch-tweak-tool: {e}")

    fn.threading.Thread(target=wait_remove, daemon=True).start()


def on_click_launch_fftt(self, _widget):
    """Launch Fastfetch Tweak Tool as real user from the Fastfetch page."""
    if fn.check_package_installed("fastfetch-tweak-tool"):
        fn.log_subsection("Launching Fastfetch Tweak Tool...")
        fn.subprocess.Popen(
            "sudo -E -u " + fn.sudo_username + " env HOME=" + fn.home + " fastfetch-tweak-tool &",
            shell=True,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        fn.GLib.idle_add(fn.show_in_app_notification, self, "Fastfetch Tweak Tool launched")
    else:
        fn.log_info("fastfetch-tweak-tool not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "fastfetch-tweak-tool not installed")

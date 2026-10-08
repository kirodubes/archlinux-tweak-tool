# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn


# Theme palette — single source of truth for the Themes page.
# Mirrors the generator's COLORS + BATCHES tables; keep in sync with
# kiro-arc-themes-generator/2-make-all-themes-for-arcolinux.sh (lines 55-98).
# Each family: (family_label, [(token, accent_hex, is_dark), ...]).
# token -> package "kiro-arc-<token>", checkbox label "kiro-arc-<token>", swatch "#<hex>".
THEME_FAMILIES = [
    ("Blues", [
        ("aqua", "66a8cb", False),
        ("archlinux-blue", "1793d1", False),
        ("arcolinux-blue", "6790eb", False),
        ("azure", "456bff", False),
        ("azure-dodger-blue", "1e9cff", False),
        ("blue-sky", "7684a8", False),
        ("botticelli", "82a4b3", False),
        ("carolina-blue", "6ba4e7", False),
        ("dodger-blue", "2a8dff", True),
        ("havelock", "6ba4e7", False),
        ("light-blue-surfn", "94c2e4", False),
        ("medium-blue", "4a71c4", False),
        ("nice-blue", "147eb8", False),
        ("polo", "688bc6", False),
        ("sky-blue", "7ec1ff", False),
        ("soft-blue", "5481e5", False),
    ]),
    ("Indigos", [
        ("azul", "3551b7", False),
        ("cornflower-blue", "3250a7", False),
        ("dawn", "566282", True),
        ("tory", "596bb0", False),
    ]),
    ("Purples", [
        ("blueberry", "52428f", False),
        ("bright-lilac", "cd58ff", False),
        ("dracul", "7e82a0", True),
        ("orchid", "ff7def", False),
        ("purpley", "8d2dc9", False),
        ("red-violet", "901265", False),
        ("twilight", "44397d", True),
        ("vampire", "555a69", True),
        ("darkish", "28293d", True),
    ]),
    ("Greens", [
        ("emerald", "1fa732", False),
        ("evopop", "1685a6", False),
        ("fern", "65b058", False),
        ("mantis", "6aa847", False),
        ("niagara", "42edcc", False),
    ]),
    ("Reds", [
        ("blood", "cf0808", False),
        ("crimson", "dc143c", False),
        ("hibiscus", "d52f61", False),
        ("mandy", "c93648", False),
        ("punch", "c03645", False),
    ]),
    ("Oranges", [
        ("casablanca", "fdb95b", False),
        ("fire", "f68516", False),
        ("numix", "ffa726", False),
        ("red-orange", "fe5100", False),
        ("rusty-orange", "e56b1a", False),
        ("tacao", "efa369", False),
        ("tangerine", "ff9500", False),
    ]),
    ("Pinks", [
        ("carnation", "fe6d88", False),
        ("froly", "fd7980", False),
        ("light-salmon", "ffa38d", False),
        ("pink", "ce6ca2", False),
        ("warm-pink", "fd3e84", False),
    ]),
    ("Greys", [
        ("light-blue-grey", "b8a8bc", False),
        ("pale-grey", "e1e3e7", True),
        ("paper", "90a4ae", False),
        ("slate-grey", "636a78", True),
        ("smoke", "a1a1a1", True),
    ]),
]


def _pkg(token):
    return "kiro-arc-" + token


def _all_tokens():
    return [token for _label, themes in THEME_FAMILIES for token, _hex, _dark in themes]


def install_themes(self):
    """Install selected arc themes with detailed logging."""
    themes_to_install = [_pkg(t) for t in _all_tokens() if self.arc_checkboxes[t].get_active()]

    if not themes_to_install:
        fn.log_warn("No themes selected for installation")
        fn.show_in_app_notification(self, "No themes selected for installation")
        return

    packages_str = " ".join(themes_to_install)
    fn.log_info(f"Installing {len(themes_to_install)} Arc theme(s): {', '.join(themes_to_install)}")
    process = fn.launch_pacman_install_in_terminal(packages_str)
    fn.show_in_app_notification(self, f"Installing {len(themes_to_install)} themes...")
    fn.wait_and_notify(process, self, "Arc themes installation complete")


def remove_themes(self):
    """Remove selected arc themes with detailed logging."""
    themes_to_remove = [_pkg(t) for t in _all_tokens() if self.arc_checkboxes[t].get_active()]

    if not themes_to_remove:
        fn.log_warn("No themes selected for removal")
        fn.show_in_app_notification(self, "No themes selected for removal")
        return

    packages_str = " ".join(themes_to_remove)
    fn.log_info(f"Removing {len(themes_to_remove)} Arc theme(s): {', '.join(themes_to_remove)}")
    process = fn.launch_pacman_remove_in_terminal(packages_str)
    fn.show_in_app_notification(self, f"Removing {len(themes_to_remove)} themes...")
    fn.wait_and_notify(process, self, "Arc themes removal complete")


def find_themes(self):
    """Check which arc themes are installed and tick their checkboxes (one bulk query)."""
    installed = fn.check_packages_installed([_pkg(t) for t in _all_tokens()])
    for token in _all_tokens():
        self.arc_checkboxes[token].set_active(installed.get(_pkg(token), False))


def set_att_checkboxes_theming_all(self):
    """Select all arc theme checkboxes."""
    for token in _all_tokens():
        self.arc_checkboxes[token].set_active(True)


def set_att_checkboxes_theming_dark(self):
    """Select only the dark arc theme checkboxes."""
    for _label, themes in THEME_FAMILIES:
        for token, _hex, is_dark in themes:
            self.arc_checkboxes[token].set_active(is_dark)


def set_att_checkboxes_theming_none(self):
    """Deselect all arc theme checkboxes."""
    for token in _all_tokens():
        self.arc_checkboxes[token].set_active(False)


def select_family(self, family_label):
    """Tick the checkboxes for one colour family and clear the rest."""
    for label, themes in THEME_FAMILIES:
        for token, _hex, _dark in themes:
            self.arc_checkboxes[token].set_active(label == family_label)


# ── Themes callbacks ─────────────────────────────────────────────────


def on_install_att_themes_clicked(self, _widget):
    """Install the checked arc theme packages."""
    fn.log_subsection("Install Arc Themes")
    fn.debug_print("Installing selected Arc themes")
    install_themes(self)


def on_remove_att_themes_clicked(self, _widget):
    """Remove the checked arc theme packages."""
    fn.log_subsection("Remove Arc Themes")
    fn.debug_print("Removing selected Arc themes")
    remove_themes(self)


def on_find_att_themes_clicked(self, _widget):
    """Scan installed packages and tick matching arc theme checkboxes."""
    fn.log_subsection("Scan for Installed Themes")
    fn.debug_print("Checking which Arc themes are installed")
    find_themes(self)
    fn.log_success("Theme scan complete")


def on_click_att_theming_all_selection(self, _widget):
    """Select all arc theme checkboxes via preset."""
    fn.log_subsection("Select All Themes")
    fn.debug_print("Enabling all Arc themes for installation")
    set_att_checkboxes_theming_all(self)
    fn.log_success("All themes selected")


def on_click_att_theming_dark_selection(self, _widget):
    """Select the dark arc theme checkboxes via preset."""
    fn.log_subsection("Select Dark Themes")
    fn.debug_print("Enabling dark-themed Arc themes")
    set_att_checkboxes_theming_dark(self)
    fn.log_success("Dark themes selected")


def on_click_att_theming_none_selection(self, _widget):
    """Deselect all arc theme checkboxes via preset."""
    fn.log_subsection("Clear Theme Selection")
    fn.debug_print("Deselecting all Arc themes")
    set_att_checkboxes_theming_none(self)
    fn.log_success("All themes deselected")


def on_click_att_family_selection(self, family_label, _widget):
    """Select one colour family of arc themes via preset."""
    fn.log_subsection(f"Select {family_label} Themes")
    fn.debug_print(f"Enabling {family_label} Arc themes")
    select_family(self, family_label)
    fn.log_success(f"{family_label} themes selected")


# ── /etc/environment helpers ───────────────

ENV_FILE = "/etc/environment"


# Plasma reads its own Qt theme; these /etc/environment keys override it and trigger
# the yellow "could not apply theme" popup. Kiro ships QT_QPA_PLATFORMTHEME; QT_STYLE_OVERRIDE may be added by hand.
_PLASMA_QT_KEYS = ("QT_QPA_PLATFORMTHEME", "QT_STYLE_OVERRIDE")


def _env_key(stripped):
    body = stripped.lstrip("#").strip()
    if "=" not in body:
        return None
    return body.split("=", 1)[0].strip()


def _is_qt_override_active(stripped):
    return not stripped.startswith("#") and _env_key(stripped) in _PLASMA_QT_KEYS


def _is_qt_override_commented(stripped):
    return stripped.startswith("#") and _env_key(stripped) in _PLASMA_QT_KEYS


def _log_plasma_qt_outcome(new_state):
    """Explain the Plasma Qt-override toggle in the terminal."""
    if new_state == "commented":
        fn.log_success(f"Commented the Qt overrides (QT_QPA_PLATFORMTHEME, QT_STYLE_OVERRIDE) in {ENV_FILE}")
        fn.log_info("Plasma now controls its own Qt theme — the yellow 'could not apply theme' popup should stop.")
        fn.log_info("LOG OUT and LOG BACK IN for Plasma to take over the theming.")
    else:
        fn.log_success(f"Restored the Qt overrides (qt5ct / Kvantum) in {ENV_FILE}")
        fn.log_info("qt5ct and Kvantum drive the Qt theme again (the non-Plasma default).")
        fn.log_info("LOG OUT and LOG BACK IN for the change to take effect.")


def _toggle_env(self, is_active, is_commented, subsection):
    """Comment every active matching line, or else uncomment every commented one; return {state, changes}."""
    fn.log_subsection(subsection)
    try:
        with open(ENV_FILE, encoding="utf-8") as env_file:
            lines = env_file.readlines()
    except OSError as error:
        fn.log_error(f"Could not read {ENV_FILE}: {error}")
        fn.show_in_app_notification(self, f"Could not read {ENV_FILE}")
        return {"state": "absent", "changes": []}

    active = [i for i, line in enumerate(lines) if is_active(line.strip())]
    commented = [i for i, line in enumerate(lines) if is_commented(line.strip())]
    if not active and not commented:
        fn.log_warn(f"No matching line found in {ENV_FILE} — nothing to toggle")
        fn.show_in_app_notification(self, f"No matching line in {ENV_FILE}")
        return {"state": "absent", "changes": []}

    changes = []
    if active:
        new_state = "commented"
        for index in active:
            from_line = lines[index].strip()
            lines[index] = "#" + lines[index].lstrip()
            changes.append((from_line, lines[index].strip()))
    else:
        new_state = "active"
        for index in commented:
            from_line = lines[index].strip()
            lines[index] = lines[index].lstrip().lstrip("#").lstrip(" \t")
            changes.append((from_line, lines[index].strip()))

    try:
        fn.shutil.copy(ENV_FILE, ENV_FILE + ".bak")
        with open(ENV_FILE, "w", encoding="utf-8") as env_file:
            env_file.writelines(lines)
    except OSError as error:
        fn.log_error(f"Could not write {ENV_FILE}: {error}")
        fn.show_in_app_notification(self, f"Could not write {ENV_FILE}")
        return {"state": "absent", "changes": []}

    for from_line, to_line in changes:
        fn.log_info(f"Changed:  {from_line}  ->  {to_line}")
    return {"state": new_state, "changes": changes}


def toggle_plasma_qt_overrides(self):
    """Comment/uncomment the Plasma-conflicting Qt override lines in /etc/environment; return {state, changes}."""
    result = _toggle_env(self, _is_qt_override_active, _is_qt_override_commented, "Toggle the Plasma Qt overrides")
    if result["state"] in ("active", "commented"):
        _log_plasma_qt_outcome(result["state"])
    return result


# Static brand-orange labels — same on every state, on every distro.
PLASMA_QT_TOGGLE_LABEL = "Enable or Disable the Plasma Qt theme overrides (/etc/environment)"


def style_toggle_button(button, text):
    """Give an /etc/environment toggle button its standing brand-orange label."""
    label = button.get_child()
    if not isinstance(label, fn.Gtk.Label):
        label = fn.Gtk.Label()
        button.set_child(label)
    label.set_markup(f'<span foreground="#FFA500">{text}</span>')


def _read_env_content():
    """Return the full text of /etc/environment, or None when it does not exist / cannot be read."""
    try:
        with open(ENV_FILE, encoding="utf-8") as env_file:
            return env_file.read()
    except FileNotFoundError:
        return None
    except OSError as error:
        fn.log_warn(f"Could not read {ENV_FILE}: {error}")
        return None


def _show_env_content_dialog(self, header):
    """Pop up the full current content of /etc/environment so the user sees the real file state."""
    content = _read_env_content()
    if content is None:
        body = f"{ENV_FILE} does not exist."
    elif not content.strip():
        body = f"{ENV_FILE} is empty."
    else:
        body = content.rstrip("\n")
    dialog = fn.Gtk.MessageDialog(
        transient_for=self,
        message_type=fn.Gtk.MessageType.INFO,
        buttons=fn.Gtk.ButtonsType.OK,
        text=header,
    )
    dialog.props.secondary_text = body
    dialog.connect("response", lambda d, _r: d.destroy())
    dialog.show()


def open_env_in_terminal(self):
    """Open /etc/environment in a terminal editor so the user can edit it directly (non-Kiro systems)."""
    fn.log_subsection("Open /etc/environment in a terminal editor")
    if not fn.shutil.which("alacritty"):
        fn.log_warn("alacritty not found — cannot open a terminal editor")
        fn.show_in_app_notification(self, "alacritty not found — open /etc/environment manually")
        return
    script = (
        'echo "Editing /etc/environment — save and close when done, then log out and back in."; '
        "${EDITOR:-nano} /etc/environment"
    )
    fn.threading.Thread(
        target=lambda: fn.subprocess.Popen(["alacritty", "-e", "bash", "-c", script]).wait(),
        daemon=True,
    ).start()
    fn.log_info("Opened /etc/environment in a terminal editor")
    fn.show_in_app_notification(self, "Editing /etc/environment in a terminal — log out and back in after saving")


def on_click_edit_environment(self, _widget):
    """Open /etc/environment in a terminal editor (non-Kiro Themes-page reminder button)."""
    open_env_in_terminal(self)


def on_click_toggle_plasma_qt(self, _widget):
    """On Kiro: comment/uncomment the Plasma-conflicting Qt overrides and pop up the change. Elsewhere: open the file."""
    if fn.get_distro_label() != "Kiro":
        open_env_in_terminal(self)
        return
    result = toggle_plasma_qt_overrides(self)
    if result["state"] not in ("commented", "active"):
        return
    _show_env_content_dialog(self, "Updated /etc/environment")
    if result["state"] == "commented":
        fn.show_in_app_notification(self, "Qt overrides OFF — Plasma controls its theme; log out and back in")
    else:
        fn.show_in_app_notification(self, "Qt overrides restored (qt5ct/Kvantum) — log out and back in")


# ── Set any system GTK theme via a dropdown (/etc/environment) ─────────

THEMES_ROOT = "/usr/share/themes"
ENV_NONE_LABEL = "None — no system-wide theme"


def list_system_gtk_themes():
    """Return GTK theme folders in /usr/share/themes that ship a gtk-3.0 or gtk-4.0 directory."""
    found = []
    try:
        for name in fn.os.listdir(THEMES_ROOT):
            theme_dir = fn.os.path.join(THEMES_ROOT, name)
            if not fn.os.path.isdir(theme_dir):
                continue
            has_gtk = fn.os.path.isdir(fn.os.path.join(theme_dir, "gtk-3.0")) or fn.os.path.isdir(
                fn.os.path.join(theme_dir, "gtk-4.0")
            )
            if has_gtk:
                found.append(name)
    except OSError as error:
        fn.log_warn(f"Could not read {THEMES_ROOT}: {error}")
    return sorted(found, key=str.lower)


def _is_gtk_theme_key(stripped):
    return _env_key(stripped) == "GTK_THEME"


def current_env_gtk_theme():
    """Return the active GTK_THEME value in /etc/environment, or None when none is set."""
    try:
        with open(ENV_FILE, encoding="utf-8") as env_file:
            for line in env_file:
                stripped = line.strip()
                if not stripped.startswith("#") and _is_gtk_theme_key(stripped):
                    return stripped.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError as error:
        fn.log_warn(f"Could not read {ENV_FILE}: {error}")
    return None


def set_env_gtk_theme(self, theme):
    """Set GTK_THEME in /etc/environment to theme, or clear it when theme is None; return {state, changes}."""
    fn.log_subsection("Set the system-wide GTK theme (/etc/environment)")
    # The file may be empty or missing on a non-Kiro box; treat both as "no lines yet".
    file_exists = fn.os.path.exists(ENV_FILE)
    lines = []
    if file_exists:
        try:
            with open(ENV_FILE, encoding="utf-8") as env_file:
                lines = env_file.readlines()
        except OSError as error:
            fn.log_error(f"Could not read {ENV_FILE}: {error}")
            fn.show_in_app_notification(self, f"Could not read {ENV_FILE}")
            return {"state": "absent", "changes": []}

    gtk_indices = [i for i, line in enumerate(lines) if _is_gtk_theme_key(line.strip())]
    changes = []

    if theme is None:
        # Comment out every active GTK_THEME line so the per-user theme takes over.
        for index in gtk_indices:
            stripped = lines[index].strip()
            if not stripped.startswith("#"):
                from_line = stripped
                lines[index] = "#" + lines[index].lstrip()
                changes.append((from_line, lines[index].strip()))
        new_state = "commented"
    else:
        new_line = f'GTK_THEME="{theme}"\n'
        if gtk_indices:
            # Reuse the first GTK_THEME line (active or commented) as the single source of truth.
            first = gtk_indices[0]
            from_line = lines[first].strip()
            lines[first] = new_line
            if from_line != new_line.strip():
                changes.append((from_line, new_line.strip()))
            # Comment any further active GTK_THEME lines so only one stays live.
            for index in gtk_indices[1:]:
                stripped = lines[index].strip()
                if not stripped.startswith("#"):
                    lines[index] = "#" + lines[index].lstrip()
                    changes.append((stripped, lines[index].strip()))
        else:
            if lines and not lines[-1].endswith("\n"):
                lines[-1] = lines[-1] + "\n"
            lines.append(new_line)
            changes.append(("(none)", new_line.strip()))
        new_state = "active"

    if not changes:
        fn.log_info("GTK_THEME already in the requested state — nothing to change")
        return {"state": new_state, "changes": []}

    try:
        if file_exists:
            fn.shutil.copy(ENV_FILE, ENV_FILE + ".bak")
        with open(ENV_FILE, "w", encoding="utf-8") as env_file:
            env_file.writelines(lines)
    except OSError as error:
        fn.log_error(f"Could not write {ENV_FILE}: {error}")
        fn.show_in_app_notification(self, f"Could not write {ENV_FILE}")
        return {"state": "absent", "changes": []}

    if not file_exists:
        fn.log_info(f"Created {ENV_FILE} (it did not exist)")
    for from_line, to_line in changes:
        fn.log_info(f"Changed:  {from_line}  ->  {to_line}")
    return {"state": new_state, "changes": changes}


def refresh_env_theme_row(self, names_attr, dropdown_attr):
    """Repopulate one /etc/environment theme dropdown from /usr/share/themes, keeping its selection."""
    from gi.repository import Gtk

    dropdown = getattr(self, dropdown_attr, None)
    if dropdown is None:
        return

    # names_attr only exists once the row has been populated, which separates the initial
    # build (preselect what /etc/environment says) from a rebuild (keep what the user picked).
    previous_names = getattr(self, names_attr, None)
    is_rebuild = previous_names is not None
    selected = dropdown.get_selected() if is_rebuild else 0
    keep = previous_names[selected - 1] if is_rebuild and 0 < selected <= len(previous_names) else None

    theme_names = list_system_gtk_themes()
    current_env_theme = current_env_gtk_theme()
    # If a GTK_THEME is already set but isn't an installed /usr/share/themes folder (e.g. a
    # ~/.themes name or a typo), still list it so "None" can't be preselected over a real value —
    # Apply on an unchanged dropdown would otherwise silently clear that theme.
    if current_env_theme and current_env_theme not in theme_names:
        theme_names = [current_env_theme] + theme_names
    # A theme that was picked but not applied yet stays listed even after it was uninstalled,
    # so a rebuild never quietly moves the selection onto a different theme.
    if keep and keep not in theme_names:
        theme_names = [keep] + theme_names
    setattr(self, names_attr, theme_names)

    dropdown.set_model(Gtk.StringList.new([ENV_NONE_LABEL] + theme_names))
    target = keep if is_rebuild else current_env_theme
    dropdown.set_selected(theme_names.index(target) + 1 if target in theme_names else 0)


def refresh_env_theme_dropdowns(self):
    """Resync every /etc/environment theme dropdown — call after themes were installed or removed."""
    refresh_env_theme_row(self, "_env_gtk_theme_names", "env_theme_dropdown")
    refresh_env_theme_row(self, "_celestial_env_theme_names", "celestial_env_dropdown")


def apply_env_theme_from(self, dropdown, theme_names):
    """Apply the theme picked in an /etc/environment dropdown, or clear it when 'None' is chosen."""
    selected = dropdown.get_selected()
    theme = None if selected == 0 else theme_names[selected - 1]
    result = set_env_gtk_theme(self, theme)
    if result["state"] == "absent":
        return
    if not result["changes"]:
        if theme:
            fn.show_in_app_notification(self, f"GTK theme already set to {theme}")
        else:
            fn.show_in_app_notification(self, "No system-wide GTK theme was set")
        return
    _show_env_content_dialog(self, "Updated /etc/environment")
    if theme:
        fn.log_success(f'Set GTK_THEME="{theme}" in {ENV_FILE}')
        fn.log_info("LOG OUT and LOG BACK IN for the system-wide theme to apply.")
        fn.show_in_app_notification(self, f"GTK theme set to {theme} — log out and back in to apply")
    else:
        fn.log_success(f"Cleared the system-wide GTK_THEME in {ENV_FILE}")
        fn.log_info("Your per-user theme takes over again. LOG OUT and LOG BACK IN to apply.")
        fn.show_in_app_notification(self, "System-wide GTK theme cleared — log out and back in")


def on_click_apply_env_theme(self, _widget):
    """Apply the Themes-page dropdown selection to /etc/environment."""
    apply_env_theme_from(self, self.env_theme_dropdown, self._env_gtk_theme_names)

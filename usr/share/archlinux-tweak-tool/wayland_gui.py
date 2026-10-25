# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
import functions as fn


def _status_markup(wm, wayland):
    if wayland.is_installed(wm):
        return '<span foreground="#FFA500"><b>Installed</b></span>'
    return '<span foreground="#888888">Not installed</span>'


def _selected_keys(self):
    return [key for key, row in self.wayland_rows.items() if row["check"].get_active() and row["check"].get_sensitive()]


def _update_button(self, wayland, desktopr, fn):
    selected = _selected_keys(self)
    has_extra_repo = (
        fn.check_nemesis_repo_active()
        or fn.check_chaotic_aur_active()
        or fn.check_cachyos_repo_active()
    )
    needs_repo = wayland.selection_needs_nemesis(selected) and not has_extra_repo
    self.wayland_repo_warning.set_visible(needs_repo)

    conflicts = wayland.selection_conflicts(selected)
    if conflicts:
        pairs = "\n".join(f"  • {a}  ✕  {b}" for a, b in conflicts)
        self.wayland_conflict_warning.set_markup(
            '<span foreground="#FFA500"><b>These picks can’t be installed together — choose one shell family:</b></span>\n'
            f'<span foreground="#FFA500">{pairs}</span>\n'
            '<span foreground="#888888">DankMaterialShell editions use Quickshell; Noctalia and Noctura use a conflicting Quickshell fork (noctalia-qs).</span>'
        )
    self.wayland_conflict_warning.set_visible(bool(conflicts))

    if not selected:
        self.wayland_install_btn.set_sensitive(False)
        self.wayland_install_btn.set_tooltip_text("Select at least one window manager")
    elif needs_repo:
        self.wayland_install_btn.set_sensitive(False)
        self.wayland_install_btn.set_tooltip_text(
            "Enable an extra repo (nemesis_repo, chaotic-aur or cachyos) in the Pacman tab to install these Kiro Wayland editions"
        )
    elif conflicts:
        self.wayland_install_btn.set_sensitive(False)
        self.wayland_install_btn.set_tooltip_text("Selected editions conflict — they use incompatible Quickshell builds; deselect one family")
    else:
        self.wayland_install_btn.set_sensitive(True)
        self.wayland_install_btn.set_tooltip_text("")

    removable = [k for k in selected if wayland.get_wm(k).get("remove") and wayland.is_installed(wayland.get_wm(k))]
    self.wayland_remove_btn.set_sensitive(bool(removable))
    self.wayland_remove_btn.set_tooltip_text("" if removable else "Select an installed window manager to remove")


def _refresh(self, wayland, desktopr, fn):
    for wm in wayland.WAYLAND_WMS:
        row = self.wayland_rows.get(wm["key"])
        if row:
            row["status"].set_markup(_status_markup(wm, wayland))
    _update_button(self, wayland, desktopr, fn)
    return False


def _on_toggle(self, _widget, wayland, desktopr, fn):
    _update_button(self, wayland, desktopr, fn)


def _on_select_all(self, _widget, active, wayland, desktopr, fn):
    fn.log_info(f"Wayland page: {'select' if active else 'deselect'} all window managers")
    for row in self.wayland_rows.values():
        if row["check"].get_sensitive():
            row["check"].set_active(active)
    _update_button(self, wayland, desktopr, fn)


def _on_install(self, _widget, wayland, desktopr, fn):
    selected = _selected_keys(self)
    if not selected:
        return
    labels = ", ".join(wayland.get_wm(k)["label"] for k in selected)
    fn.log_section(f"Wayland page: install requested for {labels}")
    fn.threading.Thread(target=wayland.install_wayland_selection, args=(self, selected), daemon=True).start()


def _on_remove(self, _widget, wayland, desktopr, fn):
    selected = [k for k in _selected_keys(self) if wayland.get_wm(k).get("remove") and wayland.is_installed(wayland.get_wm(k))]
    if not selected:
        return
    labels = ", ".join(wayland.get_wm(k)["label"] for k in selected)
    fn.log_section(f"Wayland page: remove requested for {labels}")
    fn.threading.Thread(target=wayland.remove_wayland_selection, args=(self, selected), daemon=True).start()


def _link_kind(url):
    """Short label describing where the upstream link points."""
    if "wiki." in url:
        return "wiki"
    if "codeberg.org" in url:
        return "codeberg"
    return "github"


def _build_link_button(self, Gtk, url):
    button = Gtk.Button()
    button.set_valign(Gtk.Align.CENTER)
    button.set_css_classes(["flat"])
    button.set_tooltip_text(url)
    label = Gtk.Label()
    label.set_markup(f'<i>{_link_kind(url)}</i>')
    button.set_child(label)
    button.connect("clicked", lambda _w, u=url: fn.open_url_as_user(u))
    fn.attach_link_context_menu(self, button, url)
    return button


def _build_row(self, Gtk, wayland, desktopr, wm):
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox.set_margin_top(4)

    check = Gtk.CheckButton(label=f"{wm['label']}  ·  {wm['backend']}")
    check.set_margin_start(20)
    check.set_hexpand(True)
    check.connect("toggled", functools.partial(_on_toggle, self, wayland=wayland, desktopr=desktopr, fn=fn))

    link = _build_link_button(self, Gtk, wm["link"])

    status = Gtk.Label(xalign=1)
    status.set_margin_end(20)
    status.set_size_request(110, -1)
    status.set_markup(_status_markup(wm, wayland))

    hbox.append(check)
    hbox.append(link)
    hbox.append(status)
    self.wayland_rows[wm["key"]] = {"check": check, "status": status}
    return hbox


def gui(self, Gtk, vboxstack_wayland, wayland, desktopr, fn, base_dir):
    """Create the Wayland window-manager picker page."""
    self.wayland_rows = {}

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text("Desktop - Wayland")
    lbl_title.set_name("title")
    lbl_title.set_margin_start(10)
    hbox_title.append(lbl_title)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hbox_sep.append(hseparator)

    headline = Gtk.Label(xalign=0)
    headline.set_margin_start(20)
    headline.set_margin_end(20)
    headline.set_margin_top(10)
    headline.set_wrap(True)
    headline.set_markup(
        '<span size="x-large" weight="bold">Install them all — they live side by side</span>'
    )

    intro = Gtk.Label(xalign=0)
    intro.set_margin_start(20)
    intro.set_margin_end(20)
    intro.set_margin_top(8)
    intro.set_wrap(True)
    intro.set_markup(
        "Try a Wayland window manager alongside your current desktop — pick one at the login screen afterwards. "
        "Your current session stays the default. Every edition here ships a curated Kiro config. "
        "You can install as many as you like in one go: each coexists with the others and with your "
        "existing X11 desktop, so nothing you already run is replaced."
    )

    hbox_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section = Gtk.Label(xalign=0)
    lbl_section.set_markup("<b>Available Wayland window managers</b>")
    lbl_section.set_margin_start(20)
    lbl_section.set_margin_top(12)
    lbl_section.set_hexpand(True)
    hbox_section.append(lbl_section)

    btn_select_all = Gtk.Button(label="Select all")
    btn_select_all.set_css_classes(["flat"])
    btn_select_all.set_valign(Gtk.Align.CENTER)
    btn_select_all.connect("clicked", functools.partial(_on_select_all, self, active=True, wayland=wayland, desktopr=desktopr, fn=fn))
    hbox_section.append(btn_select_all)

    btn_deselect_all = Gtk.Button(label="Deselect all")
    btn_deselect_all.set_css_classes(["flat"])
    btn_deselect_all.set_valign(Gtk.Align.CENTER)
    btn_deselect_all.set_margin_end(20)
    btn_deselect_all.connect("clicked", functools.partial(_on_select_all, self, active=False, wayland=wayland, desktopr=desktopr, fn=fn))
    hbox_section.append(btn_deselect_all)

    vbox_rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    for wm in wayland.WAYLAND_WMS:
        vbox_rows.append(_build_row(self, Gtk, wayland, desktopr, wm))

    self.wayland_repo_warning = Gtk.Label(xalign=0)
    self.wayland_repo_warning.set_margin_start(20)
    self.wayland_repo_warning.set_margin_top(10)
    self.wayland_repo_warning.set_wrap(True)
    self.wayland_repo_warning.set_markup(
        '<span foreground="#FFA500"><b>These Kiro Wayland editions need an extra repo (nemesis_repo, chaotic-aur or cachyos) — enable one in the Pacman tab first.</b></span>'
    )
    self.wayland_repo_warning.set_visible(False)

    self.wayland_conflict_warning = Gtk.Label(xalign=0)
    self.wayland_conflict_warning.set_margin_start(20)
    self.wayland_conflict_warning.set_margin_end(20)
    self.wayland_conflict_warning.set_margin_top(10)
    self.wayland_conflict_warning.set_wrap(True)
    self.wayland_conflict_warning.set_visible(False)

    buttonbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    buttonbox.set_halign(Gtk.Align.CENTER)
    buttonbox.set_margin_top(14)
    self.wayland_install_btn = Gtk.Button(label="Install selected")
    self.wayland_install_btn.connect("clicked", functools.partial(_on_install, self, wayland=wayland, desktopr=desktopr, fn=fn))
    buttonbox.append(self.wayland_install_btn)

    self.wayland_remove_btn = Gtk.Button(label="Remove selected")
    self.wayland_remove_btn.connect("clicked", functools.partial(_on_remove, self, wayland=wayland, desktopr=desktopr, fn=fn))
    buttonbox.append(self.wayland_remove_btn)

    lbl_backup_note = Gtk.Label(xalign=0)
    lbl_backup_note.set_margin_start(20)
    lbl_backup_note.set_margin_top(14)
    lbl_backup_note.set_wrap(True)
    lbl_backup_note.set_markup(
        "Configs the install overwrites are backed up to ~/.config-att first.\n"
        "Uninstalling a WM later leaves its ~/.config subfolder intact — remove it yourself if no longer needed."
    )

    vboxstack_wayland.append(hbox_title)
    vboxstack_wayland.append(hbox_sep)
    vboxstack_wayland.append(headline)
    vboxstack_wayland.append(intro)
    vboxstack_wayland.append(hbox_section)
    vboxstack_wayland.append(vbox_rows)
    vboxstack_wayland.append(self.wayland_repo_warning)
    vboxstack_wayland.append(self.wayland_conflict_warning)
    vboxstack_wayland.append(buttonbox)
    vboxstack_wayland.append(lbl_backup_note)

    self.wayland_refresh = functools.partial(_refresh, self, wayland, desktopr, fn)
    vboxstack_wayland.connect("map", lambda _w: self.wayland_refresh())
    self.wayland_refresh()

# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools

import accessibility
from att_i18n import _

# Stack child-name of the Themer page (see gui.py add_titled calls).
_THEMER_PAGE = "stack11"


def _section_header(Gtk, text):
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label = Gtk.Label(xalign=0)
    label.set_markup(f"<b>{text}</b>")
    label.set_margin_start(10)
    label.set_margin_top(10)
    label.set_margin_end(10)
    hbox.append(label)
    return hbox


def _refresh(self, fn):
    """Sync every label and switch to the live system state (build-time + on map)."""
    for app in accessibility.ACCESSIBILITY_APPS:
        label = getattr(self, f"lbl_acc_{app['key']}", None)
        if label:
            installed = fn.check_package_installed(app["packages"].split()[0])
            label.set_markup(
                _("{name} <b>installed</b>").format(name=_(app["label"])) if installed else _(app["label"])
            )

    refresh_hc = getattr(self, "refresh_high_contrast_lbl", None)
    if refresh_hc:
        refresh_hc()

    refresh_xkbset = getattr(self, "refresh_xkbset_state", None)
    if refresh_xkbset:
        refresh_xkbset()

    state = accessibility.read_accessx_state()
    for feature in accessibility.ACCESSX:
        switch = getattr(self, f"accessx_switch_{feature['key']}", None)
        if switch:
            self.accessx_initializing = True
            switch.set_active(state.get(feature["key"], False))
            self.accessx_initializing = False


def _on_accessx_toggled(self, fn, feature, switch, _widget, _param):
    if getattr(self, "accessx_initializing", False):
        return
    enabled = switch.get_active()

    def worker():
        if enabled and not accessibility.ensure_xkbset(self):
            fn.GLib.idle_add(fn.show_in_app_notification, self, _("{name} is required — install an AUR helper first").format(name="xkbset"))
            fn.GLib.idle_add(_reset_switch, self, switch)
            return
        accessibility.apply_accessx(feature, enabled)
        name = _(feature["label"])
        if enabled:
            message = _("{name} enabled (current session + saved for next login)").format(name=name)
        else:
            message = _("{name} disabled (current session)").format(name=name)
        fn.GLib.idle_add(fn.show_in_app_notification, self, message)

    fn.threading.Thread(target=worker, daemon=True).start()


def _reset_switch(self, switch):
    self.accessx_initializing = True
    switch.set_active(False)
    self.accessx_initializing = False


def gui(self, Gtk, vboxstack_accessibility, fn):
    """Create the Accessibility page: assistive tools, high contrast, X11 keyboard accessibility."""
    fn.log_info("Building Accessibility page")

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_title_label = Gtk.Label(xalign=0)
    hbox_title_label.set_text(_("Accessibility"))
    hbox_title_label.set_name("title")
    hbox_title_label.set_margin_start(10)
    hbox_title_label.set_margin_end(10)
    hbox_title.append(hbox_title_label)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_sep.append(hseparator)

    vboxstack_accessibility.append(hbox_title)
    vboxstack_accessibility.append(hbox_sep)

    # ── Assistive tools ──────────────────────────────────────────────
    vboxstack_accessibility.append(_section_header(Gtk, _("Assistive tools")))
    for app in accessibility.ACCESSIBILITY_APPS:
        hbox_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_row.set_margin_top(4)
        label = Gtk.Label(xalign=0)
        label.set_markup(_(app["label"]))
        label.set_margin_start(20)
        label.set_margin_end(10)
        label.set_hexpand(True)
        setattr(self, f"lbl_acc_{app['key']}", label)

        btn_launch = Gtk.Button(label=_("Launch/Install"))
        btn_launch.connect("clicked", functools.partial(accessibility.install_or_launch, self, app))
        btn_launch.set_margin_start(10)
        btn_launch.set_margin_end(5)

        btn_remove = Gtk.Button(label=_("Remove"))
        btn_remove.connect("clicked", functools.partial(accessibility.remove, self, app))
        btn_remove.set_margin_start(5)
        btn_remove.set_margin_end(10)

        hbox_row.append(label)
        hbox_row.append(btn_launch)
        hbox_row.append(btn_remove)
        vboxstack_accessibility.append(hbox_row)

    # ── High contrast / large text ───────────────────────────────────
    vboxstack_accessibility.append(_section_header(Gtk, _("High contrast &amp; large text")))
    hbox_hc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_hc.set_margin_top(4)
    lbl_hc = Gtk.Label(xalign=0)
    lbl_hc.set_margin_start(20)
    lbl_hc.set_margin_end(10)
    lbl_hc.set_hexpand(True)

    def refresh_high_contrast_lbl():
        if accessibility.high_contrast_installed():
            lbl_hc.set_markup(_("High-contrast themes <b>installed</b> — apply them on the Themer page"))
        else:
            lbl_hc.set_markup(_("Install high-contrast &amp; large-text GTK themes (gnome-themes-extra)"))

    self.refresh_high_contrast_lbl = refresh_high_contrast_lbl
    refresh_high_contrast_lbl()

    btn_hc_install = Gtk.Button(label=_("Install"))
    btn_hc_install.connect("clicked", functools.partial(accessibility.install_high_contrast, self))
    btn_hc_install.set_margin_start(10)
    btn_hc_install.set_margin_end(5)

    btn_hc_themer = Gtk.Button(label=_("Open Themer"))
    btn_hc_themer.set_margin_start(5)
    btn_hc_themer.set_margin_end(10)

    def open_themer(_widget):
        stack = getattr(self, "att_stack", None)
        if stack and stack.get_child_by_name(_THEMER_PAGE) is not None:
            stack.set_visible_child_name(_THEMER_PAGE)
            fn.log_info("Jumped to Themer page from Accessibility")

    btn_hc_themer.connect("clicked", open_themer)

    hbox_hc.append(lbl_hc)
    hbox_hc.append(btn_hc_install)
    hbox_hc.append(btn_hc_themer)
    vboxstack_accessibility.append(hbox_hc)

    # ── Keyboard accessibility (X11) ─────────────────────────────────
    vboxstack_accessibility.append(_section_header(Gtk, _("Keyboard accessibility (X11)")))

    # xkbset is the AUR backend that powers every toggle below; it is installed lazily
    # on first toggle. This managed row reports its state and offers a Remove button.
    hbox_xkbset = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_xkbset.set_margin_top(4)
    lbl_xkbset = Gtk.Label(xalign=0)
    lbl_xkbset.set_margin_start(20)
    lbl_xkbset.set_margin_end(10)
    lbl_xkbset.set_hexpand(True)
    btn_xkbset_remove = Gtk.Button(label=_("Remove"))
    btn_xkbset_remove.connect("clicked", functools.partial(accessibility.remove_xkbset, self))
    btn_xkbset_remove.set_margin_start(10)
    btn_xkbset_remove.set_margin_end(10)
    hbox_xkbset.append(lbl_xkbset)
    hbox_xkbset.append(btn_xkbset_remove)
    vboxstack_accessibility.append(hbox_xkbset)

    def refresh_xkbset_state():
        installed = fn.check_package_installed(accessibility.XKBSET_PKG)
        ready = installed or fn.get_aur_helper() is not None
        if installed:
            lbl_xkbset.set_markup(_("{name} <b>installed</b> — backend for the toggles below").format(name="xkbset"))
        elif ready:
            lbl_xkbset.set_markup(_("{name} will be installed automatically on first toggle").format(name="xkbset"))
        else:
            lbl_xkbset.set_markup(
                _("Requires <b>{name}</b> — install an AUR helper (e.g. yay) to enable these toggles.").format(name="xkbset")
            )
        btn_xkbset_remove.set_visible(installed)
        for feature in accessibility.ACCESSX:
            switch = getattr(self, f"accessx_switch_{feature['key']}", None)
            if switch:
                switch.set_sensitive(ready)
                switch.set_tooltip_text(
                    "" if ready else _("Requires {name} (needs an AUR helper such as yay)").format(name="xkbset")
                )

    self.refresh_xkbset_state = refresh_xkbset_state

    for feature in accessibility.ACCESSX:
        hbox_feature = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_feature.set_margin_top(4)

        # Label stacks the feature name over the exact xkbset line to drop into run.sh (selectable to copy).
        vbox_label = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        vbox_label.set_margin_start(20)
        vbox_label.set_margin_end(10)
        vbox_label.set_hexpand(True)
        vbox_label.set_valign(Gtk.Align.CENTER)
        lbl_feature = Gtk.Label(xalign=0)
        lbl_feature.set_text(_(feature["label"]))
        lbl_cmd = Gtk.Label(xalign=0)
        lbl_cmd.set_markup(f"<small><tt>{fn.GLib.markup_escape_text(feature['on'])}</tt></small>")
        lbl_cmd.set_selectable(True)
        vbox_label.append(lbl_feature)
        vbox_label.append(lbl_cmd)

        switch = Gtk.Switch()
        switch.set_valign(Gtk.Align.CENTER)
        switch.set_margin_end(10)
        setattr(self, f"accessx_switch_{feature['key']}", switch)
        switch.connect("notify::active", functools.partial(_on_accessx_toggled, self, fn, feature, switch))

        hbox_feature.append(vbox_label)
        hbox_feature.append(switch)
        vboxstack_accessibility.append(hbox_feature)

    refresh_xkbset_state()

    vboxstack_accessibility.append(_persist_note(Gtk))
    vboxstack_accessibility.append(_legend(Gtk))

    vboxstack_accessibility.connect("map", lambda _w: _refresh(self, fn))
    _refresh(self, fn)


def _persist_note(Gtk):
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label = Gtk.Label(xalign=0)
    label.set_markup(
        _(
            "<i>Toggles apply immediately and are saved for next login. On a tiling WM that ignores XDG "
            "autostart, add the equivalent xkbset line to your run.sh (or equivalent autostart script).</i>"
        )
    )
    label.set_wrap(True)
    # margin_start matches the toggle labels (20) so the wrapped second line stays aligned under the first word.
    label.set_margin_start(20)
    label.set_margin_end(10)
    label.set_margin_top(6)
    hbox.append(label)
    return hbox


def _legend(Gtk):
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    vbox.set_margin_start(20)
    vbox.set_margin_end(10)
    vbox.set_margin_top(12)
    header = Gtk.Label(xalign=0)
    header.set_markup(_("<b>What these do</b>"))
    vbox.append(header)
    entries = [
        (
            _("Sticky Keys"),
            _("press modifier keys (Shift, Ctrl, Alt, Super) one at a time instead of holding several together."),
        ),
        (_("Slow Keys"), _("a key only registers when held down briefly, so accidental light taps are ignored.")),
        (
            _("Bounce Keys"),
            _("ignores repeated presses of the same key in quick succession (accidental double-strikes)."),
        ),
        (_("Mouse Keys"), _("move the mouse pointer using the numeric keypad instead of a physical mouse.")),
    ]
    for name, desc in entries:
        lbl = Gtk.Label(xalign=0)
        lbl.set_markup(_("<small><b>{name}</b> — {desc}</small>").format(name=name, desc=desc))
        lbl.set_wrap(True)
        vbox.append(lbl)
    return vbox

# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
import privacy
from att_i18n import _


def init_privacy_lazy_load(self):
    """Refresh label and button states when page becomes visible."""
    try:
        privacy._refresh_ublock_label(self)
        privacy._refresh_hblock_label(self)
        privacy._refresh_allowlist_box(self)
    except Exception:
        pass


def gui(self, Gtk, vboxstack_privacy, fn):
    """Create the Privacy/Security configuration GUI."""
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text(_("Privacy/Security"))
    lbl_title.set_name("title")
    lbl_title.set_margin_start(10)
    hbox_title.append(lbl_title)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hbox_sep.append(hseparator)

    # ── Content blocking ───────────────────────────────────────────────────

    hbox_section1_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section1 = Gtk.Label(xalign=0)
    lbl_section1.set_markup(_("<b>Content Blocking</b>"))
    lbl_section1.set_margin_start(10)
    hbox_section1_title.append(lbl_section1)

    # uBlock Origin — install / remove
    hbox_ublock = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_ublock.set_margin_start(10)
    hbox_ublock.set_margin_end(10)

    self.lbl_ublock = Gtk.Label(xalign=0)
    self.lbl_ublock.set_hexpand(True)
    self.lbl_ublock.set_text(_("{name} for Firefox").format(name="uBlock Origin"))

    btn_install_ublock = Gtk.Button(label=_("Install {name}").format(name="uBlock"))
    btn_install_ublock.set_size_request(160, -1)
    btn_install_ublock.connect("clicked", functools.partial(privacy.on_click_install_ublock, self))

    btn_remove_ublock = Gtk.Button(label=_("Remove {name}").format(name="uBlock"))
    btn_remove_ublock.set_size_request(160, -1)
    btn_remove_ublock.connect("clicked", functools.partial(privacy.on_click_remove_ublock, self))

    hbox_ublock.append(self.lbl_ublock)
    hbox_ublock.append(btn_install_ublock)
    hbox_ublock.append(btn_remove_ublock)

    # ── Network &amp; tracking protection ────────────────────────────────────

    hbox_sep2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator2.set_hexpand(True)
    hbox_sep2.append(hseparator2)

    hbox_section2_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section2 = Gtk.Label(xalign=0)
    lbl_section2.set_markup(_("<b>Network &amp; Tracking Protection</b>"))
    lbl_section2.set_margin_start(10)
    hbox_section2_title.append(lbl_section2)

    # hblock — install / remove
    hbox_hblock_pkg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_hblock_pkg.set_margin_start(10)
    hbox_hblock_pkg.set_margin_end(10)

    self.lbl_hblock = Gtk.Label(xalign=0)
    self.lbl_hblock.set_hexpand(True)
    self.lbl_hblock.set_text(_("{name} — ad/tracker blocking via /etc/hosts").format(name="hblock"))

    btn_install_hblock = Gtk.Button(label=_("Install {name}").format(name="hblock"))
    btn_install_hblock.set_size_request(160, -1)
    btn_install_hblock.connect("clicked", functools.partial(privacy.on_click_install_hblock, self))

    btn_remove_hblock = Gtk.Button(label=_("Remove {name}").format(name="hblock"))
    btn_remove_hblock.set_size_request(160, -1)
    btn_remove_hblock.connect("clicked", functools.partial(privacy.on_click_remove_hblock, self))

    hbox_hblock_pkg.append(self.lbl_hblock)
    hbox_hblock_pkg.append(btn_install_hblock)
    hbox_hblock_pkg.append(btn_remove_hblock)

    # hblock — enable / disable
    hbox_hblock_toggle = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_hblock_toggle.set_margin_start(10)
    hbox_hblock_toggle.set_margin_end(10)

    self.lbl_hblock_status = Gtk.Label(xalign=0)
    self.lbl_hblock_status.set_hexpand(True)
    self.lbl_hblock_status.set_markup(_("Enable or disable {name} — check /etc/hosts disabled").format(name="hblock"))

    self.btn_enable_hblock = Gtk.Button(label=_("Enable {name}").format(name="hblock"))
    self.btn_enable_hblock.set_size_request(160, -1)
    self.btn_enable_hblock.set_sensitive(False)
    self.btn_enable_hblock.connect("clicked", functools.partial(privacy.on_click_enable_hblock, self))

    self.btn_disable_hblock = Gtk.Button(label=_("Disable {name}").format(name="hblock"))
    self.btn_disable_hblock.set_size_request(160, -1)
    self.btn_disable_hblock.set_sensitive(False)
    self.btn_disable_hblock.connect("clicked", functools.partial(privacy.on_click_disable_hblock, self))

    hbox_hblock_toggle.append(self.lbl_hblock_status)
    hbox_hblock_toggle.append(self.btn_enable_hblock)
    hbox_hblock_toggle.append(self.btn_disable_hblock)

    # hblock — whitelist (allowlist)
    hbox_whitelist_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_whitelist = Gtk.Label(xalign=0)
    lbl_whitelist.set_markup(_("<b>Whitelist (allowlist)</b>"))
    lbl_whitelist.set_margin_start(10)
    hbox_whitelist_title.append(lbl_whitelist)

    hbox_whitelist_add = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_whitelist_add.set_margin_start(10)
    hbox_whitelist_add.set_margin_end(10)

    self.entry_whitelist = Gtk.Entry()
    self.entry_whitelist.set_hexpand(True)
    self.entry_whitelist.set_placeholder_text(_("Paste a URL or host, e.g. marketingplatform.google.com"))
    self.entry_whitelist.connect("activate", functools.partial(privacy.on_click_add_whitelist, self))

    self.btn_add_whitelist = Gtk.Button(label=_("Add to whitelist"))
    self.btn_add_whitelist.set_size_request(160, -1)
    self.btn_add_whitelist.set_sensitive(False)
    self.btn_add_whitelist.connect("clicked", functools.partial(privacy.on_click_add_whitelist, self))

    hbox_whitelist_add.append(self.entry_whitelist)
    hbox_whitelist_add.append(self.btn_add_whitelist)

    # Current allowlist entries, each with a Remove button
    self.listbox_whitelist = Gtk.ListBox()
    self.listbox_whitelist.set_selection_mode(Gtk.SelectionMode.NONE)

    scroll_whitelist = Gtk.ScrolledWindow()
    scroll_whitelist.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll_whitelist.set_min_content_height(120)
    scroll_whitelist.set_margin_start(10)
    scroll_whitelist.set_margin_end(10)
    scroll_whitelist.set_child(self.listbox_whitelist)

    # Status feedback (shown during enable/disable)
    self.lbl_hblock_progress_msg = Gtk.Label(xalign=0)
    self.lbl_hblock_progress_msg.set_margin_start(10)
    self.lbl_hblock_progress_msg.set_visible(False)

    self.progress = Gtk.ProgressBar()
    self.progress.set_pulse_step(0.2)
    self.progress.set_margin_start(10)
    self.progress.set_margin_end(10)
    self.progress.set_visible(False)

    # ── Append to vbox ─────────────────────────────────────────────────────

    vboxstack_privacy.append(hbox_title)
    vboxstack_privacy.append(hbox_sep)

    vboxstack_privacy.append(hbox_section1_title)
    vboxstack_privacy.append(hbox_ublock)

    vboxstack_privacy.append(hbox_sep2)
    vboxstack_privacy.append(hbox_section2_title)
    vboxstack_privacy.append(hbox_hblock_pkg)
    vboxstack_privacy.append(hbox_hblock_toggle)

    vboxstack_privacy.append(hbox_whitelist_title)
    vboxstack_privacy.append(hbox_whitelist_add)
    vboxstack_privacy.append(scroll_whitelist)

    vboxstack_privacy.append(self.lbl_hblock_progress_msg)
    vboxstack_privacy.append(self.progress)

    vboxstack_privacy.connect("map", lambda _w: init_privacy_lazy_load(self))
    init_privacy_lazy_load(self)

# ============================================================
# Authors: Erik Dubois
# ============================================================

import functools
from att_i18n import _


def _section_title(Gtk, text):
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl = Gtk.Label(xalign=0)
    lbl.set_markup("<b>{text}</b>".format(text=text))
    lbl.set_margin_start(10)
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    sep.set_valign(Gtk.Align.CENTER)
    box.append(lbl)
    box.append(sep)
    return box


def gui(self, Gtk, GdkPixbuf, vboxstack_iso, iso, fn, base_dir):
    """Create the ISO page — advertises and launches the Kiro ISO Builder (KIB)."""
    from gi.repository import Gdk

    fn.log_info("ISO page loaded — Kiro ISO Builder showcase")

    # ── Page title ────────────────────────────────────────────────
    hbox_iso_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    iso_title_lbl = Gtk.Label(xalign=0)
    iso_title_lbl.set_text(_("ISO"))
    iso_title_lbl.set_name("title")
    iso_title_lbl.set_margin_start(10)
    iso_title_lbl.set_margin_end(10)
    hbox_iso_title.append(iso_title_lbl)

    # ── Kiro ISO Builder ──────────────────────────────────────────
    hbox_kib_title = _section_title(Gtk, "Kiro ISO Builder")

    hbox_kib_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.kib_status_lbl = Gtk.Label(xalign=0)
    iso._refresh_kib_lbl(self)
    self.kib_status_lbl.set_margin_start(10)
    self.kib_status_lbl.set_margin_end(10)
    hbox_kib_status.append(self.kib_status_lbl)

    hbox_kib_intro = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    kib_intro_lbl = Gtk.Label(xalign=0)
    kib_intro_lbl.set_text(
        _(
            "Build your own personalised Arch-based ISO with the Kiro ISO Builder — "
            "a GTK4 front-end with one-click host pre-flight fixes."
        )
    )
    kib_intro_lbl.set_wrap(True)
    kib_intro_lbl.set_margin_start(10)
    kib_intro_lbl.set_margin_end(10)
    hbox_kib_intro.append(kib_intro_lbl)

    hbox_kib_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_kib_btns.set_margin_start(10)
    btn_install_kib = Gtk.Button(label=_("Install kiro-iso-builder"))
    btn_install_kib.connect("clicked", functools.partial(iso.on_install_kib_clicked, self))
    btn_remove_kib = Gtk.Button(label=_("Remove kiro-iso-builder"))
    btn_remove_kib.connect("clicked", functools.partial(iso.on_remove_kib_clicked, self))
    hbox_kib_btns.append(btn_install_kib)
    hbox_kib_btns.append(btn_remove_kib)

    hbox_kib_repo_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    if not fn.check_nemesis_repo_active():
        kib_repo_note_lbl = Gtk.Label(xalign=0)
        kib_repo_note_lbl.set_markup(_("<i>Enable the Nemesis repo (Pacman page) to install kiro-iso-builder</i>"))
        kib_repo_note_lbl.set_margin_start(10)
        kib_repo_note_lbl.set_margin_end(10)
        hbox_kib_repo_note.append(kib_repo_note_lbl)

    # ── Screenshot preview ────────────────────────────────────────
    hbox_kib_preview_title = _section_title(Gtk, _("Tab preview"))

    preview_tabs = [
        ("preflight", _("Pre-flight")),
        ("desktops", _("Desktops")),
        ("kernel", _("Kernel")),
        ("packages", _("Packages")),
        ("add-apps", _("Add apps")),
        ("build", _("Build")),
        ("done", _("Done")),
    ]

    preview_stack = Gtk.Stack()
    preview_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
    preview_stack.set_transition_duration(200)
    preview_stack.set_hexpand(True)

    preview_switcher = Gtk.StackSwitcher()
    preview_switcher.set_stack(preview_stack)
    preview_switcher.set_margin_start(10)
    preview_switcher.set_margin_top(5)

    img_w, img_h = 820, 740
    for key, label in preview_tabs:
        img_path = base_dir + f"/iso_images/{key}.png"
        if fn.path.isfile(img_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(img_path, img_w, img_h)
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            page_widget = Gtk.Picture.new_for_paintable(texture)
            page_widget.set_content_fit(Gtk.ContentFit.CONTAIN)
        else:
            page_widget = Gtk.Label(label=_("{label} — screenshot coming soon").format(label=label))
            page_widget.set_size_request(img_w, 200)
        preview_stack.add_titled(page_widget, key, label)

    # ── Launch ────────────────────────────────────────────────────
    hbox_kib_launch_title = _section_title(Gtk, _("Launch"))

    hbox_kib_launch = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_kib_launch.set_margin_start(10)
    self.btn_launch_kib = Gtk.Button(label=_("Launch Kiro ISO Builder"))
    self.btn_launch_kib.set_sensitive(fn.check_package_installed("kiro-iso-builder"))
    self.btn_launch_kib.connect("clicked", functools.partial(iso.on_launch_kib_clicked, self))
    hbox_kib_launch.append(self.btn_launch_kib)

    # ── Build a vanilla Arch ISO ──────────────────────────────────
    hbox_arch_title = _section_title(Gtk, _("Build a vanilla Arch ISO"))

    hbox_arch_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.archiso_status_lbl = Gtk.Label(xalign=0)
    iso._refresh_archiso_lbl(self)
    self.archiso_status_lbl.set_margin_start(10)
    self.archiso_status_lbl.set_margin_end(10)
    hbox_arch_status.append(self.archiso_status_lbl)

    hbox_arch_intro = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    arch_intro_lbl = Gtk.Label(xalign=0)
    arch_intro_lbl.set_text(
        _(
            "Builds the official Arch Linux installer ISO with archiso's releng profile. "
            "archiso is installed first if missing — if it cannot be installed, the build "
            "does not run. The ISO lands in ~/ArchISO."
        )
    )
    arch_intro_lbl.set_wrap(True)
    arch_intro_lbl.set_margin_start(10)
    arch_intro_lbl.set_margin_end(10)
    hbox_arch_intro.append(arch_intro_lbl)

    hbox_arch_build = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_arch_build.set_margin_start(10)
    btn_build_arch = Gtk.Button(label=_("Build vanilla Arch ISO"))
    btn_build_arch.connect("clicked", functools.partial(iso.on_build_arch_iso_clicked, self))
    hbox_arch_build.append(btn_build_arch)

    # ── Pack the page ─────────────────────────────────────────────
    vboxstack_iso.append(hbox_iso_title)
    vboxstack_iso.append(hbox_kib_title)
    vboxstack_iso.append(hbox_kib_status)
    vboxstack_iso.append(hbox_kib_intro)
    vboxstack_iso.append(hbox_kib_btns)
    vboxstack_iso.append(hbox_kib_repo_note)
    vboxstack_iso.append(hbox_kib_launch_title)
    vboxstack_iso.append(hbox_kib_launch)
    vboxstack_iso.append(hbox_kib_preview_title)
    vboxstack_iso.append(preview_switcher)
    vboxstack_iso.append(preview_stack)
    vboxstack_iso.append(hbox_arch_title)
    vboxstack_iso.append(hbox_arch_status)
    vboxstack_iso.append(hbox_arch_intro)
    vboxstack_iso.append(hbox_arch_build)

# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
# pylint:disable=C0103,W0612

import functools
import desktopr_gui
import themer
from att_i18n import _


def init_themer_lazy_load(self, fn):
    """Lazy load themer switch states when page is visible"""
    try:
        import time

        start = time.time()
        if hasattr(self, "poly"):
            if fn.os.path.isfile(fn.i3wm_config) and fn.check_package_installed("kiro-i3"):
                if themer.check_polybar(themer.get_list(fn.i3wm_config)):
                    self.poly.set_active(True)
        elapsed = time.time() - start
        fn.debug_print(f"[LAZY] Themer page switches loaded in {elapsed:.3f}s")
    except Exception:
        pass


def refresh_themer_dropdowns(self, fn, themer):
    """Repopulate all WM theme combos and update their sensitivity."""
    fn.log_info("Refreshing themer dropdowns after desktop change...")

    i3_ok = fn.os.path.isfile(fn.i3wm_config) and fn.check_package_installed("kiro-i3")
    if i3_ok:
        i3_list = themer.get_list(fn.i3wm_config)
        themer.get_i3_themes(self.i3_combo, i3_list)
    else:
        self.i3_combo.get_model().splice(0, self.i3_combo.get_model().get_n_items())
    self.i3_combo.set_sensitive(i3_ok)
    self.applyi3.set_sensitive(i3_ok)
    self.reseti3.set_sensitive(i3_ok)
    self.poly.set_sensitive(i3_ok)

    aw_ok = fn.os.path.isfile(fn.awesome_config) and fn.check_package_installed("kiro-awesome")
    if aw_ok:
        try:
            awesome_list = themer.get_list(fn.awesome_config)
            awesome_lines = themer.get_awesome_themes(awesome_list)
            aw_model = self.awesome_combo.get_model()
            aw_model.splice(0, aw_model.get_n_items(), awesome_lines)
            try:
                val = int(
                    themer.get_value(awesome_list, "local chosen_theme =").replace("themes[", "").replace("]", "")
                )
                self.awesome_combo.set_selected(val - 1)
            except Exception:
                pass
        except Exception:
            pass
    else:
        aw_model = self.awesome_combo.get_model()
        aw_model.splice(0, aw_model.get_n_items())
    self.awesome_combo.set_sensitive(aw_ok)
    self.applyawesome.set_sensitive(aw_ok)
    self.resetawesome.set_sensitive(aw_ok)

    qt_ok = fn.path_check(fn.qtile_config_theme) and fn.check_package_installed("kiro-qtile")
    if qt_ok:
        qtile_list = themer.get_list(fn.qtile_config)
        themer.get_qtile_themes(self.qtile_combo, qtile_list)
    else:
        self.qtile_combo.get_model().splice(0, self.qtile_combo.get_model().get_n_items())
    self.qtile_combo.set_sensitive(qt_ok)
    self.applyqtile.set_sensitive(qt_ok)
    self.resetqtile.set_sensitive(qt_ok)

    lft_ok = fn.os.path.isfile(fn.leftwm_config) and fn.check_package_installed("kiro-leftwm")
    if lft_ok and fn.path_check(fn.leftwm_config_theme_current):
        lft_model = self.leftwm_combo.get_model()
        lft_model.splice(0, lft_model.get_n_items(), list(fn.leftwm_themes_list))
        link_theme = fn.os.path.basename(fn.os.readlink(fn.leftwm_config_theme_current))
        for i, theme in enumerate(fn.leftwm_themes_list):
            if link_theme == theme:
                self.leftwm_combo.set_selected(i)
    else:
        self.leftwm_combo.get_model().splice(0, self.leftwm_combo.get_model().get_n_items())
    self.leftwm_combo.set_sensitive(lft_ok)
    self.applyleftwm.set_sensitive(lft_ok)
    self.resetleftwm.set_sensitive(lft_ok)
    self.removeleftwm.set_sensitive(lft_ok)

    fn.log_success("Themer dropdowns refreshed")


def gui(self, Gtk, GdkPixbuf, vboxstack_themer, themer, fn, base_dir):
    """Create the Themer GUI (i3, Awesome, Qtile, Leftwm theme switchers)."""
    from gi.repository import Gdk

    # Match desktop installer preview: decode resolution vs minimum Gtk.Picture size.
    img_load = desktopr_gui.IMAGE_PREVIEW_LOAD
    img_min = desktopr_gui.IMAGE_PREVIEW_MIN
    hbox_themer_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_themer_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_themer_title = Gtk.Label(xalign=0)
    lbl_themer_title.set_text(_("Theme Switcher"))
    lbl_themer_title.set_name("title")
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_themer_sep.append(hseparator)
    hbox_themer_title.append(lbl_themer_title)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    vbox_i3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_i3.set_hexpand(True)
    vbox_i3.set_vexpand(True)
    vbox_awesome = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_awesome.set_hexpand(True)
    vbox_awesome.set_vexpand(True)
    vbox_qtile = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_qtile.set_hexpand(True)
    vbox_qtile.set_vexpand(True)
    vbox_leftwm = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_leftwm.set_hexpand(True)
    vbox_leftwm.set_vexpand(True)

    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    stack.set_transition_duration(350)
    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)

    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
    stack_switcher.set_stack(stack)

    # ── I3WM tab ─────────────────────────────────────────────────────

    lbl_i3_instructions = Gtk.Label()
    lbl_i3_instructions.set_markup(
        _(
            "Reload your window manager with <b>Super + Shift + R</b> after you make your changes..\n"
            "First install the desktop via the Desktop menu then theme it."
        )
    )

    label = Gtk.Label()
    label.set_markup(_("Select theme\n<small>(install desktop first to be able to select a theme)</small>"))
    i3_model = Gtk.StringList()
    self.i3_combo = Gtk.DropDown(model=i3_model)
    self.i3_combo.set_size_request(280, 0)

    vbox_i3_combo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    hbox_i3_theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_awesome_theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_i3_polybar_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    vbox_i3_combo.append(self.i3_combo)

    self.applyi3 = Gtk.Button(label=_("Apply theme"))
    self.applyi3.connect("clicked", functools.partial(themer.i3wm_apply_clicked, self))
    self.reseti3 = Gtk.Button(label=_("Reset"))
    self.reseti3.connect("clicked", functools.partial(themer.i3wm_reset_clicked, self))

    lbl_polybar_toggle = Gtk.Label(label=_("Toggle {name}").format(name="polybar"))
    self.poly = Gtk.Switch()
    self.poly.connect("notify::active", functools.partial(themer.on_polybar_toggle, self))

    self.applyi3.set_sensitive(False)
    self.reseti3.set_sensitive(False)
    self.poly.set_sensitive(False)

    label.set_margin_start(10)
    label.set_margin_end(10)
    label.set_hexpand(True)
    hbox_i3_theme_row.append(label)
    vbox_i3_combo.set_margin_start(10)
    vbox_i3_combo.set_margin_end(10)
    hbox_i3_theme_row.append(vbox_i3_combo)  # pack_end

    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(base_dir + "/images/i3-sample.jpg", img_load, img_load)
    if self.i3_combo.get_selected_item() is None:
        pass
    elif fn.os.path.isfile(base_dir + "/themer_data/i3" + fn.get_combo_text(self.i3_combo) + ".jpg"):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            base_dir + "/themer_data/i3/" + fn.get_combo_text(self.i3_combo) + ".jpg",
            img_load,
            img_load,
        )
    texture = Gdk.Texture.new_for_pixbuf(pixbuf)
    i3_image = Gtk.Picture.new_for_paintable(texture)
    i3_image.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
    i3_image.set_size_request(img_min, img_min)
    i3_image.set_halign(Gtk.Align.CENTER)
    i3_image.set_valign(Gtk.Align.CENTER)
    i3_image.set_hexpand(True)
    i3_image.set_vexpand(False)

    self.i3_combo.connect(
        "notify::selected",
        lambda w, _p, img, tt, ab, iw, ih: fn.update_image(self, w, img, tt, ab, iw, ih),
        i3_image,
        "i3",
        base_dir,
        img_load,
        img_load,
    )

    hbox_awesome_theme_row.append(self.reseti3)  # pack_end
    hbox_awesome_theme_row.append(self.applyi3)  # pack_end

    hbox_i3_polybar_row.append(lbl_polybar_toggle)  # pack_end
    hbox_i3_polybar_row.append(self.poly)  # pack_end

    hbox_i3_theme_row.set_margin_start(10)
    hbox_i3_theme_row.set_margin_end(10)
    vbox_i3.append(hbox_i3_theme_row)
    vbox_i3.append(hbox_i3_polybar_row)
    vbox_i3.append(i3_image)
    lbl_i3_instructions.set_hexpand(True)
    lbl_i3_instructions.set_vexpand(True)
    vbox_i3.append(lbl_i3_instructions)
    vbox_i3.append(hbox_awesome_theme_row)  # pack_end

    # ── AwesomeWM tab ────────────────────────────────────────────────

    lbl_awesome_instructions = Gtk.Label()
    lbl_awesome_instructions.set_markup(
        _(
            "Reload your window manager with <b>Super + Shift + R</b> after you make your changes..\n"
            "First install the desktop via the Desktop menu then theme it."
        )
    )

    lbl_awesome_select_theme = Gtk.Label()
    lbl_awesome_select_theme.set_markup(
        _("Select theme\n<small>(install desktop first to be able to select a theme)</small>")
    )
    awesome_model = Gtk.StringList()
    self.awesome_combo = Gtk.DropDown(model=awesome_model)
    self.awesome_combo.set_size_request(280, 0)

    vbox_awesome_combo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    hbox_awesome_theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_awesome_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    vbox_qtile_combo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    hbox_awesome_preview = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_awesome_preview.set_hexpand(True)
    hbox_awesome_preview.set_vexpand(True)

    vbox_awesome_combo.append(self.awesome_combo)
    lbl_awesome_select_theme.set_margin_start(10)
    lbl_awesome_select_theme.set_margin_end(10)
    lbl_awesome_select_theme.set_hexpand(True)
    hbox_awesome_theme_row.append(lbl_awesome_select_theme)
    vbox_awesome_combo.set_margin_start(10)
    vbox_awesome_combo.set_margin_end(10)
    hbox_awesome_theme_row.append(vbox_awesome_combo)  # pack_end

    frame = Gtk.Frame(label="")
    frmlbl = frame.get_label_widget()
    frmlbl.set_markup(_("<b>Preview</b>"))

    try:
        selected = self.awesome_combo.get_selected_item()
        if selected is not None and fn.os.path.isfile(
            base_dir + "/themer_data/awesomewm/" + fn.get_combo_text(self.awesome_combo) + ".jpg"
        ):
            pimage = GdkPixbuf.Pixbuf.new_from_file_at_size(
                base_dir + "/themer_data/awesomewm/" + fn.get_combo_text(self.awesome_combo) + ".jpg",
                img_load,
                img_load,
            )
        else:
            pimage = GdkPixbuf.Pixbuf.new_from_file_at_size(
                base_dir + "/themer_data/awesomewm/multicolor.jpg",
                img_load,
                img_load,
            )
    except Exception:
        pimage = GdkPixbuf.Pixbuf.new_from_file_at_size(
            base_dir + "/themer_data/awesomewm/multicolor.jpg",
            img_load,
            img_load,
        )

    texture = Gdk.Texture.new_for_pixbuf(pimage)
    self.image = Gtk.Picture.new_for_paintable(texture)
    self.image.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
    self.image.set_size_request(img_min, img_min)
    self.image.set_halign(Gtk.Align.CENTER)
    self.image.set_valign(Gtk.Align.CENTER)
    self.image.set_hexpand(True)
    self.image.set_vexpand(False)

    self.awesome_combo.connect(
        "notify::selected",
        lambda w, _p, img, tt, ab, iw, ih: fn.update_image(self, w, img, tt, ab, iw, ih),
        self.image,
        "awesome",
        base_dir,
        img_load,
        img_load,
    )

    frame.set_name("awesome")
    frame.set_child(self.image)

    frame.set_hexpand(True)
    frame.set_vexpand(True)
    frame.set_margin_start(10)
    frame.set_margin_end(10)
    hbox_awesome_preview.append(frame)

    self.applyawesome = Gtk.Button(label=_("Apply theme"))
    self.applyawesome.connect("clicked", functools.partial(themer.awesome_apply_clicked, self))
    self.resetawesome = Gtk.Button(label=_("Reset"))
    self.resetawesome.connect("clicked", functools.partial(themer.awesome_reset_clicked, self))

    self.applyawesome.set_sensitive(False)
    self.resetawesome.set_sensitive(False)

    hbox_awesome_btns.append(self.resetawesome)  # pack_end
    hbox_awesome_btns.append(self.applyawesome)  # pack_end

    hbox_awesome_theme_row.set_margin_start(10)
    hbox_awesome_theme_row.set_margin_end(10)
    vbox_awesome.append(hbox_awesome_theme_row)
    hbox_awesome_preview.set_margin_start(10)
    hbox_awesome_preview.set_margin_end(10)
    vbox_awesome.append(hbox_awesome_preview)
    lbl_awesome_instructions.set_hexpand(True)
    lbl_awesome_instructions.set_vexpand(True)
    lbl_awesome_instructions.set_margin_start(10)
    lbl_awesome_instructions.set_margin_end(10)
    vbox_awesome.append(lbl_awesome_instructions)
    vbox_awesome.append(hbox_awesome_btns)  # pack_end

    # ── Qtile tab ────────────────────────────────────────────────────

    lbl_qtile_instructions = Gtk.Label()
    lbl_qtile_instructions.set_markup(
        _(
            "Reload your window manager with <b>Super + Shift + R</b> after you make your changes..\n"
            "First install the desktop via the Desktop menu then theme it."
        )
    )

    labelqt = Gtk.Label()
    labelqt.set_markup(_("Select theme\n<small>(install desktop first to be able to select a theme)</small>"))
    qtile_model = Gtk.StringList()
    self.qtile_combo = Gtk.DropDown(model=qtile_model)
    self.qtile_combo.set_size_request(280, 0)
    vbox_qtile_combo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    hbox_qtile_theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_qtile_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_qtile_spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    vbox_qtile_combo.append(self.qtile_combo)

    self.applyqtile = Gtk.Button(label=_("Apply theme"))
    self.applyqtile.connect("clicked", functools.partial(themer.qtile_apply_clicked, self))
    self.resetqtile = Gtk.Button(label=_("Reset"))
    self.resetqtile.connect("clicked", functools.partial(themer.qtile_reset_clicked, self))

    self.applyqtile.set_sensitive(False)
    self.resetqtile.set_sensitive(False)

    labelqt.set_margin_start(10)
    labelqt.set_margin_end(10)
    labelqt.set_hexpand(True)
    hbox_qtile_theme_row.append(labelqt)
    vbox_qtile_combo.set_margin_start(10)
    vbox_qtile_combo.set_margin_end(10)
    hbox_qtile_theme_row.append(vbox_qtile_combo)  # pack_end

    qtile_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(base_dir + "/images/qtile-sample.jpg", img_load, img_load)
    if self.qtile_combo.get_selected_item() is None:
        pass
    elif fn.os.path.isfile(base_dir + "/themer_data/qtile/" + fn.get_combo_text(self.qtile_combo) + ".jpg"):
        qtile_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            base_dir + "/themer_data/qtile/" + fn.get_combo_text(self.qtile_combo) + ".jpg",
            img_load,
            img_load,
        )
    texture = Gdk.Texture.new_for_pixbuf(qtile_pixbuf)
    qtile_image = Gtk.Picture.new_for_paintable(texture)
    qtile_image.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
    qtile_image.set_size_request(img_min, img_min)
    qtile_image.set_halign(Gtk.Align.CENTER)
    qtile_image.set_valign(Gtk.Align.CENTER)
    qtile_image.set_hexpand(True)
    qtile_image.set_vexpand(False)

    self.qtile_combo.connect(
        "notify::selected",
        lambda w, _p, img, tt, ab, iw, ih: fn.update_image(self, w, img, tt, ab, iw, ih),
        qtile_image,
        "qtile",
        base_dir,
        img_load,
        img_load,
    )

    hbox_qtile_btns.append(self.resetqtile)  # pack_end
    hbox_qtile_btns.append(self.applyqtile)  # pack_end

    vbox_qtile.append(hbox_qtile_theme_row)
    vbox_qtile.append(hbox_qtile_spacer)
    vbox_qtile.append(qtile_image)
    lbl_qtile_instructions.set_hexpand(True)
    lbl_qtile_instructions.set_vexpand(True)
    vbox_qtile.append(lbl_qtile_instructions)
    vbox_qtile.append(hbox_qtile_btns)  # pack_end

    # ── LeftWM tab ───────────────────────────────────────────────────

    self.status_leftwm = Gtk.Label()

    lbl_leftwm_instructions = Gtk.Label()
    lbl_leftwm_instructions.set_markup(
        _(
            "Reload your window manager with <b>Super + Shift + R</b> after you make your changes..\n"
            "First install the desktop via the Desktop menu then theme it."
        )
    )

    labellft = Gtk.Label()
    labellft.set_markup(_("Select theme\n<small>(install desktop first to be able to select a theme)</small>"))
    self.leftwm_combo = Gtk.DropDown.new_from_strings([])
    self.leftwm_combo.set_size_request(280, 0)
    self.leftwm_combo.connect("notify::selected", functools.partial(themer.on_leftwm_combo_changed, self))
    vbox_leftwm_combo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    hbox_leftwm_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_leftwm_spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    vbox_leftwm_combo.append(self.leftwm_combo)

    self.applyleftwm = Gtk.Button(label=_("Install and apply selected theme"))
    self.applyleftwm.connect("clicked", functools.partial(themer.leftwm_apply_clicked, self))
    self.removeleftwm = Gtk.Button(label=_("Remove selected theme and apply {name}").format(name="Candy"))
    self.removeleftwm.connect("clicked", functools.partial(themer.leftwm_remove_clicked, self))
    self.resetleftwm = Gtk.Button(label=_("Reset selected theme"))
    self.resetleftwm.connect("clicked", functools.partial(themer.leftwm_reset_clicked, self))

    self.applyleftwm.set_sensitive(False)
    self.resetleftwm.set_sensitive(False)
    self.removeleftwm.set_sensitive(False)

    hbox_leftwm_theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    labellft.set_margin_start(10)
    labellft.set_margin_end(10)
    labellft.set_hexpand(True)
    hbox_leftwm_theme_row.append(labellft)
    vbox_leftwm_combo.set_margin_start(10)
    vbox_leftwm_combo.set_margin_end(10)
    hbox_leftwm_theme_row.append(vbox_leftwm_combo)  # pack_end

    leftwm_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(base_dir + "/images/leftwm-sample.jpg", img_load, img_load)
    if self.leftwm_combo.get_selected_item() is None:
        pass
    elif fn.os.path.isfile(base_dir + "/themer_data/leftwm/" + fn.get_combo_text(self.leftwm_combo) + ".jpg"):
        leftwm_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            base_dir + "/themer_data/leftwm/" + fn.get_combo_text(self.leftwm_combo) + ".jpg",
            img_load,
            img_load,
        )
    texture = Gdk.Texture.new_for_pixbuf(leftwm_pixbuf)
    leftwm_image = Gtk.Picture.new_for_paintable(texture)
    leftwm_image.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
    leftwm_image.set_size_request(img_min, img_min)
    leftwm_image.set_halign(Gtk.Align.CENTER)
    leftwm_image.set_valign(Gtk.Align.CENTER)
    leftwm_image.set_hexpand(True)
    leftwm_image.set_vexpand(False)

    self.leftwm_combo.connect(
        "notify::selected",
        lambda w, _p, img, tt, ab, iw, ih: fn.update_image(self, w, img, tt, ab, iw, ih),
        leftwm_image,
        "leftwm",
        base_dir,
        img_load,
        img_load,
    )

    hbox_leftwm_btns.append(self.removeleftwm)  # pack_end
    hbox_leftwm_btns.append(self.resetleftwm)  # pack_end
    hbox_leftwm_btns.append(self.applyleftwm)  # pack_end

    vbox_leftwm.append(hbox_leftwm_theme_row)
    vbox_leftwm.append(hbox_leftwm_spacer)
    vbox_leftwm.append(leftwm_image)
    lbl_leftwm_instructions.set_hexpand(True)
    lbl_leftwm_instructions.set_vexpand(True)
    vbox_leftwm.append(lbl_leftwm_instructions)
    vbox_leftwm.append(hbox_leftwm_btns)  # pack_end

    # ── Pack to stack ────────────────────────────────────────────────

    stack.add_titled(vbox_awesome, "stack2", "Awesome")
    stack.add_titled(vbox_i3, "stack1", "I3")
    stack.add_titled(vbox_leftwm, "stack4", "Leftwm")
    stack.add_titled(vbox_qtile, "stack3", "Qtile")

    vbox.append(stack_switcher)
    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vbox.append(stack)

    vboxstack_themer.append(hbox_themer_title)
    vboxstack_themer.append(hbox_themer_sep)
    vbox.set_hexpand(True)
    vbox.set_vexpand(True)
    vboxstack_themer.append(vbox)

    def _on_themer_map(_w):
        init_themer_lazy_load(self, fn)
        refresh_themer_dropdowns(self, fn, themer)

    vboxstack_themer.connect("map", _on_themer_map)
    _on_themer_map(None)

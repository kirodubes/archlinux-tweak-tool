# ============================================================
# Authors: Erik Dubois
# ============================================================

import functools
import att_i18n
import locale_settings as locale
from att_i18n import _


def gui(self, Gtk, vboxstack_locale, fn):
    """Create the Locale, Keyboard and Timezone page."""

    # ── Title ─────────────────────────────────────────────
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text(_("Locale, Keyboard & Timezone"))
    lbl_title.set_name("title")
    lbl_title.set_margin_start(10)
    lbl_title.set_margin_end(10)
    hbox_title.append(lbl_title)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hsep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep.set_hexpand(True)
    hbox_sep.append(hsep)

    # ── Section: Current Settings ─────────────────────────
    hbox_status_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_status_header = Gtk.Label(xalign=0)
    lbl_status_header.set_markup(_("<b>Current Settings</b>"))
    lbl_status_header.set_margin_start(10)
    lbl_status_header.set_margin_top(15)
    lbl_status_header.set_margin_bottom(5)
    hbox_status_header.append(lbl_status_header)

    hbox_locale_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_locale_key = Gtk.Label(xalign=0)
    lbl_locale_key.set_text(_("System Locale:"))
    lbl_locale_key.set_margin_start(10)
    lbl_locale_key.set_size_request(185, -1)
    self.lbl_locale_current = Gtk.Label(xalign=0)
    self.lbl_locale_current.set_margin_start(10)
    hbox_locale_status.append(lbl_locale_key)
    hbox_locale_status.append(self.lbl_locale_current)

    hbox_language_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_language_key = Gtk.Label(xalign=0)
    lbl_language_key.set_text(_("Language (LANGUAGE):"))
    lbl_language_key.set_margin_start(10)
    lbl_language_key.set_size_request(185, -1)
    self.lbl_language_current = Gtk.Label(xalign=0)
    self.lbl_language_current.set_margin_start(10)
    hbox_language_status.append(lbl_language_key)
    hbox_language_status.append(self.lbl_language_current)

    hbox_keymap_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_keymap_key = Gtk.Label(xalign=0)
    lbl_keymap_key.set_text(_("Console Keymap:"))
    lbl_keymap_key.set_margin_start(10)
    lbl_keymap_key.set_size_request(185, -1)
    self.lbl_keymap_current = Gtk.Label(xalign=0)
    self.lbl_keymap_current.set_margin_start(10)
    hbox_keymap_status.append(lbl_keymap_key)
    hbox_keymap_status.append(self.lbl_keymap_current)

    hbox_x11_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_x11_key = Gtk.Label(xalign=0)
    lbl_x11_key.set_text(_("X11 Layout:"))
    lbl_x11_key.set_margin_start(10)
    lbl_x11_key.set_size_request(185, -1)
    self.lbl_x11_current = Gtk.Label(xalign=0)
    self.lbl_x11_current.set_margin_start(10)
    hbox_x11_status.append(lbl_x11_key)
    hbox_x11_status.append(self.lbl_x11_current)

    hbox_tz_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_tz_key = Gtk.Label(xalign=0)
    lbl_tz_key.set_text(_("Timezone:"))
    lbl_tz_key.set_margin_start(10)
    lbl_tz_key.set_size_request(185, -1)
    self.lbl_timezone_current = Gtk.Label(xalign=0)
    self.lbl_timezone_current.set_margin_start(10)
    hbox_tz_status.append(lbl_tz_key)
    hbox_tz_status.append(self.lbl_timezone_current)

    # ── Section: System Locale ─────────────────────────────
    hbox_locale_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_locale_header = Gtk.Label(xalign=0)
    lbl_locale_header.set_markup(_("<b>System Locale</b>"))
    lbl_locale_header.set_margin_start(10)
    lbl_locale_header.set_margin_top(15)
    lbl_locale_header.set_margin_bottom(5)
    hbox_locale_header.append(lbl_locale_header)

    hbox_locale_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.locale_dropdown = Gtk.DropDown.new_from_strings([""])
    self.locale_dropdown.set_size_request(300, -1)
    self.locale_dropdown.set_margin_start(10)
    btn_locale_apply = Gtk.Button(label=_("Apply"))
    btn_locale_apply.set_margin_start(10)
    btn_locale_apply.connect("clicked", functools.partial(locale.on_apply_locale, self))
    self.lbl_locale_result = Gtk.Label(xalign=0)
    self.lbl_locale_result.set_margin_start(10)
    self.lbl_locale_result.set_wrap(True)
    hbox_locale_ctrl.append(self.locale_dropdown)
    hbox_locale_ctrl.append(btn_locale_apply)
    hbox_locale_ctrl.append(self.lbl_locale_result)

    # ── Section: Individual Categories (LC_*) ─────────────
    hbox_lc_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_lc_header = Gtk.Label(xalign=0)
    lbl_lc_header.set_markup(_("<b>Individual Categories</b>"))
    lbl_lc_header.set_margin_start(10)
    lbl_lc_header.set_margin_top(15)
    lbl_lc_header.set_margin_bottom(5)
    hbox_lc_header.append(lbl_lc_header)

    hbox_lc_intro = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_lc_intro = Gtk.Label(xalign=0)
    lbl_lc_intro.set_wrap(True)
    lbl_lc_intro.set_text(
        _("Override single categories while keeping your system language — for example English "
        "with European numbers, currency and date formatting. \"Use LANG (default)\" leaves a "
        "category following your LANG.")
    )
    lbl_lc_intro.set_margin_start(10)
    lbl_lc_intro.set_margin_end(10)
    hbox_lc_intro.append(lbl_lc_intro)

    lc_labels = {
        "LC_NUMERIC": _("Numbers (LC_NUMERIC):"),
        "LC_MONETARY": _("Currency (LC_MONETARY):"),
        "LC_TIME": _("Date & time (LC_TIME):"),
    }
    self.lc_dropdowns = {}
    hbox_lc_rows = []
    for category in locale.LC_CATEGORIES:
        hbox_lc_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_lc_row = Gtk.Label(xalign=0)
        lbl_lc_row.set_text(lc_labels[category])
        lbl_lc_row.set_margin_start(10)
        lbl_lc_row.set_size_request(200, -1)
        dropdown_lc = Gtk.DropDown.new_from_strings([""])
        dropdown_lc.set_size_request(260, -1)
        btn_lc_apply = Gtk.Button(label=_("Apply"))
        btn_lc_apply.connect("clicked", functools.partial(locale.on_apply_lc, self, category))
        hbox_lc_row.append(lbl_lc_row)
        hbox_lc_row.append(dropdown_lc)
        hbox_lc_row.append(btn_lc_apply)
        self.lc_dropdowns[category] = dropdown_lc
        hbox_lc_rows.append(hbox_lc_row)

    hbox_lc_reset = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_lc_reset = Gtk.Button(label=_("Reset all to LANG"))
    btn_lc_reset.set_margin_start(10)
    btn_lc_reset.connect("clicked", functools.partial(locale.on_reset_lc, self))
    self.lbl_lc_result = Gtk.Label(xalign=0)
    self.lbl_lc_result.set_margin_start(10)
    self.lbl_lc_result.set_wrap(True)
    hbox_lc_reset.append(btn_lc_reset)
    hbox_lc_reset.append(self.lbl_lc_result)

    # ── Section: Generate New Locale ──────────────────────
    hbox_gen_locale_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_gen_locale_header = Gtk.Label(xalign=0)
    lbl_gen_locale_header.set_markup(_("<b>Generate New Locale</b>"))
    lbl_gen_locale_header.set_margin_start(10)
    lbl_gen_locale_header.set_margin_top(15)
    lbl_gen_locale_header.set_margin_bottom(5)
    hbox_gen_locale_header.append(lbl_gen_locale_header)

    hbox_gen_locale_load = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_load_available = Gtk.Button(label=_("Load Available Locales"))
    btn_load_available.set_margin_start(10)
    self.available_locale_dropdown = Gtk.DropDown.new_from_strings([""])
    self.available_locale_dropdown.set_size_request(300, -1)
    self.available_locale_dropdown.set_sensitive(False)
    hbox_gen_locale_load.append(btn_load_available)
    hbox_gen_locale_load.append(self.available_locale_dropdown)

    hbox_gen_locale_apply = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.btn_available_apply = Gtk.Button(label=_("Apply"))
    self.btn_available_apply.set_margin_start(10)
    self.btn_available_apply.set_sensitive(False)
    self.btn_available_apply.connect("clicked", functools.partial(locale.on_apply_generate_locale, self))
    self.lbl_gen_locale_result = Gtk.Label(xalign=0)
    self.lbl_gen_locale_result.set_margin_start(10)
    self.lbl_gen_locale_result.set_wrap(True)
    hbox_gen_locale_apply.append(self.btn_available_apply)
    hbox_gen_locale_apply.append(self.lbl_gen_locale_result)

    def _on_load_available(_widget):
        available = locale.get_available_locales()
        fn.log_info(f"Loaded {len(available)} available locales")
        model = Gtk.StringList()
        for loc in available:
            model.append(loc)
        self.available_locale_dropdown.set_model(model)
        self.available_locale_dropdown.set_sensitive(True)
        self.btn_available_apply.set_sensitive(True)

    btn_load_available.connect("clicked", _on_load_available)

    # ── Section: Console Keyboard (TTY) ───────────────────
    hbox_keymap_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_keymap_header = Gtk.Label(xalign=0)
    lbl_keymap_header.set_markup(_("<b>Console Keyboard (TTY)</b>"))
    lbl_keymap_header.set_margin_start(10)
    lbl_keymap_header.set_margin_top(15)
    lbl_keymap_header.set_margin_bottom(5)
    hbox_keymap_header.append(lbl_keymap_header)

    hbox_keymap_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.keymap_dropdown = Gtk.DropDown.new_from_strings([""])
    self.keymap_dropdown.set_size_request(300, -1)
    self.keymap_dropdown.set_margin_start(10)
    btn_keymap_apply = Gtk.Button(label=_("Apply"))
    btn_keymap_apply.set_margin_start(10)
    btn_keymap_apply.connect("clicked", functools.partial(locale.on_apply_keymap, self))
    btn_keymap_sync = Gtk.Button(label=_("Sync from X11"))
    btn_keymap_sync.set_margin_start(10)
    btn_keymap_sync.connect("clicked", functools.partial(locale.on_sync_keymap, self))
    self.lbl_keymap_result = Gtk.Label(xalign=0)
    self.lbl_keymap_result.set_margin_start(10)
    self.lbl_keymap_result.set_wrap(True)
    hbox_keymap_ctrl.append(self.keymap_dropdown)
    hbox_keymap_ctrl.append(btn_keymap_apply)
    hbox_keymap_ctrl.append(btn_keymap_sync)
    hbox_keymap_ctrl.append(self.lbl_keymap_result)

    # ── Section: X11 / Wayland Keyboard ───────────────────
    hbox_x11_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_x11_header = Gtk.Label(xalign=0)
    lbl_x11_header.set_markup(_("<b>X11 / Wayland Keyboard</b>"))
    lbl_x11_header.set_margin_start(10)
    lbl_x11_header.set_margin_top(15)
    lbl_x11_header.set_margin_bottom(5)
    hbox_x11_header.append(lbl_x11_header)

    hbox_x11_layout_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_x11_layout = Gtk.Label(xalign=0)
    lbl_x11_layout.set_text(_("Layout:"))
    lbl_x11_layout.set_margin_start(10)
    lbl_x11_layout.set_size_request(70, -1)
    self.x11_layout_dropdown = Gtk.DropDown.new_from_strings([""])
    self.x11_layout_dropdown.set_size_request(250, -1)
    hbox_x11_layout_ctrl.append(lbl_x11_layout)
    hbox_x11_layout_ctrl.append(self.x11_layout_dropdown)

    hbox_x11_variant_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_x11_variant = Gtk.Label(xalign=0)
    lbl_x11_variant.set_text(_("Variant:"))
    lbl_x11_variant.set_margin_start(10)
    lbl_x11_variant.set_size_request(70, -1)
    self.x11_variant_dropdown = Gtk.DropDown.new_from_strings([""])
    self.x11_variant_dropdown.set_size_request(250, -1)
    hbox_x11_variant_ctrl.append(lbl_x11_variant)
    hbox_x11_variant_ctrl.append(self.x11_variant_dropdown)

    hbox_x11_second_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_x11_second = Gtk.Label(xalign=0)
    lbl_x11_second.set_text(_("Second layout:"))
    lbl_x11_second.set_margin_start(10)
    lbl_x11_second.set_size_request(70, -1)
    self.x11_second_dropdown = Gtk.DropDown.new_from_strings([locale.X11_NO_SECOND])
    self.x11_second_dropdown.set_size_request(250, -1)
    lbl_x11_switch = Gtk.Label(xalign=0)
    lbl_x11_switch.set_text(_("Switch between the two layouts with Alt+Shift"))
    hbox_x11_second_ctrl.append(lbl_x11_second)
    hbox_x11_second_ctrl.append(self.x11_second_dropdown)
    hbox_x11_second_ctrl.append(lbl_x11_switch)

    # Translations of "Second layout:" are wider than the other labels; keep the dropdowns aligned in every language
    x11_label_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
    for lbl in (lbl_x11_layout, lbl_x11_variant, lbl_x11_second):
        x11_label_group.add_widget(lbl)

    hbox_x11_apply = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_x11_apply = Gtk.Button(label=_("Apply"))
    btn_x11_apply.set_margin_start(10)
    btn_x11_apply.connect("clicked", functools.partial(locale.on_apply_x11, self))
    self.lbl_x11_result = Gtk.Label(xalign=0)
    self.lbl_x11_result.set_margin_start(10)
    self.lbl_x11_result.set_wrap(True)
    hbox_x11_apply.append(btn_x11_apply)
    hbox_x11_apply.append(self.lbl_x11_result)

    # Suppress variant reset while populate_dropdowns sets initial selection
    self._locale_populating = [True]

    def _on_layout_changed(dropdown, _param):
        if self._locale_populating[0]:
            return
        layout_obj = dropdown.get_selected_item()
        if layout_obj is None:
            return
        new_variants = locale.get_x11_variants(layout_obj.get_string())
        new_model = Gtk.StringList()
        for v in new_variants:
            new_model.append(v)
        self.x11_variant_dropdown.set_model(new_model)
        self.x11_variant_dropdown.set_selected(0)

    self.x11_layout_dropdown.connect("notify::selected", _on_layout_changed)

    # ── Section: Timezone ─────────────────────────────────
    hbox_tz_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_tz_header = Gtk.Label(xalign=0)
    lbl_tz_header.set_markup(_("<b>Timezone</b>"))
    lbl_tz_header.set_margin_start(10)
    lbl_tz_header.set_margin_top(15)
    lbl_tz_header.set_margin_bottom(5)
    hbox_tz_header.append(lbl_tz_header)

    hbox_tz_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.timezone_dropdown = Gtk.DropDown.new_from_strings([""])
    self.timezone_dropdown.set_size_request(300, -1)
    self.timezone_dropdown.set_margin_start(10)
    btn_tz_apply = Gtk.Button(label=_("Apply"))
    btn_tz_apply.set_margin_start(10)
    btn_tz_apply.connect("clicked", functools.partial(locale.on_apply_timezone, self))
    self.lbl_tz_result = Gtk.Label(xalign=0)
    self.lbl_tz_result.set_margin_start(10)
    self.lbl_tz_result.set_wrap(True)
    hbox_tz_ctrl.append(self.timezone_dropdown)
    hbox_tz_ctrl.append(btn_tz_apply)
    hbox_tz_ctrl.append(self.lbl_tz_result)

    # ── Section: Language Packs ───────────────────────────
    hbox_langpack_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_langpack_header = Gtk.Label(xalign=0)
    lbl_langpack_header.set_markup(_("<b>Language Packs</b>"))
    lbl_langpack_header.set_margin_start(10)
    lbl_langpack_header.set_margin_top(15)
    lbl_langpack_header.set_margin_bottom(5)
    hbox_langpack_header.append(lbl_langpack_header)

    # Our 14 languages in their own names; "System (…)" follows LANG
    hbox_langpack_choice = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_langpack_choice = Gtk.Label(xalign=0)
    lbl_langpack_choice.set_text(_("Language"))
    lbl_langpack_choice.set_margin_start(10)
    lbl_langpack_choice.set_size_request(70, -1)
    self.langpack_codes = [None, *att_i18n.available()]
    langpack_labels = [_("System ({language})").format(language=att_i18n.name(att_i18n.SYSTEM))]
    langpack_labels.extend(att_i18n.name(code) for code in self.langpack_codes[1:])
    self.langpack_dropdown = Gtk.DropDown.new_from_strings(langpack_labels)
    self.langpack_dropdown.set_size_request(250, -1)
    self.langpack_choice = locale.langpack_default_choice()
    if self.langpack_choice in self.langpack_codes:
        self.langpack_dropdown.set_selected(self.langpack_codes.index(self.langpack_choice))

    def _on_langpack_choice(dropdown, _pspec):
        self.langpack_choice = self.langpack_codes[dropdown.get_selected()]
        fn.log_info(f"Language packs: showing {self.langpack_choice or 'system language'}")
        locale.refresh_language_packs(self)

    self.langpack_dropdown.connect("notify::selected", _on_langpack_choice)
    hbox_langpack_choice.append(lbl_langpack_choice)
    hbox_langpack_choice.append(self.langpack_dropdown)

    self.lbl_langpack_intro = Gtk.Label(xalign=0)
    self.lbl_langpack_intro.set_wrap(True)
    self.lbl_langpack_intro.set_margin_start(10)
    self.lbl_langpack_intro.set_margin_end(10)

    self.langpack_rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    self.langpack_rows.set_margin_top(5)
    self.langpack_missing = []

    hbox_langpack_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.btn_langpack_install = Gtk.Button(label=_("Install language packs"))
    self.btn_langpack_install.set_margin_start(10)
    self.btn_langpack_install.set_sensitive(False)
    self.btn_langpack_install.connect("clicked", functools.partial(locale.on_install_language_packs, self))
    self.lbl_langpack_result = Gtk.Label(xalign=0)
    self.lbl_langpack_result.set_margin_start(10)
    self.lbl_langpack_result.set_wrap(True)
    hbox_langpack_install.append(self.btn_langpack_install)
    hbox_langpack_install.append(self.lbl_langpack_result)

    # ── Assemble page: overview on top, one tab per topic (like the Network page) ──
    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    stack.set_transition_duration(350)
    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)
    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
    stack_switcher.set_stack(stack)
    stack_switcher.set_margin_start(10)
    stack_switcher.set_margin_top(15)

    tabs = [
        ("stack_locale_language", _("Language"), [
            hbox_locale_header, hbox_locale_ctrl, hbox_lc_header, hbox_lc_intro, *hbox_lc_rows, hbox_lc_reset,
            hbox_gen_locale_header, hbox_gen_locale_load, hbox_gen_locale_apply,
        ]),
        ("stack_locale_keyboard", _("Keyboard"), [
            hbox_keymap_header, hbox_keymap_ctrl, hbox_x11_header, hbox_x11_layout_ctrl, hbox_x11_variant_ctrl,
            hbox_x11_second_ctrl, hbox_x11_apply,
        ]),
        ("stack_locale_timezone", _("Timezone"), [hbox_tz_header, hbox_tz_ctrl]),
        ("stack_locale_langpacks", _("Language Packs"), [
            hbox_langpack_header, hbox_langpack_choice, self.lbl_langpack_intro, self.langpack_rows,
            hbox_langpack_install,
        ]),
    ]
    for name, title, widgets in tabs:
        vbox_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        for widget in widgets:
            vbox_tab.append(widget)
        stack.add_titled(vbox_tab, name, title)

    for widget in (hbox_title, hbox_sep, hbox_status_header, hbox_locale_status, hbox_language_status,
                   hbox_keymap_status, hbox_x11_status, hbox_tz_status, stack_switcher):
        vboxstack_locale.append(widget)
    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vboxstack_locale.append(stack)
    fn.log_info("Locale page built with tabs: Language, Keyboard, Timezone, Language Packs")

    locale.populate_dropdowns(self)

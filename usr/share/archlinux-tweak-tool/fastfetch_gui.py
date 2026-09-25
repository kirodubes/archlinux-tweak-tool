# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
import functools
import fastfetch

from gi.repository import Gdk
import desktopr_gui


def init_fastfetch_lazy_load(self, fn):
    try:
        fastfetch_enabled = fastfetch.get_term_rc() and fn.path.exists("/usr/bin/fastfetch")
        lolcat_enabled = False
        if fastfetch_enabled:
            config = fn.get_config_file()
            if config:
                with open(config, "r", encoding="utf-8") as f:
                    content = f.read()
                lolcat_enabled = "fastfetch | lolcat" in content
        self.ff_initializing = True
        if hasattr(self, "fast_util"):
            self.fast_util.set_active(fastfetch_enabled)
        if hasattr(self, "fast_lolcat"):
            self.fast_lolcat.set_active(lolcat_enabled)
            self.fast_lolcat.set_sensitive(fastfetch_enabled)
        self.ff_initializing = False
        fastfetch.set_fastfetch_ui_sensitive(self, fn.path.exists("/usr/bin/fastfetch"))
    except Exception as e:
        fn.debug_print(f"[LAZY] Fastfetch lazy load failed: {e}")


def gui(self, Gtk, GdkPixbuf, vboxstack_fastfetch, fastfetch, fn, base_dir):

    img_load = desktopr_gui.IMAGE_PREVIEW_LOAD
    img_min = desktopr_gui.IMAGE_PREVIEW_MIN
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    page_title_label = Gtk.Label(xalign=0)
    page_title_label.set_text("Fastfetch Editor")
    page_title_label.set_name("title")
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_separator.append(hseparator)
    hbox_title.append(page_title_label)

    self.hbox_ff_warning = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    warning_label = Gtk.Label(xalign=0)
    warning_label.set_markup("<b>Some distros have their own configuration and/or application, investigate</b>")
    warning_label.set_margin_start(10)
    warning_label.set_margin_end(10)
    self.hbox_ff_warning.append(warning_label)

    self.fast_util = Gtk.Switch()
    fast_util_label = Gtk.Label(xalign=0)
    fast_util_label.set_markup("Fastfetch install/enable")

    self.fast_lolcat = Gtk.Switch()
    fast_lolcat_label = Gtk.Label(xalign=0)
    fast_lolcat_label.set_markup("Lolcat install/enable")

    self.fast_util.connect("notify::active", functools.partial(fastfetch.on_fast_util_toggled, self))
    self.fast_lolcat.connect("notify::active", functools.partial(fastfetch.on_fast_lolcat_toggled, self))

    applyfastfetch = Gtk.Button(label="Apply Fastfetch configuration")
    resetnormalfastfetch = Gtk.Button(label="Reset your Fastfetch backup")
    resetattfastfetch = Gtk.Button(label="Reset Fastfetch (ATT defaults)")

    applyfastfetch.connect("clicked", functools.partial(fastfetch.on_apply_fast, self))
    resetnormalfastfetch.connect("clicked", functools.partial(fastfetch.on_reset_fast, self))
    resetattfastfetch.connect("clicked", functools.partial(fastfetch.on_reset_fast_att, self))

    self.hbox_ff_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.hbox_ff_checkboxes = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.hbox_ff_checkboxes.set_margin_top(10)
    hbox_switches = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

    self.os = Gtk.CheckButton(label="Show os")
    self.host = Gtk.CheckButton(label="Show hostname")
    self.kernel = Gtk.CheckButton(label="Show kernel")
    self.uptime = Gtk.CheckButton(label="Show uptime")
    self.packages = Gtk.CheckButton(label="Show packages")
    self.shell = Gtk.CheckButton(label="Show shell")
    self.display = Gtk.CheckButton(label="Show display")
    self.de = Gtk.CheckButton(label="Show de")
    self.wm = Gtk.CheckButton(label="Show wm")
    self.wmtheme = Gtk.CheckButton(label="Show wm theme")
    self.themes = Gtk.CheckButton(label="Show theme")
    self.icons = Gtk.CheckButton(label="Show icons")
    self.term = Gtk.CheckButton(label="Show terminal")
    self.termfont = Gtk.CheckButton(label="Show terminal font")
    self.cpu = Gtk.CheckButton(label="Show cpu")
    self.gpu = Gtk.CheckButton(label="Show gpu")
    self.mem = Gtk.CheckButton(label="Show memory")
    self.swap = Gtk.CheckButton(label="Show swap")
    self.cursor = Gtk.CheckButton(label="Show cursor")
    self.font = Gtk.CheckButton(label="Show font")
    self.disks = Gtk.CheckButton(label="Show disks")
    self.l_ip = Gtk.CheckButton(label="Show local ip")
    self.p_ip = Gtk.CheckButton(label="Show public ip")
    self.local = Gtk.CheckButton(label="Show locale")
    self.batt = Gtk.CheckButton(label="Show battery")
    self.pwr = Gtk.CheckButton(label="Show power adapter")
    self.title = Gtk.CheckButton(label="Show title")
    self.cblocks = Gtk.CheckButton(label="Show color blocks")

    fastfetch.get_checkboxes(self)

    self.hbox_ff_presets = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    presets_label = Gtk.Label()
    presets_label.set_text("Or choose what to select with a button")
    btn_all_selection = Gtk.Button(label="All")
    btn_all_selection.connect("clicked", functools.partial(fastfetch.on_click_fastfetch_all_selection, self))
    btn_normal_selection = Gtk.Button(label="Normal")
    btn_normal_selection.connect("clicked", functools.partial(fastfetch.on_click_fastfetch_normal_selection, self))
    btn_small_selection = Gtk.Button(label="Small")
    btn_small_selection.connect("clicked", functools.partial(fastfetch.on_click_fastfetch_small_selection, self))
    btn_none_selection = Gtk.Button(label="None")
    btn_none_selection.connect("clicked", functools.partial(fastfetch.on_click_fastfetch_none_selection, self))
    presets_label.set_margin_start(10)
    presets_label.set_margin_end(10)
    self.hbox_ff_presets.append(presets_label)
    btn_all_selection.set_margin_start(10)
    btn_all_selection.set_margin_end(10)
    self.hbox_ff_presets.append(btn_all_selection)
    btn_normal_selection.set_margin_start(10)
    btn_normal_selection.set_margin_end(10)
    self.hbox_ff_presets.append(btn_normal_selection)
    btn_small_selection.set_margin_start(10)
    btn_small_selection.set_margin_end(10)
    self.hbox_ff_presets.append(btn_small_selection)
    btn_none_selection.set_margin_start(10)
    btn_none_selection.set_margin_end(10)
    self.hbox_ff_presets.append(btn_none_selection)

    flowbox = Gtk.FlowBox()
    flowbox.set_valign(Gtk.Align.START)
    flowbox.set_max_children_per_line(10)
    flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

    flowbox.append(self.title)
    flowbox.append(self.os)
    flowbox.append(self.host)
    flowbox.append(self.kernel)
    flowbox.append(self.uptime)
    flowbox.append(self.packages)
    flowbox.append(self.shell)
    flowbox.append(self.display)
    flowbox.append(self.de)
    flowbox.append(self.wm)
    flowbox.append(self.wmtheme)
    flowbox.append(self.themes)
    flowbox.append(self.icons)
    flowbox.append(self.font)
    flowbox.append(self.cursor)
    flowbox.append(self.term)
    flowbox.append(self.termfont)
    flowbox.append(self.cpu)
    flowbox.append(self.gpu)
    flowbox.append(self.mem)
    flowbox.append(self.swap)
    flowbox.append(self.disks)
    flowbox.append(self.l_ip)
    flowbox.append(self.p_ip)
    flowbox.append(self.batt)
    flowbox.append(self.pwr)
    flowbox.append(self.local)
    flowbox.append(self.cblocks)

    flowbox.set_hexpand(True)
    flowbox.set_vexpand(True)
    flowbox.set_margin_start(10)
    flowbox.set_margin_end(10)
    self.hbox_ff_checkboxes.append(flowbox)

    self.fastfetch_image = Gtk.Picture()
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            base_dir + "/images/fastfetch.jpg",
            img_load,
            img_load,
        )
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        self.fastfetch_image.set_paintable(texture)
    except Exception as e:
        fn.debug_print(f"Failed to load fastfetch image: {e}")
    self.fastfetch_image.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
    self.fastfetch_image.set_size_request(img_min, img_min)
    self.fastfetch_image.set_hexpand(True)
    self.fastfetch_image.set_vexpand(False)
    self.fastfetch_image.set_halign(Gtk.Align.CENTER)
    self.fastfetch_image.set_valign(Gtk.Align.CENTER)
    self.fastfetch_image.set_margin_start(10)
    self.fastfetch_image.set_margin_end(10)
    self.fastfetch_image.set_margin_top(10)
    self.fastfetch_image.set_margin_bottom(10)

    fast_util_label.set_margin_start(10)
    fast_util_label.set_margin_end(10)
    hbox_switches.append(fast_util_label)
    self.fast_util.set_margin_start(30)
    self.fast_util.set_margin_end(30)
    hbox_switches.append(self.fast_util)
    hbox_switches.append(fast_lolcat_label)
    self.fast_lolcat.set_margin_start(30)
    self.fast_lolcat.set_margin_end(30)
    hbox_switches.append(self.fast_lolcat)

    self.hbox_ff_actions.set_halign(Gtk.Align.CENTER)
    self.hbox_ff_actions.append(resetnormalfastfetch)
    self.hbox_ff_actions.append(resetattfastfetch)
    self.hbox_ff_actions.append(applyfastfetch)

    hbox_startup_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    lbl_startup_header = Gtk.Label(xalign=0)
    lbl_startup_header.set_markup("<b>Shell Startup</b>")
    lbl_startup_header.set_margin_start(10)
    lbl_startup_header.set_margin_top(10)
    hbox_startup_header.append(lbl_startup_header)

    hbox_modules_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    lbl_modules_header = Gtk.Label(xalign=0)
    lbl_modules_header.set_markup("<b>Modules</b>")
    lbl_modules_header.set_margin_start(10)
    lbl_modules_header.set_margin_top(10)
    hbox_modules_header.append(lbl_modules_header)

    vboxstack_fastfetch.append(hbox_title)
    vboxstack_fastfetch.append(hbox_separator)
    vboxstack_fastfetch.append(self.hbox_ff_warning)
    vboxstack_fastfetch.append(hbox_startup_header)
    vboxstack_fastfetch.append(hbox_switches)
    vboxstack_fastfetch.append(hbox_modules_header)
    vboxstack_fastfetch.append(self.hbox_ff_checkboxes)
    vboxstack_fastfetch.append(self.fastfetch_image)
    vboxstack_fastfetch.append(self.hbox_ff_presets)

    vboxstack_fastfetch.append(self.hbox_ff_actions)

    hbox_remove = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    hbox_remove.set_halign(Gtk.Align.CENTER)
    hbox_remove.set_margin_top(10)
    hbox_remove.set_margin_bottom(10)
    self.btn_remove_fastfetch = Gtk.Button(label="Remove Fastfetch")
    self.btn_remove_fastfetch.connect("clicked", functools.partial(fastfetch.on_remove_fast, self))
    hbox_remove.append(self.btn_remove_fastfetch)
    vboxstack_fastfetch.append(hbox_remove)

    append_fftt_section(self, Gtk, vboxstack_fastfetch, fn)

    fn.GLib.idle_add(init_fastfetch_lazy_load, self, fn, priority=fn.GLib.PRIORITY_LOW)


def append_fftt_section(self, Gtk, vboxstack_fastfetch, fn):
    """Append the Fastfetch Tweak Tool install / launch section (also shown when no fastfetch config exists)."""
    hbox_fftt_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fftt_title_lbl = Gtk.Label(xalign=0)
    hbox_fftt_title_lbl.set_markup("<b>Fastfetch Tweak Tool</b>")
    hbox_fftt_title_lbl.set_margin_start(10)
    hbox_fftt_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_fftt_title_sep.set_hexpand(True)
    hbox_fftt_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_fftt_title.append(hbox_fftt_title_lbl)
    hbox_fftt_title.append(hbox_fftt_title_sep)

    hbox_fftt_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.fftt_status_lbl = Gtk.Label(xalign=0)
    fastfetch._refresh_fftt_lbl(self)
    self.fftt_status_lbl.set_margin_start(10)
    self.fftt_status_lbl.set_margin_end(10)
    hbox_fftt_status.append(self.fftt_status_lbl)

    hbox_fftt_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fftt_btns.set_margin_start(10)
    btn_install_fftt = Gtk.Button(label="Install fastfetch-tweak-tool")
    btn_install_fftt.connect("clicked", functools.partial(fastfetch.on_install_fastfetch_tweak_tool_clicked, self))
    btn_remove_fftt = Gtk.Button(label="Remove fastfetch-tweak-tool")
    btn_remove_fftt.connect("clicked", functools.partial(fastfetch.on_remove_fastfetch_tweak_tool_clicked, self))
    hbox_fftt_btns.append(btn_install_fftt)
    hbox_fftt_btns.append(btn_remove_fftt)

    hbox_fftt_repo_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    if not fn.check_nemesis_repo_active():
        fftt_repo_note_lbl = Gtk.Label(xalign=0)
        fftt_repo_note_lbl.set_markup("<i>Enable the Nemesis repo (Pacman page) to install fastfetch-tweak-tool</i>")
        fftt_repo_note_lbl.set_margin_start(10)
        fftt_repo_note_lbl.set_margin_end(10)
        hbox_fftt_repo_note.append(fftt_repo_note_lbl)

    hbox_fftt_launch = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fftt_launch.set_margin_start(10)
    self.btn_launch_fftt = Gtk.Button(label="Launch Fastfetch Tweak Tool")
    self.btn_launch_fftt.set_sensitive(fn.check_package_installed("fastfetch-tweak-tool"))
    self.btn_launch_fftt.connect("clicked", functools.partial(fastfetch.on_click_launch_fftt, self))
    hbox_fftt_launch.append(self.btn_launch_fftt)

    hbox_fftt_about = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    fftt_about_lbl = Gtk.Label(xalign=0)
    fftt_about_lbl.set_wrap(True)
    fftt_about_lbl.set_margin_start(10)
    fftt_about_lbl.set_margin_end(10)
    fftt_about_lbl.set_margin_top(6)
    fftt_about_lbl.set_markup(
        "<b>Design your fastfetch output in clicks, with a live preview.</b>\n\n"
        "• <b>Modules</b> — show / hide, reorder and edit per-module options\n"
        "• <b>Logo &amp; Appearance</b> — 500+ built-in logos or your own image; key, title and separator colours\n"
        "• <b>Install / Enable</b> — install fastfetch, add it to bash / zsh / fish startup, optional lolcat\n"
        "• <b>Presets &amp; Raw</b> — bundled presets or the Kiro default, restore a backup, edit the JSONC\n"
        "• <b>Live preview</b> — real fastfetch output as you tweak (with vte4)\n\n"
        "<i>A backup (config.jsonc.ftt-bak) is written before every save.</i>"
    )
    hbox_fftt_about.append(fftt_about_lbl)

    vboxstack_fastfetch.append(hbox_fftt_title)
    vboxstack_fastfetch.append(hbox_fftt_status)
    vboxstack_fastfetch.append(hbox_fftt_btns)
    vboxstack_fastfetch.append(hbox_fftt_repo_note)
    vboxstack_fastfetch.append(hbox_fftt_launch)
    vboxstack_fastfetch.append(hbox_fftt_about)

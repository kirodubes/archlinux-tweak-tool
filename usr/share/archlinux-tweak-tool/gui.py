# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

# ============Functions============
import functions as fn

import backup
import btrfs
import desktopr
import maintenance
import fastfetch
import performance
import sddm
import icons
import iso
import themes
import themer
import user
import zsh_theme

# =============GUI=================
import accessibility_gui
import backup_gui
import btrfs_gui
import celestial_gui
import icons_gui
import iso_gui
import themes_gui
import autostart
import desktopr_gui
import maintenance_gui
import fastfetch_gui
import kernel_gui
import pacman_gui
import performance_gui
import sddm_gui
import privacy_gui
import services_gui
import shell_gui
import themer_gui
import user_gui
import ai_gui
import logging_gui
import network_gui
import office_gui
import system_gui
import software_gui
import streamline_gui
import funding
import packages_gui
import wallpaper
import wallpaper_gui
import wayland
import wayland_gui
import plymouth_gui
import locale_gui
import dev_gui

_SDDM_HIDDEN_DISTROS = {"prismlinux"}
_ISO_HIDDEN_DISTROS = {"mylastarch"}


def gui(self, Gtk, Gdk, GdkPixbuf, base_dir, os, Pango, GLib):
    """creation of the gui"""

    # =======================================================
    #                       App Notifications
    # =======================================================

    hbox_notification = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    self.notification_revealer = Gtk.Revealer()
    self.notification_revealer.set_reveal_child(False)

    self.notification_label = Gtk.Label()
    self.notification_label.set_hexpand(True)

    notification_bg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    notification_bg.set_size_request(-1, 30)
    notification_bg.add_css_class("att-notification-bar")
    notification_bg.append(self.notification_label)

    css_notif = Gtk.CssProvider()
    css_notif.load_from_data(b".att-notification-bar { background-color: #1a1a1a; }")
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        css_notif,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

    self.notification_revealer.set_child(notification_bg)

    self.notification_revealer.set_hexpand(True)
    self.notification_revealer.set_vexpand(False)
    hbox_notification.append(self.notification_revealer)

    # ==========================================================
    #                       CONTAINER
    # ==========================================================

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    vbox_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

    hbox.set_hexpand(True)
    hbox.set_vexpand(True)

    # ==========================================================
    #              TOP HEADER — two stacked bars
    # ==========================================================
    # Bar 1 = app title; Bar 2 = "on <distro>" label + Support/Quit
    # actions. The action buttons are created further down (with the
    # quit handler) and appended to bar_actions there — this is their home.
    header_bars = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

    bar_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    bar_title.set_margin_start(12)
    bar_title.set_margin_end(12)
    bar_title.set_margin_top(8)
    bar_title.set_margin_bottom(2)
    lbl_app_title = Gtk.Label(xalign=0)
    lbl_app_title.set_markup('<span foreground="#FFA500"><b>Arch Linux Tweak Tool</b></span>')
    lbl_app_title.set_name("title")
    lbl_app_title.set_hexpand(True)
    bar_title.append(lbl_app_title)

    bar_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    bar_actions.set_margin_start(12)
    bar_actions.set_margin_end(12)
    bar_actions.set_margin_bottom(8)
    lbl_header_distro = Gtk.Label(xalign=0)
    lbl_header_distro.set_markup("on " + fn.get_distro_label())
    lbl_header_distro.set_hexpand(True)
    bar_actions.append(lbl_header_distro)

    header_bars.append(bar_title)
    header_bars.append(bar_actions)
    header_bars.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

    vbox.append(hbox_notification)
    vbox.append(header_bars)
    vbox.append(hbox)
    self.set_child(vbox)

    # ==========================================================
    #                    INITIALIZE STACK
    # ==========================================================
    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
    stack.set_transition_duration(350)
    self.att_stack = stack

    vboxstack1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_privacy = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_fastfetch = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_themer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_desktop = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_autostart = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_services = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_user = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_maintenance = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_shells = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_icons_horst = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_icons_neocandy = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_icons_surfn = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_iso = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_packages = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_performance = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_kernels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_sddm = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_ai = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_logging = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_network = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_system = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_office = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_software = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_streamline = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_themes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_wallpaper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_wayland = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_plymouth = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_locale = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_dev = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_accessibility = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_backup = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_btrfs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_celestial = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    # ==========================================================
    #                 LAZY TAB BUILDER
    # ==========================================================

    def _defer_tab(container, build_fn):
        built = [False]

        def on_map(_widget):
            if not built[0]:
                built[0] = True
                build_fn()

        container.connect("map", on_map)

    # ==========================================================
    #                 ICONS
    # ==========================================================

    def _build_icons_neocandy():
        _, _, extras = icons.get_available_icon_counts()
        fn.log_info(f"Neo Candy icons available to install: {extras}")
        icons_gui.gui_neocandy(self, Gtk, GdkPixbuf, vboxstack_icons_neocandy, icons, fn, base_dir)

    _defer_tab(vboxstack_icons_neocandy, _build_icons_neocandy)

    def _build_icons_surfn():
        _, surfn, _ = icons.get_available_icon_counts()
        fn.log_info(f"Surfn icons available to install: {surfn}")
        icons_gui.gui_surfn(self, Gtk, GdkPixbuf, vboxstack_icons_surfn, icons, fn, base_dir)

    _defer_tab(vboxstack_icons_surfn, _build_icons_surfn)

    def _build_icons_horst():
        icons_gui.gui_horst(self, Gtk, GdkPixbuf, vboxstack_icons_horst, icons, fn, base_dir)

    _defer_tab(vboxstack_icons_horst, _build_icons_horst)

    # ==========================================================
    #                 ISO
    # ==========================================================

    _defer_tab(vboxstack_iso, lambda: iso_gui.gui(self, Gtk, GdkPixbuf, vboxstack_iso, iso, fn, base_dir))

    # ==========================================================
    #                THEMES
    # ==========================================================

    _defer_tab(vboxstack_themes, lambda: themes_gui.gui(self, Gtk, GdkPixbuf, vboxstack_themes, themes, fn, base_dir))

    # ==========================================================
    #                CELESTIAL
    # ==========================================================

    _defer_tab(vboxstack_celestial, lambda: celestial_gui.gui(self, Gtk, vboxstack_celestial, fn))

    # ==========================================================
    #                AUTOSTART
    # ==========================================================

    _defer_tab(vboxstack_autostart, lambda: autostart.gui(self, Gtk, vboxstack_autostart, fn))

    # ==========================================================
    #                ACCESSIBILITY
    # ==========================================================

    _defer_tab(vboxstack_accessibility, lambda: accessibility_gui.gui(self, Gtk, vboxstack_accessibility, fn))

    # ==========================================================
    #                BACKUP
    # ==========================================================

    _defer_tab(vboxstack_backup, lambda: backup_gui.gui(self, Gtk, vboxstack_backup, backup, fn))

    # ==========================================================
    #                BTRFS
    # ==========================================================

    _defer_tab(vboxstack_btrfs, lambda: btrfs_gui.gui(self, Gtk, vboxstack_btrfs, btrfs, fn))

    # ==========================================================
    #                DESKTOP
    # ==========================================================

    _defer_tab(
        vboxstack_desktop, lambda: desktopr_gui.gui(self, Gtk, GdkPixbuf, vboxstack_desktop, desktopr, fn, base_dir)
    )

    # # ==========================================================
    # #               FASTFETCH
    # # ==========================================================

    def _build_fastfetch():
        if fn.check_package_installed("fastfetch-git"):
            fn.log_info("fastfetch-git is installed")
        elif fn.check_package_installed("fastfetch"):
            fn.log_info("fastfetch is installed")
        else:
            fn.log_info("fastfetch / fastfetch-git: not installed")

        if fn.file_check(fn.fastfetch_config):
            fastfetch_gui.gui(self, Gtk, GdkPixbuf, vboxstack_fastfetch, fastfetch, fn, base_dir)
        else:
            hbox_ff_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox_ff_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            lbl1 = Gtk.Label(xalign=0)
            lbl1.set_text("fastfetch Editor")
            lbl1.set_name("title")
            hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            hseparator.set_hexpand(True)
            hseparator.set_vexpand(False)
            hbox_ff_separator.append(hseparator)
            hbox_ff_title.append(lbl1)
            vboxstack_fastfetch.append(hbox_ff_title)
            vboxstack_fastfetch.append(hbox_ff_separator)
            fastfetch_message = Gtk.Label()
            fastfetch_message.set_hexpand(True)
            fastfetch_message.set_markup(
                "fastfetch configuration file not found.\nInstall <b>fastfetch</b> and enable it to use this tab."
            )
            vboxstack_fastfetch.append(fastfetch_message)
            fastfetch_gui.append_fftt_section(self, Gtk, vboxstack_fastfetch, fn)

    _defer_tab(vboxstack_fastfetch, _build_fastfetch)

    # # ==========================================================
    # #               MAINTENANCE
    # # ==========================================================

    _defer_tab(
        vboxstack_maintenance,
        lambda: maintenance_gui.gui(self, Gtk, Gdk, GdkPixbuf, vboxstack_maintenance, fn, maintenance),
    )

    # ==========================================================
    #                 PACMAN
    # ==========================================================

    def _build_pacman():
        if fn.file_check(fn.pacman):
            pacman_gui.gui(self, Gtk, vboxstack1, fn)

    _defer_tab(vboxstack1, _build_pacman)

    # ==========================================================
    #                 PRIVACY - HBLOCK
    # ==========================================================

    _defer_tab(vboxstack_privacy, lambda: privacy_gui.gui(self, Gtk, vboxstack_privacy, fn))

    # ==========================================================
    #                      SERVICES
    # ==========================================================

    _defer_tab(vboxstack_services, lambda: services_gui.gui(self, Gtk, vboxstack_services, fn))

    # ==========================================================
    #                        SHELLS
    # ==========================================================

    def _build_shells():
        active = fn.get_shell()
        fn.log_info(f"Shells tab loaded — active shell: {active}")
        shell_gui.gui(self, Gtk, vboxstack_shells, zsh_theme, base_dir, GdkPixbuf, fn)

    _defer_tab(vboxstack_shells, _build_shells)

    # ==========================================================
    #                 THEMER
    # ==========================================================

    def _build_themer():
        themer_gui.gui(self, Gtk, GdkPixbuf, vboxstack_themer, themer, fn, base_dir)
        self.on_desktop_changed = lambda: themer_gui.refresh_themer_dropdowns(self, fn, themer)

    _defer_tab(vboxstack_themer, _build_themer)

    # # ==========================================================
    # #                USER
    # # ==========================================================

    _defer_tab(vboxstack_user, lambda: user_gui.gui(self, Gtk, vboxstack_user, user, fn))

    # =====================================================
    #                       PACKAGES - EXPORT/INSTALL
    # =====================================================

    _defer_tab(vboxstack_packages, lambda: packages_gui.gui(self, Gtk, vboxstack_packages, fn))

    # =====================================================
    #                       PERFORMANCE
    # =====================================================

    def _build_performance():
        performance_gui.gui(self, Gtk, vboxstack_performance, performance, fn)

    _defer_tab(vboxstack_performance, _build_performance)

    # =====================================================
    #                       SDDM
    # =====================================================

    def _build_sddm():
        sddm_gui.gui(self, Gtk, Pango, vboxstack_sddm, sddm, fn)

        def _rebuild_sddm_page():
            child = vboxstack_sddm.get_first_child()
            while child:
                vboxstack_sddm.remove(child)
                child = vboxstack_sddm.get_first_child()
            sddm_gui.gui(self, Gtk, Pango, vboxstack_sddm, sddm, fn)

        self.rebuild_sddm_page = _rebuild_sddm_page

    _defer_tab(vboxstack_sddm, _build_sddm)

    _defer_tab(vboxstack_kernels, lambda: kernel_gui.gui(self, Gtk, vboxstack_kernels, fn))

    _defer_tab(vboxstack_ai, lambda: ai_gui.gui(self, Gtk, vboxstack_ai, fn))

    _defer_tab(vboxstack_logging, lambda: logging_gui.gui(self, Gtk, vboxstack_logging, fn))

    _defer_tab(vboxstack_network, lambda: network_gui.gui(self, Gtk, vboxstack_network, fn))

    _defer_tab(vboxstack_system, lambda: system_gui.gui(self, Gtk, vboxstack_system, fn))

    _defer_tab(vboxstack_office, lambda: office_gui.gui(self, Gtk, vboxstack_office, fn))

    _defer_tab(vboxstack_software, lambda: software_gui.gui(self, Gtk, vboxstack_software, fn))

    _defer_tab(vboxstack_streamline, lambda: streamline_gui.gui(self, Gtk, vboxstack_streamline, fn))

    def _build_wallpaper():
        wallpaper_gui.gui(self, Gtk, Pango, vboxstack_wallpaper, wallpaper, fn, base_dir)

    _defer_tab(vboxstack_wallpaper, _build_wallpaper)

    _defer_tab(vboxstack_wayland, lambda: wayland_gui.gui(self, Gtk, vboxstack_wayland, wayland, desktopr, fn, base_dir))

    _defer_tab(vboxstack_plymouth, lambda: plymouth_gui.gui(self, Gtk, vboxstack_plymouth, fn))

    _defer_tab(vboxstack_locale, lambda: locale_gui.gui(self, Gtk, vboxstack_locale, fn))

    if fn.DEV:
        dev_gui.gui(self, Gtk, vboxstack_dev, fn)

    # ==========================================================
    #                   ADD TO WINDOW
    # ==========================================================
    if fn.DEV:
        stack.add_titled(vboxstack_dev, "stack_dev", "Dev")

    stack.add_titled(vboxstack_accessibility, "stack_accessibility", "Accessibility")  # accessibility tools

    stack.add_titled(vboxstack_ai, "stack_ai", "AI Tools")  # AI tools

    stack.add_titled(vboxstack_themes, "stack_themes", "Arc themes")  # arc themes

    stack.add_titled(vboxstack_autostart, "stack13", "Autostart")  # Autostart

    stack.add_titled(vboxstack_backup, "stack_backup", "Backup")  # personal-file backup (Pika / Vorta)

    # Always listed, even off btrfs: the page then renders disabled with Status
    # explaining why, so the sidebar is identical on every machine (docs/videos).
    stack.add_titled(vboxstack_btrfs, "stack_btrfs", "Btrfs")  # btrfs snapshots

    stack.add_titled(vboxstack_celestial, "stack_celestial", "Celestial themes")  # celestial GTK themes

    # Desktop installer (DEs + X11 WMs) and the Wayland WM picker, grouped as an
    # adjacent pair — the core Kiro selling point. Sidebar shows pages in add-order,
    # so these sit together. The broad page stays "Desktop" (no X11 claim) because it
    # also installs Wayland-default DEs like Plasma/GNOME.
    stack.add_titled(vboxstack_desktop, "stack12", "Desktop")  # DEs + X11 WMs
    stack.add_titled(vboxstack_wayland, "stack_wayland", "Desktop - Wayland")  # Wayland WM picker

    stack.add_titled(vboxstack_fastfetch, "stack4", "Fastfetch")  # fastfetch config

    stack.add_titled(vboxstack_icons_horst, "stack_icons_horst", "Icons Horst")  # Horst colour-folder icons (both sets)
    stack.add_titled(vboxstack_icons_neocandy, "stack_icons_neocandy", "Icons Neo Candy")  # Neo Candy icon themes
    stack.add_titled(vboxstack_icons_surfn, "stack_icons_surfn", "Icons Surfn")  # Surfn icon themes

    if fn.distr not in _ISO_HIDDEN_DISTROS:
        stack.add_titled(vboxstack_iso, "stack_iso", "ISO")  # Kiro ISO Builder showcase

    stack.add_titled(vboxstack_kernels, "stack28", "Kernels")  # kernel manager

    stack.add_titled(vboxstack_locale, "stack_locale", "Locale")  # locale, keyboard, timezone

    stack.add_titled(vboxstack_logging, "stack_logging", "Logging")  # log investigator

    stack.add_titled(vboxstack_maintenance, "stack19", "Maintenance")  # Maintenance

    stack.add_titled(vboxstack_network, "stack_network", "Network")  # network + samba

    stack.add_titled(vboxstack_office, "stack_office", "Office")  # office suites + productivity apps

    stack.add_titled(vboxstack_packages, "packages", "Packages")  # Packages

    stack.add_titled(vboxstack1, "stack6", "Pacman")  # Pacman config

    stack.add_titled(vboxstack_plymouth, "stack_plymouth", "Plymouth")  # Plymouth boot theme

    stack.add_titled(vboxstack_privacy, "stack2", "Privacy")  # Privacy

    stack.add_titled(vboxstack_performance, "stack27", "Performance")  # performance

    if fn.distr not in _SDDM_HIDDEN_DISTROS and not (
        fn.check_service_enabled("plasma-login") or fn.check_service_enabled("plasmalogin")
    ):
        stack.add_titled(vboxstack_sddm, "stack_sddm", "Sddm")  # sddm

    stack.add_titled(vboxstack_services, "stack14", "Services")  # services

    stack.add_titled(vboxstack_shells, "stack23", "Shells")  # shell

    stack.add_titled(vboxstack_software, "stack_software", "Software")  # software installers

    if fn.get_distro_label() == "Kiro":
        # Kiro-only: the category list is sourced from the Kiro ISO package set.
        stack.add_titled(vboxstack_streamline, "stack_streamline", "Streamline")  # remove optional apps by category

    stack.add_titled(vboxstack_system, "stack_system", "System")  # system inspector

    stack.add_titled(vboxstack_themer, "stack11", "Themer")  # Themer

    stack.add_titled(vboxstack_user, "stack18", "User")  # user

    stack.add_titled(vboxstack_wallpaper, "stack_wallpaper", "Wallpaper")  # wallpaper

    stack_switcher = Gtk.StackSidebar()
    stack_switcher.set_name("sidebar")
    stack_switcher.set_stack(stack)

    # =====================================================
    #                       LOGO
    # =====================================================

    ivbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    # =====================================================
    #               RESTART/QUIT BUTTON
    # =====================================================

    def on_quit(widget):
        fn.unlink("/tmp/att.lock")
        self.get_application().quit()
        fn.debug_print("Thanks for using ArchLinux Tweak Tool")
        fn.debug_print("Report issues to make it even better")
        fn.debug_print("=" * 75)

    btn_restart_att = Gtk.Button(label="Restart ATT")
    btn_restart_att.set_size_request(100, 30)
    btn_restart_att.set_visible(False)
    btn_restart_att.connect("clicked", self.on_refresh_att_clicked)
    btn_quit_att = Gtk.Button(label="Quit ATT")
    btn_quit_att.set_size_request(100, 30)
    btn_quit_att.connect("clicked", on_quit)
    btn_support_att = Gtk.Button(label="♥ Support")
    btn_support_att.set_size_request(100, 30)
    btn_support_att.add_css_class("support-button")
    btn_support_att.set_tooltip_text("Support the project")
    btn_support_att.connect("clicked", lambda _w: funding.show_support_dialog(self))

    # Action buttons live in the second header bar (built in the CONTAINER block).
    bar_actions.append(btn_restart_att)
    bar_actions.append(btn_support_att)
    bar_actions.append(btn_quit_att)

    # ── Page search ────────────────────────────────────────
    # Titles are matched live off the stack; aliases come from the generated
    # search_index.json (rebuilt by gen-search-index.py during up.sh).
    search_synonyms = {}
    search_index_path = base_dir + "/search_index.json"
    if fn.path.isfile(search_index_path):
        try:
            with open(search_index_path, encoding="utf-8") as f:
                index_pages = fn.json.load(f).get("pages", [])
            # Hand-authored keywords are authoritative; scraped labels only fill gaps.
            for field in ("keywords", "labels"):
                for page in index_pages:
                    child = page.get("child", "")
                    for keyword in page.get(field, []):
                        search_synonyms.setdefault(keyword.lower(), child)
        except (ValueError, OSError) as e:
            fn.log_warn(f"Could not load search index: {e}")

    def _find_page(query):
        """Return the stack child-name best matching query, or None."""
        q = query.strip().lower()
        if len(q) < 2:
            return None
        pages = stack.get_pages()
        titles = [
            (pages.get_item(i).get_title() or "", pages.get_item(i).get_name() or "")
            for i in range(pages.get_n_items())
        ]
        for matches in (
            lambda t: t == q,
            lambda t: t.startswith(q),
            lambda t: q in t,
        ):
            for title, name in titles:
                if matches(title.lower()):
                    return name
        for keyword, child in search_synonyms.items():
            if keyword == q or keyword.startswith(q):
                return child
        for keyword, child in search_synonyms.items():
            if q in keyword:
                return child
        return None

    def on_search_activate(entry):
        text = entry.get_text().strip()
        child = _find_page(text)
        if child and stack.get_child_by_name(child) is not None:
            stack.set_visible_child_name(child)
            fn.log_info(f"Search jumped to page: {child}")
        elif text:
            fn.show_in_app_notification(self, f"No page matches '{text}'")
            fn.log_warn(f"Search: no page matched '{text}'")

    search_entry = Gtk.SearchEntry()
    search_entry.set_placeholder_text("Search (Enter)")
    search_entry.set_margin_start(6)
    search_entry.set_margin_end(6)
    search_entry.connect("activate", on_search_activate)
    ivbox.append(search_entry)

    stack_switcher.set_size_request(70, -1)
    stack_switcher.set_hexpand(False)
    stack_switcher.set_vexpand(True)
    ivbox.append(stack_switcher)

    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vbox_content.append(stack)

    # make the content scrollable
    scrolledWindow = Gtk.ScrolledWindow()
    scrolledWindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scrolledWindow.set_child(vbox_content)

    hbox.append(ivbox)
    scrolledWindow.set_hexpand(True)
    scrolledWindow.set_vexpand(True)
    hbox.append(scrolledWindow)

    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)

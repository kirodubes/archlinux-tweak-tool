# ============================================================
# Authors: Erik Dubois
# ============================================================

import streamline
from gi.repository import GLib
from att_i18n import _, ngettext


def gui(self, Gtk, vbox_stack, fn):
    """Create the Streamline page — remove optional apps by category, save/import profiles."""
    categories = fn.load_streamline_categories()

    # ── Title ──────────────────────────────────────────────
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_name("title")
    lbl_title.set_text(_("Streamline"))
    lbl_title.set_margin_start(10)
    lbl_title.set_margin_end(10)
    hbox_title.append(lbl_title)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hbox_sep.append(hseparator)

    lbl_desc = Gtk.Label(xalign=0)
    lbl_desc.set_markup(
        _(
            " Remove optional apps that shipped on this system, grouped by category.\n"
            " Each section shows apps <b>still installed</b> (left, tick to remove) next to those"
            " <b>already removed</b> (right, tick to reinstall).\n"
            " Tick a <b>category</b> to select all its apps, then untick the ones you want to keep.\n"
            " <b>Save profile</b> stores your current selection. <b>Save removed list</b> records what's actually\n"
            " gone now (the full list minus what's still installed). Import either on a future install to re-remove."
        )
    )
    lbl_desc.set_margin_start(10)
    lbl_desc.set_margin_top(5)
    lbl_desc.set_margin_bottom(10)

    self.streamline_recursive = Gtk.CheckButton(label=_("Also remove unused dependencies (-Rns)"))
    self.streamline_recursive.set_active(True)
    self.streamline_recursive.set_margin_start(10)

    # ── Category list (scrollable) ─────────────────────────
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_vexpand(True)
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    container.set_margin_start(10)
    container.set_margin_end(10)
    scrolled.set_child(container)

    # Guard so programmatic state changes don't trigger each other's handlers.
    syncing = {"on": False}

    def sync_header(category_check, child_checks):
        """Make the category header reflect its children: all/none/some (indeterminate)."""
        states = [c.get_active() for c in child_checks]
        syncing["on"] = True
        if all(states):
            category_check.set_inconsistent(False)
            category_check.set_active(True)
        elif not any(states):
            category_check.set_inconsistent(False)
            category_check.set_active(False)
        else:
            category_check.set_active(False)
            category_check.set_inconsistent(True)
        syncing["on"] = False

    def on_category_toggled(category_check, child_checks):
        if syncing["on"]:
            return
        active = category_check.get_active()
        syncing["on"] = True
        for child_check in child_checks:
            child_check.set_active(active)
        category_check.set_inconsistent(False)
        syncing["on"] = False

    def on_child_toggled(_child_check, category_check, child_checks):
        if syncing["on"]:
            return
        sync_header(category_check, child_checks)

    def apply_filter(query):
        q = query.strip().lower()
        for headers, items in getattr(self, "streamline_sections", []):
            any_visible = False
            for name, widget in items:
                match = (not q) or (q in name)
                widget.set_visible(match)
                if match and name:
                    any_visible = True
            for header_widget in headers:
                header_widget.set_visible(any_visible)

    search_entry = Gtk.SearchEntry()
    search_entry.set_placeholder_text(_("Search packages…"))
    search_entry.set_margin_start(10)
    search_entry.set_margin_end(10)
    search_entry.connect("search-changed", lambda entry: apply_filter(entry.get_text()))

    def populate():
        child = container.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            container.remove(child)
            child = nxt

        self.streamline_checks = []
        self.streamline_reinstall_checks = []
        self.streamline_groups = []
        self.streamline_sections = []
        all_pkgs = [pkg for pkgs in categories.values() for pkg in pkgs]
        installed = fn.check_packages_installed(all_pkgs)

        # One grid for the whole list so left/right cells share rows and line up
        # vertically — installed (col 0) beside removed (col 1), row by row.
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(15)
        grid.set_row_spacing(2)
        container.append(grid)

        def _attach(widget, col, row, top=0, start=0):
            widget.set_valign(Gtk.Align.CENTER)
            if top:
                widget.set_margin_top(top)
            if start:
                widget.set_margin_start(start)
            grid.attach(widget, col, row, 1, 1)

        # Column captions.
        left_caption = Gtk.Label(xalign=0)
        left_caption.set_markup(_("<b>Still installed</b>"))
        right_caption = Gtk.Label(xalign=0)
        right_caption.set_markup(_("<b>Already removed</b>"))
        _attach(left_caption, 0, 0)
        _attach(right_caption, 1, 0)
        rule = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(rule, 0, 1, 2, 1)
        grid_row = 2

        shown = False
        for category, pkgs in categories.items():
            present_installed = [pkg for pkg in pkgs if installed.get(pkg)]
            present_removed = [pkg for pkg in pkgs if not installed.get(pkg)]
            if not present_installed and not present_removed:
                continue
            shown = True

            # Section title in BOTH columns, on the same grid row → aligned.
            left_header = Gtk.Label(xalign=0)
            left_header.set_markup(f"<b>{GLib.markup_escape_text(category)}</b>")
            if present_installed:
                category_check = Gtk.CheckButton()
                category_check.set_child(left_header)
                _attach(category_check, 0, grid_row, top=10)
                left_widget = category_check
            else:
                category_check = None
                _attach(left_header, 0, grid_row, top=10)
                left_widget = left_header
            right_header = Gtk.Label(xalign=0)
            right_header.set_markup(f"<b>{GLib.markup_escape_text(category)}</b>")
            if present_removed:
                reinstall_check = Gtk.CheckButton()
                reinstall_check.set_child(right_header)
                _attach(reinstall_check, 1, grid_row, top=10)
                right_widget = reinstall_check
            else:
                reinstall_check = None
                _attach(right_header, 1, grid_row, top=10)
                right_widget = right_header
            grid_row += 1

            removed_to_show = present_removed if present_removed else ["—"]
            placeholder = not present_removed
            child_checks = []
            reinstall_child_checks = []
            section_items = []
            for i in range(max(len(present_installed), len(removed_to_show))):
                if i < len(present_installed):
                    pkg = present_installed[i]
                    row_check = Gtk.CheckButton(label=pkg)
                    self.streamline_checks.append((pkg, row_check))
                    child_checks.append(row_check)
                    row_check.connect("toggled", on_child_toggled, category_check, child_checks)
                    _attach(row_check, 0, grid_row, start=25)
                    section_items.append((pkg.lower(), row_check))
                if i < len(removed_to_show):
                    if placeholder:
                        cell = Gtk.Label(xalign=0)
                        cell.set_text("—")
                        cell.add_css_class("dim-label")
                        _attach(cell, 1, grid_row, start=15)
                        section_items.append(("", cell))
                    else:
                        pkg_removed = removed_to_show[i]
                        reinstall_row = Gtk.CheckButton(label=pkg_removed)
                        self.streamline_reinstall_checks.append((pkg_removed, reinstall_row))
                        reinstall_child_checks.append(reinstall_row)
                        reinstall_row.connect("toggled", on_child_toggled, reinstall_check, reinstall_child_checks)
                        _attach(reinstall_row, 1, grid_row, start=15)
                        section_items.append((pkg_removed.lower(), reinstall_row))
                grid_row += 1

            if category_check is not None:
                category_check.connect("toggled", on_category_toggled, child_checks)
                self.streamline_groups.append((category_check, child_checks))
            if reinstall_check is not None:
                reinstall_check.connect("toggled", on_category_toggled, reinstall_child_checks)

            self.streamline_sections.append(([left_widget, right_widget], section_items))

        if not shown:
            lbl_empty = Gtk.Label(xalign=0)
            lbl_empty.set_text(_("No optional apps from the Kiro package list are installed on this system."))
            lbl_empty.set_margin_top(10)
            container.append(lbl_empty)

        apply_filter(search_entry.get_text())

    def on_remove(_widget):
        packages = streamline.selected_packages(self)
        if not packages:
            fn.log_warn("Streamline: remove clicked with no packages selected")
            fn.show_in_app_notification(self, _("No packages selected"))
            return
        recursive = self.streamline_recursive.get_active()
        returncode, preview = streamline.removal_preview(packages, recursive)

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=ngettext(
                "Remove {count} selected package?", "Remove {count} selected packages?", len(packages)
            ).format(count=len(packages)),
        )
        if returncode == 0:
            dialog.props.secondary_text = _("This will remove:\n\n{preview}").format(preview=preview)
        else:
            dialog.props.secondary_text = _("pacman reported a problem with this selection:\n\n{preview}").format(preview=preview)
            # Removal would fail (e.g. a dependency is required elsewhere) — block confirming it.
            dialog.set_response_sensitive(Gtk.ResponseType.YES, False)
        dialog.set_default_response(Gtk.ResponseType.NO)

        def on_response(_dialog, response):
            _dialog.destroy()
            if response == Gtk.ResponseType.YES:
                streamline.do_remove(self, packages, recursive, populate)

        dialog.connect("response", on_response)
        dialog.present()

    def on_reinstall(_widget):
        packages = streamline.selected_reinstall(self)
        if not packages:
            fn.log_warn("Streamline: reinstall clicked with no packages selected")
            fn.show_in_app_notification(self, _("No removed packages selected"))
            return
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=ngettext(
                "Reinstall {count} selected package?", "Reinstall {count} selected packages?", len(packages)
            ).format(count=len(packages)),
        )
        dialog.props.secondary_text = _("This will install:\n\n{packages}").format(packages="\n".join(packages))
        dialog.set_default_response(Gtk.ResponseType.NO)

        def on_response(_dialog, response):
            _dialog.destroy()
            if response == Gtk.ResponseType.YES:
                streamline.do_reinstall(self, packages, populate)

        dialog.connect("response", on_response)
        dialog.present()

    def on_save(_widget):
        packages = streamline.selected_packages(self)
        if not packages:
            fn.log_warn("Streamline: save clicked with no packages selected")
            fn.show_in_app_notification(self, _("No packages selected"))
            return
        streamline.save_profile(self, packages)

    def on_save_removed(_widget):
        removed = streamline.removed_packages(self)
        if not removed:
            fn.log_warn("Streamline: save-removed clicked but nothing is removed")
            fn.show_in_app_notification(self, _("Nothing removed yet — every optional app is still installed"))
            return
        streamline.save_profile(self, removed, kind="removed")

    def apply_imported(packages):
        wanted = set(packages)
        matched = 0
        syncing["on"] = True
        for pkg, check in self.streamline_checks:
            in_profile = pkg in wanted
            check.set_active(in_profile)
            if in_profile:
                matched += 1
        syncing["on"] = False
        for category_check, child_checks in self.streamline_groups:
            sync_header(category_check, child_checks)
        fn.log_info(f"Streamline: imported profile selected {matched} installed package(s)")
        fn.show_in_app_notification(
            self,
            ngettext(
                "Profile imported — {count} installed app selected",
                "Profile imported — {count} installed apps selected",
                matched,
            ).format(count=matched),
        )

    def on_import(_widget):
        import gi

        gi.require_version("Gio", "2.0")
        from gi.repository import Gio

        fn.log_subsection("Streamline — import profile")
        file_chooser = Gtk.FileChooserDialog(
            title=_("Select a Streamline profile to import"),
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        file_chooser.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        file_chooser.add_button(_("_Open"), Gtk.ResponseType.OK)
        if fn.path.isdir(fn.att_streamline_dir):
            file_chooser.set_current_folder(Gio.File.new_for_path(fn.att_streamline_dir))
        file_filter = Gtk.FileFilter()
        file_filter.set_name(_("Profile files (*.txt)"))
        file_filter.add_pattern("*.txt")
        file_chooser.add_filter(file_filter)

        handled = [False]

        def on_response(dialog, response_id, _user_data=None):
            if handled[0]:
                return
            handled[0] = True
            if response_id == Gtk.ResponseType.OK:
                selected_file = dialog.get_file()
                if selected_file:
                    apply_imported(streamline.read_profile_file(selected_file.get_path()))
            else:
                fn.show_in_app_notification(self, _("Import cancelled"))
            dialog.close()

        file_chooser.connect("response", on_response)
        file_chooser.present()

    populate()

    # ── Action bar ─────────────────────────────────────────
    # Column-aligned: left actions sit under "Still installed", right actions
    # under "Already removed", matching the two grid columns above.
    btn_remove = Gtk.Button(label=_("Remove selected"))
    btn_remove.connect("clicked", on_remove)
    btn_save = Gtk.Button(label=_("Save profile"))
    btn_save.connect("clicked", on_save)
    btn_reinstall = Gtk.Button(label=_("Reinstall selected"))
    btn_reinstall.connect("clicked", on_reinstall)
    btn_save_removed = Gtk.Button(label=_("Save removed list"))
    btn_save_removed.connect("clicked", on_save_removed)
    btn_import = Gtk.Button(label=_("Import profile"))
    btn_import.connect("clicked", on_import)

    hbox_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    hbox_actions.set_homogeneous(True)
    hbox_actions.set_margin_start(10)
    hbox_actions.set_margin_end(10)
    hbox_actions.set_margin_top(10)
    hbox_actions.set_margin_bottom(5)
    left_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    left_actions.set_halign(Gtk.Align.START)
    left_actions.append(btn_remove)
    right_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    right_actions.set_halign(Gtk.Align.START)
    right_actions.append(btn_reinstall)
    right_actions.append(btn_save_removed)
    hbox_actions.append(left_actions)
    hbox_actions.append(right_actions)

    # Page-level row (applies to the whole list, not one column) — left-aligned.
    hbox_profile = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_profile.set_halign(Gtk.Align.START)
    hbox_profile.set_margin_start(10)
    hbox_profile.set_margin_bottom(10)
    hbox_profile.append(btn_import)
    hbox_profile.append(btn_save)

    vbox_stack.append(hbox_title)
    vbox_stack.append(hbox_sep)
    vbox_stack.append(lbl_desc)
    vbox_stack.append(self.streamline_recursive)
    vbox_stack.append(search_entry)
    vbox_stack.append(scrolled)
    vbox_stack.append(hbox_actions)
    vbox_stack.append(hbox_profile)

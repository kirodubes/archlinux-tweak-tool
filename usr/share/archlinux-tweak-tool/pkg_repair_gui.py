# ============================================================
# Author: Erik Dubois
# ============================================================
# Maintenance → Repair tab — GUI. Scan → review the list → reinstall the ticked packages.

import threading

import functions as fn
import pkg_repair
from att_i18n import _, ngettext
from functions import GLib

MAX_PATHS_SHOWN = 40


def _clear(box):
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _summary(problems):
    parts = []
    damaged = len(problems["damaged"])
    perms = len(problems["permissions"])
    if damaged:
        parts.append(ngettext("{count} file missing or changed", "{count} files missing or changed",
                              damaged).format(count=damaged))
    if perms:
        parts.append(ngettext("{count} file with wrong permissions", "{count} files with wrong permissions",
                              perms).format(count=perms))
    return " · ".join(parts)


def _result_row(Gtk, self, pkg, problems, foreign):
    row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    row.set_margin_start(10)
    row.set_margin_end(10)

    line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    check = Gtk.CheckButton(label=pkg)
    check.set_active(not foreign)
    check.set_sensitive(not foreign)
    check.connect("toggled", lambda _widget: _update_reinstall_button(self))
    lbl_summary = Gtk.Label(xalign=0)
    lbl_summary.set_hexpand(True)
    summary = _summary(problems)
    if foreign:
        summary += " · " + _("not in a repo — rebuild it with your AUR helper")
    lbl_summary.set_text(summary)
    line.append(check)
    line.append(lbl_summary)
    row.append(line)

    paths = problems["damaged"] + problems["permissions"]
    shown = "\n".join(paths[:MAX_PATHS_SHOWN])
    if len(paths) > MAX_PATHS_SHOWN:
        hidden = len(paths) - MAX_PATHS_SHOWN
        shown += "\n" + ngettext("… and {count} more", "… and {count} more", hidden).format(count=hidden)
    expander = Gtk.Expander(label=_("Files"))
    lbl_paths = Gtk.Label(xalign=0)
    lbl_paths.set_text(shown)
    lbl_paths.set_selectable(True)
    lbl_paths.set_margin_start(20)
    expander.set_child(lbl_paths)
    expander.set_margin_start(25)
    row.append(expander)

    if not foreign:
        self.repair_checks[pkg] = check
    return row


def _selected(self):
    return [pkg for pkg, check in self.repair_checks.items() if check.get_active()]


def _update_reinstall_button(self):
    self.btn_repair_reinstall.set_sensitive(bool(_selected(self)))


def _show_results(self, Gtk, problems, foreign):
    self.spinner_repair.stop()
    self.btn_repair_scan.set_sensitive(True)
    _clear(self.vbox_repair_results)
    self.repair_checks = {}
    if not problems:
        self.lbl_repair_status.set_text(_("No problems found — every package file is as pacman installed it."))
        fn.log_success("Repair scan: no problems found")
    else:
        self.lbl_repair_status.set_text(ngettext(
            "{count} package has missing or changed files.",
            "{count} packages have missing or changed files.",
            len(problems)).format(count=len(problems)))
        for pkg in sorted(problems):
            self.vbox_repair_results.append(_result_row(Gtk, self, pkg, problems[pkg], pkg in foreign))
    _update_reinstall_button(self)
    return False


def _on_scan(_widget, self, Gtk):
    self.btn_repair_scan.set_sensitive(False)
    self.btn_repair_reinstall.set_sensitive(False)
    self.spinner_repair.start()
    self.lbl_repair_status.set_text(_("Scanning every installed package — this takes one to three minutes…"))

    def worker():
        try:
            problems, foreign = pkg_repair.scan()
        except Exception as error:
            fn.log_error(f"Repair scan failed: {error}")
            problems, foreign = {}, set()
        GLib.idle_add(_show_results, self, Gtk, problems, foreign)

    threading.Thread(target=worker, daemon=True).start()


def _on_reinstall(_widget, self, Gtk):
    packages = _selected(self)
    if not packages:
        return
    message = _("pacman reinstalls these packages, which rewrites their files:\n\n{packages}\n\n"
                "Your own settings in /etc are kept.").format(packages=GLib.markup_escape_text(" ".join(packages)))
    if not fn.confirm_dialog(self, _("Reinstall packages?"), message):
        fn.log_info("Repair: reinstall cancelled")
        return
    process = pkg_repair.reinstall(packages)
    fn.show_in_app_notification(self, _("Reinstalling in a terminal…"))

    def wait_and_rescan():
        if process is not None:
            process.wait()
        GLib.idle_add(_on_scan, None, self, Gtk)

    threading.Thread(target=wait_and_rescan, daemon=True).start()


def build(self, Gtk, vbox_repair):
    """Fill the Maintenance → Repair tab."""
    self.repair_checks = {}

    lbl_header = Gtk.Label(xalign=0)
    lbl_header.set_markup("<b>" + _("Repair system files") + "</b>")
    lbl_header.set_margin_start(10)
    lbl_header.set_margin_top(10)

    lbl_intro = Gtk.Label(xalign=0)
    lbl_intro.set_wrap(True)
    lbl_intro.set_margin_start(10)
    lbl_intro.set_margin_end(10)
    lbl_intro.set_text(_(
        "Checks every file of every installed package against what pacman installed: files that are missing, "
        "changed or have the wrong permissions. Settings and state in /etc and /var are skipped, and so are "
        "files that Kiro changes on purpose. "
        "The scan only reads — nothing changes until you press Reinstall selected."))

    hbox_scan = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_scan.set_margin_start(10)
    hbox_scan.set_margin_end(10)
    self.btn_repair_scan = Gtk.Button(label=_("Scan"))
    self.btn_repair_scan.connect("clicked", _on_scan, self, Gtk)
    self.spinner_repair = Gtk.Spinner()
    self.lbl_repair_status = Gtk.Label(xalign=0)
    self.lbl_repair_status.set_wrap(True)
    self.lbl_repair_status.set_hexpand(True)
    hbox_scan.append(self.btn_repair_scan)
    hbox_scan.append(self.spinner_repair)
    hbox_scan.append(self.lbl_repair_status)

    self.vbox_repair_results = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    scroll_results = Gtk.ScrolledWindow()
    scroll_results.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll_results.set_vexpand(True)
    scroll_results.set_child(self.vbox_repair_results)

    hbox_reinstall = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_reinstall.set_margin_start(10)
    hbox_reinstall.set_margin_end(10)
    hbox_reinstall.set_margin_bottom(10)
    hbox_reinstall.set_halign(Gtk.Align.END)
    self.btn_repair_reinstall = Gtk.Button(label=_("Reinstall selected"))
    self.btn_repair_reinstall.set_sensitive(False)
    self.btn_repair_reinstall.connect("clicked", _on_reinstall, self, Gtk)
    hbox_reinstall.append(self.btn_repair_reinstall)

    vbox_repair.append(lbl_header)
    vbox_repair.append(lbl_intro)
    vbox_repair.append(hbox_scan)
    vbox_repair.append(scroll_results)
    vbox_repair.append(hbox_reinstall)
    fn.debug_print("Maintenance → Repair tab built")

# ============================================================
# Author: Erik Dubois
# ============================================================
# Maintenance → History tab — GUI. pacman transactions newest first; an
# upgraded or removed package can go back to the version still in the cache.

import threading

import functions as fn
import pkg_history
from att_i18n import _, ngettext
from functions import GLib
from gi.repository import Pango

# Building a few thousand rows at once stalls GTK; transactions past this are
# reached by searching for the package.
MAX_SHOWN = 60


def _clear(box):
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _counts(entries):
    counts = {}
    for entry in entries:
        counts[entry["action"]] = counts.get(entry["action"], 0) + 1
    labels = {
        "installed": lambda n: ngettext("{count} installed", "{count} installed", n),
        "upgraded": lambda n: ngettext("{count} upgraded", "{count} upgraded", n),
        "downgraded": lambda n: ngettext("{count} downgraded", "{count} downgraded", n),
        "removed": lambda n: ngettext("{count} removed", "{count} removed", n),
        "reinstalled": lambda n: ngettext("{count} reinstalled", "{count} reinstalled", n),
    }
    return ", ".join(labels[action](n).format(count=n) for action, n in counts.items())


def _entry_text(entry):
    pkg = entry["pkg"]
    if entry["action"] in ("upgraded", "downgraded"):
        verb = _("upgraded") if entry["action"] == "upgraded" else _("downgraded")
        return f"{pkg}  —  {verb}  {entry['old']} → {entry['new']}"
    verbs = {"installed": _("installed"), "removed": _("removed"), "reinstalled": _("reinstalled")}
    return f"{pkg}  —  {verbs[entry['action']]}  {entry['new']}"


def _on_go_back(_widget, self, entry, path):
    if entry["action"] == "removed":
        title = _("Reinstall {pkg} {version}?").format(pkg=entry["pkg"], version=entry["old"])
    else:
        title = _("Go back to {pkg} {version}?").format(pkg=entry["pkg"], version=entry["old"])
    message = _("pacman installs this file from the package cache:\n\n{path}\n\n"
                "Going back one package can break packages that need the newer version — pacman stops and tells "
                "you when it can see that. The next full update upgrades it again.").format(
                    path=GLib.markup_escape_text(path))
    if not fn.confirm_dialog(self, title, message):
        fn.log_info(f"History: going back on {entry['pkg']} cancelled")
        return
    process = pkg_history.install_file(path)
    fn.show_in_app_notification(self, _("Installing from the package cache in a terminal…"))

    def wait_and_reload():
        if process is not None:
            process.wait()
        GLib.idle_add(_load, self, self.Gtk_history)

    threading.Thread(target=wait_and_reload, daemon=True).start()


def _entry_row(Gtk, self, entry, index):
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    row.set_margin_start(20)
    row.set_margin_end(10)
    lbl_entry = Gtk.Label(xalign=0)
    lbl_entry.set_text(_entry_text(entry))
    lbl_entry.set_selectable(True)
    lbl_entry.set_hexpand(True)
    row.append(lbl_entry)
    if entry["action"] in ("upgraded", "removed"):
        path = pkg_history.find_cached(entry["pkg"], entry["old"], index)
        if path:
            label = _("Reinstall {version}") if entry["action"] == "removed" else _("Go back to {version}")
            btn = Gtk.Button(label=label.format(version=entry["old"]))
            btn.connect("clicked", _on_go_back, self, entry, path)
            row.append(btn)
        else:
            lbl_entry.set_tooltip_text(_("{version} is not in the package cache").format(version=entry["old"]))
    return row


def _render(self):
    Gtk = self.Gtk_history
    _clear(self.vbox_history_list)
    needle = self.entry_history_search.get_text().strip().lower()
    shown = 0
    for transaction in self.history_transactions:
        entries = transaction["entries"]
        if needle:
            entries = [e for e in entries if needle in e["pkg"].lower()]
            if not entries:
                continue
        # counts before the command: a pacman -U with many files can be 1000+ characters
        header = f"{transaction['time']}  ·  {_counts(entries)}  ·  {transaction['command'] or 'pacman'}"
        lbl_header = Gtk.Label(label=header, xalign=0)
        lbl_header.set_ellipsize(Pango.EllipsizeMode.END)
        lbl_header.set_tooltip_text(transaction["command"])
        expander = Gtk.Expander()
        expander.set_label_widget(lbl_header)
        expander.set_margin_start(10)
        expander.set_expanded(bool(needle))
        vbox_entries = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        for entry in entries:
            vbox_entries.append(_entry_row(Gtk, self, entry, self.history_cache_index))
        expander.set_child(vbox_entries)
        self.vbox_history_list.append(expander)
        shown += 1
        if shown >= MAX_SHOWN:
            break
    if not shown:
        lbl_empty = Gtk.Label(label=_("No transactions match."))
        self.vbox_history_list.append(lbl_empty)


def _load(self, Gtk):
    self.Gtk_history = Gtk
    self.history_transactions = pkg_history.read_history()
    self.history_cache_index = pkg_history.cache_index()
    fn.debug_print(f"History: {len(self.history_transactions)} transactions, "
                   f"{len(self.history_cache_index)} cached package files")
    _render(self)
    return False


def build(self, Gtk, vbox_history):
    """Fill the Maintenance → History tab; the log is read each time the tab is shown."""
    self.history_transactions = []
    self.history_cache_index = {}

    lbl_header = Gtk.Label(xalign=0)
    lbl_header.set_markup("<b>" + _("Package history") + "</b>")
    lbl_header.set_margin_start(10)
    lbl_header.set_margin_top(10)

    lbl_intro = Gtk.Label(xalign=0)
    lbl_intro.set_wrap(True)
    lbl_intro.set_max_width_chars(100)
    lbl_intro.set_margin_start(10)
    lbl_intro.set_margin_end(10)
    lbl_intro.set_text(_(
        "Every install, update and removal from the pacman log, newest first. Did an update break something? "
        "Open it and go back to the previous version of one package, as long as that version is still in the "
        "package cache."))

    self.entry_history_search = Gtk.SearchEntry()
    self.entry_history_search.set_placeholder_text(_("Search a package…"))
    self.entry_history_search.set_margin_start(10)
    self.entry_history_search.set_margin_end(10)
    self.entry_history_search.connect("search-changed", lambda _widget: _render(self))

    self.vbox_history_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    scroll_history = Gtk.ScrolledWindow()
    scroll_history.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll_history.set_vexpand(True)
    scroll_history.set_margin_bottom(10)
    scroll_history.set_child(self.vbox_history_list)

    vbox_history.append(lbl_header)
    vbox_history.append(lbl_intro)
    vbox_history.append(self.entry_history_search)
    vbox_history.append(scroll_history)
    vbox_history.connect("map", lambda _widget: _load(self, Gtk))
    fn.debug_print("Maintenance → History tab built")

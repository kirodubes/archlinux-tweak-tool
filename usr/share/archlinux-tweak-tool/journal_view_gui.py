# ============================================================
# Author: Erik Dubois
# ============================================================
# Logging → Journal tab — GUI. The system journal as a table: boot, level, service
# and text filters; newest first.

import threading

import functions as fn
import journal_view
from att_i18n import _, ngettext
from gi.repository import Gdk, Gio, GLib, GObject, Gtk, Pango

LEVELS = (
    (journal_view.LEVEL_ERRORS, lambda: _("Errors")),
    (journal_view.LEVEL_WARNINGS, lambda: _("Warnings and errors")),
    (journal_view.LEVEL_EVERYTHING, lambda: _("Everything")),
)
DEFAULT_LEVEL = 1

COLOURS = {0: "#e06c75", 1: "#e06c75", 2: "#e06c75", 3: "#e06c75", 4: "#e5c07b"}


class JournalRow(GObject.Object):
    """One journal entry as a list-model item."""

    def __init__(self, entry):
        super().__init__()
        self.entry = entry


def _level_words():
    return {0: _("emergency"), 1: _("alert"), 2: _("critical"), 3: _("error"), 4: _("warning"), 5: _("notice"),
            6: _("info"), 7: _("debug")}


def _add_column(column_view, title, bind, expand=False):
    factory = Gtk.SignalListItemFactory()

    def setup(_factory, list_item):
        label = Gtk.Label(xalign=0)
        label.set_margin_start(6)
        label.set_margin_end(6)
        if expand:
            label.set_ellipsize(Pango.EllipsizeMode.END)
        list_item.set_child(label)

    def on_bind(_factory, list_item):
        bind(list_item.get_child(), list_item.get_item().entry)

    factory.connect("setup", setup)
    factory.connect("bind", on_bind)
    column = Gtk.ColumnViewColumn(title=title, factory=factory)
    column.set_expand(expand)
    column_view.append_column(column)


def _bind_time(label, entry):
    label.set_text(entry["time"].strftime("%d %b %H:%M:%S") if entry["time"] else "")


def _bind_level(label, entry):
    words = _level_words()
    word = GLib.markup_escape_text(words.get(entry["priority"], str(entry["priority"])))
    colour = COLOURS.get(entry["priority"])
    label.set_markup(f'<span foreground="{colour}">●</span> {word}' if colour else f"<span alpha='50%'>●</span> {word}")


def _bind_service(label, entry):
    label.set_text(entry["service"])


def _bind_message(label, entry):
    label.set_text(entry["message"].replace("\n", " "))
    label.set_tooltip_text(entry["message"][:2000])


def _boot_label(index, boot):
    if index == 0:
        return _("This boot")
    if index == 1:
        return _("Previous boot")
    if boot["first"] and boot["last"]:
        return f"{boot['first']:%Y-%m-%d %H:%M} – {boot['last']:%H:%M}"
    return str(boot["index"])


def _matches(item, self):
    entry = item.entry
    if self.journal_service and entry["service"] != self.journal_service:
        return False
    needle = self.entry_journal_search.get_text().strip().lower()
    return not needle or needle in entry["message"].lower() or needle in entry["service"].lower()


def _refilter(self):
    self.journal_filter.changed(Gtk.FilterChange.DIFFERENT)


def _set_services(self, entries):
    self.journal_services = [""] + sorted({e["service"] for e in entries}, key=str.lower)
    labels = [_("All services")] + self.journal_services[1:]
    self.journal_updating = True
    self.dropdown_journal_service.set_model(Gtk.StringList.new(labels))
    keep = self.journal_service if self.journal_service in self.journal_services else ""
    self.journal_service = keep
    self.dropdown_journal_service.set_selected(self.journal_services.index(keep))
    self.journal_updating = False


def _fill(self, entries, capped):
    self.spinner_journal.stop()
    self.journal_entries = entries
    self.journal_store.splice(0, self.journal_store.get_n_items(), [JournalRow(e) for e in entries])
    _set_services(self, entries)
    _refilter(self)
    errors, warnings, services = journal_view.summarize(entries)
    boot = _boot_label(self.dropdown_journal_boot.get_selected(),
                       self.journal_boots[self.dropdown_journal_boot.get_selected()])
    parts = [ngettext("{count} error", "{count} errors", errors).format(count=errors),
             ngettext("{count} warning", "{count} warnings", warnings).format(count=warnings)]
    text = _("{boot}: {counts} from {services}").format(
        boot=boot, counts=", ".join(parts),
        services=ngettext("{count} service", "{count} services", services).format(count=services))
    if capped:
        text += " — " + _("showing the newest {count}").format(count=journal_view.MAX_ENTRIES)
    self.lbl_journal_summary.set_text(text)
    fn.log_info(f"Journal: {len(entries)} entries loaded ({errors} errors, {warnings} warnings)")
    return False


def _reload(self):
    if not self.journal_boots:
        return
    boot = self.journal_boots[self.dropdown_journal_boot.get_selected()]["index"]
    level = LEVELS[self.dropdown_journal_level.get_selected()][0]
    self.spinner_journal.start()
    self.lbl_journal_summary.set_text(_("Reading the journal…"))

    def worker():
        entries, capped = journal_view.read_entries(boot, level)
        GLib.idle_add(_fill, self, entries, capped)

    threading.Thread(target=worker, daemon=True).start()


def _load_boots(self):
    def worker():
        boots = journal_view.list_boots()
        GLib.idle_add(_set_boots, self, boots)

    threading.Thread(target=worker, daemon=True).start()


def _set_boots(self, boots):
    self.journal_boots = boots
    self.journal_updating = True
    self.dropdown_journal_boot.set_model(Gtk.StringList.new([_boot_label(i, b) for i, b in enumerate(boots)]))
    self.dropdown_journal_boot.set_selected(0)
    self.journal_updating = False
    _reload(self)
    return False


def _on_filter_changed(_widget, _pspec, self):
    if not self.journal_updating:
        _reload(self)


def _on_service_changed(_widget, _pspec, self):
    if self.journal_updating:
        return
    index = self.dropdown_journal_service.get_selected()
    self.journal_service = self.journal_services[index] if 0 <= index < len(self.journal_services) else ""
    _refilter(self)


def _on_copy(_widget, self):
    shown = self.journal_filtered
    entries = [shown.get_item(i).entry for i in range(shown.get_n_items())]
    if not entries:
        fn.show_in_app_notification(self, _("Nothing to copy"))
        return
    Gdk.Display.get_default().get_clipboard().set(journal_view.as_text(entries))
    fn.show_in_app_notification(self, ngettext("{count} line copied", "{count} lines copied",
                                               len(entries)).format(count=len(entries)))
    fn.log_info(f"Journal: {len(entries)} lines copied to the clipboard")


def build(self, vbox_journal):
    """Fill the Logging → Journal tab; the journal is read the first time the tab is shown."""
    self.journal_boots = []
    self.journal_entries = []
    self.journal_services = [""]
    self.journal_service = ""
    self.journal_updating = False
    self.journal_loaded = False

    lbl_intro = Gtk.Label(xalign=0)
    lbl_intro.set_wrap(True)
    lbl_intro.set_max_width_chars(100)
    lbl_intro.set_margin_start(10)
    lbl_intro.set_margin_end(10)
    lbl_intro.set_margin_top(10)
    lbl_intro.set_text(_("What the system logged, newest first. Pick the previous boot to see what happened before "
                         "a freeze or a crash; hover a message to read all of it."))

    hbox_filters = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_filters.set_margin_start(10)
    hbox_filters.set_margin_end(10)
    self.dropdown_journal_boot = Gtk.DropDown.new_from_strings([_("This boot")])
    self.dropdown_journal_boot.set_tooltip_text(_("Boot"))
    self.dropdown_journal_level = Gtk.DropDown.new_from_strings([label() for _level, label in LEVELS])
    self.dropdown_journal_level.set_selected(DEFAULT_LEVEL)
    self.dropdown_journal_level.set_tooltip_text(_("Level"))
    self.dropdown_journal_service = Gtk.DropDown.new_from_strings([_("All services")])
    self.dropdown_journal_service.set_tooltip_text(_("Service"))
    self.entry_journal_search = Gtk.SearchEntry()
    self.entry_journal_search.set_placeholder_text(_("Search the messages…"))
    self.entry_journal_search.set_hexpand(True)
    self.spinner_journal = Gtk.Spinner()
    btn_refresh = Gtk.Button(label=_("Refresh"))
    for widget in (self.dropdown_journal_boot, self.dropdown_journal_level, self.dropdown_journal_service,
                   self.entry_journal_search, self.spinner_journal, btn_refresh):
        hbox_filters.append(widget)

    self.lbl_journal_summary = Gtk.Label(xalign=0)
    self.lbl_journal_summary.set_margin_start(10)
    self.lbl_journal_summary.set_margin_end(10)

    self.journal_store = Gio.ListStore(item_type=JournalRow)
    self.journal_filter = Gtk.CustomFilter.new(_matches, self)
    self.journal_filtered = Gtk.FilterListModel(model=self.journal_store, filter=self.journal_filter)
    column_view = Gtk.ColumnView(model=Gtk.NoSelection(model=self.journal_filtered))
    column_view.set_show_row_separators(True)
    _add_column(column_view, _("Time"), _bind_time)
    _add_column(column_view, _("Level"), _bind_level)
    _add_column(column_view, _("Service"), _bind_service)
    _add_column(column_view, _("Message"), _bind_message, expand=True)
    scroll_journal = Gtk.ScrolledWindow()
    scroll_journal.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll_journal.set_vexpand(True)
    scroll_journal.set_margin_start(10)
    scroll_journal.set_margin_end(10)
    scroll_journal.set_child(column_view)

    hbox_copy = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_copy.set_margin_start(10)
    hbox_copy.set_margin_end(10)
    hbox_copy.set_margin_bottom(10)
    lbl_privacy = Gtk.Label(xalign=0)
    lbl_privacy.set_wrap(True)
    lbl_privacy.set_hexpand(True)
    lbl_privacy.add_css_class("dim-label")
    lbl_privacy.set_text(_("Log lines can contain IP addresses and names — use Report a problem to share them "
                           "safely."))
    btn_copy = Gtk.Button(label=_("Copy shown lines"))
    hbox_copy.append(lbl_privacy)
    hbox_copy.append(btn_copy)

    self.dropdown_journal_boot.connect("notify::selected", _on_filter_changed, self)
    self.dropdown_journal_level.connect("notify::selected", _on_filter_changed, self)
    self.dropdown_journal_service.connect("notify::selected", _on_service_changed, self)
    self.entry_journal_search.connect("search-changed", lambda _widget: _refilter(self))
    btn_refresh.connect("clicked", lambda _widget: _reload(self))
    btn_copy.connect("clicked", _on_copy, self)

    def on_map(_widget):
        if not self.journal_loaded:
            self.journal_loaded = True
            _load_boots(self)

    vbox_journal.connect("map", on_map)
    for widget in (lbl_intro, hbox_filters, self.lbl_journal_summary, scroll_journal, hbox_copy):
        vbox_journal.append(widget)
    fn.debug_print("Logging → Journal tab built")

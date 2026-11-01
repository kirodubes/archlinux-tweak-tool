# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
import office
from att_i18n import _


def _refresh(self, fn):
    for app in office.all_apps():
        label = getattr(self, f"lbl_office_{app['key']}", None)
        if label:
            installed = fn.check_package_installed(app["packages"].split()[0])
            label.set_markup(
                _("{name} <b>installed</b>").format(name=app["label"]) if installed else app["label"]
            )


def _build_row(self, Gtk, fn, app):
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label = Gtk.Label(xalign=0)
    label.set_markup(app["label"])
    label.set_margin_start(20)
    label.set_margin_end(10)
    label.set_hexpand(True)
    setattr(self, f"lbl_office_{app['key']}", label)

    btn_launch = Gtk.Button(label=_("Launch/Install"))
    btn_launch.connect("clicked", functools.partial(office.install_or_launch, self, app))
    btn_launch.set_margin_start(10)
    btn_launch.set_margin_end(5)

    btn_remove = Gtk.Button(label=_("Remove"))
    btn_remove.connect("clicked", functools.partial(office.remove, self, app))
    btn_remove.set_margin_start(5)
    btn_remove.set_margin_end(10)

    hbox.append(label)
    hbox.append(btn_launch)
    hbox.append(btn_remove)
    return hbox


def gui(self, Gtk, vboxstack_office, fn):
    """Create the Office GUI (suites, mail, editors, PDF/notes, scanning)."""
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_title_label = Gtk.Label(xalign=0)
    hbox_title_label.set_text(_("Office"))
    hbox_title_label.set_name("title")
    hbox_title_label.set_margin_start(10)
    hbox_title_label.set_margin_end(10)
    hbox_title.append(hbox_title_label)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_sep.append(hseparator)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    stack.set_transition_duration(350)
    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)

    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
    stack_switcher.set_stack(stack)

    for index, (tab_title, apps) in enumerate(office.OFFICE_APPS.items()):
        vboxstack_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        for app in apps:
            row = _build_row(self, Gtk, fn, app)
            row.set_margin_top(4)
            vboxstack_tab.append(row)
        vboxstack_tab.set_margin_top(10)
        stack.add_titled(vboxstack_tab, f"office_tab_{index}", _(tab_title))

    vbox.append(stack_switcher)
    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vbox.append(stack)

    vboxstack_office.append(hbox_title)
    vboxstack_office.append(hbox_sep)
    vbox.set_hexpand(True)
    vbox.set_vexpand(True)
    vboxstack_office.append(vbox)

    vboxstack_office.connect("map", lambda _w: _refresh(self, fn))
    _refresh(self, fn)

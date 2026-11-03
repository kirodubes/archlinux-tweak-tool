# ============================================================
# Author: Erik Dubois
# ============================================================
# Hybrid graphics page — GUI.

import functools

import hybrid
from att_i18n import N_, _, ngettext

_GREEN = "#4e9a06"
_ORANGE = "#FFA500"

_PACKAGE_BLURBS = {
    "nvidia-prime": N_("provides prime-run for the NVIDIA driver"),
    "switcheroo-control": N_("GPU list and the desktop menu entry"),
}


def _state(ok, yes, no):
    color = _GREEN if ok else _ORANGE
    return f"<span foreground='{color}'>{yes if ok else no}</span>"


def _escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _clear(box):
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _label(Gtk, markup, margin=20, selectable=False):
    label = Gtk.Label(xalign=0)
    label.set_markup(markup)
    label.set_margin_start(margin)
    label.set_margin_end(10)
    label.set_selectable(selectable)
    label.set_wrap(True)
    return label


def _gpu_line(gpu, discrete):
    vendor = {"intel": "Intel", "amd": "AMD", "nvidia": "NVIDIA"}.get(gpu["vendor"], _("other"))
    role = _("discrete — offload target") if gpu is discrete else (
        _("drives the display") if gpu["boot_vga"] else _("secondary"))
    return _("<b>{card}</b>  {vendor} · driver <b>{driver}</b> · {role}\n<small>{name}</small>").format(
        card=gpu["card"], vendor=vendor, driver=_escape(gpu["driver"] or _("none")), role=role,
        name=_escape(gpu["name"] or gpu["slot"]),
    )


def _refresh_overrides(self, Gtk, fn):
    _clear(self.hybrid_overrides_box)
    overrides = hybrid.list_overrides()
    if not overrides:
        self.hybrid_overrides_box.append(_label(Gtk, _("<i>No overrides yet.</i>")))
    for desktop_id, name in overrides:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = _label(Gtk, _("<b>{name}</b>  <small>{path}</small>").format(
            name=_escape(name), path=_escape(f"{hybrid.USER_APPS_DIR}/{desktop_id}")))
        label.set_hexpand(True)
        button = Gtk.Button(label=_("Remove"))
        button.set_margin_end(10)
        button.set_sensitive(self.hybrid_available)
        button.connect("clicked", functools.partial(hybrid.on_click_remove_override, self, desktop_id))
        row.append(label)
        row.append(button)
        self.hybrid_overrides_box.append(row)
    self.btn_hybrid_remove_all.set_sensitive(self.hybrid_available and bool(overrides))


def refresh(self, fn):
    """Update the GPU list, package state, commands and overrides to the live system."""
    Gtk = fn.Gtk
    gpus = hybrid.list_gpus(with_names=True)
    discrete = hybrid.discrete_gpu(gpus)
    self.hybrid_prefix = hybrid.offload_prefix(discrete)

    if self.hybrid_available and len(gpus) >= 2:
        detected = ngettext("Hybrid graphics detected — {count} GPU", "Hybrid graphics detected — {count} GPUs",
                            len(gpus)).format(count=len(gpus))
        summary = _state(True, detected, "")
    elif self.hybrid_available:
        summary = _state(False, "", _("--dev: page forced on with fewer than two GPUs"))
    else:
        summary = _state(False, "", _not_available(len(gpus)))
    self.hybrid_summary_label.set_markup(summary)

    _clear(self.hybrid_gpu_box)
    for gpu in gpus:
        self.hybrid_gpu_box.append(_label(Gtk, _gpu_line(gpu, discrete), margin=30))

    any_missing = False
    for pkg in hybrid.PACKAGES:
        installed = fn.check_package_installed(pkg)
        any_missing = any_missing or not installed
        self.hybrid_pkg_labels[pkg].set_markup(_("<b>{pkg}</b> <small>— {blurb}</small> — {state}").format(
            pkg=pkg, blurb=_(_PACKAGE_BLURBS[pkg]), state=_state(installed, _("installed"), _("not installed"))))
    service_ok = fn.check_service(hybrid.SWITCHEROO_SERVICE)
    self.hybrid_service_label.set_markup(_("switcheroo-control service: {state}").format(
        state=_state(service_ok, _("running"), _("not running"))))
    switcheroo = hybrid.switcheroo_list()
    self.hybrid_switcheroo_label.set_markup(
        f"<tt><small>{_escape(switcheroo)}</small></tt>" if switcheroo else "")
    self.hybrid_switcheroo_label.set_visible(bool(switcheroo))
    self.btn_hybrid_install.set_sensitive(self.hybrid_available and any_missing)

    prefix = self.hybrid_prefix
    self.hybrid_commands_label.set_markup(_(
        "From a terminal or a launcher:   <tt><b>{prefix} &lt;app&gt;</b></tt>\n"
        "Steam → game → Properties → Launch Options:   <tt><b>{prefix} %command%</b></tt>"
    ).format(prefix=_escape(prefix)))
    if discrete is None:
        self.hybrid_prefix_note.set_text("")
    elif prefix == "prime-run" and not fn.check_package_installed("nvidia-prime"):
        self.hybrid_prefix_note.set_markup(_("<small>prime-run comes with <b>nvidia-prime</b> — install it below."
                                             "</small>"))
    elif prefix != "prime-run":
        self.hybrid_prefix_note.set_markup(_(
            "<small>The discrete GPU does not use the proprietary NVIDIA driver, so Mesa's "
            "<b>DRI_PRIME=1</b> is used instead of prime-run.</small>"))
    else:
        self.hybrid_prefix_note.set_text("")

    self.hybrid_app_dropdown.set_sensitive(self.hybrid_available)
    self.btn_hybrid_add.set_sensitive(self.hybrid_available and bool(self.hybrid_apps))
    _refresh_overrides(self, Gtk, fn)


def _not_available(count):
    return ngettext(
        "Not available — this machine has {count} graphics card; hybrid graphics needs two",
        "Not available — this machine has {count} graphics cards; hybrid graphics needs two",
        count,
    ).format(count=count)


def gui(self, Gtk, vboxstack_hybrid, hybrid, fn):
    """Create the Hybrid graphics page (always shown; inert unless there are 2+ GPUs)."""
    fn.log_info("Building Hybrid graphics page")

    # Always in the sidebar so the tab list matches on every machine (docs, videos);
    # with fewer than two GPUs everything is rendered but disabled, and Status says why.
    # --dev keeps the page live for testing on a single-GPU box.
    self.hybrid_available = hybrid.is_hybrid() or fn.DEV
    self.hybrid_prefix = "prime-run"

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    title_label = Gtk.Label(xalign=0)
    title_label.set_text(_("Hybrid graphics"))
    title_label.set_name("title")
    title_label.set_margin_start(10)
    title_label.set_margin_end(10)
    hbox_title.append(title_label)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hbox_sep.append(hseparator)

    # ── Intro ────────────────────────────────────────────────────────
    if self.hybrid_available:
        intro = _(
            "This machine has <b>two graphics cards</b>: a power-saving one that drives the screen and a\n"
            "faster discrete one. Apps start on the power-saving card unless you ask for the discrete one."
        )
    else:
        intro = _(
            "On laptops with two graphics cards (e.g. Intel + NVIDIA) this page runs chosen apps on the\n"
            "faster discrete card. This page needs <b>two graphics cards</b> — see <b>Status</b> below."
        )
    if hybrid.desktop_has_menu_entry():
        intro += _("\n\nYour desktop also offers <b>Launch using Discrete Graphics</b> in the app menu (right-click).")
    else:
        intro += _("\n\nYour desktop has no <b>Launch using Discrete Graphics</b> menu entry — use the commands "
                   "or the overrides below.")
    intro_label = _label(Gtk, intro)

    # ── Status ───────────────────────────────────────────────────────
    status_header = _label(Gtk, _("<b>Status</b>"), margin=10)
    self.hybrid_summary_label = _label(Gtk, "")
    self.hybrid_gpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    self.hybrid_pkg_labels = {pkg: _label(Gtk, "") for pkg in hybrid.PACKAGES}
    self.hybrid_service_label = _label(Gtk, "")
    self.hybrid_switcheroo_label = _label(Gtk, "", margin=30, selectable=True)

    hbox_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.btn_hybrid_install = Gtk.Button(label=_("Install missing packages"))
    self.btn_hybrid_install.set_tooltip_text(
        _("Install nvidia-prime and switcheroo-control in a terminal, then enable switcheroo-control"))
    self.btn_hybrid_install.connect("clicked", functools.partial(hybrid.on_click_install, self))
    self.btn_hybrid_install.set_margin_start(20)
    hbox_install.append(self.btn_hybrid_install)

    # ── Run once on the discrete GPU ─────────────────────────────────
    commands_header = _label(Gtk, _("<b>Run an app on the discrete GPU</b>"), margin=10)
    self.hybrid_commands_label = _label(Gtk, "", selectable=True)
    self.hybrid_prefix_note = _label(Gtk, "")

    # ── Always on the discrete GPU ───────────────────────────────────
    overrides_header = _label(Gtk, _("<b>Always run an app on the discrete GPU</b>"), margin=10)
    overrides_intro = _label(Gtk, _(
        "ATT copies the app's launcher to <b>~/.local/share/applications</b> with the command above in front.\n"
        "<span foreground='{color}'>A copy does not follow package updates of that app</span> — remove it to "
        "go back to the original launcher."
    ).format(color=_ORANGE))

    self.hybrid_apps = hybrid.list_system_apps()
    hbox_add = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.hybrid_app_dropdown = Gtk.DropDown.new_from_strings([name for _id, name in self.hybrid_apps])
    # Search needs to know which property holds the text of each StringList item.
    self.hybrid_app_dropdown.set_expression(Gtk.PropertyExpression.new(Gtk.StringObject, None, "string"))
    self.hybrid_app_dropdown.set_enable_search(True)
    self.hybrid_app_dropdown.set_hexpand(True)
    self.hybrid_app_dropdown.set_margin_start(20)
    self.btn_hybrid_add = Gtk.Button(label=_("Always use discrete GPU"))
    self.btn_hybrid_add.connect("clicked", functools.partial(hybrid.on_click_add_override, self))
    self.btn_hybrid_add.set_margin_end(10)
    hbox_add.append(self.hybrid_app_dropdown)
    hbox_add.append(self.btn_hybrid_add)

    current_header = _label(Gtk, _("<b>Current overrides</b>"), margin=10)
    self.hybrid_overrides_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    hbox_remove_all = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.btn_hybrid_remove_all = Gtk.Button(label=_("Remove all overrides"))
    self.btn_hybrid_remove_all.connect("clicked", functools.partial(hybrid.on_click_remove_all, self))
    self.btn_hybrid_remove_all.set_margin_start(20)
    hbox_remove_all.append(self.btn_hybrid_remove_all)

    for widget in (
        hbox_title, hbox_sep, intro_label,
        status_header, self.hybrid_summary_label, self.hybrid_gpu_box,
        *self.hybrid_pkg_labels.values(), self.hybrid_service_label, self.hybrid_switcheroo_label, hbox_install,
        commands_header, self.hybrid_commands_label, self.hybrid_prefix_note,
        overrides_header, overrides_intro, hbox_add, current_header, self.hybrid_overrides_box, hbox_remove_all,
    ):
        vboxstack_hybrid.append(widget)

    refresh(self, fn)

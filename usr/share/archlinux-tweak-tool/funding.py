# ============================================================
# Authors: Erik Dubois
# ============================================================

"""Funding channels for the Kiro project and the action to open them."""

import functools

import functions as fn
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

# Canonical funding channels — mirror of kiro-website/.github/FUNDING.yml.
# These URLs are stable; if a channel ever changes, edit it here.
SOURCES = [
    ("GitHub Sponsors", "https://github.com/sponsors/erikdubois", "Low fees — most reaches the project"),
    ("Patreon", "https://www.patreon.com/c/kiroproject", "Recurring membership tiers"),
    ("YouTube Membership", "https://www.youtube.com/@ErikDubois/join", "Early access and member-only perks"),
    ("Ko-fi", "https://ko-fi.com/erikdubois", "One-off donation, low fees"),
    ("PayPal", "https://www.paypal.me/erikdubois", "One-off donation"),
]


def on_click_open(self, url, _widget):
    """Open a funding URL in the real user's default browser (drop root via sudo -u)."""
    fn.open_url_as_user(url)


def show_support_dialog(self):
    """Open a dialog listing the project's funding channels (shown beside Quit).

    Deliberately NOT modal: a modal window stays pinned on top of ATT, so the browser
    opened by a funding link appears behind it and the user never sees the page.
    """
    is_kiro = fn.get_distro_label() in ("Kiro", "KiroTux")
    project_name = "Kiro" if is_kiro else "ATT"
    title_text = "Support Kiro" if is_kiro else "Support the ATT"

    fn.log_info(f"Opening Support dialog ({project_name})")

    dialog = Gtk.Window(title=title_text, transient_for=self, modal=False)
    dialog.set_default_size(460, -1)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    for side in ("start", "end", "top", "bottom"):
        getattr(box, f"set_margin_{side}")(18)

    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_markup(f'<span foreground="#FFA500"><b>{title_text}</b></span>')
    box.append(lbl_title)

    lbl_intro = Gtk.Label(xalign=0)
    lbl_intro.set_wrap(True)
    lbl_intro.set_text(
        f"{project_name} is free and open source. If it helps you, "
        "here are the ways to support its development. Thank you."
    )
    box.append(lbl_intro)

    for name, url, blurb in SOURCES:
        hbox_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_row = Gtk.Label(xalign=0)
        lbl_row.set_markup(f"<b>{name}</b> — {blurb}")
        lbl_row.set_hexpand(True)
        btn_open = Gtk.Button(label="Open")
        btn_open.set_size_request(100, 30)
        btn_open.connect("clicked", functools.partial(on_click_open, self, url))
        hbox_row.append(lbl_row)
        hbox_row.append(btn_open)
        box.append(hbox_row)

    btn_close = Gtk.Button(label="Close")
    btn_close.set_size_request(100, 30)
    btn_close.set_halign(Gtk.Align.END)
    btn_close.connect("clicked", lambda _w: dialog.close())
    box.append(btn_close)

    dialog.set_child(box)
    dialog.present()

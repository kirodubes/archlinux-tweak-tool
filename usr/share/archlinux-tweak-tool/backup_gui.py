# ============================================================
# Author: Erik Dubois
# ============================================================
# Backup page — GUI. Explains personal-file backup vs system
# snapshots, and offers Pika Backup / Vorta (BorgBackup front-ends).

import functools

import backup
from att_i18n import _


def _refresh(self, fn):
    """Update each app row to reflect the live installed state."""
    for app in backup.BACKUP_APPS:
        label = getattr(self, f"lbl_backup_{app['key']}", None)
        if label:
            installed = fn.check_package_installed(app["packages"].split()[0])
            label.set_markup(
                _("{name} <b>installed</b>").format(name=app["label"]) if installed else app["label"]
            )


def _build_row(self, Gtk, app):
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    label = Gtk.Label(xalign=0)
    label.set_markup(app["label"])
    label.set_margin_start(20)
    label.set_margin_end(10)
    label.set_hexpand(True)
    setattr(self, f"lbl_backup_{app['key']}", label)

    btn_launch = Gtk.Button(label=_("Launch/Install"))
    btn_launch.connect("clicked", functools.partial(backup.install_or_launch, self, app))
    btn_launch.set_margin_start(10)
    btn_launch.set_margin_end(5)

    btn_remove = Gtk.Button(label=_("Remove"))
    btn_remove.connect("clicked", functools.partial(backup.remove, self, app))
    btn_remove.set_margin_start(5)
    btn_remove.set_margin_end(10)

    hbox.append(label)
    hbox.append(btn_launch)
    hbox.append(btn_remove)
    return hbox


def gui(self, Gtk, vboxstack_backup, backup, fn):
    """Create the Backup page (personal-file backup with Pika Backup / Vorta)."""
    fn.log_info("Building Backup page")

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_title_label = Gtk.Label(xalign=0)
    hbox_title_label.set_text(_("Backup"))
    hbox_title_label.set_name("title")
    hbox_title_label.set_margin_start(10)
    hbox_title_label.set_margin_end(10)
    hbox_title.append(hbox_title_label)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hbox_sep.append(hseparator)

    # ── Intro: why this page exists ──────────────────────────────────
    hbox_intro = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    intro_label = Gtk.Label(xalign=0)
    intro_label.set_markup(
        _(
            "This page is about backing up <b>your personal files</b> — documents, photos,\n"
            "projects, the things you cannot reinstall. A backup keeps a <b>versioned,\n"
            "deduplicated and encrypted</b> copy of them in a separate place, so you can get\n"
            "any file back after an accidental delete, a bad edit, or a dead disk."
        )
    )
    intro_label.set_margin_start(20)
    intro_label.set_margin_end(10)
    hbox_intro.append(intro_label)

    # ── How this differs from Timeshift and Snapper ──────────────────
    hbox_diff_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    diff_header_label = Gtk.Label(xalign=0)
    diff_header_label.set_markup(_("<b>How this differs from Timeshift and Snapper</b>"))
    diff_header_label.set_margin_start(10)
    hbox_diff_header.append(diff_header_label)

    hbox_diff = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    diff_label = Gtk.Label(xalign=0)
    diff_label.set_markup(
        _(
            "<b>Timeshift</b> and <b>Snapper</b> take <b>system snapshots</b> on the <b>same disk</b>.\n"
            "They exist to roll the operating system back after a bad update or a broken package —\n"
            "Timeshift even excludes your home folder by default. They are <b>not</b> a backup of\n"
            "your documents, and if the disk dies the snapshots die with it.\n\n"
            "A <b>backup</b> is a copy of your files on a <b>different disk or another machine</b>, so\n"
            "they survive disk failure, theft, or an accidental delete. The two are complementary:\n"
            "snapshots fix the system, backups protect your data."
        )
    )
    diff_label.set_margin_start(20)
    diff_label.set_margin_end(10)
    hbox_diff.append(diff_label)

    # ── Keep a copy off-site (cloud) ─────────────────────────────────
    hbox_cloud_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    cloud_header_label = Gtk.Label(xalign=0)
    cloud_header_label.set_markup(_("<b>Keep a copy off-site (cloud)</b>"))
    cloud_header_label.set_margin_start(10)
    hbox_cloud_header.append(cloud_header_label)

    hbox_cloud = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    cloud_label = Gtk.Label(xalign=0)
    cloud_label.set_markup(
        _(
            "Both apps below are built on <b>BorgBackup</b>, which can send the same encrypted\n"
            "backup over SSH to a NAS, a home server, or a remote / <b>cloud</b> host. Aim for the\n"
            "<b>3-2-1 rule</b>: 3 copies of your data, on 2 kinds of media, with 1 of them off-site —\n"
            "so a fire, theft or ransomware at home still leaves you a safe copy."
        )
    )
    cloud_label.set_margin_start(20)
    cloud_label.set_margin_end(10)
    hbox_cloud.append(cloud_label)

    # ── Backup apps ──────────────────────────────────────────────────
    hbox_apps_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    apps_header_label = Gtk.Label(xalign=0)
    apps_header_label.set_markup(_("<b>Backup apps</b>"))
    apps_header_label.set_margin_start(10)
    hbox_apps_header.append(apps_header_label)

    app_rows = [_build_row(self, Gtk, app) for app in backup.BACKUP_APPS]

    # ── Recommendation ───────────────────────────────────────────────
    hbox_reco = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    reco_label = Gtk.Label(xalign=0)
    reco_label.set_markup(
        _(
            "<i>Our recommendation: use either one. <b>Pika Backup</b> is the simplest and blends in\n"
            "with the desktop; <b>Vorta</b> gives you more options and scheduling profiles. Both wrap\n"
            "BorgBackup, so their archives are interchangeable — pick whichever feels nicer.</i>"
        )
    )
    reco_label.set_margin_start(20)
    reco_label.set_margin_end(10)
    hbox_reco.append(reco_label)

    vboxstack_backup.append(hbox_title)
    vboxstack_backup.append(hbox_sep)
    vboxstack_backup.append(hbox_intro)
    vboxstack_backup.append(hbox_diff_header)
    vboxstack_backup.append(hbox_diff)
    vboxstack_backup.append(hbox_cloud_header)
    vboxstack_backup.append(hbox_cloud)
    vboxstack_backup.append(hbox_apps_header)
    for row in app_rows:
        row.set_margin_top(4)
        vboxstack_backup.append(row)
    vboxstack_backup.append(hbox_reco)

    vboxstack_backup.connect("map", lambda _w: _refresh(self, fn))
    _refresh(self, fn)

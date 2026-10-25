#!/usr/bin/env python3
"""Live test: run ATT's own "Install all desktops" on a test box and check every desktop afterwards.

Run through run-install-all-desktops.sh only (it guards and elevates). Developer-only, never shipped in the package.
"""

import importlib.util
import json
import os
import shlex
import subprocess
import sys
import threading
import time

APP_DIR = os.environ.get("ATT_LIVE_APP_DIR", "/usr/share/archlinux-tweak-tool")
OUT = os.environ.get("ATT_INSTALL_OUT", "/tmp/att-install-all")
TWMS_ONLY = os.environ.get("ATT_INSTALL_TWMS") == "1"
TIMEOUT = 4 * 3600
sys.path.insert(0, APP_DIR)

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk  # noqa: E402

import desktopr  # noqa: E402
import functions as fn  # noqa: E402

_spec = importlib.util.spec_from_file_location("att_main", os.path.join(APP_DIR, "archlinux-tweak-tool.py"))
att_main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(att_main)

ORDER = desktopr.TWM_INSTALL_ORDER if TWMS_ONLY else desktopr.INSTALL_ORDER
CURRENT = ["(startup)"]
ERRORS, CRASHES, DIALOGS = {}, [], []
DONE = threading.Event()

# ── Recorders ────────────────────────────────────────────────────────────────

_orig_hook = threading.excepthook


def _thread_crash(args):
    CRASHES.append(f"{CURRENT[0]}: {args.exc_type.__name__}: {args.exc_value}")
    _orig_hook(args)


threading.excepthook = _thread_crash

_orig_log_section = fn.log_section


def _log_section(message, *a, **kw):
    # install_desktop opens with "Installing <desktop> desktop": errors after it belong to that desktop
    words = str(message).split()
    if len(words) == 3 and words[0] == "Installing" and words[2] == "desktop":
        CURRENT[0] = words[1]
    return _orig_log_section(message, *a, **kw)


fn.log_section = _log_section

_orig_log_error = fn.log_error


def _log_error(message, lineno=None, cmd=None):
    ERRORS.setdefault(CURRENT[0], []).append(str(message))
    return _orig_log_error(message, lineno, cmd)


fn.log_error = _log_error

_orig_log_success = fn.log_success


def _log_success(message, *a, **kw):
    if "sequence complete" in str(message):
        DONE.set()
    return _orig_log_success(message, *a, **kw)


fn.log_success = _log_success


def _messagebox(_self, title, message):
    DIALOGS.append(f"{title}: {message}")


def _confirm(_self, title, message):
    DIALOGS.append(f"(declined) {title}: {message}")
    return False


fn.messagebox = _messagebox
fn.confirm_dialog = _confirm

# ── Terminal shim: the install terminal waits for Enter twice ────────────────


class _NoTerminalPopen(subprocess.Popen):
    def __init__(self, args, *a, **kw):
        if isinstance(args, list) and args[:2] == ["alacritty", "-e"]:
            # same command ATT would run in alacritty, with the two "Press Enter" prompts answered
            args = ["bash", "-c", "yes '' | " + shlex.join(args[2:])]
        super().__init__(args, *a, **kw)


subprocess.Popen = _NoTerminalPopen

# ── Runner ───────────────────────────────────────────────────────────────────


def _base_packages(desktop):
    return list(getattr(desktopr, desktop.replace("-", ""), []))


def _installed(name):
    # mate, mate-extra and gnome are package groups: pacman -Qi does not know them, pacman -Qg does
    if fn.check_package_installed(name):
        return True
    return subprocess.run(["pacman", "-Qg", name], capture_output=True).returncode == 0


def _results(before):
    desktopr._xsession_files = None
    desktopr._wayland_files = None
    fn.invalidate_pkg_cache()
    results = []
    for desktop in ORDER:
        session = desktopr.SESSION_FILE_ALIASES.get(desktop, desktop) + ".desktop"
        missing = [p for p in _base_packages(desktop) if not _installed(p)]
        errors = ERRORS.get(desktop, [])
        if before[desktop]:
            verdict, detail = "SKIP", "already installed before the run"
        elif not desktopr.check_desktop(desktop):
            verdict, detail = "FAIL", f"no {session} after the install"
        elif missing or errors:
            verdict, detail = "FAIL", f"missing: {', '.join(missing) or '-'}; errors: {' | '.join(errors) or '-'}"
        else:
            verdict, detail = "PASS", f"{session} present, all {len(_base_packages(desktop))} packages installed"
        results.append([desktop, verdict, detail])
    return results


def _write_report(before, started):
    results = _results(before)
    counts = {v: sum(1 for r in results if r[1] == v) for v in ("PASS", "FAIL", "SKIP")}
    report = {
        "mode": "twms" if TWMS_ONLY else "all",
        "minutes": round((time.time() - started) / 60, 1),
        "results": results,
        "counts": counts,
        "crashes": CRASHES,
        "dialogs": DIALOGS,
        "errors_outside_a_desktop": ERRORS.get("(startup)", []),
        "timed_out": not DONE.is_set(),
    }
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    for desktop, verdict, detail in results:
        print(f"{verdict:4}  {desktop:15} {detail}", flush=True)


def _start(app, win):
    started = time.time()
    deadline = started + 60

    def wait_built():
        if not hasattr(win, "att_stack"):
            if time.time() > deadline:
                print("ATT window did not build its pages within 60s", flush=True)
                app.quit()
                return False
            return True
        win.att_stack.set_visible_child_name("stack12")
        GLib.timeout_add(500, wait_page)
        return False

    def wait_page():
        if not hasattr(win, "d_combo"):
            if time.time() > deadline:
                print("Desktop page did not build within 60s", flush=True)
                app.quit()
                return False
            return True
        before = {d: desktopr.check_desktop(d) for d in ORDER}
        fn.log_info(f"Pressing ATT's {'Install all twms' if TWMS_ONLY else 'Install all desktops'}: {', '.join(ORDER)}")
        if TWMS_ONLY:
            desktopr.install_all_twms(win)
        else:
            desktopr.install_all_desktops(win)

        def wait_done():
            DONE.wait(TIMEOUT)
            GLib.idle_add(finish, before)

        threading.Thread(target=wait_done, daemon=True).start()
        return False

    def finish(before):
        _write_report(before, started)
        app.quit()
        return False

    GLib.timeout_add(500, wait_built)


def main():
    """Start the real ATT window under a separate app id and run its install-all sequence."""
    if os.geteuid() != 0 or "PKEXEC_UID" not in os.environ:
        sys.exit("Run this through run-install-all-desktops.sh: ATT runs as root with PKEXEC_UID, so the test must too.")
    os.makedirs(OUT, exist_ok=True)
    theme, prefer_dark, _src = att_main._resolve_effective_theme()
    if theme:
        os.environ["GTK_THEME"] = theme + (":dark" if prefer_dark else "")
    app = Gtk.Application(application_id="org.kiro.att-installall", flags=Gio.ApplicationFlags.NON_UNIQUE)

    def activate(_app):
        if Gdk.Display.get_default() is None:
            print("No display: check DISPLAY/WAYLAND_DISPLAY and XAUTHORITY", flush=True)
            app.quit()
            return
        css = Gtk.CssProvider()
        css.load_from_path(os.path.join(APP_DIR, "icons.css"))
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        _start(app, att_main.Main(app))

    app.connect("activate", activate)
    app.run(None)


if __name__ == "__main__":
    main()

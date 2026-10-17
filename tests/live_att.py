#!/usr/bin/env python3
"""Live test: drive the installed ATT GUI on a test box and read every change back.

Run through run-live-att.sh only (it guards, backs up and restores). Developer-only, never shipped in the package.
"""

import importlib.util
import json
import os
import pwd
import re
import shutil
import subprocess
import sys
import threading
import time

APP_DIR = os.environ.get("ATT_LIVE_APP_DIR", "/usr/share/archlinux-tweak-tool")
OUT = os.environ.get("ATT_LIVE_OUT", "/tmp/att-live")
sys.path.insert(0, APP_DIR)

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk  # noqa: E402

import autostart  # noqa: E402
import fastfetch  # noqa: E402
import functions as fn  # noqa: E402
import shell  # noqa: E402
import wallpaper  # noqa: E402

_spec = importlib.util.spec_from_file_location("att_main", os.path.join(APP_DIR, "archlinux-tweak-tool.py"))
att_main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(att_main)

USER_UID = pwd.getpwnam(fn.sudo_username).pw_uid

# ── Recorders ────────────────────────────────────────────────────────────────

CRASHES, STATUS, ERRORS, DIALOGS, BLOCKED, RESULTS, SHOTS = [], [], [], [], [], [], []

_orig_hook = threading.excepthook


def _thread_crash(args):
    # ATT's worker threads report nothing themselves: an exception there leaves a dead button
    CRASHES.append(f"{args.exc_type.__name__}: {args.exc_value}")
    _orig_hook(args)


threading.excepthook = _thread_crash

_orig_notify = fn.show_in_app_notification


def _notify(self, message):
    STATUS.append(message)
    return _orig_notify(self, message)


fn.show_in_app_notification = _notify

_orig_log_error = fn.log_error


def _log_error(message, lineno=None, cmd=None):
    ERRORS.append(str(message))
    return _orig_log_error(message, lineno, cmd)


fn.log_error = _log_error


def _messagebox(_self, title, message):
    # a real modal dialog would spin its own main loop and stall the runner
    DIALOGS.append(f"{title}: {message}")


def _confirm(_self, title, message):
    DIALOGS.append(f"(declined) {title}: {message}")
    return False


fn.messagebox = _messagebox
fn.confirm_dialog = _confirm

# ── Safety net: nothing installs, removes or opens a terminal ────────────────

# read-only queries (pacman -Q*, -Ss, -Si, -Sl, -Sg, -Sp; yay/paru -Ss) stay allowed: pages run them while building
_FORBIDDEN = re.compile(
    r"\b(pacman|paru|yay|pamac)\s+(-S(?![a-z]*[silgp])[a-z]*|-R[a-z]*|-U)\b"
    r"|\b(paru|yay)\s*$"
    r"|\b(chsh|mkinitcpio|grub-mkconfig)\b"
    r"|\bsystemctl\s+(?!--user)(\S+\s+)?(enable|disable|start|stop|restart|mask|unmask)\b"
)
_TERMINALS = {"alacritty", "kitty", "xterm", "konsole", "foot", "gnome-terminal"}


def _forbidden(args):
    argv = args.split() if isinstance(args, str) else [str(a) for a in args]
    text = " ".join(argv)
    # a terminal counts only as the program being started (also behind sudo/env/setsid), not as a package name
    launched, skip = "", False
    for arg in argv:
        if skip or "=" in arg:
            skip = False
            continue
        if arg in ("-u", "-g", "-C"):
            skip = True
            continue
        if arg.startswith("-") or os.path.basename(arg) in ("sudo", "env", "setsid", "nohup", "exec"):
            continue
        launched = os.path.basename(arg)
        break
    if launched in _TERMINALS or _FORBIDDEN.search(text):
        return text
    return None


class _GuardedPopen(subprocess.Popen):
    def __init__(self, args, *a, **kw):
        hit = _forbidden(args)
        if hit:
            BLOCKED.append(hit[:300])
            raise OSError(f"blocked by the ATT live test: {hit[:120]}")
        super().__init__(args, *a, **kw)


subprocess.Popen = _GuardedPopen
_orig_system = os.system


def _guarded_system(command):
    if _forbidden(command):
        BLOCKED.append(command[:300])
        return 1
    return _orig_system(command)


os.system = _guarded_system
fn.system = _guarded_system


def record(step, verdict, detail=""):
    RESULTS.append((step, verdict, detail))
    print(f"[{verdict}] {step}: {detail}", flush=True)


# ── Read-backs ───────────────────────────────────────────────────────────────

def sh(*cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)
    return p.returncode, (p.stdout + p.stderr).strip()


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def owned_by_user(path):
    try:
        return os.stat(path).st_uid == USER_UID
    except OSError:
        return False


def shot(name):
    path = os.path.join(OUT, "shots", f"{len(SHOTS) + 1:02d}-{name}.png")
    if os.environ.get("WAYLAND_DISPLAY"):
        sh("grim", path)
    else:
        sh("import", "-window", "root", path)
    SHOTS.append(path)
    return os.path.basename(path)


def close_popups(win):
    """Close ATT's own startup prompts (nanorc, tweak tools) so they don't cover the screenshots."""
    for w in Gtk.Window.list_toplevels():
        if w is not win and isinstance(w, Gtk.Window) and w.get_visible():
            record("Startup prompt", "INFO", f"closed '{w.get_title()}' without answering")
            w.destroy()


def find_label(widget, text):
    if isinstance(widget, Gtk.Label) and widget.get_text() == text:
        return widget
    child = widget.get_first_child()
    while child is not None:
        found = find_label(child, text)
        if found:
            return found
        child = child.get_next_sibling()
    return None


def find_type(widget, cls):
    if isinstance(widget, cls):
        return widget
    child = widget.get_first_child()
    while child is not None:
        found = find_type(child, cls)
        if found:
            return found
        child = child.get_next_sibling()
    return None


# ── Steps ────────────────────────────────────────────────────────────────────

class Step:
    """One action on the GUI, the condition that says it finished, and the read-back."""

    def __init__(self, name, act, check, until=None, timeout=20, settle=800):
        self.name, self.act, self.check = name, act, check
        self.until, self.timeout, self.settle = until or (lambda: True), timeout, settle


def show_page(win, name, attr=None):
    """Return a step that switches the stack to a page and waits until it has built."""
    stack = win.att_stack

    def built():
        if attr:
            return hasattr(win, attr)
        child = stack.get_child_by_name(name)
        return child is not None and child.get_first_child() is not None

    def chk():
        if not built():
            record(f"Page {name}: built", "FAIL", "page did not build")
    return Step(f"show {name}", lambda: stack.set_visible_child_name(name), chk, until=built, settle=1200)


def sweep_steps(win):
    steps = []
    pages = win.att_stack.get_pages()
    for i in range(pages.get_n_items()):
        page = pages.get_item(i)
        name, title = page.get_name(), page.get_title()

        def chk(n=name, t=title):
            child = win.att_stack.get_child_by_name(n)
            ok = child is not None and child.get_first_child() is not None
            record(f"Sweep: {t} builds", "PASS" if ok else "FAIL",
                   f"screenshot {shot('page-' + re.sub(r'[^a-z0-9]+', '-', t.lower()))}")
        steps.append(Step(f"sweep {title}", lambda n=name: win.att_stack.set_visible_child_name(n), chk,
                          settle=1500))
    return steps


def autostart_steps(win, st):
    name = "att-livetest"
    path = fn.autostart + name + ".desktop"
    steps = [show_page(win, "stack13", "entry_name")]

    def act_add():
        win.entry_name.set_text(name)
        win.entry_command.set_text("true")
        win.entry_comment.set_text("ATT live test entry")
        autostart.on_add_autostart(win, None)

    def chk_add():
        text = read(path) or ""
        ok = "Hidden=false" in text and "Exec=true" in text and owned_by_user(path)
        record("Autostart: entry added", "PASS" if ok else "FAIL",
               f"exists {text != ''}, owned by user {owned_by_user(path)}, row shown {row() is not None}")
    steps.append(Step("autostart add", act_add, chk_add))

    def row():
        child = win.vvbox.get_first_child()
        while child is not None:
            if find_label(child, name):
                return child
            child = child.get_next_sibling()
        return None

    def act_toggle(on):
        found = row()
        switch = find_type(found, Gtk.Switch) if found else None
        if switch is None:
            raise RuntimeError("row or switch for the test entry not found")
        switch.set_active(on)

    def chk_toggle(on):
        text = read(path) or ""
        want = f"Hidden={'false' if on else 'true'}"
        ok = want in text and owned_by_user(path)
        record(f"Autostart: toggled {'on' if on else 'off'}", "PASS" if ok else "FAIL",
               f"want {want}, owned by user {owned_by_user(path)}")
    steps.append(Step("autostart off", lambda: act_toggle(False), lambda: chk_toggle(False)))
    steps.append(Step("autostart on", lambda: act_toggle(True), lambda: chk_toggle(True)))

    def act_remove():
        found = row()
        if found is None:
            raise RuntimeError("row for the test entry not found")
        autostart.on_auto_remove_clicked(win, None, found, name)

    def chk_remove():
        ok = not os.path.exists(path) and row() is None
        record("Autostart: entry removed", "PASS" if ok else "FAIL",
               f"file gone {not os.path.exists(path)}, row gone {row() is None}")
    steps.append(Step("autostart remove", act_remove, chk_remove))
    return steps


# checkbox attribute -> fastfetch module name, as fastfetch.get_checkboxes reads them
_FF_MODULES = {
    "title": "title", "os": "os", "host": "host", "kernel": "kernel", "uptime": "uptime", "packages": "packages",
    "shell": "shell", "display": "display", "de": "de", "wm": "wm", "wmtheme": "wmtheme", "themes": "theme",
    "icons": "icons", "font": "font", "cursor": "cursor", "term": "terminal", "termfont": "terminalfont",
    "cpu": "cpu", "gpu": "gpu", "mem": "memory", "swap": "swap", "disks": "disk", "l_ip": "localip",
    "p_ip": "publicip", "batt": "battery", "pwr": "poweradapter", "local": "locale", "cblocks": "colors",
}


def fastfetch_steps(win, st):
    if not os.path.exists("/usr/bin/fastfetch"):
        return [Step("fastfetch", lambda: None,
                     lambda: record("Fastfetch", "INFO", "fastfetch not installed: skipped, no install path run"))]
    cfg = fn.fastfetch_config
    if not os.path.isfile(cfg):
        # the editor (checkboxes, presets, resets) is only built when a config exists; KiroTux keeps none on purpose
        return [Step("fastfetch", lambda: None,
                     lambda: record("Fastfetch", "INFO", f"no {cfg}: the page shows no editor, nothing to drive"))]
    steps = [show_page(win, "stack4", "fast_util")]

    def chk_att_defaults():
        ok = read(cfg) == read(fn.fastfetch_kiro) and owned_by_user(cfg)
        record("Fastfetch: Reset to ATT defaults copies the template", "PASS" if ok else "FAIL",
               f"same as template {read(cfg) == read(fn.fastfetch_kiro)}, owned by user {owned_by_user(cfg)}")
    steps.append(Step("fastfetch att defaults", lambda: fastfetch.on_reset_fast_att(win, None), chk_att_defaults))

    for label, setter, preset in (("Small", fastfetch.set_checkboxes_small, fastfetch._PRESET_SMALL),
                                  ("All", fastfetch.set_checkboxes_all, fastfetch._PRESET_ALL)):
        def act(s=setter):
            s(win)
            fastfetch.on_apply_fast(win, None)

        def chk(lbl=label, p=preset):
            raw = (read(cfg) or "").lower()
            # entries are plain strings ("os") or objects ({"type": "os", ...}); comments are already stripped
            modules = [(m if isinstance(m, str) else str(m.get("type", ""))).lower()
                       for m in fastfetch.get_fastfetch().get("modules", [])]
            # a module the file never lists can't be switched on by commenting, so only judge the ones it has
            # a module entry, commented or not: '"type": "os"' or a bare '"os",' line; never a key like "display": {
            listed = [a for a, mod in _FF_MODULES.items()
                      if re.search(rf'"type"\s*:\s*"{mod}"|^\s*(//)?\s*"{mod}"\s*,?\s*$', raw, re.MULTILINE)]
            wrong = [a for a in listed if (_FF_MODULES[a] in modules) != p[a]]
            rc, out = sh("sudo", "-u", fn.sudo_username, "fastfetch", "-c", cfg, "--logo", "none", "--pipe")
            parses = rc == 0 and "error" not in out.lower()
            record(f"Fastfetch: preset {lbl} applied to config.jsonc", "PASS" if not wrong and parses and
                   owned_by_user(cfg) else "FAIL", f"wrong modules {wrong}, fastfetch runs {parses}"
                   f"{'' if parses else ' (' + out[:120] + ')'}, owned by user {owned_by_user(cfg)}; "
                   f"screenshot {shot('fastfetch-' + lbl.lower())}")
        steps.append(Step(f"fastfetch preset {label}", act, chk))

    def chk_reset():
        bak = read(cfg + "-bak")
        if bak is None:
            record("Fastfetch: Reset from backup", "INFO", "no config.jsonc-bak, Reset has nothing to restore")
            return
        ok = read(cfg) == bak and owned_by_user(cfg)
        record("Fastfetch: Reset restores config.jsonc-bak", "PASS" if ok else "FAIL",
               f"same as -bak {read(cfg) == bak}, owned by user {owned_by_user(cfg)}")
    steps.append(Step("fastfetch reset", lambda: fastfetch.on_reset_fast(win, None), chk_reset))
    return steps


def shell_steps(win, st):
    steps = [show_page(win, "stack23")]
    targets = [("bash", fn.bash_config, fn.bashrc_kiro, shell.on_install_att_bashrc_clicked,
                shell.on_bash_reset_clicked)]
    if shutil.which("fish"):
        targets.append(("fish", fn.fish_config, fn.fish_config_kiro, shell.on_install_att_fish_config_clicked,
                        shell.on_fish_reset_clicked))
    else:
        steps.append(Step("fish", lambda: None, lambda: record("Shells: fish", "INFO", "fish not installed: skipped")))

    for name, cfg, source, apply_cb, reset_cb in targets:
        if not os.path.isfile(source):
            steps.append(Step(f"{name} source", lambda: None,
                              lambda n=name, s=source: record(f"Shells: {n}", "INFO", f"{s} missing: skipped")))
            continue

        def chk_apply(n=name, c=cfg, s=source):
            ok = read(c) == read(s) and owned_by_user(c)
            bak = c + "-bak"
            bak_owner = "n/a" if not os.path.exists(bak) else owned_by_user(bak)
            record(f"Shells: ATT {n} config applied", "PASS" if ok and bak_owner is not False else "FAIL",
                   f"same as ATT file {read(c) == read(s)}, owned by user {owned_by_user(c)}, "
                   f"-bak owned by user {bak_owner}")
        steps.append(Step(f"{name} apply", lambda cb=apply_cb: cb(win, None), chk_apply))

        def chk_reset(n=name, c=cfg):
            bak = read(c + "-bak")
            if bak is None:
                record(f"Shells: {n} Reset", "INFO", "no -bak file, Reset has nothing to restore")
                return
            ok = read(c) == bak and owned_by_user(c)
            note = "" if bak == st["pre"].get(c) else "; note: the -bak differs from the file before the test"
            record(f"Shells: {n} Reset restores the -bak", "PASS" if ok else "FAIL",
                   f"same as -bak {read(c) == bak}, owned by user {owned_by_user(c)}{note}")
        steps.append(Step(f"{name} reset", lambda cb=reset_cb: cb(win, None), chk_reset))
    return steps


def _wallpaper_live(path):
    """Return how the running session shows the wallpaper path, or '' when it can't be read back."""
    _rc, procs = sh("pgrep", "-a", "-u", fn.sudo_username, "-x", "swaybg|wbg")
    if path in procs:
        return procs
    user = wallpaper._wayland_user_cmd() if os.environ.get("WAYLAND_DISPLAY") else []
    if user and shutil.which("noctalia"):
        _rc, out = sh(*user, "noctalia", "msg", "wallpaper-get")
        if path in out:
            return out
    for client in ("awww", "swww"):
        if shutil.which(client):
            _rc, out = sh(*user, client, "query")
            if path in out:
                return out
    fehbg = read(os.path.join(fn.home, ".fehbg")) or ""
    return fehbg if path in fehbg else ""


def wallpaper_steps(win, st):
    steps = [show_page(win, "stack_wallpaper", "wallpaper_folder_entry")]

    def act():
        folder = win.wallpaper_folder_entry.get_text().strip()
        images = sorted(f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))) \
            if os.path.isdir(folder) else []
        st["wall"] = os.path.join(folder, images[0]) if images else None
        st["wall_mark"] = len(STATUS)
        if st["wall"]:
            wallpaper._on_thumb_clicked(win, None, st["wall"])
            wallpaper.on_apply_wallpaper(win)

    def done():
        return not st.get("wall") or len(STATUS) > st["wall_mark"]

    def chk():
        if not st["wall"]:
            record("Wallpaper", "INFO", "no images in the ATT wallpaper folder")
            return
        said = STATUS[st["wall_mark"]:]
        set_ok = any(s.startswith("Wallpaper set") for s in said)
        live = _wallpaper_live(st["wall"])
        verdict = "PASS" if set_ok and live else ("INFO" if set_ok else "FAIL")
        record("Wallpaper: applied", verdict, f"status {said}; live read-back "
               f"{live.splitlines()[0] if live else 'not readable for this setter'}; screenshot {shot('wallpaper')}")
    steps.append(Step("wallpaper apply", act, chk, until=done, timeout=30, settle=2500))
    return steps


def build_steps(win):
    st = {"pre": {}}

    def chk_baseline():
        close_popups(win)
        for path in (fn.bash_config, fn.fish_config, fn.fastfetch_config):
            st["pre"][path] = read(path)
        record("Baseline", "INFO", f"user {fn.sudo_username}, distro {fn.distr}, "
               f"session {'wayland' if os.environ.get('WAYLAND_DISPLAY') else 'x11'}; screenshot {shot('baseline')}")
    # ATT's own startup (backups, permission fixes) runs in a thread: let it finish before touching anything
    steps = [Step("baseline", lambda: None, chk_baseline, settle=6000)]
    # the nanorc prompt chains a second prompt on destroy
    steps.append(Step("popups", lambda: None, lambda: close_popups(win), settle=1500))
    steps += sweep_steps(win)
    steps += autostart_steps(win, st)
    steps += fastfetch_steps(win, st)
    steps += shell_steps(win, st)
    steps += wallpaper_steps(win, st)
    return steps


# ── Runner ───────────────────────────────────────────────────────────────────

class Runner:
    """Run the steps one by one on the GTK main loop."""

    def __init__(self, app, win):
        self.app, self.win, self.steps, self.i = app, win, [], 0
        self.t0 = time.monotonic()

    def start(self):
        GLib.timeout_add(500, self._build)

    def _build(self):
        # Main builds its pages in an idle callback after __init__, so att_stack appears later
        if not hasattr(self.win, "att_stack"):
            if time.monotonic() - self.t0 < 60:
                return True
            record("Startup", "FAIL", "ATT window did not build its pages within 60s")
            self._finish()
            return False
        try:
            self.steps = build_steps(self.win)
        except Exception as e:  # report instead of hanging the main loop
            record("Startup", "FAIL", f"building the steps raised {type(e).__name__}: {e}")
            self._finish()
            return False
        GLib.timeout_add(3000, self._next)
        return False

    def _next(self):
        if self.i >= len(self.steps):
            self._finish()
            return False
        self.cur = self.steps[self.i]
        self.i += 1
        self.marks = (len(CRASHES), len(ERRORS), len(DIALOGS), len(BLOCKED))
        self.t0 = time.monotonic()
        print(f"-- {self.cur.name}", flush=True)
        try:
            self.cur.act()
        except Exception as e:  # report and carry on with the next step
            record(self.cur.name, "FAIL", f"action raised {type(e).__name__}: {e}")
            GLib.timeout_add(300, self._next)
            return False
        GLib.timeout_add(250, self._wait)
        return False

    def _wait(self):
        done = self.cur.until()
        if done or time.monotonic() - self.t0 > self.cur.timeout:
            if not done:
                record(self.cur.name, "FAIL", f"no result within {self.cur.timeout}s")
            GLib.timeout_add(self.cur.settle, self._check)
            return False
        return True

    def _check(self):
        try:
            self.cur.check()
        except Exception as e:  # report and carry on
            record(self.cur.name, "FAIL", f"check raised {type(e).__name__}: {e}")
        for label, items, mark in (("worker crashed", CRASHES, self.marks[0]), ("ATT logged an error", ERRORS,
                                   self.marks[1]), ("dialog shown", DIALOGS, self.marks[2]),
                                   ("blocked a terminal/install/system command", BLOCKED, self.marks[3])):
            for item in items[mark:]:
                record(self.cur.name, "FAIL", f"{label}: {item}")
        GLib.timeout_add(300, self._next)
        return False

    def _finish(self):
        counts = {v: sum(1 for r in RESULTS if r[1] == v) for v in ("PASS", "FAIL", "INFO")}
        with open(os.path.join(OUT, "report.json"), "w", encoding="utf-8") as f:
            json.dump({"results": RESULTS, "crashes": CRASHES, "errors": ERRORS, "dialogs": DIALOGS,
                       "blocked": BLOCKED, "status": STATUS, "counts": counts}, f, indent=1)
        print(f"== {counts}", flush=True)
        self.app.quit()


def main():
    """Start the real ATT window under a separate app id and run the steps."""
    if os.geteuid() != 0 or "PKEXEC_UID" not in os.environ:
        sys.exit("Run this through run-live-att.sh: ATT runs as root with PKEXEC_UID, so the test must too.")
    os.makedirs(os.path.join(OUT, "shots"), exist_ok=True)
    # same theme hand-off as ATT's own __main__: GTK_THEME must be set before the display opens
    theme, prefer_dark, _src = att_main._resolve_effective_theme()
    if theme:
        os.environ["GTK_THEME"] = theme + (":dark" if prefer_dark else "")
    app = Gtk.Application(application_id="org.kiro.att-livetest", flags=Gio.ApplicationFlags.NON_UNIQUE)

    def activate(_app):
        if Gdk.Display.get_default() is None:
            print("No display: check DISPLAY/WAYLAND_DISPLAY and XAUTHORITY", flush=True)
            app.quit()
            return
        css = Gtk.CssProvider()
        css.load_from_path(os.path.join(APP_DIR, "icons.css"))
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        window = att_main.Main(app)
        Runner(app, window).start()

    app.connect("activate", activate)
    app.run(None)


if __name__ == "__main__":
    main()

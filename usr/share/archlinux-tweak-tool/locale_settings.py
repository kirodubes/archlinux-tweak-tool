# ============================================================
# Authors: Erik Dubois
# ============================================================

import os
import shutil
import stat
import tempfile
import threading
import subprocess
import functions as fn
from gi.repository import GLib, Gtk
import att_i18n
from att_i18n import _

# Per-category locale overrides exposed in the UI. Each can follow LANG (unset)
# or carry its own generated locale, e.g. English system + European formatting.
LC_SENTINEL = _("Use LANG (default)")
LC_CATEGORIES = ["LC_NUMERIC", "LC_MONETARY", "LC_TIME"]
X11_NO_SECOND = _("(none)")
X11_SWITCH_OPTION = "grp:alt_shift_toggle"


def set_result(label, message, state="ok"):
    """Update an inline result label next to an Apply button (pending/ok/fail)."""
    palette = {"pending": ("#FFA500", ""), "ok": ("#8ec07c", "✓ "), "fail": ("#fb4934", "✗ ")}
    color, icon = palette[state]
    markup = f'<span foreground="{color}">{icon}{GLib.markup_escape_text(message)}</span>'
    GLib.idle_add(label.set_markup, markup)


def _fetch(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()


def _is_utf8_locale(name):
    """Only offer UTF-8 locales; latin-1 ones (e.g. fr_BE) break non-ASCII output."""
    return "utf-8" in name.lower() or "utf8" in name.lower()


def _language_from_locale(locale_val):
    """Map a locale (es_ES.UTF-8) to its LANGUAGE code (es_ES); '' for C/POSIX."""
    base = locale_val.split(".")[0].split("@")[0]
    return "" if base in ("C", "POSIX", "") else base


def _language_leads_with(language, lang_code):
    """True if the colon-separated LANGUAGE list already starts with lang_code."""
    return bool(lang_code) and language.split(":")[0] == lang_code


def _set_dropdown(dropdown, items, current):
    model = Gtk.StringList()
    for item in items:
        model.append(item)
    dropdown.set_model(model)
    try:
        idx = items.index(current)
    except ValueError:
        idx = 0
    dropdown.set_selected(idx)


def _parse_localectl():
    result = subprocess.run(["localectl", "status"], capture_output=True, text=True)
    data = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            key, _unused, val = line.partition(":")
            data[key.strip()] = val.strip()
    return data


def _read_locale_conf():
    """Parse /etc/locale.conf into a dict of LOCALE variables (authoritative source)."""
    conf = {}
    try:
        with open("/etc/locale.conf") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, _unused, val = stripped.partition("=")
                conf[key.strip()] = val.strip().strip('"')
    except OSError:
        pass
    return conf


def _write_language(language):
    """Rewrite the LANGUAGE line in /etc/locale.conf, or remove it when empty."""
    try:
        with open("/etc/locale.conf") as f:
            lines = [ln for ln in f if not ln.strip().startswith("LANGUAGE=")]
    except OSError:
        lines = []
    if language:
        lines.append(f"LANGUAGE={language}\n")
    try:
        with open("/etc/locale.conf", "w") as f:
            f.writelines(lines)
        fn.log_info(f"Set LANGUAGE={language} in /etc/locale.conf" if language else "Cleared LANGUAGE in /etc/locale.conf")
    except OSError as e:
        fn.log_error(f"Could not update LANGUAGE: {e}")


def _apply_locale_vars(self, conf, summary, result_label, log_summary=None):
    """Apply LANG + LC_* via localectl, writing any LANGUAGE setting to the file separately."""
    # localectl validates each value as a single locale name and refuses a colon-separated
    # LANGUAGE list, so LANGUAGE is excluded from the call and written to the file afterwards.
    language = conf.get("LANGUAGE", "")
    assignments = [f"{k}={v}" for k, v in conf.items() if v and k != "LANGUAGE"]
    if not assignments:
        fn.log_warn("No locale variables to set")
        set_result(result_label, _("No locale variables to set"), "fail")
        return
    try:
        subprocess.run(["localectl", "set-locale", *assignments], check=True)
        if "LANGUAGE" in conf:
            _write_language(language)
        fn.log_success(log_summary or summary)
        set_result(result_label, summary, "ok")
        GLib.idle_add(fn.show_in_app_notification, self, summary)
    except subprocess.CalledProcessError as e:
        fn.log_error(f"Failed to set locale: {e}")
        set_result(result_label, _("Failed: {error}").format(error=e), "fail")
    refresh_status(self)


def get_x11_variants(layout):
    result = subprocess.run(["localectl", "list-x11-keymap-variants", layout], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    return [""] + lines if lines else [""]


def refresh_status(self):
    status = _parse_localectl()
    lang = status.get("System Locale", "LANG=—").replace("LANG=", "")
    vc_keymap = status.get("VC Keymap", "—")
    x11_layout = status.get("X11 Layout", "—")
    x11_variant = status.get("X11 Variant", "")
    x11_display = x11_layout + (f" ({x11_variant})" if x11_variant.strip(",") else "")

    tz_result = subprocess.run(
        ["timedatectl", "show", "--property=Timezone", "--value"], capture_output=True, text=True
    )
    timezone = tz_result.stdout.strip() or "—"
    language = _read_locale_conf().get("LANGUAGE", "")

    GLib.idle_add(self.lbl_locale_current.set_text, lang)
    GLib.idle_add(self.lbl_language_current.set_text, language or _("(not set)"))
    GLib.idle_add(self.lbl_keymap_current.set_text, vc_keymap)
    GLib.idle_add(self.lbl_x11_current.set_text, x11_display)
    GLib.idle_add(self.lbl_timezone_current.set_text, timezone)


def populate_dropdowns(self):
    def _run():
        locales = [loc for loc in (_fetch(["localectl", "list-locales"]) or []) if _is_utf8_locale(loc)] or [
            "en_US.UTF-8"
        ]
        keymaps = _fetch(["localectl", "list-keymaps"]) or ["us"]
        x11_layouts = _fetch(["localectl", "list-x11-keymap-layouts"]) or ["us"]
        timezones = _fetch(["timedatectl", "list-timezones"]) or ["UTC"]

        status = _parse_localectl()
        current_locale = status.get("System Locale", "LANG=en_US.UTF-8").replace("LANG=", "")
        current_keymap = status.get("VC Keymap", "")
        x11_layout_raw = status.get("X11 Layout", "")
        x11_variant_raw = status.get("X11 Variant", "")
        layout_parts = x11_layout_raw.split(",")
        current_x11_layout = layout_parts[0]
        current_x11_second = layout_parts[1] if len(layout_parts) > 1 else X11_NO_SECOND
        current_x11_variant = x11_variant_raw.split(",")[0]
        current_tz = subprocess.run(
            ["timedatectl", "show", "--property=Timezone", "--value"], capture_output=True, text=True
        ).stdout.strip()

        variants = get_x11_variants(current_x11_layout) if current_x11_layout else [""]
        x11_display = x11_layout_raw + (f" ({x11_variant_raw})" if x11_variant_raw.strip(",") else "")

        conf = _read_locale_conf()
        lc_items = [LC_SENTINEL] + locales
        lc_current = {cat: conf.get(cat, "") for cat in LC_CATEGORIES}

        def _populate():
            _set_dropdown(self.locale_dropdown, locales, current_locale)
            _set_dropdown(self.keymap_dropdown, keymaps, current_keymap)
            _set_dropdown(self.timezone_dropdown, timezones, current_tz)
            _set_dropdown(self.x11_layout_dropdown, x11_layouts, current_x11_layout)
            _set_dropdown(self.x11_variant_dropdown, variants, current_x11_variant)
            _set_dropdown(self.x11_second_dropdown, [X11_NO_SECOND] + x11_layouts, current_x11_second)
            for cat in LC_CATEGORIES:
                _set_dropdown(self.lc_dropdowns[cat], lc_items, lc_current[cat] or LC_SENTINEL)
            self._locale_populating[0] = False
            self.lbl_locale_current.set_text(current_locale or "—")
            self.lbl_language_current.set_text(conf.get("LANGUAGE", "") or _("(not set)"))
            self.lbl_keymap_current.set_text(current_keymap or "—")
            self.lbl_x11_current.set_text(x11_display or "—")
            self.lbl_timezone_current.set_text(current_tz or "—")

        GLib.idle_add(_populate)

    threading.Thread(target=_run, daemon=True).start()
    refresh_language_packs(self)


# ── Language packs ─────────────────────────────────────────────────────
# Arch ships app translations and spell-check dictionaries as separate packages.
# app      : package that must be installed before its pack is offered
# prefix   : pack name = prefix + candidate, tried in order
# patterns : candidates built from the locale's language (ll) and country (cc)
_APP_PATTERNS = ("{ll}-{cc}", "{ll}", "{ll}-{ll}")
LANGPACK_APPS = [
    {"app": "firefox", "label": "Firefox", "prefix": "firefox-i18n-", "patterns": _APP_PATTERNS},
    {"app": "thunderbird", "label": "Thunderbird", "prefix": "thunderbird-i18n-", "patterns": _APP_PATTERNS},
    {"app": "libreoffice-fresh", "label": "LibreOffice", "prefix": "libreoffice-fresh-", "patterns": _APP_PATTERNS},
    {"app": "libreoffice-still", "label": "LibreOffice", "prefix": "libreoffice-still-", "patterns": _APP_PATTERNS},
    # comprehensive = the French superset dictionary; _any = the all-countries Spanish one
    {"app": "hunspell", "label": "Hunspell", "prefix": "hunspell-",
     "patterns": ("{ll}_{cc}", "{ll}-{cc}", "{ll}", "{ll}_any", "{ll}-comprehensive")},
]
# English is built into these apps; their en-us pack would add nothing.
_BUILTIN_PACKS = {"firefox-i18n-en-us", "thunderbird-i18n-en-us"}
# Firefox and Thunderbird ignore an installed language pack until intl.locale.requested is set:
# "" follows the system language, "de" asks for German. A default pref, so the app's own setting still wins.
_LANGUAGE_PREFS = {
    "firefox-i18n-": "/usr/lib/firefox/browser/defaults/preferences/att-language.js",
    "thunderbird-i18n-": "/usr/lib/thunderbird/defaults/pref/att-language.js",
}


def _requested_locale(package, prefix):
    """firefox-i18n-pt-br -> pt-BR, the locale code Firefox and Thunderbird expect."""
    ll, _sep, cc = package[len(prefix):].partition("-")
    return f"{ll}-{cc.upper()}" if cc else ll


def _wanted_language_prefs(packages, follow_system, english=False):
    """Return {pref file: content} for the Firefox/Thunderbird packs among packages."""
    wanted = {}
    for prefix, target in _LANGUAGE_PREFS.items():
        pkg = next((p for p in packages if p.startswith(prefix)), None)
        if not os.path.isdir(os.path.dirname(target)):
            continue
        if pkg is not None:
            value = "" if follow_system else _requested_locale(pkg, prefix)
        elif english and not follow_system:
            value = "en-US"  # English is built in: no pack, only the request
        else:
            continue
        wanted[target] = ("// Written by ArchLinux Tweak Tool (Locale page, Language Packs).\n"
                          f'pref("intl.locale.requested", "{value}");\n')
    return wanted


def _stale_language_prefs(wanted):
    """Return the pref files whose content differs from what the packs need."""
    stale = []
    for target, content in wanted.items():
        try:
            with open(target, encoding="utf-8") as f:
                if f.read() == content:
                    continue
        except OSError:
            pass
        stale.append(target)
    return stale


def _write_language_prefs(self, packages):
    """Make Firefox/Thunderbird use their installed language pack."""
    wanted = _wanted_language_prefs(packages, self.langpack_follow_system, self.langpack_english)
    for target, content in wanted.items():
        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            fn.log_info(f"Wrote {target}: {content.splitlines()[-1]}")
        except OSError as e:
            fn.log_error(f"Could not write {target}: {e}")


def langpack_default_choice():
    """ATT's own language when it differs from the system language, else None (= system)."""
    chosen = att_i18n.ACTIVE
    system = _read_locale_conf().get("LANG", "") or "en_US.UTF-8"
    return chosen if chosen and chosen.split("_")[0] != system.split("_")[0].split(".")[0] else None


def _pack_language(choice):
    """Return (locale to look packs up for, how to show it, follows the system language)."""
    system = _read_locale_conf().get("LANG", "") or "en_US.UTF-8"
    if choice is None or choice.split("_")[0] == system.split("_")[0].split(".")[0]:
        return system, system, True
    return ("en_US" if choice == "en" else choice), att_i18n.name(choice), False


def find_language_packs(lang, repo_names, installed):
    """Return (label, package) for every pack that exists for lang and whose app is installed."""
    base = lang.split(".")[0].split("@")[0]
    ll, _sep, cc = base.lower().partition("_")
    if not ll or ll in ("c", "posix"):
        return []
    packs = []
    for entry in LANGPACK_APPS:
        if entry["app"] not in installed:
            continue
        for pattern in entry["patterns"]:
            if "{cc}" in pattern and not cc:
                continue
            name = entry["prefix"] + pattern.format(ll=ll, cc=cc)
            if name in repo_names:
                if name not in _BUILTIN_PACKS:
                    packs.append((entry["label"], name))
                break
    return packs


def refresh_language_packs(self):
    """Rebuild the Language Packs rows for ATT's chosen language (else the system's) in the background."""
    def _run():
        choice = getattr(self, "langpack_choice", None)
        lang, shown, self.langpack_follow_system = _pack_language(choice)
        self.langpack_english = lang.startswith("en")
        repo_names = set(_fetch(["pacman", "-Slq"]))
        installed = {entry["app"] for entry in LANGPACK_APPS if fn.check_package_installed(entry["app"])}
        packs = find_language_packs(lang, repo_names, installed)
        status = [(label, pkg, fn.check_package_installed(pkg)) for label, pkg in packs]
        self.langpack_missing = [pkg for _label, pkg, done in status if not done]
        self.langpack_installed = [pkg for _label, pkg, done in status if done]
        self.langpack_stale = _stale_language_prefs(
            _wanted_language_prefs(self.langpack_installed, self.langpack_follow_system, self.langpack_english))
        fn.log_info(f"Language packs for {lang}: {', '.join(pkg for _l, pkg in packs) or 'none'}")
        GLib.idle_add(_show, shown, status)

    def _show(lang, status):
        child = self.langpack_rows.get_first_child()
        while child is not None:
            self.langpack_rows.remove(child)
            child = self.langpack_rows.get_first_child()
        self.lbl_langpack_intro.set_text(
            _("Some apps ship their translations and spell-check dictionaries as separate packages. "
              "These are the ones for {language}.").format(language=lang)
        )
        for label, pkg, done in status:
            row = Gtk.Label(xalign=0)
            row.set_margin_start(10)
            state = _("installed") if done else _("not installed")
            row.set_markup(f"{GLib.markup_escape_text(label)} — <tt>{pkg}</tt> — {state}")
            self.langpack_rows.append(row)
        self.btn_langpack_install.set_sensitive(bool(self.langpack_missing or self.langpack_stale))
        if not status:
            set_result(self.lbl_langpack_result,
                       _("No app on this system needs a separate language pack for {language}.").format(language=lang), "ok")
        elif not self.langpack_missing and not self.langpack_stale:
            set_result(self.lbl_langpack_result,
                       _("All language packs for {language} are installed.").format(language=lang), "ok")
        else:
            self.lbl_langpack_result.set_text("")

    threading.Thread(target=_run, daemon=True).start()


def on_install_language_packs(self, _widget):
    """Install the missing language packs in one terminal, then refresh the rows."""
    packages = list(getattr(self, "langpack_missing", []))
    if not packages:
        # packs already there (installed by hand), only their pref was missing or out of date
        _write_language_prefs(self, getattr(self, "langpack_installed", []))
        fn.show_in_app_notification(self, _("Restart the apps to use their language packs."))
        refresh_language_packs(self)
        return
    fn.log_subsection(f"Locale - Install language packs: {' '.join(packages)}")
    process = fn.launch_pacman_install_in_terminal(" ".join(packages))
    set_result(self.lbl_langpack_result, _("Installing in the terminal…"), "pending")

    def _wait():
        if process is not None:
            process.communicate()
        fn.invalidate_pkg_cache()
        done = [pkg for pkg in packages if fn.check_package_installed(pkg)]
        _write_language_prefs(self, done)
        if len(done) == len(packages):
            fn.log_success(f"Language packs installed: {' '.join(done)}")
            GLib.idle_add(fn.show_in_app_notification, self,
                          _("Language packs installed: {packages}. Restart the apps to use them.").format(
                              packages=", ".join(done)))
        else:
            fn.log_warn(f"Language packs not all installed: {' '.join(sorted(set(packages) - set(done)))}")
        refresh_language_packs(self)

    threading.Thread(target=_wait, daemon=True).start()


def on_apply_locale(self, _widget):
    fn.log_subsection("Locale - Apply System Locale")
    obj = self.locale_dropdown.get_selected_item()
    if obj is None:
        return
    locale_val = obj.get_string()

    conf = _read_locale_conf()
    conf["LANG"] = locale_val

    # LANGUAGE overrides LANG for UI translations, so a stale LANGUAGE would silently
    # keep the old display language. When it would shadow the new locale, align it
    # automatically so the change takes effect (the Current Settings row shows the result).
    new_language = _language_from_locale(locale_val)
    current_language = conf.get("LANGUAGE", "")
    if current_language and not _language_leads_with(current_language, new_language):
        conf["LANGUAGE"] = new_language
        fn.log_info(f"Aligned LANGUAGE to {new_language or '(cleared)'} so the new locale takes effect")

    fn.log_info(f"Setting LANG={locale_val} (preserving per-category LC_* overrides)")
    set_result(self.lbl_locale_result, _("Applying…"), "pending")

    def _apply():
        _apply_locale_vars(
            self,
            conf,
            _("System locale set to {locale} — log out to apply").format(locale=locale_val),
            self.lbl_locale_result,
            f"System locale set to {locale_val} — log out to apply",
        )
        refresh_language_packs(self)

    threading.Thread(target=_apply, daemon=True).start()


def on_apply_lc(self, category, _widget):
    fn.log_subsection(f"Locale - Apply {category}")
    dropdown = self.lc_dropdowns.get(category)
    if dropdown is None:
        return
    obj = dropdown.get_selected_item()
    if obj is None:
        return
    choice = obj.get_string()
    set_result(self.lbl_lc_result, _("Applying…"), "pending")

    def _apply():
        conf = _read_locale_conf()
        if choice == LC_SENTINEL:
            conf.pop(category, None)
            log_summary = f"{category} reset to follow LANG"
            summary = _("{category} reset to follow LANG").format(category=category)
        else:
            conf[category] = choice
            log_summary = f"{category} set to {choice}"
            summary = _("{category} set to {locale}").format(category=category, locale=choice)
        fn.log_info(log_summary)
        _apply_locale_vars(self, conf, summary, self.lbl_lc_result, log_summary)

    threading.Thread(target=_apply, daemon=True).start()


def on_reset_lc(self, _widget):
    fn.log_subsection("Locale - Reset per-category overrides to LANG")
    set_result(self.lbl_lc_result, _("Applying…"), "pending")

    def _reset():
        conf = _read_locale_conf()
        for category in LC_CATEGORIES:
            conf.pop(category, None)
        _apply_locale_vars(self, conf, _("Per-category locale overrides reset to LANG"), self.lbl_lc_result)
        for dropdown in self.lc_dropdowns.values():
            GLib.idle_add(dropdown.set_selected, 0)

    threading.Thread(target=_reset, daemon=True).start()


def _do_apply_keymap(self, keymap):
    fn.log_info(f"Setting VC keymap: {keymap}")
    try:
        subprocess.run(["localectl", "set-keymap", keymap], check=True)
        fn.log_success(f"Console keymap set to {keymap}")
        set_result(self.lbl_keymap_result, _("Console keymap set to {keymap}").format(keymap=keymap), "ok")
        GLib.idle_add(fn.show_in_app_notification, self, _("Console keymap set to {keymap}").format(keymap=keymap))
    except subprocess.CalledProcessError as e:
        fn.log_error(f"Failed to set keymap: {e}")
        set_result(self.lbl_keymap_result, _("Failed: {error}").format(error=e), "fail")
    refresh_status(self)


def on_apply_keymap(self, _widget):
    fn.log_subsection("Locale - Apply Console Keymap")
    obj = self.keymap_dropdown.get_selected_item()
    if obj is None:
        return
    set_result(self.lbl_keymap_result, _("Applying…"), "pending")
    threading.Thread(target=_do_apply_keymap, args=(self, obj.get_string()), daemon=True).start()


def on_sync_keymap(self, _widget):
    fn.log_subsection("Locale - Sync TTY keymap from X11 layout")

    set_result(self.lbl_keymap_result, _("Syncing…"), "pending")

    def _sync():
        status = _parse_localectl()
        # A two-layout setup ("us,ara") syncs its first layout; the TTY has no layout switching
        x11_layout = status.get("X11 Layout", "").split(",")[0]
        if not x11_layout:
            fn.log_warn("No X11 layout set, cannot sync")
            set_result(self.lbl_keymap_result, _("No X11 layout set — cannot sync"), "fail")
            return
        model = self.keymap_dropdown.get_model()
        if not model:
            fn.log_warn("Keymap list not loaded yet — cannot sync")
            set_result(self.lbl_keymap_result, _("Keymap list not loaded yet — cannot sync"), "fail")
            return
        n = model.get_n_items()
        for i in range(n):
            if model.get_item(i).get_string() == x11_layout:
                GLib.idle_add(self.keymap_dropdown.set_selected, i)
                break
        else:
            fn.log_warn(f"No TTY keymap matching '{x11_layout}' — sync not possible")
            set_result(self.lbl_keymap_result, _("No TTY keymap matching '{layout}'").format(layout=x11_layout), "fail")
            return
        _do_apply_keymap(self, x11_layout)

    threading.Thread(target=_sync, daemon=True).start()


def _follow_locale1_on_plasma():
    # KWin on Plasma Wayland ignores localectl unless kwinrc says FollowLocale1=true
    if not (shutil.which("kwin_wayland") and shutil.which("kwriteconfig6")):
        return False
    subprocess.run(
        ["runuser", "-u", fn.sudo_username, "--", "env", "HOME=" + fn.home,
         "kwriteconfig6", "--file", "kwinrc", "--group", "Wayland", "--key", "FollowLocale1", "true"],
        check=True,
    )
    return True


def on_apply_x11(self, _widget):
    """Set the X11/Wayland keyboard layout, optionally with a second layout toggled by Alt+Shift."""
    fn.log_subsection("Locale - Apply X11 Keyboard Layout")
    layout_obj = self.x11_layout_dropdown.get_selected_item()
    if layout_obj is None:
        return
    layout = layout_obj.get_string()
    variant_obj = self.x11_variant_dropdown.get_selected_item()
    variant = variant_obj.get_string() if variant_obj else ""
    second_obj = self.x11_second_dropdown.get_selected_item()
    second = second_obj.get_string() if second_obj else X11_NO_SECOND
    if second in (X11_NO_SECOND, layout):
        layouts, variants, options = layout, variant, ""
    else:
        layouts, variants, options = f"{layout},{second}", f"{variant}," if variant else "", X11_SWITCH_OPTION
    shown = f"{layouts} {variants.strip(',')}".strip()
    fn.log_info(f"Setting X11 layout: {layouts} variant: {variants or '(none)'} options: {options or '(none)'}")
    set_result(self.lbl_x11_result, _("Applying…"), "pending")

    def _apply():
        try:
            # localectl takes LAYOUT MODEL VARIANT OPTIONS in that order, so the model must come before the variant
            model = _parse_localectl().get("X11 Model", "") or "pc105"
            subprocess.run(["localectl", "set-x11-keymap", layouts, model, variants, options], check=True)
            fn.log_success(f"X11 layout set to {shown}")
            summary = _("X11 layout set to {layout}").format(layout=shown)
            if _follow_locale1_on_plasma():
                fn.log_success("Plasma: set FollowLocale1=true in ~/.config/kwinrc")
                summary += " — " + _("Plasma: log out and back in to use it")
            set_result(self.lbl_x11_result, summary, "ok")
            GLib.idle_add(fn.show_in_app_notification, self, _("X11 layout set to {layout}").format(layout=shown))
        except subprocess.CalledProcessError as e:
            fn.log_error(f"Failed to set X11 layout: {e}")
            set_result(self.lbl_x11_result, _("Failed: {error}").format(error=e), "fail")
        refresh_status(self)

    threading.Thread(target=_apply, daemon=True).start()


def get_available_locales():
    try:
        with open("/usr/share/i18n/SUPPORTED") as f:
            lines = f.readlines()
    except OSError:
        return []
    locales = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        # parts[1] is the charset; only offer UTF-8 so users cannot generate a
        # latin-1 locale that breaks non-ASCII output (e.g. "fr_BE ISO-8859-1").
        if len(parts) >= 2 and parts[1].upper() == "UTF-8":
            locales.append(parts[0])
    return sorted(set(locales))


def _update_locale_gen(locale_val):
    try:
        with open("/usr/share/i18n/SUPPORTED") as f:
            supported_map = {}
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                parts = stripped.split()
                if len(parts) >= 2:
                    supported_map[parts[0]] = stripped
    except OSError:
        fn.log_error("Cannot read /usr/share/i18n/SUPPORTED")
        return False

    full_entry = supported_map.get(locale_val)
    if full_entry is None:
        fn.log_warn(f"No SUPPORTED entry for {locale_val} — using bare name (charset may be missing)")
        full_entry = locale_val

    try:
        with open("/etc/locale.gen") as f:
            lines = f.readlines()
    except OSError:
        fn.log_error("Cannot read /etc/locale.gen")
        return False

    if any(line.strip() == full_entry for line in lines):
        fn.log_info(f"{locale_val} already enabled in /etc/locale.gen")
        return True

    new_lines = []
    uncommented = False
    for line in lines:
        stripped = line.strip()
        if stripped in (f"#{full_entry}", f"# {full_entry}"):
            new_lines.append(f"{full_entry}\n")
            uncommented = True
        else:
            new_lines.append(line)

    if not uncommented:
        new_lines.append(f"{full_entry}\n")
        fn.log_info(f"Appended {full_entry} to /etc/locale.gen")
    else:
        fn.log_info(f"Uncommented {locale_val} in /etc/locale.gen")

    try:
        with open("/etc/locale.gen", "w") as f:
            f.writelines(new_lines)
        fn.log_success("Updated /etc/locale.gen")
        return True
    except OSError as e:
        fn.log_error(f"Cannot write /etc/locale.gen: {e}")
        return False


def on_apply_generate_locale(self, _widget):
    fn.log_subsection("Locale - Generate New Locale")
    obj = self.available_locale_dropdown.get_selected_item()
    if obj is None or not obj.get_string():
        fn.log_warn("No locale selected")
        set_result(self.lbl_gen_locale_result, _("No locale selected"), "fail")
        return
    locale_val = obj.get_string()
    fn.log_info(f"Generating locale: {locale_val}")
    set_result(self.lbl_gen_locale_result, _("Generating {locale} in terminal…").format(locale=locale_val), "pending")

    script = f"""#!/bin/bash
set -euo pipefail
RESET=$(tput sgr0)
CYAN=$(tput setaf 6)
GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
YELLOW=$(tput setaf 3)
separator() {{ printf '%*s\\n' "${{COLUMNS:-80}}" '' | tr ' ' '-'; }}
header()  {{ separator; echo "${{CYAN}}>>> $*${{RESET}}"; separator; }}
success() {{ echo "${{GREEN}}[OK]  $*${{RESET}}"; }}
info()    {{ echo "      $*"; }}
warn()    {{ echo "${{YELLOW}}[!!]  $*${{RESET}}"; }}
error()   {{ echo "${{RED}}[!!]  $*${{RESET}}"; }}

header "Generate Locale: {locale_val}"
info "Running locale-gen..."
locale-gen
success "locale-gen completed"

header "Set System Locale"
localectl set-locale "LANG={locale_val}"
success "System locale set to {locale_val}"

read -p "Press Enter to close..."
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
        f.write(script)
        tmp_path = f.name
    os.chmod(tmp_path, stat.S_IRWXU)
    fn.show_in_app_notification(self, _("Generating locale {locale}...").format(locale=locale_val))

    def _run():
        if not _update_locale_gen(locale_val):
            os.unlink(tmp_path)
            set_result(self.lbl_gen_locale_result, _("Failed to update /etc/locale.gen"), "fail")
            return
        proc = subprocess.Popen(
            ["alacritty", "-e", "bash", tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.wait()
        os.unlink(tmp_path)
        fn.log_success(f"Locale {locale_val} generated and set")
        set_result(self.lbl_gen_locale_result, _("Locale {locale} generated and set — log out to apply").format(locale=locale_val), "ok")
        GLib.idle_add(populate_dropdowns, self)

    threading.Thread(target=_run, daemon=True).start()


def on_apply_timezone(self, _widget):
    fn.log_subsection("Locale - Apply Timezone")
    obj = self.timezone_dropdown.get_selected_item()
    if obj is None:
        return
    tz = obj.get_string()
    fn.log_info(f"Setting timezone: {tz}")
    set_result(self.lbl_tz_result, _("Applying…"), "pending")

    def _apply():
        try:
            subprocess.run(["timedatectl", "set-timezone", tz], check=True)
            fn.log_success(f"Timezone set to {tz}")
            set_result(self.lbl_tz_result, _("Timezone set to {timezone}").format(timezone=tz), "ok")
            GLib.idle_add(fn.show_in_app_notification, self, _("Timezone set to {timezone}").format(timezone=tz))
        except subprocess.CalledProcessError as e:
            fn.log_error(f"Failed to set timezone: {e}")
            set_result(self.lbl_tz_result, _("Failed: {error}").format(error=e), "fail")
        refresh_status(self)

    threading.Thread(target=_apply, daemon=True).start()

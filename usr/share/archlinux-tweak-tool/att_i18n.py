"""Load ATT's gettext catalogs and persist its language choice.

ATT runs as root through pkexec and parses the English output of the commands it runs, so this module never
touches LANG, LANGUAGE or LC_* in the environment: it only builds a translation object.
"""

import gettext
import json
import os
import pwd
from pathlib import Path

DOMAIN = "archlinux-tweak-tool"
_LOCAL_LOCALE_DIR = Path(__file__).resolve().parents[1] / "locale"
LOCALE_DIR = _LOCAL_LOCALE_DIR if _LOCAL_LOCALE_DIR.is_dir() else Path("/usr/share/locale")

NAMES = {
    "en": "English", "nl": "Nederlands", "de": "Deutsch", "es": "Español", "fr": "Français",
    "pt_BR": "Português (Brasil)", "ru": "Русский", "hu": "Magyar", "it": "Italiano", "tr": "Türkçe",
    "pl": "Polski", "ro": "Română", "zh_CN": "简体中文", "ja": "日本語",
}


def _real_user():
    """Return the pwd entry of the user who started ATT, or None when unknown."""
    uid = os.environ.get("PKEXEC_UID")
    try:
        return pwd.getpwuid(int(uid)) if uid else pwd.getpwuid(os.getuid())
    except (KeyError, ValueError):
        return None


def _prefs_path():
    user = _real_user()
    home = user.pw_dir if user else os.path.expanduser("~")
    return os.path.join(home, ".config", "archlinux-tweak-tool", "prefs.json")


PREFS_PATH = _prefs_path()


def available():
    """Return English and every language with a compiled catalog."""
    return ["en", *sorted(p.parent.parent.name for p in LOCALE_DIR.glob(f"*/LC_MESSAGES/{DOMAIN}.mo"))]


def name(code):
    """Return the language's own name, or its code when unknown."""
    return NAMES.get(code) or NAMES.get(code.split("_")[0]) or code


def _load_prefs():
    try:
        with open(PREFS_PATH, encoding="utf-8") as prefs_file:
            prefs = json.load(prefs_file)
    except (OSError, ValueError):
        return {}
    return prefs if isinstance(prefs, dict) else {}


def chosen():
    """Return the saved language choice, or None to follow the system."""
    code = _load_prefs().get("language")
    return code if code in available() else None


def _give_to_user(path):
    user = _real_user()
    if user and os.geteuid() == 0:
        os.chown(path, user.pw_uid, user.pw_gid)


def save_choice(code):
    """Save a language choice; None means follow the system. Files stay owned by the real user."""
    prefs = _load_prefs()
    prefs["language"] = code
    folder = os.path.dirname(PREFS_PATH)
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
        _give_to_user(folder)
    with open(PREFS_PATH, "w", encoding="utf-8") as prefs_file:
        json.dump(prefs, prefs_file, indent=2)
    _give_to_user(PREFS_PATH)


def _locale_conf_language():
    try:
        with open("/etc/locale.conf", encoding="utf-8") as conf:
            for line in conf:
                key, _sep, value = line.strip().partition("=")
                if key == "LANG":
                    return value.strip("\"'")
    except OSError:
        pass
    return ""


def _system_language():
    """Return the user's language: ATT_USER_LANG (set by the launcher), then /etc/locale.conf."""
    for value in (os.environ.get("ATT_USER_LANG", ""), _locale_conf_language()):
        code = value.split(":")[0].split(".")[0]
        if code and code not in ("C", "POSIX"):
            return code
    return "en"


_SIBLING = {"pt": "pt_BR", "zh": "zh_CN"}


def _shown(code):
    codes = available()
    base = code.split("_")[0]
    for candidate in (code, base, _SIBLING.get(base)):
        if candidate in codes:
            return candidate
    return "en"


SYSTEM = _shown(_system_language())
ACTIVE = os.environ.get("ATT_LANGUAGE") or chosen()

_translation = gettext.translation(DOMAIN, localedir=LOCALE_DIR, languages=[ACTIVE or SYSTEM], fallback=True)
_ = _translation.gettext
ngettext = _translation.ngettext


def N_(text):
    """Mark a string for translation without translating it here."""
    return text

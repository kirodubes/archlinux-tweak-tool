#!/usr/bin/env python3
"""Generate the Surfn + Neo Candy icon-theme tables and folder thumbnails for the Icons page.

Run automatically by up.sh. Both families are standalone colour-variant packages with the
same shape (sources in ~/EDU/<set>-* plus ~/KIRO for surfn-kiro, build recipes in ~/KIRO-PKG-BUILD-ICONS); the Icons
Surfn / Icons Neo Candy pages stay in sync without hand-editing icons.py for every variant.

For each variant this records token / package / family, and renders a small folder preview
by loading the theme's canonical folder icon (folder.png or folder.svg — PNG, then scalable,
then largest numbered size, since small numbered folders are often the `currentColor` symbolic
outline; following index.theme `Inherits=` for sparse overlays) scaled to a PNG via GdkPixbuf.

Outputs (one pair per set):
  * usr/share/archlinux-tweak-tool/data/<set>_families.json
  * usr/share/archlinux-tweak-tool/images/<set>/<token>.png
"""

import json
import os
import re
import sys
from os import path

import gi

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf  # noqa: E402

SCRIPT_DIR = path.dirname(path.realpath(__file__))
APP_DIR = path.join(SCRIPT_DIR, "usr/share/archlinux-tweak-tool")
DATA_DIR = path.join(APP_DIR, "data")
IMAGES_DIR = path.join(APP_DIR, "images")
THUMB_SIZE = 28

HOME = path.expanduser("~")
SRC_ROOT = os.environ.get("SURFN_SRC_ROOT", path.join(HOME, "EDU"))
# Kiro-owned themes (surfn-kiro) live in ~/KIRO; ~/EDU wins when a token exists in both.
EXTRA_SRC_ROOTS = [os.environ.get("SURFN_KIRO_SRC_ROOT", path.join(HOME, "KIRO"))]
PKG_ROOT = os.environ.get("SURFN_PKG_ROOT", path.join(HOME, "KIRO-PKG-BUILD-ICONS"))

# Display order of the families; tokens within a family are sorted alphabetically.
FAMILY_ORDER = ["Mint-X", "Mint-Y", "Tela", "Plasma", "Numix", "Papirus", "Arc / Breeze", "Horst", "Other"]
ARC_BREEZE = {"arc-breeze", "breeze-arc", "breeze-dark"}

# (label, source prefix, base token, output json, thumbnail subdir)
ICON_SETS = [
    ("Surfn", "surfn-", "surfn", "surfn_families.json", "surfn"),
    ("Neo Candy", "neo-candy-", "neo-candy-icons", "neocandy_families.json", "neocandy"),
]

_THEME_DIR_INDEX = {}
_TOKEN_ROOT = {}


def _classify(token, prefix):
    rest = token[len(prefix):] if token.startswith(prefix) else token
    if rest.startswith("mint-x"):
        return "Mint-X"
    if rest.startswith("mint-y"):
        return "Mint-Y"
    if rest.startswith("tela"):
        return "Tela"
    if rest.startswith("plasma"):
        return "Plasma"
    if rest.startswith("numix"):
        return "Numix"
    if rest.startswith("papirus"):
        return "Papirus"
    if rest.startswith("horst"):
        return "Horst"
    if rest in ARC_BREEZE:
        return "Arc / Breeze"
    return "Other"


def _theme_dir(token):
    icons_root = path.join(_TOKEN_ROOT.get(token, SRC_ROOT), token, "usr/share/icons")
    if not path.isdir(icons_root):
        return None
    for name in sorted(os.listdir(icons_root)):
        if path.isdir(path.join(icons_root, name)):
            return name
    return None


def _package_name(token):
    # Variant recipe dirs are named <token>; the base recipe dir is <token>-icons-git / <token>-git.
    for recipe in (token, token + "-icons-git", token + "-git"):
        pkgbuild = path.join(PKG_ROOT, recipe, "PKGBUILD")
        try:
            with open(pkgbuild, "r", encoding="utf-8") as f:
                for line in f:
                    m = re.match(r"\s*pkgname=\(?\s*['\"]?([^'\"()\s]+)", line)
                    if m:
                        return m.group(1)
        except OSError:
            continue
    return token + "-icons-git"


def _icon_size(p):
    """Sort weight for a folder icon path: scalable (full-colour vector) beats numbered sizes."""
    if "scalable" in p.lower():
        return 10000
    m = re.search(r"/(\d+)(?:@\d+x)?/", p)
    return int(m.group(1)) if m else 0


def _folder_in_root(theme_root):
    """Return the best folder.png/folder.svg under an absolute theme root, or None."""
    if not path.isdir(theme_root):
        return None
    hits = []
    for dirpath, _dirnames, filenames in os.walk(theme_root):
        for fname in filenames:
            if fname in ("folder.png", "folder.svg"):
                hits.append(path.join(dirpath, fname))
    if not hits:
        return None
    hits.sort(key=lambda p: (p.endswith(".png"), _icon_size(p)), reverse=True)
    return hits[0]


def _canonical_folder(token, theme_dir, _seen=None):
    """Folder icon for a theme, following index.theme Inherits to a sibling theme when absent."""
    if _seen is None:
        _seen = set()
    if theme_dir in _seen:
        return None
    _seen.add(theme_dir)

    theme_root = path.join(_TOKEN_ROOT.get(token, SRC_ROOT), token, "usr/share/icons", theme_dir)
    found = _folder_in_root(theme_root)
    if found:
        return found

    index = path.join(theme_root, "index.theme")
    try:
        with open(index, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("Inherits="):
                    for parent in line.split("=", 1)[1].split(","):
                        parent_token = _THEME_DIR_INDEX.get(parent.strip())
                        if parent_token:
                            found = _canonical_folder(parent_token, parent.strip(), _seen)
                            if found:
                                return found
    except OSError:
        pass
    return None


def _write_thumbnail(folder_path, thumb_dir, token):
    out = path.join(thumb_dir, token + ".png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(folder_path, THUMB_SIZE, THUMB_SIZE)
    pixbuf.savev(out, "png", [], [])
    return out


def _generate_set(label, prefix, base_token, data_filename, thumb_subdir):
    thumb_dir = path.join(IMAGES_DIR, thumb_subdir)
    data_out = path.join(DATA_DIR, data_filename)
    os.makedirs(thumb_dir, exist_ok=True)

    _TOKEN_ROOT.clear()
    for root in [SRC_ROOT] + [r for r in EXTRA_SRC_ROOTS if path.isdir(r)]:
        for name in os.listdir(root):
            if name in _TOKEN_ROOT or not (name == base_token or name.startswith(prefix)):
                continue
            if path.isdir(path.join(root, name, "usr/share/icons")):
                _TOKEN_ROOT[name] = root
    tokens = sorted(_TOKEN_ROOT)

    _THEME_DIR_INDEX.clear()
    for token in tokens:
        td = _theme_dir(token)
        if td:
            _THEME_DIR_INDEX[td] = token

    families = {fam: [] for fam in FAMILY_ORDER}
    no_thumb = []
    for token in tokens:
        theme_dir = _theme_dir(token)
        families[_classify(token, prefix)].append({"token": token, "package": _package_name(token)})

        folder = _canonical_folder(token, theme_dir) if theme_dir else None
        if not folder:
            base_dir = _theme_dir(base_token)
            if base_dir:
                folder = _canonical_folder(base_token, base_dir)
        if folder:
            try:
                _write_thumbnail(folder, thumb_dir, token)
            except Exception as error:  # noqa: BLE001 - a bad SVG/PNG must not abort the run
                no_thumb.append(f"{token} ({error})")
        else:
            no_thumb.append(token)

    ordered = {fam: sorted(items, key=lambda e: e["token"]) for fam, items in families.items() if families[fam]}
    with open(data_out, "w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2)
        f.write("\n")

    total = sum(len(v) for v in ordered.values())
    tag = thumb_subdir
    print(f"[{tag}] {total} variants across {len(ordered)} families -> {path.relpath(data_out, SCRIPT_DIR)}")
    if no_thumb:
        print(f"[{tag}] no folder preview for: {', '.join(no_thumb)}", file=sys.stderr)


def main():
    if not path.isdir(SRC_ROOT):
        print(f"source root not found: {SRC_ROOT} — skipping", file=sys.stderr)
        return 0
    os.makedirs(DATA_DIR, exist_ok=True)
    for entry in ICON_SETS:
        _generate_set(*entry)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Generate search_index.json from the ATT GUI source + search_synonyms.json.

Run automatically by up.sh. For every page it records three things:

  * title    — scraped from gui.py's add_titled() calls (matched live by the app too)
  * keywords — hand-authored aliases from search_synonyms.json
  * labels   — text scraped from that page's modules, so a control or option is
               findable by what it actually says on screen

Label scraping reads two things from each page's `*_gui` module AND its sibling
logic module (`<base>.py`):

  * button/label/markup text — set_text / set_label / set_markup / label= strings
  * data-list options        — string constants inside list/tuple/set/dict literals
                               (e.g. the `desktops = [...]` list of environments),
                               passed through a hardening filter that drops command,
                               flag and path noise.

The module->page link is derived from gui.py: each `<module>.gui(... vboxstack_x ...)`
call is tied to the `add_titled(vboxstack_x, "child", "Title")` that ships it.
Aliases keyed to a page title that no longer exists are reported as drift (non-fatal).
"""

import ast
import json
import re
import sys
from os import path

SCRIPT_DIR = path.dirname(path.realpath(__file__))
APP_DIR = path.join(SCRIPT_DIR, "usr/share/archlinux-tweak-tool")
GUI_PY = path.join(APP_DIR, "gui.py")
SYNONYMS = path.join(SCRIPT_DIR, "search_synonyms.json")
OUTPUT = path.join(APP_DIR, "search_index.json")

# the title is either a plain literal or wrapped for translation: _("Title") / N_("Title")
ADD_TITLED = re.compile(
    r'add_titled\(\s*([A-Za-z0-9_]+)\s*,\s*"([^"]+)"\s*,\s*(?:N?_\(\s*)?"([^"]+)"\s*\)?\s*\)'
)
MODULE_CALL = re.compile(r'([a-z_]+)\.gui\([^)]*?(vboxstack[A-Za-z0-9_]*)')
MARKUP_TAG = re.compile(r"<[^>]+>")
WORD = re.compile(r"[a-z0-9]+")

LABEL_CALLS = {"set_text", "set_label", "set_markup"}

# Generic UI verbs, English function words, and command/packaging noise — present
# on nearly every page (or every install command), so they carry no signal about
# WHICH page owns a control.
STOPWORDS = {
    "the", "and", "with", "for", "your", "you", "this", "that", "from", "into",
    "are", "was", "will", "not", "have", "has", "its", "out", "off", "all", "any",
    "use", "used", "via", "per", "page", "tab", "true", "false", "none",
    "view", "install", "installed", "installing", "uninstall", "remove", "removed",
    "enable", "enabled", "disable", "disabled", "apply", "applied", "reset",
    "open", "close", "click", "set", "get", "show", "hide", "save", "edit",
    "current", "currently", "select", "selected", "please", "note",
    "pacman", "pkexec", "sudo", "bash", "makepkg", "paru", "yay", "needed",
    "noconfirm", "ask", "git", "edu", "cp", "rsync", "systemctl",
}


def info(msg):
    print(f"[search-index] {msg}")


def warn(msg):
    print(f"[search-index] WARN: {msg}", file=sys.stderr)


def parse_gui():
    """Return (var_to_page, module_to_var) parsed from gui.py.

    var_to_page maps a vboxstack variable to {"child", "title"}; module_to_var
    maps a *_gui module name to the vboxstack variable it builds into.
    """
    with open(GUI_PY, encoding="utf-8") as f:
        source = f.read()
    var_to_page = {var: {"child": child, "title": title} for var, child, title in ADD_TITLED.findall(source)}
    module_to_var = {module: var for module, var in MODULE_CALL.findall(source)}
    return var_to_page, module_to_var


def load_synonyms():
    """Return {title: [keywords]} from the seed file, ignoring underscore keys."""
    with open(SYNONYMS, encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def _tokens(text):
    """Lowercase, strip markup, split into meaningful word tokens."""
    clean = MARKUP_TAG.sub(" ", text)
    return {
        word
        for word in WORD.findall(clean.lower())
        if len(word) >= 3 and not word.isdigit() and word not in STOPWORDS
    }


def _is_optionish(value):
    """True if a data-list string looks like a user option, not a command/flag/path."""
    value = value.strip()
    if len(value) < 2 or value[0] == "-":
        return False
    if any(c in value for c in "/=$%{}\\:"):
        return False
    return any(c.isalpha() for c in value)


def _literal(node):
    """Return the English text of a string node, looking through _("…"), N_("…"), ngettext() and .format()."""
    # Since the 2026-11-01 translation every label is _("…"); reading only bare literals lost 61% of the tokens.
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in ("_", "N_", "ngettext") and node.args:
            return _literal(node.args[0])
        if isinstance(func, ast.Attribute) and func.attr == "format":
            return _literal(func.value)
    return None


def scrape_module(module):
    """Return the set of meaningful tokens in a module's label text and data lists."""
    module_path = path.join(APP_DIR, f"{module}.py")
    if not path.isfile(module_path):
        return set()
    with open(module_path, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            warn(f"could not parse {module}.py — skipping")
            return set()

    tokens = set()
    for node in ast.walk(tree):
        # Button/label/markup text — keep multi-word phrases verbatim.
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in LABEL_CALLS:
                text = _literal(node.args[0]) if node.args else None
                if text:
                    tokens |= _tokens(text)
            for kw in node.keywords:
                text = _literal(kw.value) if kw.arg == "label" else None
                if text:
                    tokens |= _tokens(text)
        # Data-list options — string constants inside literals, hardened against noise.
        elif isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
            elements = node.elts if not isinstance(node, ast.Dict) else node.keys + node.values
            for elt in elements:
                text = _literal(elt) if elt is not None else None
                if text and _is_optionish(text):
                    tokens |= _tokens(text)
    return tokens


def main():
    var_to_page, module_to_var = parse_gui()
    info(f"Found {len(var_to_page)} pages, {len(module_to_var)} GUI modules in gui.py")
    synonyms = load_synonyms()

    titles = {page["title"] for page in var_to_page.values()}
    for title in synonyms:
        if title not in titles:
            warn(f"synonym key '{title}' matches no page title in gui.py — drift, skipping")

    # child -> scraped tokens, accumulated from each page's gui module + logic sibling
    labels_by_child = {}
    for module, var in module_to_var.items():
        page = var_to_page.get(var)
        if page is None:
            continue
        bucket = labels_by_child.setdefault(page["child"], set())
        bucket |= scrape_module(module)
        sibling = module[: -len("_gui")] if module.endswith("_gui") else None
        if sibling:
            bucket |= scrape_module(sibling)

    entries = []
    for page in sorted(var_to_page.values(), key=lambda p: p["title"]):
        keywords = synonyms.get(page["title"], [])
        labels = sorted(labels_by_child.get(page["child"], set()) - {k.lower() for k in keywords})
        entries.append({
            "title": page["title"],
            "child": page["child"],
            "keywords": keywords,
            "labels": labels,
        })

    out = {
        "_generated": "by gen-search-index.py — do not edit; edit search_synonyms.json",
        "pages": entries,
    }
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    total_labels = sum(len(e["labels"]) for e in entries)
    info(f"Wrote {len(entries)} pages, {total_labels} scraped tokens to {OUTPUT}")


if __name__ == "__main__":
    main()

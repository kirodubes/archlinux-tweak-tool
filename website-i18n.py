"""Generate the translated ATT website pages (docs/nl/index.html, ...) from docs/index.html and website-i18n/."""
# Trimmed copy of kiroproject.be's build-i18n.py for this one-page site. docs/index.html stays the single source;
# only the text comes from website-i18n/<lang>.po. Every unit (a sentence with its inline markup, a label, an alt
# text) goes to website-i18n/website.pot; msgmerge folds that into each <lang>.po, so an English sentence that
# changes turns its translation fuzzy and a removed one obsolete. Open units stay English on the translated page.
# GitHub Pages has no build step: run this after every English change and commit docs/<lang>/ with it.
#
#   python3 website-i18n.py                   refresh website.pot, merge each .po, write docs/<lang>/index.html
#   python3 website-i18n.py --strict          same, exit 1 when anything is untranslated, fuzzy or obsolete
#   python3 website-i18n.py --todo nl         print nl's open units as "@@ <id>" blocks
#   python3 website-i18n.py --fill nl FILE    merge "@@ <id>" blocks with translations into nl.po
import argparse
import hashlib
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "docs"
I18N = Path(__file__).resolve().parent / "website-i18n"
POT = I18N / "website.pot"
SITE = "https://kirodubes.github.io/archlinux-tweak-tool/"
PAGES = ["index.html"]

# folder = key, tag = <html lang> + hreflang (BCP 47), locale = gettext locale. Order is the switcher order,
# the same 13 languages and order as kiroproject.be.
LANGS = {code: {"tag": tag, "locale": locale, "name": name, "pages": PAGES} for code, tag, locale, name in [
    ("nl", "nl", "nl_BE", "Nederlands"),
    ("de", "de", "de_DE", "Deutsch"),
    ("es", "es", "es_ES", "Español"),
    ("ru", "ru", "ru_RU", "Русский"),
    ("fr", "fr", "fr_FR", "Français"),
    ("pt-br", "pt-BR", "pt_BR", "Português (Brasil)"),
    ("it", "it", "it_IT", "Italiano"),
    ("hu", "hu", "hu_HU", "Magyar"),
    ("tr", "tr", "tr_TR", "Türkçe"),
    ("pl", "pl", "pl_PL", "Polski"),
    ("ro", "ro", "ro_RO", "Română"),
    ("ja", "ja", "ja_JP", "日本語"),
    ("zh", "zh-Hans", "zh_CN", "简体中文"),
]}

TOKEN_RE = re.compile(
    r"<!--.*?-->|<(script|style|pre|svg|textarea|code)\b[^>]*>.*?</\1\s*>|<[^>]+>|[^<]+",
    re.DOTALL | re.IGNORECASE,
)
TAG_NAME_RE = re.compile(r"</?([a-zA-Z][a-zA-Z0-9-]*)")
INLINE = {"a", "span", "strong", "em", "b", "i", "kbd", "br", "small", "abbr", "sup", "sub", "mark", "u", "s",
          "wbr"}
VOID = {"br", "wbr"}
OPAQUE = ("<!--", "<script", "<style", "<pre", "<svg", "<textarea")
ATTR_RE = re.compile(r'\b(alt|title|aria-label|placeholder|data-gallery-alt)="([^"]*)"')
META_RE = re.compile(r'<meta\s[^>]*(?:name|property)="(?:description|og:title|og:description|og:image:alt|'
                     r'twitter:title|twitter:description|twitter:image:alt)"')
CONTENT_RE = re.compile(r'\bcontent="([^"]*)"')
# Visible text inside inline scripts: the copy button's 'Copied!'.
SCRIPT_RE = re.compile(r"""\b(title|desc): "([^"]*)"|(textContent = )'([^']*)'"""
                       r"""|(textContent = \w+ \? )'([^']*)' : '([^']*)'""")
URL_ATTR_RE = re.compile(r'\b(href|src|data-zoom|data-gallery-img|poster)="([^"]*)"')
SRCSET_RE = re.compile(r'\bsrcset="([^"]*)"')
BLOCK_RE = {name: re.compile(rf"(<!-- i18n:{name} -->).*?(<!-- /i18n:{name} -->)", re.DOTALL)
            for name in ("alternates", "switch")}
WS_RE = re.compile(r"\s+")
# Values that change every release become {0}, {1}, ... in the catalog, so a translated sentence survives
# the monthly version, date, size and checksum bump; the real values go back in after lookup.
VOLATILE_RE = re.compile(r"v\d{2}\.\d{2}\.\d{2}(?:\.\d+)?|\b\d{4}-\d{2}-\d{2}\b|\b[0-9a-f]{32}\b"
                         r"|\b\d+(?:\.\d+)?(?:&nbsp;|\s)?[GM]B\b")
PLACEHOLDER_RE = re.compile(r"\{(\d+)\}")
TAGS_RE = re.compile(r"<[^>]+>|&[a-z]+;|&#\d+;")
WORD_RE = re.compile(r"^[(\"“«„]?[^\W\d_]{2,}[.,:;!?)\"”»“]*$")


def norm(text):
    return WS_RE.sub(" ", text).strip()


def unit_id(key):
    return hashlib.sha1(key.encode()).hexdigest()[:8]


def classify(tok):
    """Return text, inline-open, inline-close, inline-void, inline-opaque or block."""
    if not tok.startswith("<"):
        return "text"
    if tok.startswith(OPAQUE):
        return "block"
    m = TAG_NAME_RE.match(tok)
    name = m.group(1).lower() if m else ""
    if name == "code":
        return "inline-opaque"
    if name not in INLINE:
        return "block"
    if name in VOID or tok.endswith("/>"):
        return "inline-void"
    return "inline-close" if tok.startswith("</") else "inline-open"


def page_url(lang, name):
    """Absolute URL of a page in a language (None = English)."""
    path = "" if name == "index.html" else name
    return SITE + (f"{lang}/" if lang else "") + path


def alternates(name):
    langs = [code for code, cfg in LANGS.items() if name in cfg["pages"]]
    if not langs:
        return ""
    links = [f'<link rel="alternate" hreflang="en" href="{page_url(None, name)}" />']
    links += [f'<link rel="alternate" hreflang="{LANGS[c]["tag"]}" href="{page_url(c, name)}" />' for c in langs]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{page_url(None, name)}" />')
    return "\n    " + "\n    ".join(links) + "\n    "


def switcher(name, current):
    """Language menu for page `name` seen in language `current` (None = English); links stay relative."""
    up = "../" if current else ""
    items = [(None, "en", "English", up + name)]
    for code, cfg in LANGS.items():
        href = (name if code == current else f"../{code}/{name}") if current else f"{code}/{name}"
        items.append((code, cfg["tag"], cfg["name"], href))
    label = (LANGS[current]["tag"] if current else "en").split("-")[0].upper()
    links = "\n".join(
        f'              <a href="{href}" lang="{tag}" hreflang="{tag}"'
        + (' aria-current="page"' if code == current else "") + f">{text}</a>"
        for code, tag, text, href in items)
    return f"""
          <details class="lang-menu">
            <summary aria-label="Language" title="Language">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              <span>{label}</span>
            </summary>
            <div class="lang-list">
{links}
            </div>
          </details>
          """


def fill_block(html, block, content):
    return BLOCK_RE[block].sub(lambda m: m.group(1) + content + m.group(2), html)


class Page:
    """One English page rendered into one language with a catalog (empty catalog = collect units only)."""

    def __init__(self, name, lang=None, catalog=None):
        self.name, self.lang, self.catalog = name, lang, catalog or {}
        self.units = []

    def lookup(self, key):
        """Translation of a normalised unit, or None; units without a single word are not text."""
        values = []

        def hold(m):
            values.append(m.group(0))
            return f"{{{len(values) - 1}}}"

        # The English pages glue a dash to the word before it (&nbsp;&mdash;) so it never starts a line; the
        # catalog keeps the plain spelling, so that typography never turns a translation fuzzy.
        key = VOLATILE_RE.sub(hold, key.replace("&nbsp;&mdash;", " &mdash;"))
        if "@@" in key or not any(WORD_RE.match(w) for w in TAGS_RE.sub(" ", key).split()):
            return None
        self.units.append(key)
        out = self.catalog.get(key)
        if out is None:
            return None
        return PLACEHOLDER_RE.sub(lambda m: values[int(m.group(1))], out).replace(" &mdash;", "&nbsp;&mdash;")

    def translate_run(self, toks):
        """Translate a run of text + inline tags as one unit when it holds a sentence, else per element."""
        joined = "".join(toks)
        if not joined.strip():
            return joined
        depth, top_text, balanced = 0, False, True
        for tok in toks:
            kind = classify(tok)
            if kind == "inline-open":
                depth += 1
            elif kind == "inline-close":
                depth -= 1
                balanced = balanced and depth >= 0
            elif kind in ("text", "inline-opaque") and depth == 0 and tok.strip():
                top_text = True
        balanced = balanced and depth == 0
        if balanced and top_text:
            out = self.lookup(norm(joined))
            if out is None:
                return joined
            return joined[: len(joined) - len(joined.lstrip())] + out + joined[len(joined.rstrip()):]
        if balanced:
            return self.translate_children(toks)
        return "".join(self.translate_run([t]) if classify(t) == "text" else t for t in toks)

    def translate_children(self, toks):
        """A run without top-level text (nav links side by side): translate each element's content."""
        out, i = [], 0
        while i < len(toks):
            if classify(toks[i]) != "inline-open":
                out.append(toks[i])
                i += 1
                continue
            depth, j = 0, i
            while j < len(toks):
                kind = classify(toks[j])
                depth += (kind == "inline-open") - (kind == "inline-close")
                if depth == 0:
                    break
                j += 1
            out += [toks[i], self.translate_run(toks[i + 1:j]), toks[j]]
            i = j + 1
        return "".join(out)

    def translate_value(self, value):
        out = self.lookup(norm(value)) if value.strip() else None
        return value if out is None else out

    def translate_tag(self, tok):
        """Translate the human-readable attributes of a tag."""
        if tok.startswith("<meta"):
            if not META_RE.match(tok):
                return tok
            return CONTENT_RE.sub(lambda m: f'content="{self.translate_value(m.group(1))}"', tok)
        return ATTR_RE.sub(lambda m: f'{m.group(1)}="{self.translate_value(m.group(2))}"', tok)

    def translate_script(self, tok):
        if "src=" in tok.split(">", 1)[0] or "ld+json" in tok.split(">", 1)[0]:
            return tok

        def repl(m):
            if m.group(1):
                return f'{m.group(1)}: "{self.translate_value(m.group(2))}"'
            if m.group(3):
                return f"{m.group(3)}'{self.translate_value(m.group(4))}'"
            return f"{m.group(5)}'{self.translate_value(m.group(6))}' : '{self.translate_value(m.group(7))}'"

        return SCRIPT_RE.sub(repl, tok)

    def translate(self, html):
        out, run = [], []
        for m in TOKEN_RE.finditer(html):
            tok = m.group(0)
            kind = classify(tok)
            if kind == "block":
                if run:
                    out.append(self.translate_run(run))
                    run = []
                if tok.startswith("<script"):
                    out.append(self.translate_script(tok))
                else:
                    out.append(tok if tok.startswith(OPAQUE) else self.translate_tag(tok))
            else:
                run.append(tok if kind in ("text", "inline-opaque") else self.translate_tag(tok))
        if run:
            out.append(self.translate_run(run))
        return "".join(out)

    def fix_url(self, url):
        """Relative links from /<lang>/: translated pages stay in the folder, everything else goes up."""
        if not url or url.startswith(("http:", "https:", "//", "/", "#", "mailto:", "data:", "javascript:", "tel:")):
            return url
        if re.split(r"[#?]", url)[0] in LANGS[self.lang]["pages"]:
            return url
        return "../" + url

    def localise(self, html):
        """Point the language attribute, canonical URL and relative paths at /<lang>/."""
        tag = LANGS[self.lang]["tag"]
        html = html.replace('<html lang="en"', f'<html lang="{tag}"', 1)
        own, local = page_url(None, self.name), page_url(self.lang, self.name)
        html = re.sub(rf'(<link rel="canonical" href="){re.escape(own)}"', rf'\g<1>{local}"', html)
        html = re.sub(rf'(<meta property="og:url"\s+content="){re.escape(own)}"', rf'\g<1>{local}"', html)
        html = URL_ATTR_RE.sub(lambda m: f'{m.group(1)}="{self.fix_url(m.group(2))}"', html)
        return SRCSET_RE.sub(
            lambda m: 'srcset="' + ", ".join(
                " ".join([self.fix_url(p.split()[0]), *p.split()[1:]]) for p in m.group(1).split(",")) + '"',
            html,
        )

    def render(self):
        html = (ROOT / self.name).read_text(encoding="utf-8")
        # Blocks are emptied first so the language names never become units, and filled last so their
        # links are not rewritten.
        html = fill_block(fill_block(html, "alternates", "@@ALT@@"), "switch", "@@SWITCH@@")
        html = self.translate(html)
        if self.lang:
            html = self.localise(html)
        html = html.replace("@@ALT@@", alternates(self.name)).replace("@@SWITCH@@", switcher(self.name, self.lang))
        return html



def write_if_changed(path, text):
    """Write only on change, so an unchanged language shows no diff."""
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def po_str(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t") + '"'


PO_HEADER = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n"Content-Transfer-Encoding: 8bit\\n"\n'


def write_pot(units):
    """units: {key: [page, ...]} in first-seen order."""
    entries = [PO_HEADER]
    for key, pages in units.items():
        entries.append(f"#. id {unit_id(key)}\n#: {' '.join(pages)}\nmsgid {po_str(key)}\nmsgstr \"\"\n")
    write_if_changed(POT, "# ATT website, generated by website-i18n.py: do not edit.\n" + "\n".join(entries))


def run(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def read_mo(path):
    """Translated, non-fuzzy entries of a compiled catalog (msgfmt leaves out untranslated and fuzzy)."""
    data = path.read_bytes()
    count, orig, trans = struct.unpack("<3I", data[8:20])
    catalog = {}
    for i in range(count):
        olen, ooff = struct.unpack("<2I", data[orig + 8 * i:orig + 8 * i + 8])
        tlen, toff = struct.unpack("<2I", data[trans + 8 * i:trans + 8 * i + 8])
        if olen:
            catalog[data[ooff:ooff + olen].decode()] = data[toff:toff + tlen].decode()
    return catalog


def merge_and_compile(lang):
    """Merge website.pot into <lang>.po (create it if new), return (catalog, msgfmt statistics, obsolete count)."""
    po = I18N / f"{lang}.po"
    if po.exists():
        run("msgmerge", "--quiet", "--update", "--backup=none", "--previous", str(po), str(POT))
    else:
        run("msginit", "--no-translator", f"--locale={LANGS[lang]['locale']}.UTF-8", f"--input={POT}",
            f"--output-file={po}")
    with tempfile.TemporaryDirectory() as tmp:
        mo = Path(tmp) / f"{lang}.mo"
        stats = run("msgfmt", "--statistics", "-o", str(mo), str(po)).stderr.strip()
        catalog = read_mo(mo)
    obsolete = sum(1 for line in po.read_text(encoding="utf-8").splitlines() if line.startswith("#~ msgid"))
    return catalog, stats, obsolete


def todo(lang, units, catalog):
    for key in units:
        if key not in catalog:
            print(f"@@ {unit_id(key)}\n{key}\n")


def fill(lang, units, path):
    """Apply "@@ <id>" blocks to <lang>.po; the new translations win over fuzzy or empty ones."""
    by_id = {unit_id(k): k for k in units}
    entries, unknown = [PO_HEADER], []
    for block in re.split(r"^@@ ", Path(path).read_text(encoding="utf-8"), flags=re.MULTILINE)[1:]:
        uid, _, text = block.partition("\n")
        key, text = by_id.get(uid.strip()), norm(text)
        if key is None:
            unknown.append(uid.strip())
        elif text:
            entries.append(f"msgid {po_str(key)}\nmsgstr {po_str(text)}\n")
    po = I18N / f"{lang}.po"
    with tempfile.TemporaryDirectory() as tmp:
        frag = Path(tmp) / "fill.po"
        frag.write_text("\n".join(entries), encoding="utf-8")
        run("msgcat", "--use-first", "-o", str(po), str(frag), str(po))
    run("msgmerge", "--quiet", "--update", "--backup=none", "--previous", str(po), str(POT))
    print(f"{lang}: filled {len(entries) - 1} unit(s)" + (f", unknown ids: {' '.join(unknown)}" if unknown else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true", help="exit 1 on untranslated, fuzzy or obsolete entries")
    ap.add_argument("--todo", metavar="LANG", help="print the open units of LANG")
    ap.add_argument("--fill", nargs=2, metavar=("LANG", "FILE"), help="merge translated @@ blocks into LANG.po")
    args = ap.parse_args()

    # The English pages get their switcher and hreflang blocks first; the units come from the result.
    units = {}
    for name in PAGES:
        page = Page(name)
        html = page.render()
        write_if_changed(ROOT / name, html)
        for key in page.units:
            units.setdefault(key, [])
            if name not in units[key]:
                units[key].append(name)
    write_pot(units)

    if args.fill:
        fill(args.fill[0], units, args.fill[1])
    problems = 0
    for lang, cfg in LANGS.items():
        if (args.todo or (args.fill and args.fill[0])) not in (None, lang):
            continue
        catalog, stats, obsolete = merge_and_compile(lang)
        if args.todo:
            todo(lang, [k for k in units if any(p in cfg["pages"] for p in units[k])], catalog)
            continue
        for name in cfg["pages"]:
            write_if_changed(ROOT / lang / name, Page(name, lang, catalog).render())
        print(f"{lang}: {stats.rstrip('.')}" + (f", {obsolete} obsolete" if obsolete else ""))
        open_units = sum(1 for k in units if k not in catalog)
        problems += open_units + obsolete
    return 1 if args.strict and problems else 0


if __name__ == "__main__":
    sys.exit(main())

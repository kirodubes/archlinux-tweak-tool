# ATT website (GitHub Pages)

The one-page ArchLinux Tweak Tool site, served by GitHub Pages from this folder
(`main` branch, `/docs` path) at **https://kirodubes.github.io/archlinux-tweak-tool/**.

Static HTML and CSS, no framework. Open `index.html` and it works. The only build step is
the translations (see below); GitHub Pages serves the committed files as they are.

## Layout

```
index.html          the whole page (English, the single source)
<lang>/index.html   generated translations: nl de es ru fr pt-br it hu tr pl ro ja zh
                    (never edit by hand)
css/style.css       verbatim copy of Kiro-HQ/web-shared/style.css — do not edit here
css/att.css         ATT-specific components (themes, lightbox, back-to-top, cards)
assets/branding/    favicons + logo (shared Kiro branding)
assets/screenshots/ att1..att24.webp, converted from this repo's images/
```

## Rules

- **Never hand-edit `css/style.css`.** It is a copy of the canonical stylesheet in
  `Kiro-HQ/web-shared/style.css`; edit there and re-propagate. Anything ATT-only goes in
  `css/att.css`, which loads after it.
- The footer between the `KIRO:FOOTER` markers is managed by
  `Kiro-HQ/propagate-web-shared.sh` — do not edit it by hand.
- No emoji in page copy. Inline SVG or nothing.
- Every image needs real alt text, `loading="lazy"`, and explicit `width`/`height`.

## Translations

Same gettext pipeline as kiroproject.be. `../website-i18n.py` (repo root, so it is not
served) reads `index.html`, writes the units to `../website-i18n/website.pot`, merges that
into `../website-i18n/<lang>.po`, and renders `<lang>/index.html` with relative links,
`hreflang` alternates and the language menu. GitHub Pages has no build step, so after any
English change:

```bash
python3 website-i18n.py                 # report open units per language, re-render
python3 website-i18n.py --todo nl > f   # open units as "@@ <id>" blocks; translate under each id
python3 website-i18n.py --fill nl f     # merge them into nl.po
python3 website-i18n.py --strict        # exit 1 while any language has open units
```

Then commit `index.html`, the changed `.po` files and the `<lang>/` pages together. An
untranslated sentence shows in English on a translated page until it is filled. The ATT
page names reuse the app's own translations in `../po/` (`msgmerge -C`), so the site and
the app call each page the same thing. Language rules and register: `Kiro-HQ/TRANSLATIONS/`.
The page needs both empty marker pairs, `<!-- i18n:alternates -->` in `<head>` and
`<!-- i18n:switch -->` in the header; the script fills them.

## Themes

Six: `nordic` (default), `slate`, `carbon`, `ember`, plus two light grounds, `sepia` and
`paper`. The picker writes `data-theme` and `data-mode` on `<html>` before first paint and
persists the choice in `localStorage`. Light themes share their component overrides via
`[data-mode="light"]`, so a new light theme needs only a token block.

The accent colour is switchable independently (five palettes). On light grounds the accent
is darkened through `--accent-ink` — 55% raw accent, the highest share that keeps every
accent above WCAG AA on both light themes.

## Refreshing the screenshots

The gallery is generated from this repository's `images/att1.png` … `att24.png`:

```bash
for i in $(seq 1 24); do
  magick "images/att${i}.png" -resize 1280x -quality 82 "docs/assets/screenshots/att${i}.webp"
done
```

Captions and alt text are hardcoded in `index.html` and follow the page order in the main
README's gallery table. If a screenshot is re-shot for a different page, update the
caption, the alt text and that table together.

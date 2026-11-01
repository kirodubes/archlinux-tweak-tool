#!/bin/bash
set -euo pipefail
##################################################################################################################
# Author    : Erik Dubois
# Website   : https://kiroproject.be
##################################################################################################################
#
#   Purpose:
#   - Extract every _() / N_() / ngettext() string of usr/share/archlinux-tweak-tool/*.py into
#     po/archlinux-tweak-tool.pot.
#   - Merge that template into each po/<lang>.po and compile it into
#     usr/share/locale/<lang>/LC_MESSAGES/archlinux-tweak-tool.mo.
#   - Write the menu entry usr/share/applications/archlinux-tweak-tool.desktop from
#     po/archlinux-tweak-tool.desktop.in. Edit the .in file, never the .desktop (it is overwritten).
#
##################################################################################################################

RESET=$(tput sgr0)
CYAN=$(tput setaf 6)
GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
YELLOW=$(tput setaf 3)

separator() {
    echo "${CYAN}===============================================================================${RESET}"
}

header() {
    echo ""
    separator
    echo "${CYAN}  $1${RESET}"
    separator
}

success() { echo "${GREEN}  ✓ $1${RESET}"; }
info()    { echo "    $1"; }
warn()    { echo "${YELLOW}  ⚠ $1${RESET}"; }
error()   { echo "${RED}  ✗ $1${RESET}"; }

trap 'error "Command failed at line $LINENO"' ERR

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$SCRIPT_DIR")"
DOMAIN="archlinux-tweak-tool"
APP_DIR="usr/share/archlinux-tweak-tool"
POT="$SCRIPT_DIR/$DOMAIN.pot"
DESKTOP_IN="$SCRIPT_DIR/$DOMAIN.desktop.in"
DESKTOP="$REPO/usr/share/applications/$DOMAIN.desktop"

# ── Extract ───────────────────────────────────────────────────────────────────
header "Extracting the strings into $(basename "$POT")"
# relative paths only: the source comments in the .pot must not carry a home folder
(cd "$REPO" && xgettext --language=Python --from-code=UTF-8 --keyword=_ --keyword=N_ --keyword=ngettext:1,2 \
    --add-comments=TRANSLATORS --package-name="$DOMAIN" --sort-by-file \
    -o "$POT" "$APP_DIR"/*.py)
(cd "$REPO" && xgettext --language=Desktop --join-existing -o "$POT" "po/$(basename "$DESKTOP_IN")")
success "$(grep -c '^msgid ' "$POT") entries (the first is the header)"

# ── Merge and compile ─────────────────────────────────────────────────────────
for po in "$SCRIPT_DIR"/*.po; do
    [[ -e "$po" ]] || continue
    lang="$(basename "$po" .po)"
    header "Catalog: $lang"
    msgmerge --quiet --update --backup=none "$po" "$POT"
    mo="$REPO/usr/share/locale/$lang/LC_MESSAGES/$DOMAIN.mo"
    mkdir -p "$(dirname "$mo")"
    # --check also verifies that every {placeholder} of the English survives in the translation
    msgfmt --check --statistics -o "$mo" "$po"
    success "$mo"
done

# ── Menu entry ────────────────────────────────────────────────────────────────
header "Menu entry"
# msgfmt --desktop reads the languages from po/LINGUAS
find "$SCRIPT_DIR" -maxdepth 1 -name '*.po' -printf '%f\n' | sed 's/\.po$//' | sort > "$SCRIPT_DIR/LINGUAS"
msgfmt --desktop --template="$DESKTOP_IN" -d "$SCRIPT_DIR" -o "$DESKTOP"
success "$(basename "$DESKTOP") written"

header "make-mo.sh done"

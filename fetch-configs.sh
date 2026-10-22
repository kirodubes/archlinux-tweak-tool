#!/bin/bash
set -euo pipefail
#####################################################################
# Author    : Erik Dubois
# Website   : https://kiroproject.be
#####################################################################
#
#   DO NOT JUST RUN THIS. EXAMINE AND JUDGE. RUN AT YOUR OWN RISK.
#
# Purpose:
#   Refresh the "MIRROR" config files ATT ships under
#   usr/share/archlinux-tweak-tool/data/ by re-fetching each from the repo
#   that actually owns it (GitHub raw, main branch). The list of files and
#   their source repos lives in data-sources.tsv.
#
# Why:
#   ATT carries copies of configs owned by other repos (kiro-bash-config,
#   kiro-zsh-config, kiro-fish-config, kiro-dot-files, kiro-iso,
#   kiro-variety-config) and writes them onto the
#   user's system. With no sync those copies silently drift from what a real
#   Kiro install ships. This pulls the canonical version every time, so the
#   single source of truth stays in the source repo, not in ATT's tree.
#   See CONFIG_SOURCES.md for the full classification.
#####################################################################

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

MANIFEST="${SCRIPT_DIR}/data-sources.tsv"
DATA_DIR="${SCRIPT_DIR}/usr/share/archlinux-tweak-tool/data"
RAW_BASE="https://raw.githubusercontent.com"

#####################################################################
# Colors
#####################################################################
if command -v tput >/dev/null 2>&1 && [[ -t 1 ]]; then
    RED="$(tput setaf 1)"
    GREEN="$(tput setaf 2)"
    YELLOW="$(tput setaf 3)"
    BLUE="$(tput setaf 4)"
    CYAN="$(tput setaf 6)"
    RESET="$(tput sgr0)"
else
    RED="" GREEN="" YELLOW="" BLUE="" CYAN="" RESET=""
fi

#####################################################################
# Logging
#####################################################################
log_section() {
    echo
    echo "${GREEN}############################################################################${RESET}"
    echo "$1"
    echo "${GREEN}############################################################################${RESET}"
    echo
}

log_info() {
    echo
    echo "${BLUE}############################################################################${RESET}"
    echo "$1"
    echo "${BLUE}############################################################################${RESET}"
    echo
}

log_warn() {
    echo
    echo "${YELLOW}############################################################################${RESET}"
    echo "$1"
    echo "${YELLOW}############################################################################${RESET}"
    echo
}

log_error() {
    echo
    echo "${RED}############################################################################${RESET}"
    echo "$1"
    echo "${RED}############################################################################${RESET}"
    echo
}

log_success() {
    echo
    echo "${GREEN}############################################################################${RESET}"
    echo "$1"
    echo "${GREEN}############################################################################${RESET}"
    echo
}

#####################################################################
# Error handling
#####################################################################
on_error() {
    local lineno="$1"
    local cmd="$2"
    echo
    echo "${RED}ERROR on line ${lineno}: ${cmd}${RESET}"
    echo
    sleep 10
}

trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

#####################################################################
# Functions
#####################################################################
fetch_one() {
    # Fetch a single manifest entry. Returns: 0 updated, 1 unchanged, 2 failed.
    local dest="$1" repo="$2" path="$3"
    local url="${RAW_BASE}/${repo}/refs/heads/main/${path}"
    local target="${DATA_DIR}/${dest}"
    local tmp

    tmp="$(mktemp)"
    if ! curl -fsSL "${url}" -o "${tmp}"; then
        rm -f "${tmp}"
        echo "${RED}  ✗ ${dest}${RESET}  — fetch failed (${repo}:${path})"
        return 2
    fi

    mkdir -p "$(dirname "${target}")"
    if [[ -f "${target}" ]] && cmp -s "${tmp}" "${target}"; then
        rm -f "${tmp}"
        echo "${CYAN}  = ${dest}${RESET}  — unchanged"
        return 1
    fi

    cp "${tmp}" "${target}"
    rm -f "${tmp}"
    echo "${GREEN}  ✓ ${dest}${RESET}  — updated from ${repo}"
    return 0
}

fetch_all() {
    local dest repo path
    local updated=0 unchanged=0 failed=0 rc

    log_section "Fetching MIRROR configs from source repos"

    while IFS=$'\t' read -r dest repo path; do
        [[ -z "${dest}" || "${dest}" == \#* ]] && continue

        rc=0
        fetch_one "${dest}" "${repo}" "${path}" || rc=$?
        case "${rc}" in
            0) updated=$((updated + 1)) ;;
            1) unchanged=$((unchanged + 1)) ;;
            2) failed=$((failed + 1)) ;;
        esac
    done < "${MANIFEST}"

    echo
    echo "${BLUE}Summary:${RESET} ${updated} updated, ${unchanged} unchanged, ${failed} failed"

    if [[ "${failed}" -gt 0 ]]; then
        log_warn "${failed} file(s) failed to fetch — local copies left untouched"
        return 1
    fi
}

fetch_skell() {
    # ATT ships the skel-restore tool as usr/bin/skell. It is a GENERATED,
    # verbatim copy of kiro-system-files' kiro-skell (the single source of
    # truth) — that script is self-contained on purpose so it runs here with
    # no Kiro-only library. It names itself via "$(basename "$0")", so the
    # copy needs no rewriting: dropped in as skell, it prints "skell".
    # Edit kiro-skell in kiro-system-files, never this generated copy.
    local url="${RAW_BASE}/kirodubes/kiro-system-files/refs/heads/main/usr/local/bin/kiro-skell"
    local target="${SCRIPT_DIR}/usr/bin/skell"
    local tmp

    log_section "Fetching skell from kiro-system-files (kiro-skell)"

    tmp="$(mktemp)"
    if ! curl -fsSL "${url}" -o "${tmp}"; then
        rm -f "${tmp}"
        log_warn "skell fetch failed — local usr/bin/skell left untouched"
        return 1
    fi

    if [[ -f "${target}" ]] && cmp -s "${tmp}" "${target}"; then
        rm -f "${tmp}"
        echo "${CYAN}  = usr/bin/skell${RESET}  — unchanged"
        return 0
    fi

    install -Dm755 "${tmp}" "${target}"
    rm -f "${tmp}"
    echo "${GREEN}  ✓ usr/bin/skell${RESET}  — regenerated from kiro-system-files/kiro-skell"
}

#####################################################################
# Main
#####################################################################
main() {
    if [[ ! -f "${MANIFEST}" ]]; then
        log_error "Manifest not found: ${MANIFEST}"
        exit 1
    fi
    if [[ ! -d "${DATA_DIR}" ]]; then
        log_error "Data dir not found: ${DATA_DIR}"
        exit 1
    fi

    fetch_all

    # Non-fatal: a transient outage must not block the commit/push.
    fetch_skell || log_warn "skell not refreshed this run"

    log_success "$(basename "$0") done"
}

main "$@"

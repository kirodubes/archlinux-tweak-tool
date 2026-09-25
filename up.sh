#!/bin/bash
set -euo pipefail
#####################################################################
# Author    : Erik Dubois
# Website   : https://kiroproject.be
#####################################################################
#
#   DO NOT JUST RUN THIS. EXAMINE AND JUDGE. RUN AT YOUR OWN RISK.
#
#####################################################################

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

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
clean_pycache() {
    local found
    found=$(find "${SCRIPT_DIR}" -type d -name "__pycache__" 2>/dev/null)

    if [[ -n "${found}" ]]; then
        log_section "Cleaning __pycache__"
        find "${SCRIPT_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        log_success "__pycache__ removed"
    fi
}

git_pull() {
    log_section "Git pull"
    git -C "${SCRIPT_DIR}" pull || log_warn "Git pull failed — continuing with local state"
}

ensure_git_remote_configured() {
    local remote_url
    if ! git -C "${SCRIPT_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        log_error "${SCRIPT_DIR} is not a git repository — up.sh must be run from inside a project repo"
        exit 1
    fi
    remote_url="$(git -C "${SCRIPT_DIR}" remote get-url origin 2>/dev/null || true)"
    if [[ "${remote_url}" != git@* ]]; then
        log_warn "Git remote is not SSH (${remote_url:-unset}) — running setup.sh to fix"
        bash "${SCRIPT_DIR}/setup.sh"
    fi
}

git_commit_and_push() {
    local branch

    log_section "Git add / commit / push"
    git -C "${SCRIPT_DIR}" add --all .

    if [[ -z "$(git -C "${SCRIPT_DIR}" status --porcelain)" ]]; then
        log_info "Nothing to commit — working tree clean"
    else
        git -C "${SCRIPT_DIR}" commit -m "${COMMIT_MSG:-update}" || log_error "Git commit failed"
    fi

    branch="$(git -C "${SCRIPT_DIR}" rev-parse --abbrev-ref HEAD)"

    if ! git -C "${SCRIPT_DIR}" push -u origin "${branch}"; then
        log_warn "Push rejected — rebasing on remote changes and retrying"
        git -C "${SCRIPT_DIR}" pull --rebase origin "${branch}" || { log_error "Rebase failed — resolve conflicts manually"; return 1; }
        git -C "${SCRIPT_DIR}" push -u origin "${branch}" || log_error "Git push failed after rebase"
    fi
}

#####################################################################
# Main
#####################################################################
main() {
    ensure_git_remote_configured
    git_pull
    clean_pycache

    if [[ -f "${SCRIPT_DIR}/vendored-refresh.sh" ]]; then
        log_section "Running vendored-refresh.sh"
        # Non-fatal: a transient mirror outage must not block the commit/push.
        bash "${SCRIPT_DIR}/vendored-refresh.sh" || log_warn "vendored-refresh.sh failed — continuing without refreshed packages"
    fi

    if [[ -f "${SCRIPT_DIR}/repo.sh" ]]; then
        log_section "Running repo.sh"
        bash "${SCRIPT_DIR}/repo.sh"
    fi

    if [[ -f "${SCRIPT_DIR}/fetch-configs.sh" ]]; then
        log_section "Running fetch-configs.sh"
        bash "${SCRIPT_DIR}/fetch-configs.sh"
    fi

    if [[ -f "${SCRIPT_DIR}/gen-search-index.py" ]]; then
        log_section "Regenerating search index"
        # Non-fatal: a stale index must not block the commit/push.
        python3 "${SCRIPT_DIR}/gen-search-index.py" || log_warn "search index generation failed — continuing"
    fi

    if [[ -f "${SCRIPT_DIR}/gen-streamline-list.py" ]]; then
        log_section "Regenerating Streamline package list"
        # Non-fatal: a stale list must not block the commit/push.
        python3 "${SCRIPT_DIR}/gen-streamline-list.py" || log_warn "streamline list generation failed — continuing"
    fi

    if [[ -f "${SCRIPT_DIR}/gen-icons-list.py" ]]; then
        log_section "Regenerating Surfn + Neo Candy icon tables + folder thumbnails"
        # Non-fatal: a stale table must not block the commit/push.
        python3 "${SCRIPT_DIR}/gen-icons-list.py" || log_warn "icon list generation failed — continuing"
    fi

    git_commit_and_push

    log_success "$(basename "$0") done"
}

main "$@"

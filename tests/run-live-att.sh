#!/bin/bash
set -euo pipefail
##################################################################################################################
# Author    : Erik Dubois
# Website   : https://kiroproject.be
##################################################################################################################
#
#   DO NOT JUST RUN THIS. EXAMINE AND JUDGE. RUN AT YOUR OWN RISK.
#
##################################################################################################################
#
# Purpose: developer-only live test of the INSTALLED archlinux-tweak-tool on a throwaway test machine.
#          Refuses to run unless /etc/att-live-test-box exists (create it by hand on test boxes only).
#          Backs up the files it touches, starts ATT's real window as root the way the launcher does
#          (pkexec-style PKEXEC_UID), runs live_att.py (page-build sweep, Autostart, Fastfetch, Shells,
#          Wallpaper, each change read back), then restores the backup and reports any root-owned file
#          ATT left in the home folder. Run it as your normal user from a terminal in the desktop session,
#          or over SSH while that user is logged in to a graphical session: bash run-live-att.sh
# Why:     att-check proves prerequisites but never presses a button; this shows whether settings really change.
#
##################################################################################################################

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OUT="/tmp/att-live"
BACKUP="${OUT}/backup"
MARKER="/etc/att-live-test-box"
TOUCHED=(
    "${HOME}/.config/autostart"
    "${HOME}/.config/fastfetch"
    "${HOME}/.config/fish"
    "${HOME}/.bashrc"
    "${HOME}/.zshrc"
    "${HOME}/.fehbg"
)

if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
    RESET="$(tput sgr0 2>/dev/null || true)"
    CYAN="$(tput setaf 6 2>/dev/null || true)"
    GREEN="$(tput setaf 2 2>/dev/null || true)"
    RED="$(tput setaf 1 2>/dev/null || true)"
    YELLOW="$(tput setaf 3 2>/dev/null || true)"
else
    RESET="" CYAN="" GREEN="" RED="" YELLOW=""
fi

separator() { echo "${CYAN}===============================================================================${RESET}"; }
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

on_error() {
    error "ERROR on line $1: $2"
    error "The backup is still in ${BACKUP} — put it back with: bash $(basename "$0") --restore"
    sleep 10
}
trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

# ── Functions ─────────────────────────────────────────────────────────────────

guard() {
    header "Guard: test machines only"
    if [[ "${EUID}" -eq 0 ]]; then
        error "Run this as your normal user, not root — it elevates the test itself"
        exit 1
    fi
    if [[ ! -f "${MARKER}" ]]; then
        error "${MARKER} not found: this is not marked as a test machine"
        info "The live test changes this machine. On a throwaway test box only: sudo touch ${MARKER}"
        exit 1
    fi
    if pgrep -f '/usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py' >/dev/null; then
        error "ArchLinux Tweak Tool is running — close it first"
        exit 1
    fi
    if [[ ! -f "${SCRIPT_DIR}/live_att.py" ]]; then
        error "live_att.py not found next to this script"
        exit 1
    fi
    warn "This changes and then restores: ${TOUCHED[*]}"
    success "Marked test machine, user $(id -un)"
}

find_session() {
    header "Finding the graphical session"
    export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
    if [[ -z "${WAYLAND_DISPLAY:-}" && -z "${DISPLAY:-}" ]]; then
        # over SSH: take the session's Wayland socket, else the first X display
        local socket
        socket="$(find "${XDG_RUNTIME_DIR}" -maxdepth 1 -type s -name 'wayland-*' -printf '%f\n' 2>/dev/null | sort | head -n1)"
        if [[ -n "${socket}" ]]; then
            export WAYLAND_DISPLAY="${socket}"
        elif [[ -S /tmp/.X11-unix/X0 ]]; then
            export DISPLAY=":0"
            export XAUTHORITY="${XAUTHORITY:-${HOME}/.Xauthority}"
        else
            error "No Wayland socket or X display found — log in to a desktop session first"
            exit 1
        fi
    fi
    if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
        SESSION="wayland"
        command -v grim >/dev/null || warn "grim not installed: no screenshots"
    else
        SESSION="x11"
        command -v import >/dev/null || warn "imagemagick (import) not installed: no screenshots"
    fi
    success "Session ${SESSION} (${WAYLAND_DISPLAY:-${DISPLAY:-}})"
}

backup_state() {
    header "Backing up what the test touches"
    if [[ -d "${BACKUP}" && ! -f "${OUT}/restored" ]]; then
        error "The previous run was never restored — a new run would overwrite its backup"
        info "First run: bash $(basename "$0") --restore"
        exit 1
    fi
    sudo -v
    sudo rm -rf "${OUT}"
    mkdir -p "${BACKUP}"
    local path
    for path in "${TOUCHED[@]}"; do
        if [[ -e "${path}" ]]; then
            cp -a "${path}" "${BACKUP}/"
            echo "${path}" >> "${OUT}/existed"
            info "saved ${path}"
        fi
    done
    touch "${OUT}/existed"
    find "${HOME}" -xdev -user root 2>/dev/null | sort > "${OUT}/root-before" || true
    find "${HOME}" -xdev -name '*-bak' 2>/dev/null | sort > "${OUT}/bak-before" || true
    pgrep -a -u "$(id -un)" -x 'swaybg|wbg' | cut -d' ' -f2- > "${OUT}/wall-procs" || true
    local client
    for client in awww swww; do
        if command -v "${client}" >/dev/null; then
            "${client}" query 2>/dev/null | sed -n 's/.*image: //p' | head -n1 > "${OUT}/wall-${client}" || true
        fi
    done
    LOCK_EXISTED="no"
    if [[ -e /tmp/att.lock ]]; then
        LOCK_EXISTED="yes"
    fi
    success "Backup in ${BACKUP}"
}

run_driver() {
    header "Driving ATT (watch the screen, do not touch it)"
    local backend="wayland"
    if [[ "${SESSION}" == "x11" ]]; then
        backend="x11"
    fi
    DRIVER_RC=0
    # keep sudo's timestamp alive so the restore after a long run never stops at a password prompt
    while sleep 60; do sudo -n -v 2>/dev/null || true; done &
    local keepalive=$!
    # a failing driver is a test result, not a script error: catch it so the restore still runs
    # shellcheck disable=SC2024  # tee writes the log as the user on purpose
    sudo env PKEXEC_UID="$(id -u)" DISPLAY="${DISPLAY:-}" WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-}" \
        XAUTHORITY="${XAUTHORITY:-}" XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR}" GDK_BACKEND="${backend}" \
        GSK_RENDERER=cairo LIBGL_ALWAYS_SOFTWARE=1 ATT_LIVE_OUT="${OUT}" \
        python3 "${SCRIPT_DIR}/live_att.py" > >(tee "${OUT}/console.log") 2>&1 || DRIVER_RC=$?
    kill "${keepalive}" 2>/dev/null || true
    if [[ "${LOCK_EXISTED}" == "no" ]]; then
        sudo rm -f /tmp/att.lock
    fi
    sudo chown -R "$(id -un):" "${OUT}"
    info "driver exit code ${DRIVER_RC}"
}

check_ownership() {
    header "Root-owned files ATT left in your home folder"
    find "${HOME}" -xdev -user root 2>/dev/null | sort > "${OUT}/root-after" || true
    comm -13 "${OUT}/root-before" "${OUT}/root-after" > "${OUT}/root-new"
    if [[ -s "${OUT}/root-new" ]]; then
        NEW_ROOT_FILES="yes"
        local path
        while IFS= read -r path; do
            error "root-owned: ${path}"
        done < "${OUT}/root-new"
    else
        NEW_ROOT_FILES="no"
        success "None"
    fi
}

restore_state() {
    header "Restoring the backup"
    local path
    for path in "${TOUCHED[@]}"; do
        sudo rm -rf "${path}"
        if grep -qxF "${path}" "${OUT}/existed"; then
            cp -a "${BACKUP}/$(basename "${path}")" "${path}"
            info "restored ${path}"
        fi
    done
    find "${HOME}" -xdev -name '*-bak' 2>/dev/null | sort > "${OUT}/bak-after" || true
    while IFS= read -r path; do
        # ATT also backs up whole folders (e.g. variety/scripts-bak); these did not exist before the run
        sudo rm -rf "${path}"
        info "removed new backup ${path}"
    done < <(comm -13 "${OUT}/bak-before" "${OUT}/bak-after")
    restore_wallpaper
    touch "${OUT}/restored"
    success "Back to the state before the test"
}

restore_wallpaper() {
    local line client image
    if [[ -s "${OUT}/wall-procs" ]]; then
        pkill -u "$(id -un)" -x 'swaybg|wbg' || true
        while IFS= read -r line; do
            # shellcheck disable=SC2086  # the saved command line is re-split on purpose
            setsid -f ${line} >/dev/null 2>&1
            info "wallpaper: restarted ${line}"
        done < "${OUT}/wall-procs"
    fi
    for client in awww swww; do
        image="$(cat "${OUT}/wall-${client}" 2>/dev/null || true)"
        if [[ -n "${image}" && -f "${image}" ]]; then
            "${client}" img "${image}" >/dev/null 2>&1 || true
            info "wallpaper: ${client} back on ${image}"
        fi
    done
    if [[ -f "${HOME}/.fehbg" ]]; then
        bash "${HOME}/.fehbg" >/dev/null 2>&1 || true
    fi
}

report() {
    header "Report"
    if [[ ! -f "${OUT}/report.json" ]]; then
        error "No report.json — the driver stopped early, see ${OUT}/console.log"
        return 1
    fi
    local verdict line
    while IFS=$'\t' read -r verdict line; do
        case "${verdict}" in
            FAIL) error "${line}" ;;
            COUNT) info "${line}" ;;
        esac
    done < <(python3 -c '
import json, sys
data = json.load(open(sys.argv[1]))
for step, verdict, detail in data["results"]:
    if verdict == "FAIL":
        print(f"FAIL\t{step}: {detail}")
print("COUNT\t" + ", ".join(f"{k} {v}" for k, v in data["counts"].items()))
' "${OUT}/report.json")
    info "Full report: ${OUT}/report.json — screenshots: ${OUT}/shots"
    if [[ "${NEW_ROOT_FILES}" == "yes" ]]; then
        return 1
    fi
    python3 -c 'import json, sys; sys.exit(json.load(open(sys.argv[1]))["counts"]["FAIL"] > 0)' "${OUT}/report.json"
}

main() {
    guard
    find_session
    if [[ "${1:-}" == "--restore" ]]; then
        if [[ ! -d "${BACKUP}" ]]; then
            error "No backup in ${BACKUP} — nothing to restore"
            exit 1
        fi
        sudo -v
        if [[ "$(stat -c %U "${OUT}")" != "$(id -un)" ]]; then
            sudo chown -R "$(id -un):" "${OUT}"
        fi
        check_ownership
        restore_state
        success "$(basename "$0") --restore done"
        return
    fi
    backup_state
    run_driver
    check_ownership
    restore_state
    if report; then
        success "$(basename "$0") done — all steps PASS or INFO"
    else
        error "$(basename "$0") done — findings above"
        exit 1
    fi
}

main "$@"

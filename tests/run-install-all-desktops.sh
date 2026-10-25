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
# Purpose: developer-only live test of ATT's "Install all desktops" (Desktop page, --dev buttons) on a throwaway
#          test machine. Refuses to run unless /etc/att-live-test-box exists (create it by hand on test boxes only).
#          Brings the system up to date, starts ATT's real window as root the way the launcher does (PKEXEC_UID),
#          runs install_all_desktops.py (ATT's own install sequence; the alacritty terminal is replaced by a shell
#          that answers the two "Press Enter" prompts), then reports per desktop: session file present, every
#          package installed, no ATT errors. Nothing is restored: the desktops stay installed.
#          Run it as your normal user while logged in to a graphical session (locally or over SSH):
#            bash run-install-all-desktops.sh            all 15 X11 desktops (INSTALL_ORDER, Plasma last)
#            bash run-install-all-desktops.sh --twms     only the 9 tiling WMs (TWM_INSTALL_ORDER)
#          Follow up with ~/.bin/kiro-vm-session-cycle.sh -H <host> -S <dir> to log into each one and screenshot it.
# Why:     the --dev buttons exist but need someone to press Enter 30 times; this runs them unattended on any box.
#
##################################################################################################################

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OUT="/tmp/att-install-all"
MARKER="/etc/att-live-test-box"
TWMS=0

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
        info "This installs every desktop, Plasma and GNOME included (one-way). On a throwaway test box only: sudo touch ${MARKER}"
        exit 1
    fi
    if pgrep -f '/usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py' >/dev/null; then
        error "ArchLinux Tweak Tool is running — close it first"
        exit 1
    fi
    if [[ ! -f "${SCRIPT_DIR}/install_all_desktops.py" ]]; then
        error "install_all_desktops.py not found next to this script"
        exit 1
    fi
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
            # the display manager keeps the cookie in its own file: borrow it from a process of the active
            # seat0 session; processes and cookie files left over from earlier logins hold stale cookies
            local sid pid pids auth=""
            for sid in $(loginctl list-sessions --no-legend | awk -v u="$(id -un)" '$3 == u && $4 == "seat0" {print $1}'); do
                [[ "$(loginctl show-session "${sid}" -P State 2>/dev/null)" == "active" ]] || continue
                pids="$(cat "/sys/fs/cgroup/user.slice/user-$(id -u).slice/session-${sid}.scope/cgroup.procs" 2>/dev/null || true)"
                break
            done
            for pid in ${pids:-$(pgrep -u "$(id -u)")}; do
                auth="$({ tr '\0' '\n' < "/proc/${pid}/environ"; } 2>/dev/null | sed -n 's/^XAUTHORITY=//p' | head -n1 || true)"
                [[ -n "${auth}" && -f "${auth}" ]] && break
                auth=""
            done
            export XAUTHORITY="${auth:-${HOME}/.Xauthority}"
            info "XAUTHORITY ${XAUTHORITY}"
        else
            error "No Wayland socket or X display found — log in to a desktop session first"
            exit 1
        fi
    fi
    SESSION="x11"
    if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
        SESSION="wayland"
    fi
    success "Session ${SESSION} (${WAYLAND_DISPLAY:-${DISPLAY:-}})"
}

upgrade() {
    header "Bringing the system up to date"
    # ATT installs with pacman -S: on a stale database that is a partial upgrade or a 404
    sudo -v
    sudo pacman -Syu --noconfirm
    success "System up to date"
}

run_driver() {
    header "Running ATT's install-all sequence (watch the screen, do not touch it)"
    local backend="wayland"
    if [[ "${SESSION}" == "x11" ]]; then
        backend="x11"
    fi
    sudo rm -rf "${OUT}"
    mkdir -p "${OUT}"
    DRIVER_RC=0
    while sleep 60; do sudo -n -v 2>/dev/null || true; done &
    local keepalive=$!
    # shellcheck disable=SC2024  # tee writes the log as the user on purpose
    sudo env PKEXEC_UID="$(id -u)" DISPLAY="${DISPLAY:-}" WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-}" \
        XAUTHORITY="${XAUTHORITY:-}" XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR}" GDK_BACKEND="${backend}" \
        GSK_RENDERER=cairo LIBGL_ALWAYS_SOFTWARE=1 ATT_INSTALL_OUT="${OUT}" ATT_INSTALL_TWMS="${TWMS}" \
        ATT_LIVE_APP_DIR="${ATT_LIVE_APP_DIR:-/usr/share/archlinux-tweak-tool}" \
        python3 "${SCRIPT_DIR}/install_all_desktops.py" > >(tee "${OUT}/console.log") 2>&1 || DRIVER_RC=$?
    kill "${keepalive}" 2>/dev/null || true
    sudo rm -f /tmp/att.lock
    sudo chown -R "$(id -un):" "${OUT}"
    info "driver exit code ${DRIVER_RC}"
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
            PASS) success "${line}" ;;
            SKIP) info "${line}" ;;
            FAIL) error "${line}" ;;
            COUNT) info "${line}" ;;
        esac
    done < <(python3 -c '
import json, sys
data = json.load(open(sys.argv[1]))
for desktop, verdict, detail in data["results"]:
    print(f"{verdict}\t{desktop}: {detail}")
for crash in data["crashes"]:
    print(f"FAIL\tthread crash: {crash}")
if data["timed_out"]:
    print("FAIL\tthe sequence never reported complete")
minutes = data["minutes"]
print("COUNT\t" + ", ".join(f"{k} {v}" for k, v in data["counts"].items()) + f" in {minutes} min")
' "${OUT}/report.json")
    info "Full report: ${OUT}/report.json — console: ${OUT}/console.log"
    python3 -c '
import json, sys
data = json.load(open(sys.argv[1]))
sys.exit(data["counts"]["FAIL"] > 0 or bool(data["crashes"]) or data["timed_out"])
' "${OUT}/report.json"
}

main() {
    if [[ "${1:-}" == "--twms" ]]; then
        TWMS=1
    fi
    guard
    find_session
    upgrade
    run_driver
    if report; then
        success "$(basename "$0") done — every desktop installed"
    else
        error "$(basename "$0") done — findings above"
        exit 1
    fi
}

main "$@"

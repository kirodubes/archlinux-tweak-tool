# ============================================================
# Author: Erik Dubois
# ============================================================
# "Report a problem" header button (Kiro / KiroTux only). Runs kiro-report from
# kiro-system-files: a diagnostic log with IP, MAC, UUID, machine-id, hostname and
# username removed, copied to the clipboard ready for the Kiro Discussions board.

import shutil
import subprocess
import threading

import functions as fn
from att_i18n import _
from functions import GLib

DISCUSSIONS_URL = "https://github.com/kirodubes/kiro-discussions/discussions"


def available():
    """True on Kiro / KiroTux with kiro-report installed."""
    return fn.get_distro_label() in ("Kiro", "KiroTux") and shutil.which("kiro-report") is not None


def _run_report():
    script = """
kiro-report --copy
echo ''
echo '=== When you close this window, the Kiro Discussions page opens in your browser ==='
read -p 'Press Enter to close...'
"""
    # kiro-report finds the real user through PKEXEC_UID / SUDO_USER, which alacritty inherits
    return subprocess.Popen(["alacritty", "-e", "bash", "-c", script],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def on_report_clicked(self, _widget):
    """Explain what is collected, run kiro-report, then open the Discussions board."""
    message = _(
        "Kiro collects a report about this system: hardware, drivers, installed packages, failed services, "
        "recent errors and recent updates.\n\n"
        "Private details (IP and MAC addresses, disk IDs, machine ID, computer name and username) are removed. "
        "The report is saved in your home folder and copied to the clipboard.\n\n"
        "Then the Kiro Discussions page opens: start a new discussion, describe the problem and paste the report. "
        "Read it once before you post — it will be public. You need a GitHub account to post.")
    if not fn.confirm_dialog(self, _("Report a problem?"), message):
        fn.log_info("Report a problem: cancelled")
        return
    fn.log_section("Report a problem — running kiro-report --copy")
    try:
        process = _run_report()
    except OSError as error:
        fn.log_error(f"Could not start kiro-report: {error}")
        return
    fn.show_in_app_notification(self, _("Collecting the report in a terminal…"))

    def wait_then_open():
        process.wait()
        GLib.idle_add(fn.open_url_as_user, DISCUSSIONS_URL)

    threading.Thread(target=wait_then_open, daemon=True).start()

# ============================================================
# Author: Erik Dubois
# ============================================================
# "Report a problem" header button. On Kiro / KiroTux it runs kiro-report from
# kiro-system-files and opens the Kiro Discussions board; on every other Arch-based
# system it builds ATT's own report (att_report.py) and opens ATT's GitHub issues.
# Both reports have IP, MAC, UUID, machine-id, hostname and username removed.

import os
import shutil
import subprocess
import threading

import att_report
import functions as fn
from att_i18n import _
from functions import Gdk, GLib

DISCUSSIONS_URL = "https://github.com/kirodubes/kiro-discussions/discussions"


# pkexec starts ATT with PATH=/usr/sbin:/usr/bin:/sbin:/bin, but kiro-system-files installs
# kiro-report (and the kiro-diag / kiro-audit it calls) in /usr/local/bin
LOCAL_PATH = "/usr/local/sbin:/usr/local/bin"


def _kiro_report():
    return shutil.which("kiro-report", path=f"{LOCAL_PATH}:{os.environ.get('PATH', '')}")


def _uses_kiro_report():
    return fn.get_distro_label() in ("Kiro", "KiroTux") and _kiro_report() is not None


def tooltip():
    """Tooltip for the header button: where the report goes on this system."""
    if _uses_kiro_report():
        return _("Send a privacy-safe system report to the Kiro Discussions board")
    return _("Send a privacy-safe system report to the ATT issue tracker on GitHub")


def _run_report():
    script = f"""
export PATH="{LOCAL_PATH}:$PATH"
kiro-report --copy
echo ''
echo '=== When you close this window, the Kiro Discussions page opens in your browser ==='
read -p 'Press Enter to close...'
"""
    # kiro-report finds the real user through PKEXEC_UID / SUDO_USER, which alacritty inherits
    return subprocess.Popen(["alacritty", "-e", "bash", "-c", script],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def on_report_clicked(self, _widget):
    """Explain what is collected, build the report, then open the place to post it."""
    if _uses_kiro_report():
        _report_kiro(self)
    else:
        _report_att(self)


def _report_kiro(self):
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


def _report_att(self):
    distro = fn.get_distro_label()
    message = _(
        "ATT collects a report about this system: hardware, drivers, repositories, installed packages, "
        "failed services, recent errors, recent updates and the ATT log of this session.\n\n"
        "Private details (IP and MAC addresses, disk IDs, machine ID, computer name and username) are removed. "
        "The report is saved in your home folder and copied to the clipboard.\n\n"
        "Then the ATT issue page on GitHub opens: describe the problem with ATT and paste the report. "
        "Problems with {distro} itself belong on the {distro} forum. "
        "Read the report once before you post — it will be public. You need a GitHub account to post."
    ).format(distro=distro)
    if not fn.confirm_dialog(self, _("Report a problem?"), message):
        fn.log_info("Report a problem: cancelled")
        return
    fn.log_section(f"Report a problem — building the ATT report ({distro})")
    fn.show_in_app_notification(self, _("Collecting the report…"))

    def build_then_open():
        try:
            path = att_report.save(att_report.build())
        except OSError as error:
            fn.log_error(f"Could not write the report: {error}")
            GLib.idle_add(fn.show_in_app_notification, self, _("Could not write the report: {error}").format(
                error=error))
            return
        GLib.idle_add(_copy_and_open, self, path)

    threading.Thread(target=build_then_open, daemon=True).start()


def _copy_and_open(self, path):
    with open(path, "r", encoding="utf-8") as f:
        # GitHub renders Markdown: a fenced block keeps the report readable once pasted
        Gdk.Display.get_default().get_clipboard().set(f"```\n{f.read()}\n```\n")
    fn.log_info("Report copied to the clipboard; opening the ATT issue page")
    fn.show_in_app_notification(self, _("Report saved as {path} and copied to the clipboard").format(path=path))
    fn.open_url_as_user(att_report.ISSUES_URL)
    return False

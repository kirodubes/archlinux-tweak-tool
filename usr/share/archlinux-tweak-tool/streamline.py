# ============================================================
# Authors: Erik Dubois
# ============================================================

import functions as fn
from gi.repository import GLib
from att_i18n import _


def selected_packages(self):
    """Return the installed package names whose left-column checkbutton is ticked."""
    return [pkg for pkg, check in getattr(self, "streamline_checks", []) if check.get_active()]


def selected_reinstall(self):
    """Return the already-removed package names whose right-column checkbutton is ticked."""
    return [pkg for pkg, check in getattr(self, "streamline_reinstall_checks", []) if check.get_active()]


def removal_preview(packages, recursive):
    """Return (returncode, text) listing the packages a removal would take out, removing nothing."""
    # Use -Rs (not -Rns) with --print: pacman rejects --print together with -n
    # (--nosave), and -n only affects config-file saving, not which packages go.
    flag = "-Rs" if recursive else "-R"
    result = fn.subprocess.run(
        ["pacman", flag, "--print"] + packages,
        capture_output=True,
        text=True,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


def do_remove(self, packages, recursive, refresh_cb):
    """Launch the removal in a popup terminal and refresh the page once it closes."""
    fn.log_subsection("Streamline — removing selected packages")
    fn.debug_print(f"Removing ({'-Rns' if recursive else '-R'}): {' '.join(packages)}")
    pkg_string = " ".join(packages)
    if recursive:
        process = fn.launch_pacman_remove_recursive_in_terminal(pkg_string)
    else:
        process = fn.launch_pacman_remove_in_terminal(pkg_string)
    fn.show_in_app_notification(self, _("Removal terminal opened"))

    def wait_and_refresh():
        if process is not None:
            process.wait()
        fn.invalidate_pkg_cache()
        GLib.idle_add(refresh_cb)
        GLib.idle_add(fn.show_in_app_notification, self, _("Streamline removal finished"))

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def removed_packages(self):
    """Return optional packages from the Streamline list that are no longer installed.

    This is the after-the-fact view: the full TIER 3 list minus what's still
    installed on this system — i.e. what has actually been removed (or was never
    present). Importing it on a fresh full install re-removes the same apps.
    """
    categories = fn.load_streamline_categories()
    all_pkgs = [pkg for pkgs in categories.values() for pkg in pkgs]
    installed = fn.check_packages_installed(all_pkgs)
    return [pkg for pkg in all_pkgs if not installed.get(pkg)]


def do_reinstall(self, packages, refresh_cb):
    """Reinstall the given packages in a popup terminal and refresh once it closes."""
    fn.log_subsection("Streamline — reinstalling selected packages")
    fn.debug_print(f"Reinstalling: {' '.join(packages)}")
    pkg_string = " ".join(packages)
    helper = fn.get_aur_helper()
    if helper:
        process = fn.launch_aur_install_in_terminal(helper, pkg_string)
    else:
        process = fn.launch_pacman_install_in_terminal(pkg_string)
    fn.show_in_app_notification(self, _("Install terminal opened"))

    def wait_and_refresh():
        if process is not None:
            process.wait()
        fn.invalidate_pkg_cache()
        GLib.idle_add(refresh_cb)
        GLib.idle_add(fn.show_in_app_notification, self, _("Streamline reinstall finished"))

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def save_profile(self, packages, kind="profile"):
    """Write the package names to a timestamped Streamline file, return its path."""
    fn.log_subsection(f"Streamline — saving {kind} list")
    if not fn.path.isdir(fn.att_streamline_dir):
        fn.makedirs(fn.att_streamline_dir, 0o766)
        fn.permissions(fn.att_streamline_dir)
    filename = "streamline-%s-%s-%s.txt" % (
        kind,
        fn.datetime.datetime.today().date(),
        fn.datetime.datetime.today().time().strftime("%H-%M-%S"),
    )
    file_path = fn.path.join(fn.att_streamline_dir, filename)
    header = (
        "# ============================================================================\n"
        "# Streamline package list  —  archlinux-tweak-tool (ATT)\n"
        "# ============================================================================\n"
        "# WHAT THIS IS\n"
        "#   A plain list of package names, one per line. These are packages to be\n"
        "#   REMOVED from the system — not packages to install.\n"
        "#\n"
        "# HOW TO USE IT\n"
        "#   1. Open ATT -> Streamline page.\n"
        '#   2. Click "Import profile" and choose this file; matching installed apps\n'
        "#      get ticked automatically.\n"
        '#   3. Click "Remove selected" to uninstall them (review the confirmation).\n'
        "#\n"
        "# WHY KEEP IT\n"
        "#   Save it off the machine before a reinstall. On a fresh Kiro install every\n"
        "#   optional app is present again — importing this file re-removes the same\n"
        "#   set in one pass, so you don't redo it by hand.\n"
        "#\n"
        f'# Kind: {kind}   ("profile" = your current selection; "removed" = what was already gone)\n'
        f"# Saved: {fn.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "# Lines starting with # are ignored. Edit freely.\n"
        "# ============================================================================\n"
        "\n"
    )
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(packages) + "\n")
    fn.permissions(file_path)
    fn.log_success(f"Streamline {kind} list saved to {file_path}")
    fn.show_in_app_notification(self, _("Saved: {filename}").format(filename=filename))
    return file_path


def read_profile_file(file_path):
    """Return the package names listed in a saved profile file (skips blanks/comments)."""
    packages = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                packages.append(stripped)
    return packages

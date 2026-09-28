# ============================================================
# Authors: Erik Dubois
# ============================================================

import kernel
import kernel_distros

_SCX_GUIDE_PATH = "/usr/share/doc/archlinux-tweak-tool/SCX_SCHEDULER_GUIDE.md"


def gui(self, Gtk, vboxstack, fn):
    """Create the kernel manager GUI."""
    # ── Title ──────────────────────────────────────────────
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text("Kernel Manager")
    lbl_title.set_name("title")
    lbl_title.set_margin_start(10)
    lbl_title.set_margin_end(10)
    hbox_title.append(lbl_title)

    # ── Chaotic-AUR notice ────────────────────────────────
    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    hbox_sep.append(sep)

    hbox_notice = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_notice = Gtk.Label(xalign=0)
    lbl_notice.set_text("You will see the chaotic-aur kernels only when adding the repo in the Pacman tab.")
    lbl_notice.set_margin_start(10)
    lbl_notice.set_margin_end(10)
    hbox_notice.append(lbl_notice)

    # ── Running kernel info ────────────────────────────────
    hbox_running = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_running = Gtk.Label(xalign=0)
    lbl_running.set_margin_start(10)
    lbl_running.set_markup("Running kernel: <b>...</b>")
    hbox_running.append(lbl_running)

    vboxstack.append(hbox_title)
    vboxstack.append(hbox_sep)
    vboxstack.append(hbox_notice)
    vboxstack.append(hbox_running)

    # ── CPU Scheduler pointer (sched-ext / scx) ───────────────
    # Live scheduler swapping is handled by CachyOS's scx-manager (ships on the
    # Kiro ISO), not by ATT — this is just a signpost to it plus the guide.
    _build_section_title(Gtk, vboxstack, "CPU Scheduler", subtitle="sched-ext / scx")
    fn.log_info("Kernels page: CPU Scheduler (scx-manager) pointer shown")

    hbox_scx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_scx.set_margin_start(25)
    hbox_scx.set_margin_end(10)

    lbl_scx = Gtk.Label(xalign=0)
    lbl_scx.set_markup(
        "Switch the live CPU scheduler (lavd, bpfland, rusty…) without a reboot using "
        "<b>scx-manager</b> — already installed. Pick a scheduler and profile, then Apply."
    )
    lbl_scx.set_wrap(True)
    lbl_scx.set_hexpand(True)
    hbox_scx.append(lbl_scx)

    btn_scx_guide = Gtk.Button()
    lbl_scx_guide = Gtk.Label()
    lbl_scx_guide.set_markup("<i>read the guide</i>")
    btn_scx_guide.set_child(lbl_scx_guide)
    btn_scx_guide.set_css_classes(["flat"])
    btn_scx_guide.set_margin_start(10)
    btn_scx_guide.connect("clicked", lambda _b: fn.open_doc_in_editor(_SCX_GUIDE_PATH))
    hbox_scx.append(btn_scx_guide)
    vboxstack.append(hbox_scx)

    hbox_scx_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_scx_note.set_margin_start(25)
    hbox_scx_note.set_margin_end(10)
    lbl_scx_note = Gtk.Label(xalign=0)
    lbl_scx_note.set_markup(
        "<small>Both of Kiro's kernels — <b>CachyOS</b> (default) and <b>Zen</b> "
        "— support scx-manager's settings.</small>"
    )
    lbl_scx_note.set_wrap(True)
    hbox_scx_note.append(lbl_scx_note)
    vboxstack.append(hbox_scx_note)

    total = len(kernel.KERNELS)
    standard = sum(1 for k in kernel.KERNELS if not k.get("requires_chaotic"))
    chaotic = total - standard
    fn.log_info(f"Kernels available to install: {total} total ({standard} standard, {chaotic} chaotic-AUR)")

    def _fetch_running_kernel():
        running_pkg = kernel.get_running_kernel()
        running_info = running_pkg or "unknown"
        if running_pkg:
            installed = kernel.get_installed_kernels()
            if running_pkg in installed:
                version = installed.get(running_pkg, "")
                if version:
                    running_info = f"{running_pkg} {version}"
        fn.GLib.idle_add(lambda: lbl_running.set_markup(f"Running kernel: <b>{running_info}</b>") or False)

    fn.threading.Thread(target=_fetch_running_kernel, daemon=True).start()

    # rEFInd is checked first because CachyOS commonly ships it and `bootctl
    # is-installed` can false-positive when systemd-boot binaries are present
    # on the ESP without being the active loader.
    if kernel.is_refind():
        refresh_boot = _build_refind_entry_selector(self, Gtk, vboxstack, fn)
    elif kernel.is_systemd_boot():
        refresh_boot = _build_boot_entry_selector(self, Gtk, vboxstack, fn)
    elif kernel.is_limine():
        refresh_boot = _build_limine_entry_selector(self, Gtk, vboxstack, fn)
    elif kernel.is_grub():
        refresh_boot = _build_grub_entry_selector(self, Gtk, vboxstack, fn)
    else:
        _build_boot_entry_unavailable(Gtk, vboxstack)
        refresh_boot = None

    # ── Dracut section ────────────────────────────────────────
    if kernel.is_dracut():
        _build_section_title(Gtk, vboxstack, "Dracut — Initramfs Generator")

        hbox_dracut = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_dracut.set_margin_start(25)
        hbox_dracut.set_margin_end(10)

        lbl_dracut = Gtk.Label(xalign=0)
        lbl_dracut.set_text("Regenerate all initramfs images for all installed kernels.")
        lbl_dracut.set_hexpand(True)

        btn_dracut = Gtk.Button(label="Regenerate All Initramfs")
        btn_dracut.set_size_request(200, -1)

        def on_dracut_clicked(_widget):
            btn_dracut.set_sensitive(False)
            fn.log_subsection("Dracut: regenerate-all triggered by user")

            def _run():
                proc = kernel.run_dracut(self)
                if proc:
                    proc.wait()
                fn.GLib.idle_add(
                    lambda: (
                        (
                            btn_dracut.set_sensitive(True),
                            fn.show_in_app_notification(self, "Dracut: initramfs regeneration complete"),
                        )
                        and False
                    )
                )

            fn.threading.Thread(target=_run, daemon=True).start()

        btn_dracut.connect("clicked", on_dracut_clicked)
        hbox_dracut.append(lbl_dracut)
        hbox_dracut.append(btn_dracut)
        vboxstack.append(hbox_dracut)

    # ── Section 1: Arch kernels ────────────────────────────────
    _build_section_title(Gtk, vboxstack, "Arch Kernels", subtitle="core / extra")
    vbox_standard_kernels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack.append(vbox_standard_kernels)
    fn.GLib.idle_add(
        lambda: (
            _populate_kernel_rows(
                self, Gtk, vbox_standard_kernels, fn, refresh_boot, only_chaotic=False, show_group_headers=False
            )
            or False
        ),
        priority=fn.GLib.PRIORITY_LOW,
    )

    # ── Section 2: CachyOS native kernels ─────────────────────
    if fn.check_cachyos_repo_active():
        btn_cachyos = Gtk.Button(label="Load Available Kernels")
        _build_section_title(Gtk, vboxstack, "CachyOS Kernels", subtitle="cachyos repo", btn=btn_cachyos)

        vbox_cachyos_rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vboxstack.append(vbox_cachyos_rows)

        def _already_shown_pkgs():
            return {k["pkg"] for k in kernel.KERNELS if not k.get("requires_chaotic")}

        def _populate_cachyos_rows(found):
            _clear_box(vbox_cachyos_rows)
            if not found:
                lbl_none = Gtk.Label(xalign=0)
                lbl_none.set_text("No additional CachyOS kernels found.")
                lbl_none.set_margin_start(10)
                vbox_cachyos_rows.append(lbl_none)
                fn.log_info("CachyOS kernel scan: no additional kernels found.")
                return
            installed_pkgs = kernel.get_installed_kernels()
            cpu_info = kernel.get_cpu_info()
            running_pkg = kernel.get_running_kernel()
            for k in found:
                _build_kernel_row(
                    self, Gtk, vbox_cachyos_rows, fn, k, running_pkg, installed_pkgs, cpu_info, refresh_boot
                )
            fn.log_success(f"CachyOS kernels loaded: {len(found)} kernel(s).")

        # Auto-populate from cache if available
        cached = kernel.load_cachyos_kernel_cache(_already_shown_pkgs())
        if cached is not None:
            _populate_cachyos_rows(cached)
            btn_cachyos.set_label("Check for New Kernels")
            fn.log_info(f"CachyOS kernel cache: auto-loaded {len(cached)} kernel(s).")

        def on_cachyos_action(_widget):
            fn.log_subsection("Scan for CachyOS kernels")
            btn_cachyos.set_sensitive(False)
            btn_cachyos.set_label("Scanning...")

            def do_scan():
                found = kernel.get_cachyos_available_kernels(_already_shown_pkgs())
                fn.GLib.idle_add(_finish_scan, found)

            def _finish_scan(found):
                _populate_cachyos_rows(found)
                btn_cachyos.set_label("Check for New Kernels")
                btn_cachyos.set_sensitive(True)

            fn.threading.Thread(target=do_scan, daemon=True).start()

        btn_cachyos.connect("clicked", on_cachyos_action)

    # ── Section 3: Chaotic-AUR kernels ────────────────────────
    _build_section_title(Gtk, vboxstack, "Chaotic-AUR Kernels")
    vbox_chaotic_kernels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack.append(vbox_chaotic_kernels)

    last_chaotic = [fn.check_chaotic_aur_active()]
    _populate_kernel_rows(self, Gtk, vbox_chaotic_kernels, fn, refresh_boot, only_chaotic=True)

    def on_map(_widget):
        current = fn.check_chaotic_aur_active()
        if current == last_chaotic[0]:
            return
        last_chaotic[0] = current
        _clear_box(vbox_chaotic_kernels)
        _populate_kernel_rows(self, Gtk, vbox_chaotic_kernels, fn, refresh_boot, only_chaotic=True)

    vbox_chaotic_kernels.connect("map", on_map)


def _check_repo_blocked(fn, missing):
    repo_checks = {
        "nemesis-repo": fn.check_nemesis_repo_active,
        "chaotic-aur": fn.check_chaotic_aur_active,
    }
    return [req for req in missing if req.get("repo") in repo_checks and not repo_checks[req["repo"]]()]


def _offer_install_packages(self, Gtk, fn, missing):
    blocked = _check_repo_blocked(fn, missing)

    if blocked:
        repos_needed = sorted({req["repo"] for req in blocked})
        repo_str = " and ".join(repos_needed)
        pkg_lines = "\n".join(f"  • {req['pkg']}\n    Why: {req['reason']}" for req in blocked)
        fn.log_warn(f"Cannot install missing packages — {repo_str} not enabled in pacman.conf")
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Repository not enabled — action blocked",
            secondary_text=(
                f"ATT needs the following package(s) to manage kernels safely:\n\n"
                f"{pkg_lines}\n\n"
                f"Fix: enable {repo_str} in ATT > Pacman tab, then retry."
            ),
        )
        dialog.connect("response", lambda d, _r: d.destroy())
        dialog.present()
        return

    pkg_list = "\n".join(f"  • {req['pkg']} ({req['repo']})" for req in missing)
    reasons = "\n".join(f"  • {req['reason']}" for req in missing)

    dialog = Gtk.MessageDialog(
        transient_for=self,
        modal=True,
        message_type=Gtk.MessageType.QUESTION,
        buttons=Gtk.ButtonsType.YES_NO,
        text="Missing required packages",
        secondary_text=(
            f"The following packages are needed for full kernel management:\n\n"
            f"{pkg_list}\n\n"
            f"Reason:\n{reasons}\n\n"
            f"Would you like to install them now?"
        ),
    )

    def on_response(_dialog, response):
        _dialog.destroy()
        if response == Gtk.ResponseType.YES:
            _install_missing_packages(self, fn, missing)

    dialog.connect("response", on_response)
    dialog.present()


def _install_missing_packages(self, fn, missing):
    pkg_names = [req["pkg"] for req in missing]
    repos = sorted({req.get("repo", "") for req in missing if req.get("repo")})
    pkgs = " ".join(f'"{p}"' for p in pkg_names)
    repo_hint = "  [!!] Enable " + " and ".join(repos) + " in ATT > Pacman tab and retry." if repos else ""
    script = f"""#!/bin/bash
tput setaf 6
echo "================================================================"
echo "  Installing required packages"
echo "================================================================"
tput sgr0

pacman -S {pkgs} --noconfirm --needed
RESULT=$?

echo
if [ $RESULT -eq 0 ]; then
    tput setaf 2
    echo "================================================================"
    echo "  ✓ Successfully installed required packages"
    echo "================================================================"
    tput sgr0
else
    tput setaf 1
    echo "================================================================"
    echo "  ✗ Installation failed"
    echo "================================================================"
    echo ""
    echo "  [!!] Package(s) not found in enabled repositories."
    echo "{repo_hint}"
    tput sgr0
fi

echo
echo "###############################################################################"
echo "###                DONE - YOU CAN CLOSE THIS WINDOW                        ####"
echo "###############################################################################"
read -p 'Press Enter to close...'"""
    fn.log_subsection("Installing missing kernel management packages...")
    fn.show_in_app_notification(self, f"Installing {', '.join(pkg_names)}...")
    fn.threading.Thread(
        target=lambda: fn.subprocess.Popen(["alacritty", "-e", "bash", "-c", script]).wait(),
        daemon=True,
    ).start()


def _install_packages_then_kernel(self, Gtk, fn, missing, pkg, headers, on_complete=None):
    blocked = _check_repo_blocked(fn, missing)

    if blocked:
        repos_needed = sorted({req["repo"] for req in blocked})
        repo_str = " and ".join(repos_needed)
        pkg_lines = "\n".join(f"  • {req['pkg']}\n    Why: {req['reason']}" for req in blocked)
        fn.log_warn(f"Cannot install missing packages — {repo_str} not enabled in pacman.conf")
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Repository not enabled — action blocked",
            secondary_text=(
                f"ATT needs the following package(s) to manage kernels safely:\n\n"
                f"{pkg_lines}\n\n"
                f"Fix: enable {repo_str} in ATT > Pacman tab, then retry."
            ),
        )
        dialog.connect("response", lambda d, _r: d.destroy())
        dialog.present()
        return

    pkg_names = [req["pkg"] for req in missing]
    prereq_pkgs = " ".join(f'"{p}"' for p in pkg_names)
    prereq_list = "\n".join(f"  • {req['pkg']} ({req['repo']})" for req in missing)
    reasons = "\n".join(f"  • {req['reason']}" for req in missing)

    dialog = Gtk.MessageDialog(
        transient_for=self,
        modal=True,
        message_type=Gtk.MessageType.QUESTION,
        buttons=Gtk.ButtonsType.YES_NO,
        text="Missing required packages",
        secondary_text=(
            f"The following packages are needed for full kernel management:\n\n"
            f"{prereq_list}\n\n"
            f"Reason:\n{reasons}\n\n"
            f"ATT will install the required packages and then install {pkg} in one terminal."
        ),
    )

    def on_response(_dialog, response):
        _dialog.destroy()
        if response != Gtk.ResponseType.YES:
            return

        script = f"""#!/bin/bash
tput setaf 6
echo "================================================================"
echo "  Step 1 - Installing required packages"
echo "================================================================"
tput sgr0

pacman -S {prereq_pkgs} --noconfirm --needed
RESULT=$?

if [ $RESULT -ne 0 ]; then
    tput setaf 1
    echo "================================================================"
    echo "  X Required packages failed - aborting kernel install"
    echo "================================================================"
    tput sgr0
    read -p 'Press Enter to close...'
    exit 1
fi

tput setaf 2
echo "  OK Required packages installed"
tput sgr0

echo
tput setaf 6
echo "================================================================"
echo "  Step 2 - Installing kernel: {pkg}"
echo "  Headers: {headers}"
echo "================================================================"
tput sgr0

pacman -S "{pkg}" "{headers}" --noconfirm --needed
RESULT=$?

echo
if [ $RESULT -eq 0 ]; then
    tput setaf 2
    echo "================================================================"
    echo "  OK Successfully installed {pkg}"
    echo "================================================================"
    tput sgr0
else
    tput setaf 1
    echo "================================================================"
    echo "  X Failed to install {pkg}"
    echo "================================================================"
    tput sgr0
fi

echo
echo "###############################################################################"
echo "###                DONE - YOU CAN CLOSE THIS WINDOW                        ####"
echo "###############################################################################"
read -p 'Press Enter to close...'"""

        fn.log_subsection(f"Installing prerequisites + kernel {pkg} in one terminal...")
        fn.show_in_app_notification(self, f"Installing {', '.join(pkg_names)} and {pkg}...")

        def _run():
            fn.subprocess.Popen(["alacritty", "-e", "bash", "-c", script]).wait()
            if on_complete:
                on_complete()

        fn.threading.Thread(target=_run, daemon=True).start()

    dialog.connect("response", on_response)
    dialog.present()


def _clear_box(box):
    child = box.get_first_child()
    while child:
        nxt = child.get_next_sibling()
        box.remove(child)
        child = nxt


def _build_section_title(Gtk, vboxstack, title, subtitle="", btn=None):
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox.set_margin_top(14)
    hbox.set_margin_bottom(6)

    lbl = Gtk.Label(xalign=0)
    markup = f"<b><big>{title}</big></b>"
    if subtitle:
        markup += f"  <small>({subtitle})</small>"
    lbl.set_markup(markup)
    lbl.set_margin_start(10)

    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    sep.set_margin_start(8)

    hbox.append(lbl)
    hbox.append(sep)
    if btn:
        btn.set_margin_end(10)
        hbox.append(btn)
    vboxstack.append(hbox)


def _populate_kernel_rows(self, Gtk, vbox_kernels, fn, refresh_boot, only_chaotic=None, show_group_headers=True):
    chaotic_enabled = fn.check_chaotic_aur_active()
    installed_pkgs = kernel.get_installed_kernels()
    cpu_info = kernel.get_cpu_info()
    running_pkg = kernel.get_running_kernel()
    # Repos drop kernels over time (e.g. chaotic-aur's -x64v3 mainline/vfio builds): hide rows that can't be
    # installed, but keep installed ones so they stay removable, and hide nothing if the query failed.
    sync_pkgs = kernel.get_sync_packages()
    hidden = [k["pkg"] for k in kernel.KERNELS
              if sync_pkgs and k["pkg"] not in sync_pkgs and k["pkg"] not in installed_pkgs]
    if hidden:
        fn.log_info(f"Kernels not in the enabled repos, hidden: {', '.join(hidden)}")
    current_group = None
    for k in kernel.KERNELS:
        if k["pkg"] in hidden:
            continue
        is_chaotic = bool(k.get("requires_chaotic"))
        if only_chaotic is True and not is_chaotic:
            continue
        if only_chaotic is False and is_chaotic:
            continue
        if is_chaotic and not chaotic_enabled:
            continue
        grp = k.get("group", "")
        if grp != current_group:
            current_group = grp
            if show_group_headers:
                source = "chaotic-aur" if is_chaotic else "core / extra"
                _build_group_header(Gtk, vbox_kernels, grp, source)
        _build_kernel_row(self, Gtk, vbox_kernels, fn, k, running_pkg, installed_pkgs, cpu_info, refresh_boot)


def _build_group_header(Gtk, vboxstack, title, source=""):
    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    hbox_sep.append(sep)

    hbox_hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl = Gtk.Label(xalign=0)
    markup = f"<b>{title}</b>  <small>({source})</small>" if source else f"<b>{title}</b>"
    lbl.set_markup(markup)
    lbl.set_margin_start(10)
    lbl.set_margin_end(10)
    hbox_hdr.append(lbl)

    vboxstack.append(hbox_sep)
    vboxstack.append(hbox_hdr)


def _build_kernel_row(self, Gtk, vboxstack, fn, k, running_pkg, installed_pkgs, cpu_info, refresh_boot=None):
    pkg = k["pkg"]
    headers = k["headers"]
    compatible = kernel.is_kernel_compatible(k, cpu_info)

    hbox_label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl = Gtk.Label(xalign=0)
    lbl.set_markup(f"<b>{k['label']}</b>  <small>{k['description']}</small>")
    lbl.set_margin_start(25)
    hbox_label.append(lbl)
    url = k.get("url", "")
    if url:
        btn_link = Gtk.Button()
        lbl_more_info = Gtk.Label()
        lbl_more_info.set_markup("<i>more info</i>")
        btn_link.set_child(lbl_more_info)
        btn_link.set_css_classes(["flat"])
        btn_link.set_margin_start(10)
        btn_link.connect(
            "clicked",
            lambda _b, u=url: fn.open_url_as_user(u),
        )
        hbox_label.append(btn_link)
        fn.attach_link_context_menu(self, btn_link, url)

    hbox_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_row.set_margin_start(25)
    hbox_row.set_margin_end(10)

    status_label = Gtk.Label(xalign=0)
    status_label.set_hexpand(True)

    btn = Gtk.Button()
    btn.set_size_request(160, -1)

    handler_id = [None]

    def refresh(sl=status_label, b=btn, p=pkg, h=headers, hid=handler_id, rk=running_pkg, c=compatible, _pre=None):
        pkgs = _pre if _pre is not None else kernel.get_installed_kernels()
        installed = p in pkgs
        is_running = rk == p
        if installed:
            version = pkgs.get(p, "")
            ver_str = f"  <small>{version}</small>" if version else ""
            if is_running:
                sl.set_markup(f"<b>installed</b>{ver_str}  <small>(running)</small>")
            else:
                sl.set_markup(f"<b>installed</b>{ver_str}")
            b.set_label(f"Remove {p}")
            b.set_sensitive(not is_running)
        elif not c:
            sl.set_markup("<small>not compatible with your CPU</small>")
            b.set_label(f"Install {p}")
            b.set_sensitive(False)
            return False
        else:
            sl.set_markup("not installed")
            b.set_label(f"Install {p}")
            b.set_sensitive(True)

        if hid[0]:
            b.disconnect(hid[0])
            hid[0] = None

        def launch_and_wait(process, action, pkg_name):
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success(f"{action} completed for {pkg_name}")
            grub_proc = kernel.run_grub_update(self)
            if grub_proc:
                grub_proc.wait()
            dracut_proc = kernel.run_dracut(self)
            if dracut_proc:
                dracut_proc.wait()
            fn.GLib.idle_add(
                lambda: (
                    fn.show_in_app_notification(self, f"{action} completed for {pkg_name}"),
                    refresh(),
                    refresh_boot() if refresh_boot else None,
                )
            )

        if installed and not is_running:
            hid[0] = b.connect(
                "clicked",
                lambda _w: fn.threading.Thread(
                    target=launch_and_wait,
                    args=(kernel.remove_kernel(self, p, h), "Removal", p),
                    daemon=True,
                ).start(),
            )
        elif not installed:

            def on_install_clicked(_w, _p=p, _h=h):
                missing = kernel_distros.get_missing_requirements()
                if missing:
                    for req in missing:
                        fn.log_warn(f"Missing: {req['pkg']} — {req['reason']}")

                    def on_complete(_pkg=_p, _hdr=_h):
                        fn.invalidate_pkg_cache()
                        fn.log_success(f"Installation completed for {_pkg}")
                        grub_proc = kernel.run_grub_update(self)
                        if grub_proc:
                            grub_proc.wait()
                        dracut_proc = kernel.run_dracut(self)
                        if dracut_proc:
                            dracut_proc.wait()
                        fn.GLib.idle_add(
                            lambda: (
                                fn.show_in_app_notification(self, f"Installation completed for {_pkg}"),
                                refresh(),
                                refresh_boot() if refresh_boot else None,
                            )
                        )

                    _install_packages_then_kernel(self, Gtk, fn, missing, _p, _h, on_complete)
                    return
                fn.threading.Thread(
                    target=launch_and_wait,
                    args=(kernel.install_kernel(self, _p, _h), "Installation", _p),
                    daemon=True,
                ).start()

            hid[0] = b.connect("clicked", on_install_clicked)

        return False

    refresh(_pre=installed_pkgs)

    hbox_row.append(status_label)
    hbox_row.append(btn)

    vboxstack.append(hbox_label)
    vboxstack.append(hbox_row)


def _build_boot_entry_selector(self, Gtk, vboxstack, fn):
    boot_entries = kernel.get_boot_entries()
    if not boot_entries:
        return

    current_default = kernel.get_default_boot_entry()

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    hbox_sep.append(sep)

    hbox_hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl = Gtk.Label(xalign=0)
    lbl.set_markup("<b>Default Boot Entry (systemd-boot)</b>")
    lbl.set_margin_start(10)
    lbl.set_margin_end(10)
    hbox_hdr.append(lbl)

    vboxstack.append(hbox_sep)
    vboxstack.append(hbox_hdr)

    hbox_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_row.set_margin_start(25)
    hbox_row.set_margin_end(10)

    combo = Gtk.ComboBoxText()
    combo.set_hexpand(True)
    combo_active_id = [None]
    id_to_title = {}

    for entry_id, title, kernel_pkg in boot_entries:
        label = f"{title} — {kernel_pkg}" if kernel_pkg else title
        combo.append(entry_id, label)
        id_to_title[entry_id] = label
        if entry_id == current_default:
            combo_active_id[0] = entry_id

    if combo_active_id[0]:
        combo.set_active_id(combo_active_id[0])

    lbl_current = Gtk.Label(xalign=0)
    lbl_current.set_margin_start(25)
    if current_default:
        current_label = id_to_title.get(current_default, current_default)
        lbl_current.set_markup(f"<small>Current: {current_label}</small>")
    else:
        lbl_current.set_markup("<small>Current: unknown</small>")

    def on_set_default(_widget):
        missing = kernel_distros.get_missing_requirements()
        if missing:
            for req in missing:
                fn.log_warn(f"Missing required package: {req['pkg']} from {req['repo']} — {req['reason']}")
            _offer_install_packages(self, Gtk, fn, missing)
            return

        selected_id = combo.get_active_id()
        if selected_id:
            label = id_to_title.get(selected_id, selected_id)
            fn.log_info(f"Setting default boot entry to: {label}")
            success = kernel.set_default_boot_entry(selected_id)
            if success:
                fn.log_success(f"Default boot entry set to: {label} — Reboot to verify")
                _refresh_boot_entry_display(label, lbl_current)
                fn.show_in_app_notification(self, f"Default boot entry set to: {label} — Reboot to verify")
            else:
                fn.log_error(f"Failed to set default boot entry: {label}")
                fn.show_in_app_notification(self, f"Failed to set default boot entry: {label}")

    btn_set = Gtk.Button(label="Set as Default")
    btn_set.set_size_request(160, -1)
    btn_set.connect("clicked", on_set_default)

    hbox_row.append(combo)
    hbox_row.append(btn_set)

    vboxstack.append(hbox_row)
    vboxstack.append(lbl_current)

    def refresh_combo():
        new_entries = kernel.get_boot_entries()
        combo.remove_all()
        id_to_title.clear()
        for entry_id, title, kernel_pkg in new_entries:
            label = f"{title} — {kernel_pkg}" if kernel_pkg else title
            combo.append(entry_id, label)
            id_to_title[entry_id] = label
        new_default = kernel.get_default_boot_entry()
        if new_default:
            combo.set_active_id(new_default)
            current_label = id_to_title.get(new_default, new_default)
            lbl_current.set_markup(f"<small>Current: {current_label}</small>")

    return refresh_combo


def _build_limine_entry_selector(self, Gtk, vboxstack, fn):
    boot_entries = kernel.get_limine_boot_entries()
    if not boot_entries:
        return None

    current_default = kernel.get_default_limine_entry()

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    hbox_sep.append(sep)

    hbox_hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl = Gtk.Label(xalign=0)
    lbl.set_markup("<b>Default Boot Entry (limine)</b>")
    lbl.set_margin_start(10)
    lbl.set_margin_end(10)
    hbox_hdr.append(lbl)

    vboxstack.append(hbox_sep)
    vboxstack.append(hbox_hdr)

    hbox_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_row.set_margin_start(25)
    hbox_row.set_margin_end(10)

    combo = Gtk.ComboBoxText()
    combo.set_hexpand(True)
    index_to_title = {}

    for idx, title in boot_entries:
        combo.append(idx, title)
        index_to_title[idx] = title

    if current_default and current_default in index_to_title:
        combo.set_active_id(current_default)
    elif boot_entries:
        combo.set_active_id(boot_entries[0][0])

    lbl_current = Gtk.Label(xalign=0)
    lbl_current.set_margin_start(25)
    if current_default:
        current_label = index_to_title.get(current_default, current_default)
        lbl_current.set_markup(f"<small>Current: {current_label}</small>")
    else:
        lbl_current.set_markup("<small>Current: unknown</small>")

    def on_set_default(_widget):
        selected_id = combo.get_active_id()
        if selected_id:
            label = index_to_title.get(selected_id, selected_id)
            fn.log_info(f"Setting limine default boot entry to: {label} (index {selected_id})")
            success = kernel.set_default_limine_entry(selected_id)
            if success:
                fn.log_success(f"Limine default boot entry set to: {label} — Reboot to verify")
                _refresh_boot_entry_display(label, lbl_current)
                fn.show_in_app_notification(self, f"Default boot entry set to: {label} — Reboot to verify")
            else:
                fn.log_error(f"Failed to set limine default boot entry: {label}")
                fn.show_in_app_notification(self, f"Failed to set limine default boot entry: {label}")

    btn_set = Gtk.Button(label="Set as Default")
    btn_set.set_size_request(160, -1)
    btn_set.connect("clicked", on_set_default)

    hbox_row.append(combo)
    hbox_row.append(btn_set)

    vboxstack.append(hbox_row)
    vboxstack.append(lbl_current)

    def refresh_combo():
        new_entries = kernel.get_limine_boot_entries()
        combo.remove_all()
        index_to_title.clear()
        for idx, title in new_entries:
            combo.append(idx, title)
            index_to_title[idx] = title
        new_default = kernel.get_default_limine_entry()
        if new_default:
            combo.set_active_id(new_default)
            current_label = index_to_title.get(new_default, new_default)
            lbl_current.set_markup(f"<small>Current: {current_label}</small>")

    return refresh_combo


def _build_grub_entry_selector(self, Gtk, vboxstack, fn):
    boot_entries = kernel.get_grub_boot_entries()
    if not boot_entries:
        fn.log_warn("GRUB boot entries: grub.cfg found but no menuentry lines parsed.")
        return None

    grub_default_saved = kernel.is_grub_default_saved()
    current_default = kernel.get_default_grub_entry()
    fn.log_subsection("GRUB Boot Entry Selector")
    fn.log_info(f"GRUB entries found: {len(boot_entries)}, current default: {current_default}")

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    hbox_sep.append(sep)

    hbox_hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_hdr = Gtk.Label(xalign=0)
    lbl_hdr.set_markup("<b>Default Boot Entry (GRUB)</b>")
    lbl_hdr.set_margin_start(10)
    lbl_hdr.set_margin_end(10)
    hbox_hdr.append(lbl_hdr)

    vboxstack.append(hbox_sep)
    vboxstack.append(hbox_hdr)

    hbox_warn = None
    if not grub_default_saved:
        fn.log_warn("GRUB_DEFAULT is not set to 'saved' — will fix automatically on Set as Default.")
        hbox_warn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_warn = Gtk.Label(xalign=0)
        lbl_warn.set_markup(
            '<small><b>Note:</b> GRUB_DEFAULT is not set to "saved" in /etc/default/grub.\n'
            "ATT will fix this automatically when you click Set as Default.</small>"
        )
        lbl_warn.set_margin_start(25)
        lbl_warn.set_margin_end(10)
        lbl_warn.set_wrap(True)
        hbox_warn.append(lbl_warn)
        vboxstack.append(hbox_warn)

    hbox_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_row.set_margin_start(25)
    hbox_row.set_margin_end(10)

    combo = Gtk.ComboBoxText()
    combo.set_hexpand(True)
    index_to_title = {}

    for idx, title in boot_entries:
        combo.append(idx, title)
        index_to_title[idx] = title

    if current_default and current_default in index_to_title:
        combo.set_active_id(current_default)
    elif boot_entries:
        combo.set_active_id(boot_entries[0][0])

    lbl_current = Gtk.Label(xalign=0)
    lbl_current.set_margin_start(25)
    if current_default:
        current_label = index_to_title.get(current_default, current_default)
        lbl_current.set_markup(f"<small>Current: {current_label}</small>")
    else:
        lbl_current.set_markup("<small>Current: unknown</small>")

    def on_set_default(_widget):
        selected_id = combo.get_active_id()
        if not selected_id:
            return
        label = index_to_title.get(selected_id, selected_id)

        def finish(success):
            if success:
                fn.log_success(f"GRUB default boot entry set to: {label} — Reboot to verify")
                _refresh_boot_entry_display(label, lbl_current)
                fn.show_in_app_notification(self, f"Default boot entry set to: {label} — Reboot to verify")
            else:
                fn.log_error(f"Failed to set GRUB default boot entry: {label}")
                fn.show_in_app_notification(self, f"Failed to set GRUB default boot entry: {label}")

        if not kernel.is_grub_default_saved():
            if not kernel.set_grub_default_saved():
                fn.show_in_app_notification(self, "Failed to fix GRUB_DEFAULT in /etc/default/grub")
                return
            if hbox_warn:
                fn.GLib.idle_add(hbox_warn.set_visible, False)
            fn.log_info(f"Setting GRUB default boot entry to: {label} (index {selected_id})")

            def do_update_and_set():
                grub_proc = kernel.run_grub_update(self)
                if grub_proc:
                    grub_proc.wait()
                fn.GLib.idle_add(finish, kernel.set_default_grub_entry(selected_id))

            fn.threading.Thread(target=do_update_and_set, daemon=True).start()
        else:
            fn.log_info(f"Setting GRUB default boot entry to: {label} (index {selected_id})")
            finish(kernel.set_default_grub_entry(selected_id))

    btn_set = Gtk.Button(label="Set as Default")
    btn_set.set_size_request(160, -1)
    btn_set.connect("clicked", on_set_default)

    hbox_row.append(combo)
    hbox_row.append(btn_set)

    vboxstack.append(hbox_row)
    vboxstack.append(lbl_current)

    def refresh_combo():
        new_entries = kernel.get_grub_boot_entries()
        combo.remove_all()
        index_to_title.clear()
        for idx, title in new_entries:
            combo.append(idx, title)
            index_to_title[idx] = title
        new_default = kernel.get_default_grub_entry()
        if new_default and new_default in index_to_title:
            combo.set_active_id(new_default)
            current_label = index_to_title.get(new_default, new_default)
            lbl_current.set_markup(f"<small>Current: {current_label}</small>")

    return refresh_combo


def _build_refind_entry_selector(self, Gtk, vboxstack, fn):
    boot_entries = kernel.get_refind_boot_entries()
    if not boot_entries:
        fn.log_warn("rEFInd boot entries: no vmlinuz-* files found in /boot.")
        return None

    current_default = kernel.get_default_refind_entry()
    fn.log_info(f"rEFInd entries found: {len(boot_entries)}, current default: {current_default}")

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    hbox_sep.append(sep)

    hbox_hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_hdr = Gtk.Label(xalign=0)
    lbl_hdr.set_markup("<b>Default Boot Entry (rEFInd)</b>")
    lbl_hdr.set_margin_start(10)
    lbl_hdr.set_margin_end(10)
    hbox_hdr.append(lbl_hdr)

    vboxstack.append(hbox_sep)
    vboxstack.append(hbox_hdr)

    hbox_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_row.set_margin_start(25)
    hbox_row.set_margin_end(10)

    combo = Gtk.ComboBoxText()
    combo.set_hexpand(True)
    value_to_label = {}

    for value, label in boot_entries:
        combo.append(value, label)
        value_to_label[value] = label

    if current_default and current_default in value_to_label:
        combo.set_active_id(current_default)
    elif boot_entries:
        combo.set_active_id(boot_entries[0][0])

    lbl_current = Gtk.Label(xalign=0)
    lbl_current.set_margin_start(25)
    if current_default:
        current_label = value_to_label.get(current_default, current_default)
        lbl_current.set_markup(f"<small>Current: {current_label}</small>")
    else:
        lbl_current.set_markup("<small>Current: unknown</small>")

    def on_set_default(_widget):
        selected_id = combo.get_active_id()
        if not selected_id:
            return
        label = value_to_label.get(selected_id, selected_id)
        fn.log_info(f"Setting rEFInd default boot entry to: {label} (value {selected_id})")
        success = kernel.set_default_refind_entry(selected_id)
        if success:
            fn.log_success(f"rEFInd default boot entry set to: {label} — Reboot to verify")
            _refresh_boot_entry_display(label, lbl_current)
            fn.show_in_app_notification(self, f"Default boot entry set to: {label} — Reboot to verify")
        else:
            fn.log_error(f"Failed to set rEFInd default boot entry: {label}")
            fn.show_in_app_notification(self, f"Failed to set rEFInd default boot entry: {label}")

    btn_set = Gtk.Button(label="Set as Default")
    btn_set.set_size_request(160, -1)
    btn_set.connect("clicked", on_set_default)

    hbox_row.append(combo)
    hbox_row.append(btn_set)

    vboxstack.append(hbox_row)
    vboxstack.append(lbl_current)

    def refresh_combo():
        new_entries = kernel.get_refind_boot_entries()
        combo.remove_all()
        value_to_label.clear()
        for value, label in new_entries:
            combo.append(value, label)
            value_to_label[value] = label
        new_default = kernel.get_default_refind_entry()
        if new_default and new_default in value_to_label:
            combo.set_active_id(new_default)
            current_label = value_to_label.get(new_default, new_default)
            lbl_current.set_markup(f"<small>Current: {current_label}</small>")

    return refresh_combo


def _build_boot_entry_unavailable(Gtk, vboxstack):
    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    hbox_sep.append(sep)

    hbox_hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_hdr = Gtk.Label(xalign=0)
    lbl_hdr.set_markup("<b>Default Boot Entry</b>")
    lbl_hdr.set_margin_start(10)
    lbl_hdr.set_margin_end(10)
    hbox_hdr.append(lbl_hdr)

    hbox_msg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_msg = Gtk.Label(xalign=0)
    lbl_msg.set_text(
        "Setting a default boot entry is only available on systemd-boot, limine, GRUB, and rEFInd systems."
    )
    lbl_msg.set_margin_start(25)
    lbl_msg.set_margin_end(10)
    lbl_msg.set_margin_top(5)
    lbl_msg.set_margin_bottom(10)
    hbox_msg.append(lbl_msg)

    vboxstack.append(hbox_sep)
    vboxstack.append(hbox_hdr)
    vboxstack.append(hbox_msg)


def _refresh_boot_entry_display(entry_id, label_widget):
    label_widget.set_markup(f"<small>Current: {entry_id}</small>")

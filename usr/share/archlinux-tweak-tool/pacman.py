# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn
import maintenance


def _sync_if_db_missing(self, repo_name):
    db_path = f"/var/lib/pacman/sync/{repo_name}.db"
    if not fn.path.exists(db_path):
        maintenance.on_update_pacman_databases_clicked(self, None)
    else:
        fn.log_info(f"Database already exists for {repo_name} — skipping sync")


def on_nemesis_toggle(self, widget, active):
    if hasattr(self, "initializing") and self.initializing:
        return
    from pacman_functions import repo_exist, append_repo, toggle_test_repos, ensure_nemesis_packages
    import desktopr_gui

    if widget.get_active():
        process = ensure_nemesis_packages(self)
        if process is not None:

            def _finish_nemesis_setup(proc):
                proc.wait()
                fn.log_info("Nemesis setup terminal closed — appending repo")
                if not repo_exist("[nemesis_repo]"):
                    append_repo(self, fn.nemesis_repo)
                    fn.log_info("Nemesis repo added to /etc/pacman.conf")
                    fn.GLib.idle_add(
                        fn.show_in_app_notification, self, "Repo has been added to /etc/pacman.conf"
                    )
                fn.GLib.idle_add(_sync_if_db_missing, self, "nemesis_repo")
                fn.GLib.idle_add(desktopr_gui.update_button_state, self, fn)
                fn.GLib.idle_add(self.refresh_aur_buttons)

            fn.threading.Thread(target=_finish_nemesis_setup, args=(process,), daemon=True).start()
            return

    if not repo_exist("[nemesis_repo]"):
        append_repo(self, fn.nemesis_repo)
        fn.log_info("Repo added to /etc/pacman.conf")
        fn.show_in_app_notification(self, "Repo has been added to /etc/pacman.conf")
    else:
        toggle_test_repos(self, widget.get_active(), "nemesis")
    if widget.get_active():
        _sync_if_db_missing(self, "nemesis_repo")
    desktopr_gui.update_button_state(self, fn)
    fn.GLib.timeout_add(100, self.refresh_aur_buttons)


def on_chaotic_toggle(self, widget, active):
    if hasattr(self, "initializing") and self.initializing:
        return
    from pacman_functions import repo_exist, append_repo, toggle_test_repos, ensure_chaotic_packages
    import desktopr_gui

    if widget.get_active():
        process = ensure_chaotic_packages(self)
        if process is not None:

            def _finish_chaotic_setup(proc):
                proc.wait()
                fn.log_info("Chaotic-AUR setup terminal closed — appending repo")
                if not repo_exist("[chaotic-aur]"):
                    append_repo(self, fn.chaotic_aur_repo)
                    fn.log_info("Chaotic-AUR repo added to /etc/pacman.conf")
                    fn.GLib.idle_add(
                        fn.show_in_app_notification, self, "Chaotic-AUR repo has been added to /etc/pacman.conf"
                    )
                fn.GLib.idle_add(_sync_if_db_missing, self, "chaotic-aur")
                fn.GLib.idle_add(desktopr_gui.update_button_state, self, fn)
                fn.GLib.idle_add(self.refresh_aur_buttons)

            fn.threading.Thread(target=_finish_chaotic_setup, args=(process,), daemon=True).start()
            return

    if not repo_exist("[chaotic-aur]"):
        append_repo(self, fn.chaotic_aur_repo)
        fn.debug_print("Repo added to /etc/pacman.conf")
        fn.show_in_app_notification(self, "Chaotic-AUR repo has been added to /etc/pacman.conf")
    else:
        toggle_test_repos(self, widget.get_active(), "chaotics")

    if widget.get_active():
        _sync_if_db_missing(self, "chaotic-aur")
    desktopr_gui.update_button_state(self, fn)
    fn.GLib.timeout_add(100, self.refresh_aur_buttons)


def on_cachyos_toggle(self, widget, active):
    if hasattr(self, "initializing") and self.initializing:
        return
    from pacman_functions import repo_exist, append_repo, toggle_test_repos, ensure_cachyos_packages

    if widget.get_active():
        process = ensure_cachyos_packages(self)
        if process is not None:

            def _finish_cachyos_setup(proc):
                proc.wait()
                fn.log_info("CachyOS setup terminal closed — appending repo")
                if not repo_exist("[cachyos]"):
                    append_repo(self, fn.cachyos_repo)
                    fn.log_info("CachyOS repo added to /etc/pacman.conf")
                    fn.GLib.idle_add(
                        fn.show_in_app_notification, self, "CachyOS repo has been added to /etc/pacman.conf"
                    )
                fn.GLib.idle_add(_sync_if_db_missing, self, "cachyos")

            fn.threading.Thread(target=_finish_cachyos_setup, args=(process,), daemon=True).start()
            return

    if not repo_exist("[cachyos]"):
        append_repo(self, fn.cachyos_repo)
        fn.debug_print("Repo added to /etc/pacman.conf")
        fn.show_in_app_notification(self, "CachyOS repo has been added to /etc/pacman.conf")
    else:
        toggle_test_repos(self, widget.get_active(), "cachyos")

    if widget.get_active():
        _sync_if_db_missing(self, "cachyos")


def on_pacman_toggle1(self, widget, active):
    if hasattr(self, "initializing") and self.initializing:
        return
    from pacman_functions import repo_exist, append_repo, toggle_test_repos

    if not repo_exist("[core-testing]"):
        append_repo(self, fn.arch_testing_repo)
        fn.log_info("Repo added to /etc/pacman.conf")
        fn.show_in_app_notification(self, "Repo has been added to /etc/pacman.conf")
    else:
        toggle_test_repos(self, widget.get_active(), "testing")
    if widget.get_active():
        _sync_if_db_missing(self, "core-testing")


def on_pacman_toggle2(self, widget, active):
    if hasattr(self, "initializing") and self.initializing:
        return
    from pacman_functions import repo_exist, append_repo, toggle_test_repos

    if not repo_exist("[core]"):
        append_repo(self, fn.arch_core_repo)
        fn.log_info("Repo added to /etc/pacman.conf")
        fn.show_in_app_notification(self, "Repo has been added to /etc/pacman.conf")
    else:
        toggle_test_repos(self, widget.get_active(), "core")
    if widget.get_active():
        _sync_if_db_missing(self, "core")


def on_pacman_toggle3(self, widget, active):
    if hasattr(self, "initializing") and self.initializing:
        return
    from pacman_functions import repo_exist, append_repo, toggle_test_repos

    if not repo_exist("[extra]"):
        append_repo(self, fn.arch_extra_repo)
        fn.log_info("Repo added to /etc/pacman.conf")
        fn.show_in_app_notification(self, "Repo has been added to /etc/pacman.conf")
    else:
        toggle_test_repos(self, widget.get_active(), "extra")
    if widget.get_active():
        _sync_if_db_missing(self, "extra")


def on_pacman_toggle4(self, widget, active):
    if hasattr(self, "initializing") and self.initializing:
        return
    from pacman_functions import repo_exist, append_repo, toggle_test_repos

    if not repo_exist("[extra-testing]"):
        append_repo(self, fn.arch_extra_testing_repo)
        fn.log_info("Repo added to /etc/pacman.conf")
        fn.show_in_app_notification(self, "Repo has been added to /etc/pacman.conf")
    else:
        toggle_test_repos(self, widget.get_active(), "community-testing")
    if widget.get_active():
        _sync_if_db_missing(self, "extra-testing")


def on_pacman_toggle6(self, widget, active):
    if hasattr(self, "initializing") and self.initializing:
        return
    from pacman_functions import repo_exist, append_repo, toggle_test_repos

    if not repo_exist("[multilib-testing]"):
        append_repo(self, fn.arch_multilib_testing_repo)
        fn.log_info("Repo added to /etc/pacman.conf")
        fn.show_in_app_notification(self, "Repo has been added to /etc/pacman.conf")
    else:
        toggle_test_repos(self, widget.get_active(), "multilib-testing")
    if widget.get_active():
        _sync_if_db_missing(self, "multilib-testing")


def on_pacman_toggle7(self, widget, active):
    if hasattr(self, "initializing") and self.initializing:
        return
    from pacman_functions import repo_exist, append_repo, toggle_test_repos

    if not repo_exist("[multilib]"):
        append_repo(self, fn.arch_multilib_repo)
        fn.log_info("Repo added to /etc/pacman.conf")
        fn.show_in_app_notification(self, "Repo has been added to /etc/pacman.conf")
    else:
        toggle_test_repos(self, widget.get_active(), "multilib")
    if widget.get_active():
        _sync_if_db_missing(self, "multilib")


def custom_repo_clicked(self, _widget):
    fn.log_subsection("Adding custom repo...")
    from pacman_functions import append_repo

    custom_repo_text = self.textview_custom_repo.get_buffer()
    startiter, enditer = custom_repo_text.get_bounds()
    repo_content = custom_repo_text.get_text(startiter, enditer, True)

    if len(repo_content.strip()) < 5:
        fn.log_warn("No custom repo defined")
        fn.show_in_app_notification(self, "No custom repo defined")
        return

    fn.debug_print(f"Custom repo content: {repo_content}")
    append_repo(self, repo_content)
    try:
        fn.update_repos(self)
        fn.log_success("Custom repo added")
    except Exception as error:
        fn.log_error(f"Error: {error}")
        fn.log_warn("Check /etc/pacman.conf for correctness")


def reset_pacman_blank(self, _widget):
    fn.log_subsection("Resetting pacman.conf to blank state...")
    fn.log_info_concise(f"  From: {fn.pacman}")
    fn.log_info_concise(f"  To:   {fn.pacman}-bak")
    fn.shutil.copy(fn.pacman, fn.pacman + "-bak")
    fn.log_info_concise(f"  From: {fn.blank_pacman_att}")
    fn.log_info_concise(f"  To:   {fn.pacman}")
    fn.shutil.copy(fn.blank_pacman_att, fn.pacman)
    fn.invalidate_pacman_conf_cache()
    fn.keep_kirotux_repo()
    fn.log_success("Blank pacman.conf created")
    fn.log_info("Add repositories in desired order, ATT will reboot automatically")
    fn.restart_program()


def reset_pacman_local(self, _widget):
    fn.log_subsection("Resetting pacman.conf from backup...")
    if fn.path.isfile(fn.pacman + "-bak"):
        fn.log_info_concise(f"  From: {fn.pacman}-bak")
        fn.log_info_concise(f"  To:   {fn.pacman}")
        fn.shutil.copy(fn.pacman + "-bak", fn.pacman)
        fn.invalidate_pacman_conf_cache()
        fn.keep_kirotux_repo()
        fn.log_success("pacman.conf reset from -bak")
        fn.show_in_app_notification(self, "Default Settings Applied - check in a terminal")
    fn.GLib.timeout_add(500, lambda: update_repos_switches(self))


def reset_pacman_online(self, _widget):
    fn.log_subsection("Resetting pacman.conf to ATT defaults...")
    fn.log_info_concise(f"  From: {fn.pacman_att}")
    fn.log_info_concise(f"  To:   {fn.pacman}")
    fn.shutil.copy(fn.pacman_att, fn.pacman)
    fn.invalidate_pacman_conf_cache()
    fn.keep_kirotux_repo()
    fn.log_success("ATT version of pacman.conf saved")
    fn.show_in_app_notification(self, "Default Settings Applied - check in a terminal")
    fn.GLib.timeout_add(500, lambda: update_repos_switches(self))


def edit_pacman_conf_clicked(self, _widget):
    fn.log_subsection("Edit pacman.conf")
    fn.show_in_app_notification(self, "Opening pacman.conf in terminal")
    fn.subprocess.Popen(
        ["alacritty", "-e", "sudo", "nano", fn.pacman],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )


def update_repos_switches(self):
    """Read pacman.conf and sync all repo toggle switches to match."""
    from pacman_functions import check_repo

    self.initializing = True
    try:
        self.checkbutton2.set_active(check_repo("[core-testing]"))
        self.checkbutton6.set_active(check_repo("[core]"))
        self.checkbutton7.set_active(check_repo("[extra]"))
        self.checkbutton5.set_active(check_repo("[extra-testing]"))
        self.checkbutton3.set_active(check_repo("[multilib-testing]"))
        self.checkbutton8.set_active(check_repo("[multilib]"))
        self.nemesis_switch.set_active(check_repo("[nemesis_repo]"))
        self.chaotic_switch.set_active(check_repo("[chaotic-aur]"))
        self.cachyos_switch.set_active(check_repo("[cachyos]"))
    finally:
        self.initializing = False
    if hasattr(self, "parallel_downloads_label"):
        try:
            with open(fn.pacman, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("ParallelDownloads"):
                        value = line.split("=")[1].strip()
                        self.parallel_downloads_label.set_markup(f"ParallelDownloads: {value}")
                        break
        except Exception:
            pass


def check_parallel_downloads(lists, value):
    """Return the ParallelDownloads line from pacman.conf, or None."""
    if fn.path.isfile(fn.pacman):
        try:
            pos = fn.get_position(lists, value)
            val = lists[pos].strip()
            return val
        except Exception as error:
            fn.log_error(str(error))


def set_parallel_downloads(self, _widget):
    """Write the selected ParallelDownloads value to pacman.conf."""
    fn.log_subsection("Setting parallel downloads...")
    if fn.path.isfile(fn.pacman):
        try:
            with open(fn.pacman, "r", encoding="utf-8") as f:
                lines = f.readlines()
                f.close()
            par_downloads = fn.get_combo_text(self.parallel_downloads)
            fn.log_info_concise(f"  Value : {par_downloads}")
            fn.log_info_concise(f"  File  : {fn.pacman}")
            pos_par_down = fn.get_position(lines, "ParallelDownloads")
            lines[pos_par_down] = "ParallelDownloads = " + par_downloads + "\n"

            with open(fn.pacman, "w", encoding="utf-8") as f:
                f.writelines(lines)
            fn.invalidate_pacman_conf_cache()
            fn.log_success(f"ParallelDownloads = {par_downloads} saved to {fn.pacman}")
            fn.show_in_app_notification(self, "Settings Saved Successfully")
            if hasattr(self, "parallel_downloads_label"):
                self.parallel_downloads_label.set_markup(f"ParallelDownloads: {par_downloads}")

        except Exception as error:
            fn.log_error(f"Error: {error}")
            fn.messagebox(
                self,
                "Failed!!",
                'There seems to have been a problem in "set_parallel_downloads"',
            )


def pop_parallel_downloads(self):
    """Return the current ParallelDownloads index (0-based) for preselecting the dropdown."""
    if fn.path.isfile(fn.pacman):
        try:
            with open(fn.pacman, "r", encoding="utf-8") as f:
                lines = f.readlines()
                f.close()
        except Exception as error:
            fn.log_error(str(error))
            fn.messagebox(
                self,
                "Failed!!",
                'There seems to have been a problem in "pop_parallel_downloads"',
            )
    try:
        parallel_downloads = check_parallel_downloads(lines, "ParallelDownloads").split("=")[1]
        active_number = int(parallel_downloads) - 1
        return active_number
    except IndexError:
        active_number = ""


def on_click_apply_parallel_downloads(self, _widget):
    fn.log_subsection("Apply Parallel Downloads")
    set_parallel_downloads(self, _widget)

import time

import functions as fn
from att_i18n import _
from gi.repository import GLib

URL_OLLAMA = "https://ollama.com/"
URL_WEBUI = "https://openwebui.com/"
URL_JAN = "https://jan.ai/"
URL_AICHAT = "https://github.com/sigoden/aichat"
URL_CLAUDE_CLI = "https://code.claude.com/docs/en/cli-reference"
URL_AIDER = "https://aider.chat/"
URL_CODEX = "https://developers.openai.com/codex/cli"
URL_ANTIGRAVITY_CLI = "https://antigravity.google/"
URL_ANTIGRAVITY = "https://antigravity.google/product/antigravity-2"
URL_OPENCODE = "https://opencode.ai"
URL_COPILOT = "https://github.com/github/gh-copilot"
URL_OPENCLAW = "https://github.com/openclaw/openclaw"
URL_CHATGPT_DOCS = "https://academy.openai.com/"
URL_CLAUDE_WEB_DOCS = "https://claude.com/resources/tutorials?open_in_browser=1"
URL_GEMINI_WEB_DOCS = "https://gemini.google.com/"
URL_PERPLEXITY_DOCS = "https://www.perplexity.ai/hub/getting-started"
URL_DALLE_DOCS = "https://openai.com/index/dall-e-3/"
URL_MIDJOURNEY_DOCS = "https://docs.midjourney.com/hc/en-us/articles/33329261836941-Getting-Started-Guide"
URL_LEONARDO_DOCS = "https://leonardo.ai/learn/"
URL_FIREFLY_DOCS = "https://www.adobe.com/learn/firefly"

_FS_SETTLE_DELAY = 1

# Pacman packages required before the AUR build can succeed, keyed by AUR package name.
_INSTALL_DEPS = {
    "claude-code": ["debugedit"],
}

AIDER_PATH = f"/home/{fn.sudo_username}/.local/bin/aider"
CODEX_PATHS = [
    "/usr/bin/codex",
    "/usr/local/bin/codex",
    f"/home/{fn.sudo_username}/.local/bin/codex",
    f"/home/{fn.sudo_username}/.npm-global/bin/codex",
]
ANTIGRAVITY_CLI_PATHS = ["/usr/bin/agy"]
ANTIGRAVITY_PATHS = ["/usr/bin/antigravity"]
OPENCODE_PATHS = [
    "/usr/bin/opencode",
    "/usr/local/bin/opencode",
    f"/home/{fn.sudo_username}/.local/bin/opencode",
    f"/home/{fn.sudo_username}/.npm-global/bin/opencode",
]
COPILOT_PATHS = [
    "/usr/bin/copilot",
    "/usr/local/bin/copilot",
    f"/home/{fn.sudo_username}/.local/bin/copilot",
    f"/home/{fn.sudo_username}/.npm-global/bin/copilot",
]
OPENCLAW_PATHS = ["/usr/bin/openclaw"]


def _read_temp_file(process):
    if not hasattr(process, "temp_file"):
        return ""
    try:
        with open(process.temp_file) as f:
            return f.read()
    except OSError:
        return ""


def on_click_ai_ollama(self, _widget):
    try:
        if fn.path.exists("/usr/bin/ollama"):
            fn.log_subsection("Removing ollama...")
            process = fn.launch_pacman_remove_in_terminal("ollama")

            def wait_removal():
                if process is None:
                    return
                process.wait()
                fn.invalidate_pkg_cache()
                fn.log_success("ollama removed successfully")
                GLib.idle_add(self.lbl_ai_ollama.set_markup, _("Ollama - Local LLM runner"))
                GLib.idle_add(self.btn_ai_ollama.set_label, _("Install"))
                GLib.idle_add(fn.show_in_app_notification, self, _("ollama removal complete"))

            fn.threading.Thread(target=wait_removal, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("ollama removal started"))
        else:
            has_nvidia = fn.path.exists("/dev/nvidia0")
            pkgs = "ollama ollama-cuda" if has_nvidia else "ollama"
            fn.log_subsection(f"Installing {pkgs}...")
            fn.debug_print(f"NVIDIA GPU detected: {has_nvidia}")
            process = fn.launch_pacman_install_in_terminal(pkgs)

            def wait_install():
                try:
                    if process is None:
                        return
                    process.wait()
                    fn.invalidate_pkg_cache()
                    error_output = _read_temp_file(process)
                    if fn.path.exists("/usr/bin/ollama"):
                        fn.log_success("ollama installed successfully")
                        GLib.idle_add(self.lbl_ai_ollama.set_markup, _("Ollama - Local LLM runner <b>installed</b>"))
                        GLib.idle_add(self.btn_ai_ollama.set_label, _("Remove"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("ollama installation complete"))
                    else:
                        fn.log_warn("ollama binary NOT found, installation may have failed")
                        fn.check_missing_repo_error(self, error_output, "ollama")
                except Exception as e:
                    fn.log_error(f"Error during ollama installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("ollama installation started"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_jan(self, _widget):
    try:
        if fn.path.exists("/usr/bin/jan"):
            fn.log_subsection("Removing jan...")
            process = fn.launch_pacman_remove_in_terminal("jan-bin")

            def wait_removal():
                if process is None:
                    return
                process.wait()
                fn.invalidate_pkg_cache()
                fn.log_success("jan removed successfully")
                GLib.idle_add(self.lbl_ai_jan.set_markup, _("Jan - Offline desktop AI"))
                GLib.idle_add(self.btn_ai_jan.set_label, _("Install"))
                GLib.idle_add(fn.show_in_app_notification, self, _("jan removal complete"))

            fn.threading.Thread(target=wait_removal, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("jan removal started"))
        else:
            # jan-bin ships only in the [cachyos] repo, which Kiro disables by default.
            # Guard up front so we never launch a doomed "target not found" install.
            if not fn.check_cachyos_repo_active():
                fn.log_warn("cachyos repo not enabled — jan-bin unavailable")
                GLib.idle_add(
                    fn.show_in_app_notification,
                    self,
                    _("Jan needs the cachyos repo. Enable [cachyos] in pacman.conf first."),
                )
                return
            fn.log_subsection("Installing jan-bin...")
            process = fn.launch_pacman_install_in_terminal("jan-bin")

            def wait_install():
                try:
                    if process is None:
                        return
                    process.wait()
                    fn.invalidate_pkg_cache()
                    error_output = _read_temp_file(process)
                    if fn.path.exists("/usr/bin/jan"):
                        fn.log_success("jan installed successfully")
                        GLib.idle_add(self.lbl_ai_jan.set_markup, _("Jan - Offline desktop AI <b>installed</b>"))
                        GLib.idle_add(self.btn_ai_jan.set_label, _("Remove"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("jan installation complete"))
                    else:
                        fn.log_warn("jan binary NOT found, installation may have failed")
                        fn.check_missing_repo_error(self, error_output, "jan-bin")
                except Exception as e:
                    fn.log_error(f"Error during jan installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("jan installation started"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_aichat(self, _widget):
    try:
        if fn.path.exists("/usr/bin/aichat"):
            fn.log_subsection("Removing aichat...")
            process = fn.launch_pacman_remove_in_terminal("aichat")

            def wait_removal():
                if process is None:
                    return
                process.wait()
                fn.invalidate_pkg_cache()
                fn.log_success("aichat removed successfully")
                GLib.idle_add(self.lbl_ai_aichat.set_markup, _("aichat - All-in-one LLM CLI"))
                GLib.idle_add(self.btn_ai_aichat.set_label, _("Install"))
                GLib.idle_add(fn.show_in_app_notification, self, _("aichat removal complete"))

            fn.threading.Thread(target=wait_removal, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("aichat removal started"))
        else:
            fn.log_subsection("Installing aichat...")
            process = fn.launch_pacman_install_in_terminal("aichat")

            def wait_install():
                try:
                    if process is None:
                        return
                    process.wait()
                    fn.invalidate_pkg_cache()
                    error_output = _read_temp_file(process)
                    if fn.path.exists("/usr/bin/aichat"):
                        fn.log_success("aichat installed successfully")
                        GLib.idle_add(self.lbl_ai_aichat.set_markup, _("aichat - All-in-one LLM CLI <b>installed</b>"))
                        GLib.idle_add(self.btn_ai_aichat.set_label, _("Remove"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("aichat installation complete"))
                    else:
                        fn.log_warn("aichat binary NOT found, installation may have failed")
                        fn.check_missing_repo_error(self, error_output, "aichat")
                except Exception as e:
                    fn.log_error(f"Error during aichat installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("aichat installation started"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_webui(self, _widget):
    try:
        if fn.path.exists("/usr/bin/open-webui"):
            fn.log_subsection("Removing open-webui...")
            process = fn.launch_pacman_remove_in_terminal("open-webui")

            def wait_removal():
                if process is None:
                    return
                process.wait()
                fn.invalidate_pkg_cache()
                fn.log_success("open-webui removed successfully")
                GLib.idle_add(self.lbl_ai_webui.set_markup, _("Open WebUI - Browser UI for Ollama"))
                GLib.idle_add(self.btn_ai_webui.set_label, _("Install"))
                GLib.idle_add(fn.show_in_app_notification, self, _("open-webui removal complete"))

            fn.threading.Thread(target=wait_removal, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("open-webui removal started"))
        else:
            aur_helper = fn.get_aur_helper()
            if aur_helper is None:
                fn.log_warn("No AUR helper found — install yay or paru first")
                GLib.idle_add(fn.show_in_app_notification, self, _("No AUR helper found. Install yay or paru first."))
                return
            fn.log_subsection("Installing open-webui...")
            process = fn.launch_aur_install_in_terminal(aur_helper, "open-webui")

            def wait_install():
                try:
                    if process is None:
                        return
                    process.wait()
                    fn.invalidate_pkg_cache()
                    error_output = _read_temp_file(process)
                    if fn.path.exists("/usr/bin/open-webui"):
                        fn.log_success("open-webui installed successfully")
                        GLib.idle_add(
                            self.lbl_ai_webui.set_markup,
                            _("Open WebUI - Browser UI for Ollama <b>installed</b>"),
                        )
                        GLib.idle_add(self.btn_ai_webui.set_label, _("Remove"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("open-webui installation complete"))
                    else:
                        fn.log_warn("open-webui binary NOT found, installation may have failed")
                        fn.check_missing_repo_error(self, error_output, "open-webui")
                except Exception as e:
                    fn.log_error(f"Error during open-webui installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("open-webui installation started"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def _aur_install_with_deps_in_terminal(aur_helper, package, username=None):
    """Launch an alacritty terminal that installs missing pacman deps then runs the AUR helper."""
    if username is None:
        username = fn.sudo_username
    deps = _INSTALL_DEPS.get(package, [])
    dep_script = ""
    if deps:
        checks = " ".join(deps)
        dep_script = (
            f"echo '=== Checking build dependencies ==='; "
            f"for dep in {checks}; do "
            f'pacman -Q "$dep" &>/dev/null && echo "  $dep already installed" || '
            f'(echo "  Installing $dep..."; pacman -S --noconfirm --needed "$dep"); '
            f"done; echo ''; "
        )
    script = (
        f"{dep_script}"
        f"unset GIT_DIR GIT_WORK_TREE; sudo -H -u {username} {aur_helper} -S --noconfirm {package};"
        " echo ''; echo '=== Installation complete ==='"
        " && echo 'You can close this window'"
        " && read -p 'Press Enter to close...'"
    )
    return fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )


def on_click_ai_claude(self, _widget):
    try:
        if fn.path.exists("/usr/bin/claude"):
            fn.log_subsection("Removing claude-code...")
            process = fn.launch_pacman_remove_in_terminal("claude-code")

            def wait_removal():
                if process is None:
                    return
                process.wait()
                fn.invalidate_pkg_cache()
                fn.log_success("claude-code removed successfully")
                GLib.idle_add(self.lbl_ai_claude.set_markup, _("Claude Code - Anthropic CLI"))
                GLib.idle_add(self.btn_ai_claude.set_label, _("Install"))
                GLib.idle_add(fn.show_in_app_notification, self, _("claude-code removal complete"))

            fn.threading.Thread(target=wait_removal, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("claude-code removal started"))
        else:
            aur_helper = fn.get_aur_helper()
            if aur_helper is None:
                fn.log_warn("No AUR helper found — install yay or paru first")
                GLib.idle_add(fn.show_in_app_notification, self, _("No AUR helper found. Install yay or paru first."))
                return
            fn.log_subsection("Installing claude-code...")
            process = _aur_install_with_deps_in_terminal(aur_helper, "claude-code")

            def wait_install():
                try:
                    if process is None:
                        return
                    process.wait()
                    fn.invalidate_pkg_cache()
                    error_output = _read_temp_file(process)
                    if fn.path.exists("/usr/bin/claude"):
                        fn.log_success("claude-code installed successfully")
                        GLib.idle_add(self.lbl_ai_claude.set_markup, _("Claude Code - Anthropic CLI <b>installed</b>"))
                        GLib.idle_add(self.btn_ai_claude.set_label, _("Remove"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("claude-code installation complete"))
                    else:
                        fn.log_warn("claude-code binary NOT found, installation may have failed")
                        fn.check_missing_repo_error(self, error_output, "claude-code")
                except Exception as e:
                    fn.log_error(f"Error during claude-code installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("claude-code installation started"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_aider(self, _widget):
    try:
        if fn.path.exists("/usr/bin/aider") or fn.path.exists(AIDER_PATH):
            fn.log_subsection("Removing aider...")
            aur_helper = fn.get_aur_helper()
            script = f"rm -f {AIDER_PATH}; "
            if aur_helper:
                script += f"sudo -u {fn.sudo_username} {aur_helper} -Rs --noconfirm aider-install; "
            script += (
                "echo ''; echo '=== Removal complete ==='"
                " && echo 'You can close this window'"
                " && read -p 'Press Enter to close...'"
            )
            fn.debug_print(f"Terminal cmd: {script}")
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )

            def wait_removal():
                process.wait()
                fn.invalidate_pkg_cache()
                fn.log_success("aider removed successfully")
                GLib.idle_add(self.lbl_ai_aider.set_markup, _("Aider - AI pair programming"))
                GLib.idle_add(self.btn_ai_aider.set_label, _("Install"))
                GLib.idle_add(fn.show_in_app_notification, self, _("aider removal complete"))

            fn.threading.Thread(target=wait_removal, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("aider removal started"))
        else:
            aur_helper = fn.get_aur_helper()
            if aur_helper is None:
                fn.log_warn("No AUR helper found — install yay or paru first")
                GLib.idle_add(fn.show_in_app_notification, self, _("No AUR helper found. Install yay or paru first."))
                return
            fn.log_subsection("Installing aider...")
            process = fn.launch_aur_install_in_terminal(aur_helper, "aider-install")

            def wait_install():
                try:
                    if process is None:
                        return
                    process.wait()
                    fn.invalidate_pkg_cache()
                    fn.log_subsection("Running aider-install setup...")
                    GLib.idle_add(fn.show_in_app_notification, self, _("Running aider setup..."))
                    setup_script = f"sudo -u {fn.sudo_username} aider-install; read -p 'Press Enter to close...'"
                    fn.debug_print(f"Terminal cmd: {setup_script}")
                    setup_process = fn.subprocess.Popen(
                        ["alacritty", "-e", "bash", "-c", setup_script],
                        stdout=fn.subprocess.PIPE,
                        stderr=fn.subprocess.PIPE,
                    )
                    setup_process.wait()
                    if fn.path.exists("/usr/bin/aider") or fn.path.exists(AIDER_PATH):
                        fn.log_success("aider installed successfully")
                        GLib.idle_add(self.lbl_ai_aider.set_markup, _("Aider - AI pair programming <b>installed</b>"))
                        GLib.idle_add(self.btn_ai_aider.set_label, _("Remove"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("aider installation complete"))
                    else:
                        fn.log_warn(f"Aider binary NOT found. Checked: /usr/bin/aider and {AIDER_PATH}")
                except Exception as e:
                    fn.log_error(f"Error during aider installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("aider installation started"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_codex(self, _widget):
    try:
        codex_installed = any(fn.path.exists(p) for p in CODEX_PATHS)

        if codex_installed:
            fn.log_subsection("Removing codex...")
            process = fn.launch_npm_remove_in_terminal("@openai/codex")
            if process:

                def wait_removal():
                    try:
                        process.wait()
                        fn.invalidate_pkg_cache()
                        time.sleep(_FS_SETTLE_DELAY)
                        GLib.idle_add(self.lbl_ai_codex.set_markup, _("OpenAI Codex CLI"))
                        GLib.idle_add(self.btn_ai_codex.set_label, _("Install"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("Codex removal complete"))
                    except Exception as e:
                        fn.log_error(f"Error during codex removal: {e}")

                fn.threading.Thread(target=wait_removal, daemon=True).start()
                GLib.idle_add(fn.show_in_app_notification, self, _("Codex removal started"))
            else:
                GLib.idle_add(fn.show_in_app_notification, self, _("Codex removal failed"))
        else:
            fn.log_subsection("Installing codex...")
            process = fn.launch_npm_install_in_terminal("@openai/codex")
            if process:

                def wait_install():
                    try:
                        process.wait()
                        fn.invalidate_pkg_cache()
                        time.sleep(_FS_SETTLE_DELAY)
                        if any(fn.path.exists(p) for p in CODEX_PATHS):
                            fn.log_success("codex installed successfully")
                            GLib.idle_add(self.lbl_ai_codex.set_markup, _("OpenAI Codex CLI <b>installed</b>"))
                            GLib.idle_add(self.btn_ai_codex.set_label, _("Remove"))
                            GLib.idle_add(fn.show_in_app_notification, self, _("Codex installation complete"))
                        else:
                            fn.log_warn(f"Codex binary NOT found. Checked: {CODEX_PATHS}")
                    except Exception as e:
                        fn.log_error(f"Error during codex installation: {e}")

                fn.threading.Thread(target=wait_install, daemon=True).start()
                GLib.idle_add(fn.show_in_app_notification, self, _("Codex installation started"))
            else:
                GLib.idle_add(fn.show_in_app_notification, self, _("Codex installation failed"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_antigravity_cli(self, _widget):
    try:
        if any(fn.path.exists(p) for p in ANTIGRAVITY_CLI_PATHS):
            fn.log_subsection("Removing antigravity-cli...")
            process = fn.launch_pacman_remove_in_terminal("antigravity-cli")

            def wait_removal():
                if process is None:
                    return
                process.wait()
                fn.invalidate_pkg_cache()
                fn.log_success("antigravity-cli removed successfully")
                GLib.idle_add(self.lbl_ai_antigravity_cli.set_markup, _("Antigravity-cli"))
                GLib.idle_add(self.btn_ai_antigravity_cli.set_label, _("Install"))
                GLib.idle_add(fn.show_in_app_notification, self, _("antigravity-cli removal complete"))

            fn.threading.Thread(target=wait_removal, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("antigravity-cli removal started"))
        else:
            aur_helper = fn.get_aur_helper()
            if aur_helper is None:
                fn.log_warn("No AUR helper found — install yay or paru first")
                GLib.idle_add(fn.show_in_app_notification, self, _("No AUR helper found. Install yay or paru first."))
                return
            fn.log_subsection("Installing antigravity-cli...")
            process = fn.launch_aur_install_in_terminal(aur_helper, "antigravity-cli")

            def wait_install():
                try:
                    if process is None:
                        return
                    process.wait()
                    fn.invalidate_pkg_cache()
                    if any(fn.path.exists(p) for p in ANTIGRAVITY_CLI_PATHS):
                        fn.log_success("antigravity-cli installed successfully")
                        GLib.idle_add(self.lbl_ai_antigravity_cli.set_markup, _("Antigravity-cli <b>installed</b>"))
                        GLib.idle_add(self.btn_ai_antigravity_cli.set_label, _("Remove"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("antigravity-cli installation complete"))
                    else:
                        fn.log_warn(f"antigravity-cli binary NOT found. Checked: {ANTIGRAVITY_CLI_PATHS}")
                except Exception as e:
                    fn.log_error(f"Error during antigravity-cli installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("antigravity-cli installation started"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_antigravity(self, _widget):
    try:
        if any(fn.path.exists(p) for p in ANTIGRAVITY_PATHS):
            fn.log_subsection("Removing antigravity...")
            process = fn.launch_pacman_remove_in_terminal("antigravity")

            def wait_removal():
                if process is None:
                    return
                process.wait()
                fn.invalidate_pkg_cache()
                fn.log_success("antigravity removed successfully")
                GLib.idle_add(self.lbl_ai_antigravity.set_markup, _("Antigravity (previous gemini)"))
                GLib.idle_add(self.btn_ai_antigravity.set_label, _("Install"))
                GLib.idle_add(fn.show_in_app_notification, self, _("antigravity removal complete"))

            fn.threading.Thread(target=wait_removal, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("antigravity removal started"))
        else:
            aur_helper = fn.get_aur_helper()
            if aur_helper is None:
                fn.log_warn("No AUR helper found — install yay or paru first")
                GLib.idle_add(fn.show_in_app_notification, self, _("No AUR helper found. Install yay or paru first."))
                return
            fn.log_subsection("Installing antigravity...")
            process = fn.launch_aur_install_in_terminal(aur_helper, "antigravity")

            def wait_install():
                try:
                    if process is None:
                        return
                    process.wait()
                    fn.invalidate_pkg_cache()
                    if any(fn.path.exists(p) for p in ANTIGRAVITY_PATHS):
                        fn.log_success("antigravity installed successfully")
                        GLib.idle_add(
                            self.lbl_ai_antigravity.set_markup, _("Antigravity (previous gemini) <b>installed</b>")
                        )
                        GLib.idle_add(self.btn_ai_antigravity.set_label, _("Remove"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("antigravity installation complete"))
                    else:
                        fn.log_warn(f"antigravity binary NOT found. Checked: {ANTIGRAVITY_PATHS}")
                except Exception as e:
                    fn.log_error(f"Error during antigravity installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("antigravity installation started"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_opencode(self, _widget):
    try:
        opencode_installed = any(fn.path.exists(p) for p in OPENCODE_PATHS)

        if opencode_installed:
            fn.log_subsection("Removing opencode...")
            process = fn.launch_npm_remove_in_terminal("opencode-ai")
            if process:

                def wait_removal():
                    try:
                        process.wait()
                        fn.invalidate_pkg_cache()
                        time.sleep(_FS_SETTLE_DELAY)
                        GLib.idle_add(self.lbl_ai_opencode.set_markup, _("OpenCode - TUI AI coding assistant"))
                        GLib.idle_add(self.btn_ai_opencode.set_label, _("Install"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("OpenCode removal complete"))
                    except Exception as e:
                        fn.log_error(f"Error during opencode removal: {e}")

                fn.threading.Thread(target=wait_removal, daemon=True).start()
                GLib.idle_add(fn.show_in_app_notification, self, _("OpenCode removal started"))
            else:
                GLib.idle_add(fn.show_in_app_notification, self, _("OpenCode removal failed"))
        else:
            fn.log_subsection("Installing opencode...")
            process = fn.launch_npm_install_in_terminal("opencode-ai")
            if process:

                def wait_install():
                    try:
                        process.wait()
                        fn.invalidate_pkg_cache()
                        time.sleep(_FS_SETTLE_DELAY)
                        if any(fn.path.exists(p) for p in OPENCODE_PATHS):
                            fn.log_success("opencode installed successfully")
                            GLib.idle_add(
                                self.lbl_ai_opencode.set_markup,
                                _("OpenCode - TUI AI coding assistant <b>installed</b>"),
                            )
                            GLib.idle_add(self.btn_ai_opencode.set_label, _("Remove"))
                            GLib.idle_add(fn.show_in_app_notification, self, _("OpenCode installation complete"))
                        else:
                            fn.log_warn(f"OpenCode binary NOT found. Checked: {OPENCODE_PATHS}")
                    except Exception as e:
                        fn.log_error(f"Error during opencode installation: {e}")

                fn.threading.Thread(target=wait_install, daemon=True).start()
                GLib.idle_add(fn.show_in_app_notification, self, _("OpenCode installation started"))
            else:
                GLib.idle_add(fn.show_in_app_notification, self, _("OpenCode installation failed"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_copilot(self, _widget):
    try:
        copilot_installed = any(fn.path.exists(p) for p in COPILOT_PATHS)

        if copilot_installed:
            fn.log_subsection("Removing github copilot cli...")
            process = fn.launch_npm_remove_in_terminal("@github/copilot")
            if process:

                def wait_removal():
                    try:
                        process.wait()
                        fn.invalidate_pkg_cache()
                        time.sleep(_FS_SETTLE_DELAY)
                        GLib.idle_add(self.lbl_ai_copilot.set_markup, _("GitHub Copilot CLI"))
                        GLib.idle_add(self.btn_ai_copilot.set_label, _("Install"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("Copilot CLI removal complete"))
                    except Exception as e:
                        fn.log_error(f"Error during copilot removal: {e}")

                fn.threading.Thread(target=wait_removal, daemon=True).start()
                GLib.idle_add(fn.show_in_app_notification, self, _("Copilot CLI removal started"))
            else:
                GLib.idle_add(fn.show_in_app_notification, self, _("Copilot CLI removal failed"))
        else:
            fn.log_subsection("Installing github copilot cli...")
            process = fn.launch_npm_install_in_terminal("@github/copilot")
            if process:

                def wait_install():
                    try:
                        process.wait()
                        fn.invalidate_pkg_cache()
                        time.sleep(_FS_SETTLE_DELAY)
                        if any(fn.path.exists(p) for p in COPILOT_PATHS):
                            fn.log_success("github copilot cli installed successfully")
                            GLib.idle_add(self.lbl_ai_copilot.set_markup, _("GitHub Copilot CLI <b>installed</b>"))
                            GLib.idle_add(self.btn_ai_copilot.set_label, _("Remove"))
                            GLib.idle_add(fn.show_in_app_notification, self, _("Copilot CLI installation complete"))
                        else:
                            fn.log_warn(f"Copilot binary NOT found. Checked: {COPILOT_PATHS}")
                    except Exception as e:
                        fn.log_error(f"Error during copilot installation: {e}")

                fn.threading.Thread(target=wait_install, daemon=True).start()
                GLib.idle_add(fn.show_in_app_notification, self, _("Copilot CLI installation started"))
            else:
                GLib.idle_add(fn.show_in_app_notification, self, _("Copilot CLI installation failed"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def on_click_ai_openclaw(self, _widget):
    try:
        if any(fn.path.exists(p) for p in OPENCLAW_PATHS):
            fn.log_subsection("Removing openclaw...")
            process = fn.launch_pacman_remove_in_terminal("openclaw")

            def wait_removal():
                if process is None:
                    return
                process.wait()
                fn.invalidate_pkg_cache()
                fn.log_success("openclaw removed successfully")
                GLib.idle_add(self.lbl_ai_openclaw.set_markup, _("OpenClaw - Multi-channel AI gateway"))
                GLib.idle_add(self.btn_ai_openclaw.set_label, _("Install"))
                GLib.idle_add(fn.show_in_app_notification, self, _("openclaw removal complete"))

            fn.threading.Thread(target=wait_removal, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("openclaw removal started"))
        else:
            aur_helper = fn.get_aur_helper()
            if aur_helper is None:
                fn.log_warn("No AUR helper found — install yay or paru first")
                GLib.idle_add(fn.show_in_app_notification, self, _("No AUR helper found. Install yay or paru first."))
                return
            fn.log_subsection("Installing openclaw...")
            process = fn.launch_aur_install_in_terminal(aur_helper, "openclaw")

            def wait_install():
                try:
                    if process is None:
                        return
                    process.wait()
                    fn.invalidate_pkg_cache()
                    if any(fn.path.exists(p) for p in OPENCLAW_PATHS):
                        fn.log_success("openclaw installed successfully")
                        GLib.idle_add(
                            self.lbl_ai_openclaw.set_markup, _("OpenClaw - Multi-channel AI gateway <b>installed</b>")
                        )
                        GLib.idle_add(self.btn_ai_openclaw.set_label, _("Remove"))
                        GLib.idle_add(fn.show_in_app_notification, self, _("openclaw installation complete"))
                    else:
                        fn.log_warn(f"openclaw binary NOT found. Checked: {OPENCLAW_PATHS}")
                except Exception as e:
                    fn.log_error(f"Error during openclaw installation: {e}")

            fn.threading.Thread(target=wait_install, daemon=True).start()
            GLib.idle_add(fn.show_in_app_notification, self, _("openclaw installation started"))
    except Exception as error:
        fn.log_error(f"Error: {error}")


def open_url_in_browser(self, url):
    fn.open_url_as_user(url)


def on_click_ai_ollama_link(self, _widget):
    open_url_in_browser(self, URL_OLLAMA)


def on_click_ai_webui_link(self, _widget):
    open_url_in_browser(self, URL_WEBUI)


def on_click_ai_jan_link(self, _widget):
    open_url_in_browser(self, URL_JAN)


def on_click_ai_aichat_link(self, _widget):
    open_url_in_browser(self, URL_AICHAT)


def on_click_ai_claude_link(self, _widget):
    open_url_in_browser(self, URL_CLAUDE_CLI)


def on_click_ai_aider_link(self, _widget):
    open_url_in_browser(self, URL_AIDER)


def on_click_ai_antigravity_cli_link(self, _widget):
    open_url_in_browser(self, URL_ANTIGRAVITY_CLI)


def on_click_ai_antigravity_link(self, _widget):
    open_url_in_browser(self, URL_ANTIGRAVITY)


def on_click_ai_codex_link(self, _widget):
    open_url_in_browser(self, URL_CODEX)


def on_click_ai_opencode_link(self, _widget):
    open_url_in_browser(self, URL_OPENCODE)


def on_click_ai_copilot_link(self, _widget):
    open_url_in_browser(self, URL_COPILOT)


def on_click_ai_openclaw_link(self, _widget):
    open_url_in_browser(self, URL_OPENCLAW)


def on_click_ai_chatgpt(self, _widget):
    open_url_in_browser(self, "https://chatgpt.com")


def on_click_ai_chatgpt_link(self, _widget):
    open_url_in_browser(self, URL_CHATGPT_DOCS)


def on_click_ai_claude_web_link(self, _widget):
    open_url_in_browser(self, URL_CLAUDE_WEB_DOCS)


def on_click_ai_gemini_web_link(self, _widget):
    open_url_in_browser(self, URL_GEMINI_WEB_DOCS)


def on_click_ai_perplexity_link(self, _widget):
    open_url_in_browser(self, URL_PERPLEXITY_DOCS)


def on_click_ai_claude_web(self, _widget):
    open_url_in_browser(self, "https://claude.ai")


def on_click_ai_gemini_web(self, _widget):
    open_url_in_browser(self, "https://gemini.google.com")


def on_click_ai_perplexity(self, _widget):
    open_url_in_browser(self, "https://perplexity.ai")


def on_click_ai_dalle_link(self, _widget):
    open_url_in_browser(self, URL_DALLE_DOCS)


def on_click_ai_dalle(self, _widget):
    open_url_in_browser(self, "https://openai.com/dall-e-3")


def on_click_ai_midjourney_link(self, _widget):
    open_url_in_browser(self, URL_MIDJOURNEY_DOCS)


def on_click_ai_midjourney(self, _widget):
    open_url_in_browser(self, "https://www.midjourney.com")


def on_click_ai_leonardo_link(self, _widget):
    open_url_in_browser(self, URL_LEONARDO_DOCS)


def on_click_ai_leonardo(self, _widget):
    open_url_in_browser(self, "https://leonardo.ai")


def on_click_ai_firefly_link(self, _widget):
    open_url_in_browser(self, URL_FIREFLY_DOCS)


def on_click_ai_firefly(self, _widget):
    open_url_in_browser(self, "https://www.adobe.com/products/firefly")

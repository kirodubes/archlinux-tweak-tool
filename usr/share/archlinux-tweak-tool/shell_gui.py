# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functools
import shell
from att_i18n import _


def _build_zsh_installed_content(self, vbox, Gtk, zsh_theme, base_dir, GdkPixbuf, fn):
    from gi.repository import Gdk

    hbox_zsh_status_lbl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.zsh_completions_lbl = Gtk.Label(xalign=0)
    if fn.check_package_installed("zsh-completions"):
        self.zsh_completions_lbl.set_markup(_("Zsh-completion is already <b>installed</b>"))
    else:
        self.zsh_completions_lbl.set_markup(_("Zsh-completion is <b>not</b> installed"))
    self.zsh_completions_lbl.set_margin_start(10)
    self.zsh_completions_lbl.set_margin_end(10)
    hbox_zsh_status_lbl.append(self.zsh_completions_lbl)

    hbox_zsh_completions_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.install_zsh_completions = Gtk.Button(label=_("Install zsh-completion"))
    self.install_zsh_completions.connect("clicked", functools.partial(shell.on_install_zsh_completions_clicked, self))
    self.remove_zsh_completions = Gtk.Button(label=_("Remove zsh-completion"))
    self.remove_zsh_completions.connect("clicked", functools.partial(shell.on_remove_zsh_completions_clicked, self))
    hbox_zsh_completions_btns.set_margin_start(10)
    hbox_zsh_completions_btns.append(self.install_zsh_completions)
    hbox_zsh_completions_btns.append(self.remove_zsh_completions)

    hbox_zsh_syntax_lbl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.zsh_syntax_lbl = Gtk.Label(xalign=0)
    if fn.check_package_installed("zsh-syntax-highlighting"):
        self.zsh_syntax_lbl.set_markup(_("Zsh-syntax-highlighting is already <b>installed</b>"))
    else:
        self.zsh_syntax_lbl.set_markup(_("Zsh-syntax-highlighting is not installed"))
    self.zsh_syntax_lbl.set_margin_start(10)
    self.zsh_syntax_lbl.set_margin_end(10)
    hbox_zsh_syntax_lbl.append(self.zsh_syntax_lbl)

    hbox_zsh_syntax_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.install_zsh_syntax_highlighting = Gtk.Button(label=_("Install Zsh-syntax-highlighting"))
    self.install_zsh_syntax_highlighting.connect(
        "clicked", functools.partial(shell.on_install_zsh_syntax_highlighting_clicked, self)
    )
    self.remove_zsh_syntax_highlighting = Gtk.Button(label=_("Remove Zsh-syntax-highlighting"))
    self.remove_zsh_syntax_highlighting.connect(
        "clicked", functools.partial(shell.on_remove_zsh_syntax_highlighting_clicked, self)
    )
    hbox_zsh_syntax_btns.set_margin_start(10)
    hbox_zsh_syntax_btns.append(self.install_zsh_syntax_highlighting)
    hbox_zsh_syntax_btns.append(self.remove_zsh_syntax_highlighting)

    # ── Oh-my-zsh ─────────────────────────────────────────────────

    hbox_zsh_omz_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_zsh_omz_title_lbl = Gtk.Label(xalign=0)
    hbox_zsh_omz_title_lbl.set_markup("<b>Oh-my-zsh</b>")
    hbox_zsh_omz_title_lbl.set_margin_start(10)
    hbox_zsh_omz_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_zsh_omz_title_sep.set_hexpand(True)
    hbox_zsh_omz_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_zsh_omz_title.append(hbox_zsh_omz_title_lbl)
    hbox_zsh_omz_title.append(hbox_zsh_omz_title_sep)

    hbox_zsh_omz_lbl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.zsh_omz_lbl = Gtk.Label(xalign=0)
    if fn.check_package_installed("oh-my-zsh-git"):
        self.zsh_omz_lbl.set_markup(_("Oh-my-zsh-git is already <b>installed</b>"))
    else:
        self.zsh_omz_lbl.set_markup(_("Oh-my-zsh-git is not installed"))
    self.zsh_omz_lbl.set_margin_start(10)
    self.zsh_omz_lbl.set_margin_end(10)
    hbox_zsh_omz_lbl.append(self.zsh_omz_lbl)

    hbox_zsh_omz_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.install_zsh_omz = Gtk.Button(label=_("Install Oh-my-zsh"))
    self.install_zsh_omz.connect("clicked", functools.partial(shell.install_oh_my_zsh, self))
    self.remove_zsh_omz = Gtk.Button(label=_("Remove Oh-my-zsh"))
    self.remove_zsh_omz.connect("clicked", functools.partial(shell.remove_oh_my_zsh, self))
    hbox_zsh_omz_btns.set_margin_start(10)
    hbox_zsh_omz_btns.append(self.install_zsh_omz)
    hbox_zsh_omz_btns.append(self.remove_zsh_omz)

    # ── ATT config ────────────────────────────────────────────────

    hbox_zsh_att_config_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_zsh_att_config_title_lbl = Gtk.Label(xalign=0)
    hbox_zsh_att_config_title_lbl.set_markup(_("<b>ATT config</b>"))
    hbox_zsh_att_config_title_lbl.set_margin_start(10)
    hbox_zsh_att_config_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_zsh_att_config_sep.set_hexpand(True)
    hbox_zsh_att_config_sep.set_valign(Gtk.Align.CENTER)
    hbox_zsh_att_config_title.append(hbox_zsh_att_config_title_lbl)
    hbox_zsh_att_config_title.append(hbox_zsh_att_config_sep)

    hbox_zsh_config_lbl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    hbox_zsh_config_lbl_txt = Gtk.Label(xalign=0)
    hbox_zsh_config_lbl_txt.set_markup(_("Overwrite your ~/.zshrc with the ATT zshrc"))
    hbox_zsh_config_lbl_txt.set_margin_start(10)
    hbox_zsh_config_lbl_txt.set_margin_end(10)
    hbox_zsh_config_lbl.append(hbox_zsh_config_lbl_txt)

    hbox_zsh_config_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.install_zsh_config = Gtk.Button(label=_("Install the ATT zshrc configuration"))
    self.install_zsh_config.connect("clicked", functools.partial(shell.on_install_att_zshrc_clicked, self))
    self.zsh_reset = Gtk.Button(label=_("Reset back to the original ~/.zshrc"))
    self.zsh_reset.connect("clicked", functools.partial(shell.on_zshrc_reset_clicked, self))
    hbox_zsh_config_btns.set_margin_start(10)
    hbox_zsh_config_btns.append(self.install_zsh_config)
    hbox_zsh_config_btns.append(self.zsh_reset)

    # ── Themes ────────────────────────────────────────────────────

    hbox_zsh_themes_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_zsh_themes_title_lbl = Gtk.Label(xalign=0)
    hbox_zsh_themes_title_lbl.set_markup(_("<b>Themes</b>"))
    hbox_zsh_themes_title_lbl.set_margin_start(10)
    hbox_zsh_themes_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_zsh_themes_sep.set_hexpand(True)
    hbox_zsh_themes_sep.set_valign(Gtk.Align.CENTER)
    hbox_zsh_themes_title.append(hbox_zsh_themes_title_lbl)
    hbox_zsh_themes_title.append(hbox_zsh_themes_sep)

    hbox_zsh_themes_dropdown = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_zsh_themes_dropdown_lbl = Gtk.Label(xalign=0)
    hbox_zsh_themes_dropdown_lbl.set_markup(_("Zsh themes"))
    hbox_zsh_themes_dropdown_lbl.set_margin_start(10)
    hbox_zsh_themes_dropdown_lbl.set_margin_end(10)
    self.zsh_themes = Gtk.DropDown.new_from_strings([])
    self.zsh_themes.set_size_request(300, 20)
    zsh_theme.get_themes(self.zsh_themes)
    self.zsh_themes.set_margin_start(10)
    self.zsh_themes.set_margin_end(10)
    hbox_zsh_themes_dropdown.append(hbox_zsh_themes_dropdown_lbl)
    hbox_zsh_themes_dropdown.append(self.zsh_themes)

    hbox_zsh_apply_theme_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.termset = Gtk.Button(label=_("Apply Zsh theme"))
    self.termset.connect("clicked", functools.partial(shell.on_zsh_apply_theme, self))
    omz_installed = fn.check_package_installed("oh-my-zsh-git")
    self.termset.set_sensitive(omz_installed)
    self.zsh_themes.set_sensitive(omz_installed)
    self.termset.set_margin_start(10)
    self.termset.set_margin_end(10)
    hbox_zsh_apply_theme_btn.append(self.termset)

    image_width = 800
    image_height = 500
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(base_dir + "/images/zsh-sample.jpg", image_width, image_height)
    if self.zsh_themes.get_selected_item() is None:
        pass
    elif fn.path.isfile(base_dir + "/images/zsh_previews/" + fn.get_combo_text(self.zsh_themes) + ".jpg"):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            base_dir + "/images/zsh_previews/" + fn.get_combo_text(self.zsh_themes) + ".jpg",
            image_width,
            image_height,
        )
    texture = Gdk.Texture.new_for_pixbuf(pixbuf)
    image = Gtk.Picture.new_for_paintable(texture)
    image.set_content_fit(Gtk.ContentFit.CONTAIN)
    image.set_margin_top(0)
    image.set_hexpand(False)
    image.set_vexpand(False)

    self.zsh_themes.connect(
        "notify::selected",
        lambda w, _p, img, tt, ab, iw, ih: fn.update_image(self, w, img, tt, ab, iw, ih),
        image,
        "zsh",
        base_dir,
        image_width,
        image_height,
    )

    # ── Change shell ──────────────────────────────────────────────

    hbox_zsh_change_shell_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_zsh_change_shell_title_lbl = Gtk.Label(xalign=0)
    hbox_zsh_change_shell_title_lbl.set_markup(_("<b>Change shell</b>"))
    hbox_zsh_change_shell_title_lbl.set_margin_start(10)
    hbox_zsh_change_shell_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_zsh_change_shell_sep.set_hexpand(True)
    hbox_zsh_change_shell_sep.set_valign(Gtk.Align.CENTER)
    hbox_zsh_change_shell_title.append(hbox_zsh_change_shell_title_lbl)
    hbox_zsh_change_shell_title.append(hbox_zsh_change_shell_sep)

    hbox_zsh_logout_warning = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_zsh_logout_warning_lbl = Gtk.Label(xalign=0)
    hbox_zsh_logout_warning_lbl.set_markup(
        _("Restart your terminal to apply the new Zsh theme\n<b>If you just switched shell, log-out first</b>")
    )
    hbox_zsh_logout_warning_lbl.set_margin_start(10)
    hbox_zsh_logout_warning_lbl.set_margin_end(10)
    hbox_zsh_logout_warning.append(hbox_zsh_logout_warning_lbl)

    hbox_zsh_shell_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    tozsh = Gtk.Button(label=_("Apply zsh"))
    tozsh.connect("clicked", functools.partial(shell.tozsh_apply, self))
    hbox_zsh_shell_buttons.set_margin_start(10)
    hbox_zsh_shell_buttons.append(tozsh)

    vbox.append(hbox_zsh_status_lbl)
    vbox.append(hbox_zsh_completions_btns)
    vbox.append(hbox_zsh_syntax_lbl)
    vbox.append(hbox_zsh_syntax_btns)
    vbox.append(hbox_zsh_att_config_title)
    vbox.append(hbox_zsh_config_lbl)
    vbox.append(hbox_zsh_config_btns)
    vbox.append(hbox_zsh_omz_title)
    vbox.append(hbox_zsh_omz_lbl)
    vbox.append(hbox_zsh_omz_btns)
    vbox.append(hbox_zsh_themes_title)
    vbox.append(hbox_zsh_themes_dropdown)
    vbox.append(hbox_zsh_apply_theme_btn)
    vbox.append(image)
    vbox.append(hbox_zsh_change_shell_title)
    vbox.append(hbox_zsh_logout_warning)
    vbox.append(hbox_zsh_shell_buttons)


def gui(self, Gtk, vboxstack_shells, zsh_theme, base_dir, GdkPixbuf, fn):
    """Create the Shells configuration GUI (bash, zsh, fish, extra tools)."""
    hbox_shells_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_shells_title_lbl = Gtk.Label(xalign=0)
    hbox_shells_title_lbl.set_text(_("Shells"))
    hbox_shells_title_lbl.set_name("title")
    hbox_shells_title_lbl.set_margin_start(10)
    hbox_shells_title_lbl.set_margin_end(10)
    hbox_shells_title.append(hbox_shells_title_lbl)

    hbox_shells_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_shells_sep.append(hseparator)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    vbox_bash = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_zsh = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_fish = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox_extra = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    stack.set_transition_duration(350)
    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)

    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
    stack_switcher.set_stack(stack)

    if fn.check_package_installed("bash"):
        # ── Bash ─────────────────────────────────────────────────────

        hbox_bash_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_bash_title_lbl = Gtk.Label(xalign=0)
        hbox_bash_title_lbl.set_text("Bash")
        hbox_bash_title_lbl.set_name("title")
        hbox_bash_title.append(hbox_bash_title_lbl)

        hbox_bash_top_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        hseparator.set_hexpand(True)
        hseparator.set_vexpand(False)
        hbox_bash_top_sep.append(hseparator)

        # ── Installation ──────────────────────────────────────────────

        hbox_installation_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_installation_title_lbl = Gtk.Label(xalign=0)
        hbox_installation_title_lbl.set_markup(_("<b>Installation</b>"))
        hbox_installation_title_lbl.set_margin_start(10)
        hbox_installation_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_installation_sep.set_hexpand(True)
        hbox_installation_sep.set_valign(Gtk.Align.CENTER)
        hbox_installation_title.append(hbox_installation_title_lbl)
        hbox_installation_title.append(hbox_installation_sep)

        hbox_bash_completion_lbl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.bash_completion_lbl = Gtk.Label(xalign=0)
        if fn.check_package_installed("bash"):
            self.bash_completion_lbl.set_markup(_("Bash is already <b>installed</b>"))
        else:
            self.bash_completion_lbl.set_markup(_("Bash is not installed"))
        if fn.check_package_installed("bash-completion"):
            self.bash_completion_lbl.set_markup(_("Bash and bash-completion are already <b>installed</b>"))
        else:
            self.bash_completion_lbl.set_markup(_("Bash is already installed and bash-completion is not installed"))
        self.bash_completion_lbl.set_margin_start(10)
        self.bash_completion_lbl.set_margin_end(10)
        hbox_bash_completion_lbl.append(self.bash_completion_lbl)

        hbox_bash_completion_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        install_bash_completion = Gtk.Button(label=_("Install bash-completion"))
        install_bash_completion.connect("clicked", functools.partial(shell.on_install_bash_completion_clicked, self))
        remove_bash_completion = Gtk.Button(label=_("Remove bash-completion"))
        remove_bash_completion.connect("clicked", functools.partial(shell.on_remove_bash_completion_clicked, self))
        hbox_bash_completion_btns.set_margin_start(10)
        hbox_bash_completion_btns.append(install_bash_completion)
        hbox_bash_completion_btns.append(remove_bash_completion)

        # ── ATT config ────────────────────────────────────────────────

        hbox_att_config_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_att_config_title_lbl = Gtk.Label(xalign=0)
        hbox_att_config_title_lbl.set_markup(_("<b>ATT config</b>"))
        hbox_att_config_title_lbl.set_margin_start(10)
        hbox_att_config_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_att_config_sep.set_hexpand(True)
        hbox_att_config_sep.set_valign(Gtk.Align.CENTER)
        hbox_att_config_title.append(hbox_att_config_title_lbl)
        hbox_att_config_title.append(hbox_att_config_sep)

        hbox_bash_config_lbl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox_bash_config_lbl_txt = Gtk.Label(xalign=0)
        hbox_bash_config_lbl_txt.set_markup(_("Overwrite your ~/.bashrc with the ATT bashrc"))
        hbox_bash_config_lbl_txt.set_margin_start(10)
        hbox_bash_config_lbl_txt.set_margin_end(10)
        hbox_bash_config_lbl.append(hbox_bash_config_lbl_txt)

        hbox_bash_config_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.install_bash_config = Gtk.Button(label=_("Install the ATT bashrc configuration"))
        self.install_bash_config.connect("clicked", functools.partial(shell.on_install_att_bashrc_clicked, self))
        self.bash_reset = Gtk.Button(label=_("Reset back to your original ~/.bashrc"))
        self.bash_reset.connect("clicked", functools.partial(shell.on_bash_reset_clicked, self))
        hbox_bash_config_btns.set_margin_start(10)
        hbox_bash_config_btns.append(self.install_bash_config)
        hbox_bash_config_btns.append(self.bash_reset)

        # ── Change shell ──────────────────────────────────────────────

        hbox_change_shell_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_change_shell_title_lbl = Gtk.Label(xalign=0)
        hbox_change_shell_title_lbl.set_markup(_("<b>Change shell</b>"))
        hbox_change_shell_title_lbl.set_margin_start(10)
        hbox_change_shell_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_change_shell_sep.set_hexpand(True)
        hbox_change_shell_sep.set_valign(Gtk.Align.CENTER)
        hbox_change_shell_title.append(hbox_change_shell_title_lbl)
        hbox_change_shell_title.append(hbox_change_shell_sep)

        hbox_logout_warning = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_logout_warning_lbl = Gtk.Label()
        hbox_logout_warning_lbl.set_markup(_("<b>If you just switched shell, log-out first</b>"))
        hbox_logout_warning_lbl.set_margin_start(10)
        hbox_logout_warning_lbl.set_margin_end(10)
        hbox_logout_warning.append(hbox_logout_warning_lbl)

        hbox_shell_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        tobash = Gtk.Button(label=_("Apply bash"))
        tobash.connect("clicked", functools.partial(shell.tobash_apply, self))
        hbox_shell_buttons.set_margin_start(10)
        hbox_shell_buttons.append(tobash)

        # ── Append to vbox ───────────────────────────────────────────

        vbox_bash.append(hbox_bash_title)
        vbox_bash.append(hbox_bash_top_sep)
        vbox_bash.append(hbox_installation_title)
        vbox_bash.append(hbox_bash_completion_lbl)
        vbox_bash.append(hbox_bash_completion_btns)
        vbox_bash.append(hbox_att_config_title)
        vbox_bash.append(hbox_bash_config_lbl)
        vbox_bash.append(hbox_bash_config_btns)
        vbox_bash.append(hbox_change_shell_title)
        vbox_bash.append(hbox_logout_warning)
        vbox_bash.append(hbox_shell_buttons)

    else:
        # no bash installed
        hbox_bash_missing_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_bash_missing_title_lbl = Gtk.Label(xalign=0)
        hbox_bash_missing_title_lbl.set_text(_("Bash is not installed"))
        hbox_bash_missing_title_lbl.set_name("title")
        hbox_bash_missing_title.append(hbox_bash_missing_title_lbl)

        hbox_bash_missing_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        hseparator.set_hexpand(True)
        hseparator.set_vexpand(False)
        hbox_bash_missing_sep.append(hseparator)

        message = Gtk.Label()
        message.set_markup(_("<b>Bash does not seem to be installed</b>"))

        vbox_bash.append(hbox_bash_missing_title)
        vbox_bash.append(hbox_bash_missing_sep)
        vbox_bash.append(message)

    # ── Zsh ──────────────────────────────────────────────────────────

    self.zsh_vbox = vbox_zsh

    # ── Title ─────────────────────────────────────────────────────

    hbox_zsh_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_zsh_title_lbl = Gtk.Label(xalign=0)
    hbox_zsh_title_lbl.set_text("Zsh")
    hbox_zsh_title_lbl.set_name("title")
    hbox_zsh_title.append(hbox_zsh_title_lbl)

    hbox_zsh_top_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator_zsh = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator_zsh.set_hexpand(True)
    hseparator_zsh.set_vexpand(False)
    hbox_zsh_top_sep.append(hseparator_zsh)

    # ── Installation (always active) ──────────────────────────────

    hbox_zsh_installation_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_zsh_installation_title_lbl = Gtk.Label(xalign=0)
    hbox_zsh_installation_title_lbl.set_markup(_("<b>Installation</b>"))
    hbox_zsh_installation_title_lbl.set_margin_start(10)
    hbox_zsh_installation_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_zsh_installation_sep.set_hexpand(True)
    hbox_zsh_installation_sep.set_valign(Gtk.Align.CENTER)
    hbox_zsh_installation_title.append(hbox_zsh_installation_title_lbl)
    hbox_zsh_installation_title.append(hbox_zsh_installation_sep)

    hbox_zsh_status_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.zsh_status_lbl = Gtk.Label(xalign=0)
    if fn.check_package_installed("zsh"):
        self.zsh_status_lbl.set_markup(_("Zsh is <b>installed</b>"))
        self.zsh_status_lbl.set_margin_start(10)
        self.zsh_status_lbl.set_margin_end(10)
        hbox_zsh_status_row.append(self.zsh_status_lbl)

    hbox_zsh_install_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.install_zsh = Gtk.Button(label=_("Install Zsh"))
    self.install_zsh.connect("clicked", functools.partial(shell.on_install_zsh_clicked, self))
    self.remove_zsh = Gtk.Button(label=_("Remove Zsh"))
    self.remove_zsh.connect("clicked", functools.partial(shell.on_remove_zsh_clicked, self))
    hbox_zsh_install_btns.set_margin_start(10)
    hbox_zsh_install_btns.append(self.install_zsh)
    hbox_zsh_install_btns.append(self.remove_zsh)

    vbox_zsh.append(hbox_zsh_title)
    vbox_zsh.append(hbox_zsh_top_sep)
    vbox_zsh.append(hbox_zsh_installation_title)
    if fn.check_package_installed("zsh"):
        vbox_zsh.append(hbox_zsh_status_row)
    vbox_zsh.append(hbox_zsh_install_btns)

    # ── Config + rest (greyed when zsh absent) ────────────────────

    self.zsh_config_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    _build_zsh_installed_content(self, self.zsh_config_section, Gtk, zsh_theme, base_dir, GdkPixbuf, fn)
    if not fn.check_package_installed("zsh"):
        self.zsh_config_section.set_sensitive(False)
    vbox_zsh.append(self.zsh_config_section)

    # ── Fish ─────────────────────────────────────────────────────────

    # ── Title ─────────────────────────────────────────────────────

    hbox_fish_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fish_title_lbl = Gtk.Label(xalign=0)
    hbox_fish_title_lbl.set_text("Fish")
    hbox_fish_title_lbl.set_name("title")
    hbox_fish_title.append(hbox_fish_title_lbl)

    hbox_fish_top_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_fish_top_sep.append(hseparator)

    # ── Installation (always active) ──────────────────────────────

    hbox_fish_installation_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fish_installation_title_lbl = Gtk.Label(xalign=0)
    hbox_fish_installation_title_lbl.set_markup(_("<b>Installation</b>"))
    hbox_fish_installation_title_lbl.set_margin_start(10)
    hbox_fish_installation_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_fish_installation_sep.set_hexpand(True)
    hbox_fish_installation_sep.set_valign(Gtk.Align.CENTER)
    hbox_fish_installation_title.append(hbox_fish_installation_title_lbl)
    hbox_fish_installation_title.append(hbox_fish_installation_sep)

    hbox_fish_status_lbl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.fish_status_lbl = Gtk.Label(xalign=0)
    if fn.check_package_installed("fish"):
        self.fish_status_lbl.set_markup(_("Fish is <b>installed</b>"))
        self.fish_status_lbl.set_margin_start(10)
        self.fish_status_lbl.set_margin_end(10)
        hbox_fish_status_lbl.append(self.fish_status_lbl)

    hbox_fish_install_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.install_fish = Gtk.Button(label=_("Install Fish"))
    self.install_fish.connect("clicked", functools.partial(shell.on_install_only_fish_clicked, self))
    self.remove_fish = Gtk.Button(label=_("Remove Fish"))
    self.remove_fish.connect("clicked", functools.partial(shell.on_remove_only_fish_clicked, self))
    hbox_fish_install_btns.set_margin_start(10)
    hbox_fish_install_btns.append(self.install_fish)
    hbox_fish_install_btns.append(self.remove_fish)

    # ── Config + Change shell (greyed when fish absent) ───────────

    self.fish_config_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    hbox_fish_att_config_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fish_att_config_title_lbl = Gtk.Label(xalign=0)
    hbox_fish_att_config_title_lbl.set_markup(_("<b>ATT config</b>"))
    hbox_fish_att_config_title_lbl.set_margin_start(10)
    hbox_fish_att_config_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_fish_att_config_sep.set_hexpand(True)
    hbox_fish_att_config_sep.set_valign(Gtk.Align.CENTER)
    hbox_fish_att_config_title.append(hbox_fish_att_config_title_lbl)
    hbox_fish_att_config_title.append(hbox_fish_att_config_sep)

    hbox_fish_config_lbl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    hbox_fish_config_lbl_txt = Gtk.Label(xalign=0)
    hbox_fish_config_lbl_txt.set_markup(_("Overwrite your ~/.config/fish/config.fish with the ATT config"))
    hbox_fish_config_lbl_txt.set_margin_start(10)
    hbox_fish_config_lbl_txt.set_margin_end(10)
    hbox_fish_config_lbl.append(hbox_fish_config_lbl_txt)

    hbox_fish_config_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.install_fish_config = Gtk.Button(label=_("Install the ATT config.fish"))
    self.install_fish_config.connect("clicked", functools.partial(shell.on_install_att_fish_config_clicked, self))
    self.fish_reset = Gtk.Button(label=_("Reset back to the original ~/.config/fish/config.fish"))
    self.fish_reset.connect("clicked", functools.partial(shell.on_fish_reset_clicked, self))
    hbox_fish_config_btns.set_margin_start(10)
    hbox_fish_config_btns.append(self.install_fish_config)
    hbox_fish_config_btns.append(self.fish_reset)

    hbox_fish_change_shell_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fish_change_shell_title_lbl = Gtk.Label(xalign=0)
    hbox_fish_change_shell_title_lbl.set_markup(_("<b>Change shell</b>"))
    hbox_fish_change_shell_title_lbl.set_margin_start(10)
    hbox_fish_change_shell_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_fish_change_shell_sep.set_hexpand(True)
    hbox_fish_change_shell_sep.set_valign(Gtk.Align.CENTER)
    hbox_fish_change_shell_title.append(hbox_fish_change_shell_title_lbl)
    hbox_fish_change_shell_title.append(hbox_fish_change_shell_sep)

    hbox_fish_logout_warning = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_fish_logout_warning_lbl = Gtk.Label(xalign=0)
    hbox_fish_logout_warning_lbl.set_markup(
        _("Restart your terminal to apply the new Fish config\n<b>If you just switched shell, log-out first</b>")
    )
    hbox_fish_logout_warning_lbl.set_margin_start(10)
    hbox_fish_logout_warning_lbl.set_margin_end(10)
    hbox_fish_logout_warning.append(hbox_fish_logout_warning_lbl)

    hbox_fish_shell_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    tofish = Gtk.Button(label=_("Apply fish"))
    tofish.connect("clicked", functools.partial(shell.tofish_apply, self))
    hbox_fish_shell_btns.set_margin_start(10)
    hbox_fish_shell_btns.append(tofish)

    self.fish_config_section.append(hbox_fish_att_config_title)
    self.fish_config_section.append(hbox_fish_config_lbl)
    self.fish_config_section.append(hbox_fish_config_btns)
    self.fish_config_section.append(hbox_fish_change_shell_title)
    self.fish_config_section.append(hbox_fish_logout_warning)
    self.fish_config_section.append(hbox_fish_shell_btns)

    if not fn.check_package_installed("fish"):
        self.fish_config_section.set_sensitive(False)

    # ── Fish Tweak Tool ───────────────────────────────────────────
    hbox_ftt_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_ftt_title_lbl = Gtk.Label(xalign=0)
    hbox_ftt_title_lbl.set_markup(_("<b>Fish Tweak Tool</b>"))
    hbox_ftt_title_lbl.set_margin_start(10)
    hbox_ftt_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_ftt_title_sep.set_hexpand(True)
    hbox_ftt_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_ftt_title.append(hbox_ftt_title_lbl)
    hbox_ftt_title.append(hbox_ftt_title_sep)

    hbox_ftt_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.ftt_status_lbl = Gtk.Label(xalign=0)
    shell._refresh_ftt_lbl(self)
    self.ftt_status_lbl.set_margin_start(10)
    self.ftt_status_lbl.set_margin_end(10)
    hbox_ftt_status.append(self.ftt_status_lbl)

    hbox_ftt_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_ftt_btns.set_margin_start(10)
    btn_install_ftt = Gtk.Button(label=_("Install fish-tweak-tool"))
    btn_install_ftt.connect("clicked", functools.partial(shell.on_install_fish_tweak_tool_clicked, self))
    btn_remove_ftt = Gtk.Button(label=_("Remove fish-tweak-tool"))
    btn_remove_ftt.connect("clicked", functools.partial(shell.on_remove_fish_tweak_tool_clicked, self))
    hbox_ftt_btns.append(btn_install_ftt)
    hbox_ftt_btns.append(btn_remove_ftt)

    hbox_ftt_repo_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    if not fn.check_nemesis_repo_active():
        ftt_repo_note_lbl = Gtk.Label(xalign=0)
        ftt_repo_note_lbl.set_markup(_("<i>Enable the Nemesis repo (Pacman page) to install fish-tweak-tool</i>"))
        ftt_repo_note_lbl.set_margin_start(10)
        ftt_repo_note_lbl.set_margin_end(10)
        hbox_ftt_repo_note.append(ftt_repo_note_lbl)

    hbox_ftt_launch = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_ftt_launch.set_margin_start(10)
    self.btn_launch_ftt = Gtk.Button(label=_("Launch Fish Tweak Tool"))
    self.btn_launch_ftt.set_sensitive(fn.check_package_installed("fish-tweak-tool"))
    self.btn_launch_ftt.connect("clicked", functools.partial(shell.on_click_launch_ftt_from_shells, self))
    hbox_ftt_launch.append(self.btn_launch_ftt)

    hbox_ftt_about = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    ftt_about_lbl = Gtk.Label(xalign=0)
    ftt_about_lbl.set_wrap(True)
    ftt_about_lbl.set_margin_start(10)
    ftt_about_lbl.set_margin_end(10)
    ftt_about_lbl.set_margin_top(6)
    ftt_about_lbl.set_markup(
        _("<b>Set up your fish shell in clicks — no config files to edit.</b>\n\n"
        "• <b>Presets</b> — apply a whole look (prompt + plugins + theme + greeting) in one click\n"
        "• <b>Prompts</b> — install Tide, Hydro or Pure, or pick a built-in style (one active at a time)\n"
        "• <b>Plugins</b> — toggle the must-haves via fisher: fzf, autopair, sponge, puffer-fish\n"
        "• <b>Themes</b> — 25 colour themes with a live hover preview and dark / light variants\n"
        "• <b>Settings</b> — greeting (fastfetch or custom), cursor shape, one-click backup &amp; restore\n"
        "• <b>No black box</b> — every change runs in a terminal so you see the exact command\n\n"
        "<i>Your fish config is always backed up before any change.</i>")
    )
    hbox_ftt_about.append(ftt_about_lbl)

    vbox_fish.append(hbox_fish_title)
    vbox_fish.append(hbox_fish_top_sep)
    vbox_fish.append(hbox_fish_installation_title)
    if fn.check_package_installed("fish"):
        vbox_fish.append(hbox_fish_status_lbl)
    vbox_fish.append(hbox_fish_install_btns)
    vbox_fish.append(self.fish_config_section)
    vbox_fish.append(hbox_ftt_title)
    vbox_fish.append(hbox_ftt_status)
    vbox_fish.append(hbox_ftt_btns)
    vbox_fish.append(hbox_ftt_repo_note)
    vbox_fish.append(hbox_ftt_launch)
    vbox_fish.append(hbox_ftt_about)

    # ── Extra tools ──────────────────────────────────────────────────

    hbox_extra_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_extra_controls_lbl = Gtk.Label()
    hbox_extra_controls_lbl.set_markup(
        _("The shell configurations of the ATT contain\
 aliases that require certain applications\n\
\nHere you can select the missing applications and install them\n\
Activate the nemesis repo (when needed) to install all of them\n\n\
Applications that were NOT installed will be <b>unselected</b> again\n\
Activate the necessary repos")
    )
    self.select_all = Gtk.CheckButton(label=_("Select them all"))
    self.select_all.connect("notify::active", functools.partial(shell.on_select_all_toggle, self))
    hbox_extra_controls_lbl.set_margin_top(20)
    hbox_extra_controls_lbl.set_margin_start(10)
    hbox_extra_controls_lbl.set_margin_end(10)
    hbox_extra_controls_lbl.set_hexpand(False)
    hbox_extra_controls.append(hbox_extra_controls_lbl)
    self.select_all.set_margin_start(10)
    self.select_all.set_margin_end(10)
    hbox_extra_controls.append(self.select_all)  # pack_end

    # hbox_bash_title2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    # self.select_all = Gtk.CheckButton(label="Select them all")
    # #hbox_bash_title2.set_margin_top(20)
    # hbox_bash_title2.pack_start(self.select_all, False, False, 10)

    self.expac = Gtk.CheckButton(label="expac")
    self.ripgrep = Gtk.CheckButton(label="ripgrep")
    self.yay = Gtk.CheckButton(label="yay-git")
    self.paru = Gtk.CheckButton(label="paru-git")
    self.bat = Gtk.CheckButton(label="bat")
    self.downgrade = Gtk.CheckButton(label="downgrade")
    self.hw_probe = Gtk.CheckButton(label="hw-probe")
    self.rate_mirrors = Gtk.CheckButton(label="rate-mirrors")
    self.most = Gtk.CheckButton(label="most")
    self.fzf = Gtk.CheckButton(label="fzf")

    flowbox = Gtk.FlowBox()
    flowbox.set_valign(Gtk.Align.START)
    flowbox.set_max_children_per_line(2)
    flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

    flowbox.append(self.expac)
    flowbox.append(self.ripgrep)
    flowbox.append(self.yay)
    flowbox.append(self.paru)
    flowbox.append(self.bat)
    flowbox.append(self.downgrade)
    flowbox.append(self.hw_probe)
    flowbox.append(self.rate_mirrors)
    flowbox.append(self.most)
    flowbox.append(self.fzf)

    extra_shell_applications = Gtk.Button(label=_("Install packages"))
    extra_shell_applications.connect("clicked", functools.partial(shell.on_extra_shell_applications_clicked, self))

    vbox_extra.append(hbox_extra_controls)
    # vbox_extra.pack_start(hbox_bash_title2, False, False, 0)
    vbox_extra.append(flowbox)
    remove_shell_applications = Gtk.Button(label=_("Remove packages"))
    remove_shell_applications.connect(
        "clicked", functools.partial(shell.on_extra_shell_applications_remove_clicked, self)
    )

    hbox_extra_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_extra_btn.set_margin_start(10)
    hbox_extra_btn.append(extra_shell_applications)
    hbox_extra_btn.append(remove_shell_applications)
    vbox_extra.append(hbox_extra_btn)
    # vbox_extra.pack_start(install_only_fish, False, False, 0)

    # ── Alacritty tab ────────────────────────────────────────────────

    vbox_alacritty = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    # ── Alacritty ─────────────────────────────────────────────────

    hbox_alacritty_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_alacritty_title_lbl = Gtk.Label(xalign=0)
    hbox_alacritty_title_lbl.set_markup("<b>Alacritty</b>")
    hbox_alacritty_title_lbl.set_margin_start(10)
    hbox_alacritty_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_alacritty_title_sep.set_hexpand(True)
    hbox_alacritty_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_alacritty_title.append(hbox_alacritty_title_lbl)
    hbox_alacritty_title.append(hbox_alacritty_title_sep)

    hbox_alacritty_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.alacritty_status_lbl = Gtk.Label(xalign=0)
    shell._refresh_alacritty_lbl(self)
    self.alacritty_status_lbl.set_margin_start(10)
    self.alacritty_status_lbl.set_margin_end(10)
    hbox_alacritty_status.append(self.alacritty_status_lbl)

    hbox_alacritty_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_alacritty_btns.set_margin_start(10)
    btn_install_alacritty = Gtk.Button(label=_("Install Alacritty"))
    btn_install_alacritty.connect("clicked", functools.partial(shell.on_install_alacritty_clicked, self))
    btn_remove_alacritty = Gtk.Button(label=_("Remove Alacritty"))
    btn_remove_alacritty.connect("clicked", functools.partial(shell.on_remove_alacritty_clicked, self))
    hbox_alacritty_btns.append(btn_install_alacritty)
    hbox_alacritty_btns.append(btn_remove_alacritty)

    # ── Alacritty Tweak Tool ───────────────────────────────────────

    hbox_att_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_att_title_lbl = Gtk.Label(xalign=0)
    hbox_att_title_lbl.set_markup(_("<b>Alacritty Tweak Tool</b>"))
    hbox_att_title_lbl.set_margin_start(10)
    hbox_att_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_att_title_sep.set_hexpand(True)
    hbox_att_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_att_title.append(hbox_att_title_lbl)
    hbox_att_title.append(hbox_att_title_sep)

    hbox_att_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    self.att_status_lbl = Gtk.Label(xalign=0)
    shell._refresh_att_lbl(self)
    self.att_status_lbl.set_margin_start(10)
    self.att_status_lbl.set_margin_end(10)
    hbox_att_status.append(self.att_status_lbl)

    hbox_att_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_att_btns.set_margin_start(10)
    btn_install_att = Gtk.Button(label=_("Install alacritty-tweak-tool"))
    btn_install_att.connect("clicked", functools.partial(shell.on_install_alacritty_tweak_tool_clicked, self))
    btn_remove_att = Gtk.Button(label=_("Remove alacritty-tweak-tool"))
    btn_remove_att.connect("clicked", functools.partial(shell.on_remove_alacritty_tweak_tool_clicked, self))
    hbox_att_btns.append(btn_install_att)
    hbox_att_btns.append(btn_remove_att)

    hbox_att_repo_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    if not fn.check_nemesis_repo_active():
        att_repo_note_lbl = Gtk.Label(xalign=0)
        att_repo_note_lbl.set_markup(_("<i>Enable the Nemesis repo (Pacman page) to install alacritty-tweak-tool</i>"))
        att_repo_note_lbl.set_margin_start(10)
        att_repo_note_lbl.set_margin_end(10)
        hbox_att_repo_note.append(att_repo_note_lbl)

    # ── Tab previews ──────────────────────────────────────────────

    from gi.repository import Gdk

    hbox_att_preview_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_att_preview_title_lbl = Gtk.Label(xalign=0)
    hbox_att_preview_title_lbl.set_markup(_("<b>Alacritty Tweak Tool - Tab preview</b>"))
    hbox_att_preview_title_lbl.set_margin_start(10)
    hbox_att_preview_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_att_preview_title_sep.set_hexpand(True)
    hbox_att_preview_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_att_preview_title.append(hbox_att_preview_title_lbl)
    hbox_att_preview_title.append(hbox_att_preview_title_sep)

    att_preview_tabs = [
        ("themes", _("Themes")),
        ("appearance", _("Appearance")),
        ("advanced", _("Advanced")),
        ("behavior", _("Behavior")),
        ("creator", _("Creator")),
    ]

    preview_stack = Gtk.Stack()
    preview_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
    preview_stack.set_transition_duration(200)
    preview_stack.set_hexpand(True)

    preview_switcher = Gtk.StackSwitcher()
    preview_switcher.set_stack(preview_stack)
    preview_switcher.set_margin_start(10)
    preview_switcher.set_margin_top(5)

    img_w, img_h = 800, 500
    for key, label in att_preview_tabs:
        img_path = base_dir + f"/alacritty_images/{key}.png"
        if fn.path.isfile(img_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(img_path, img_w, img_h)
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            page_widget = Gtk.Picture.new_for_paintable(texture)
            page_widget.set_content_fit(Gtk.ContentFit.CONTAIN)
        else:
            page_widget = Gtk.Label(label=_("{name} — screenshot coming soon").format(name=label))
            page_widget.set_size_request(img_w, 200)
        preview_stack.add_titled(page_widget, key, label)

    # ── Launch ────────────────────────────────────────────────────

    hbox_att_launch_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_att_launch_title_lbl = Gtk.Label(xalign=0)
    hbox_att_launch_title_lbl.set_markup(_("<b>Launch</b>"))
    hbox_att_launch_title_lbl.set_margin_start(10)
    hbox_att_launch_title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hbox_att_launch_title_sep.set_hexpand(True)
    hbox_att_launch_title_sep.set_valign(Gtk.Align.CENTER)
    hbox_att_launch_title.append(hbox_att_launch_title_lbl)
    hbox_att_launch_title.append(hbox_att_launch_title_sep)

    hbox_alacritty_launch = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_alacritty_launch.set_margin_start(10)
    self.btn_launch_att = Gtk.Button(label=_("Launch Alacritty Tweak Tool"))
    self.btn_launch_att.set_sensitive(fn.check_package_installed("alacritty-tweak-tool"))
    self.btn_launch_att.connect("clicked", functools.partial(shell.on_click_launch_att_from_shells, self))
    hbox_alacritty_launch.append(self.btn_launch_att)

    vbox_alacritty.append(hbox_alacritty_title)
    vbox_alacritty.append(hbox_alacritty_status)
    vbox_alacritty.append(hbox_alacritty_btns)
    vbox_alacritty.append(hbox_att_title)
    vbox_alacritty.append(hbox_att_status)
    vbox_alacritty.append(hbox_att_btns)
    vbox_alacritty.append(hbox_att_repo_note)
    hbox_att_tagline = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    att_tagline_lbl = Gtk.Label(xalign=0)
    att_tagline_lbl.set_text(_("304 themes to choose from or create your own theme with the click of a button"))
    att_tagline_lbl.set_margin_start(10)
    att_tagline_lbl.set_margin_end(10)
    hbox_att_tagline.append(att_tagline_lbl)

    vbox_alacritty.append(hbox_att_launch_title)
    vbox_alacritty.append(hbox_alacritty_launch)
    vbox_alacritty.append(hbox_att_tagline)
    vbox_alacritty.append(hbox_att_preview_title)
    vbox_alacritty.append(preview_switcher)
    vbox_alacritty.append(preview_stack)

    # ── Pack to stack ────────────────────────────────────────────────

    active_shell = fn.get_shell()
    stack.add_titled(vbox_bash, "stack1", _("BASH (active)") if active_shell == "bash" else "BASH")
    stack.add_titled(vbox_zsh, "stack2", _("ZSH (active)") if active_shell == "zsh" else "ZSH")
    stack.add_titled(vbox_fish, "stack3", _("FISH (active)") if active_shell == "fish" else "FISH")
    stack.add_titled(vbox_alacritty, "stack4", "ALACRITTY")
    stack.add_titled(vbox_extra, "stack5", _("EXTRA"))

    vbox.append(stack_switcher)
    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vbox.append(stack)

    vboxstack_shells.append(hbox_shells_title)
    vboxstack_shells.append(hbox_shells_sep)
    vbox.set_hexpand(True)
    vbox.set_vexpand(True)
    vboxstack_shells.append(vbox)

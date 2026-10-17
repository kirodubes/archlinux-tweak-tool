# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

from ast import literal_eval
import functools
import functions as fn
from gi.repository import Gtk, Gio, GdkPixbuf, Gdk


def get_startups(name):
    try:
        with open(fn.autostart + name + ".desktop", encoding="utf-8") as f:
            lines = f.readlines()
        state = True
    except Exception:
        return True

    if fn.check_content("Hidden=", fn.autostart + name + ".desktop"):
        try:
            pos = fn.get_position(lines, "Hidden=")
            state = lines[pos].split("=")[1].strip()

            state = state.capitalize()
            state = not literal_eval(state)
            return state
        except Exception as error:
            fn.log_error(str(error))
            return True
    else:
        return state


def add_autostart(self, name, com, comnt):
    lists = list(fn.listdir(fn.home + "/.config/autostart"))
    if name + ".desktop" not in lists:
        content = (
            "[Desktop Entry]\n\
Encoding=UTF-8\n\
Version=1.0\n\
Type=Application\n\
Name="
            + name
            + "\n\
Comment="
            + comnt
            + "\n\
Exec="
            + com
            + "\n\
TryExec="
            + com
            + "\n\
StartupNotify=false\n\
X-GNOME-Autostart-enabled=true\n\
Terminal=false\n\
Hidden=false\n"
        )

        desktop_file = fn.home + "/.config/autostart/" + name + ".desktop"
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(content)
        # ATT runs as root: without this the user could not edit their own autostart entry
        fn.permissions(desktop_file)
        add_row(self, name)


# ====================================================================
# AUTOSTART CALLBACKS
# ====================================================================


def on_add_entry_changed(self, _widget):
    if len(self.entry_name.get_text()) >= 3 and len(self.entry_command.get_text()) >= 3:
        self.abutton.set_sensitive(True)


def on_auto_toggle(self, widget, data, lbl):
    desktop_file = fn.autostart + lbl + ".desktop"
    active = widget.get_active()
    hidden_value = str(not active).lower()
    fn.log_subsection(f"Toggle Autostart: {lbl}")
    fn.debug_print(f"  File   : {desktop_file}")
    fn.debug_print(f"  Active : {active}")
    fn.debug_print(f"  Hidden : {hidden_value}")
    try:
        with open(desktop_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if fn.check_content("Hidden=", desktop_file):
            pos = fn.get_position(lines, "Hidden=")
            val = lines[pos].split("=")[1].strip()
            lines[pos] = lines[pos].replace(val, hidden_value)
            fn.debug_print(f"  Action : updated Hidden= at line {pos}")
        else:
            lines.append(f"Hidden={hidden_value}\n")
            fn.debug_print(f"  Action : appended Hidden={hidden_value}")
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
        fn.debug_print("  Result : written successfully")
        fn.log_success(f"{lbl} autostart {'enabled' if active else 'disabled'}")
        fn.GLib.idle_add(fn.show_in_app_notification, self, f"{lbl} {'enabled' if active else 'disabled'}")
    except Exception as error:
        fn.debug_print(f"  Result : FAILED - {error}")
        fn.log_error(f"Failed to toggle autostart for {lbl}: {error}")


def on_auto_remove_clicked(self, _gesture_or_widget, listbox, lbl):
    desktop_file = fn.autostart + lbl + ".desktop"
    fn.log_subsection(f"Remove Autostart: {lbl}")
    fn.debug_print(f"  File   : {desktop_file}")
    try:
        fn.unlink(desktop_file)
        fn.debug_print("  Result : removed successfully")
        fn.log_success(f"{lbl} removed from autostart")
        fn.GLib.idle_add(fn.show_in_app_notification, self, f"{lbl} removed from autostart")
        self.vvbox.remove(listbox)
    except Exception as error:
        fn.debug_print(f"  Result : FAILED - {error}")
        fn.log_error(f"Failed to remove {lbl} from autostart: {error}")


def clear_autostart(self):
    child = self.vvbox.get_first_child()
    while child is not None:
        next_child = child.get_next_sibling()
        self.vvbox.remove(child)
        child = next_child


def load_autostart(self, files, base_dir=None):
    clear_autostart(self)

    for x in files:
        add_row(self, x, base_dir)


def add_row(self, x, base_dir=None):
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    vbox_switch = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

    lbl = Gtk.Label(xalign=0)
    lbl.set_text(x)

    swtch = Gtk.Switch()
    swtch.set_active(get_startups(x))
    swtch.connect("notify::active", functools.partial(on_auto_toggle, self, lbl=x))

    listbox = Gtk.ListBox()

    image_path = (
        fn.path.join(base_dir, "images/remove.png")
        if base_dir
        else fn.path.join(fn.path.dirname(__file__), "images/remove.png")
    )
    pbfb = GdkPixbuf.Pixbuf.new_from_file_at_size(image_path, 28, 28)
    texture = Gdk.Texture.new_for_pixbuf(pbfb)
    fbimage = Gtk.Image.new_from_paintable(texture)
    fbimage.set_cursor(Gdk.Cursor.new_from_name("pointer"))
    fbimage.set_tooltip_text("Remove")

    _listbox = listbox
    _text = lbl.get_text()
    fb_gesture = Gtk.GestureClick.new()
    fb_gesture.connect(
        "pressed",
        lambda g, n, x, _y, lb=_listbox, t=_text: on_auto_remove_clicked(self, g, lb, t),
    )
    fbimage.add_controller(fb_gesture)

    lbl.set_hexpand(True)
    hbox.append(lbl)
    swtch.set_margin_top(10)
    swtch.set_margin_bottom(10)
    vbox_switch.append(swtch)
    hbox.append(vbox_switch)
    hbox.append(fbimage)

    vbox_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    hbox.set_margin_top(5)
    hbox.set_margin_bottom(5)
    vbox_row.append(hbox)

    listbox.set_selection_mode(Gtk.SelectionMode.NONE)
    listboxrow = Gtk.ListBoxRow()
    listboxrow.set_child(vbox_row)
    listbox.append(listboxrow)

    self.vvbox.append(listbox)


def on_add_autostart(self, _widget):
    name = self.entry_name.get_text()
    command = self.entry_command.get_text()
    fn.log_subsection("Add Autostart")
    fn.debug_print(f"  Name   : {name}")
    fn.debug_print(f"  Command: {command}")
    if len(name) > 1 and len(command) > 1:
        add_autostart(self, name, command, self.entry_comment.get_text())
        fn.log_success(f"{name} added to autostart")
        fn.GLib.idle_add(fn.show_in_app_notification, self, f"{name} added to autostart")
    else:
        fn.log_info("Name and Command must be at least 2 characters")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "Name and Command must be at least 2 characters")


def on_exec_browse(self, _widget):
    fn.log_subsection("Browse for executable")
    dialog = Gtk.FileChooserDialog(
        title="Please choose a file",
        transient_for=self,
        action=Gtk.FileChooserAction.OPEN,
    )
    dialog.set_select_multiple(False)
    dialog.set_current_folder(Gio.File.new_for_path(fn.home))
    dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
    dialog.add_button("_Open", Gtk.ResponseType.OK)
    dialog.connect("response", lambda d, r: open_response_auto(self, d, r))
    dialog.present()


def open_response_auto(self, dialog, response):
    if response == Gtk.ResponseType.OK:
        files = dialog.get_files()
        if files:
            filepath = files[0].get_path()
            fn.debug_print(f"  File   : {filepath}")
            self.entry_command.set_text(filepath)
        dialog.destroy()
    elif response == Gtk.ResponseType.CANCEL:
        dialog.destroy()


# ====================================================================
# AUTOSTART GUI
# ====================================================================


def gui(self, Gtk, vboxstack_autostart, _fn):
    base_dir = fn.path.dirname(fn.path.realpath(__file__))

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text("Autostart")
    lbl_title.set_name("title")
    hbox_title.append(lbl_title)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_sep.append(hseparator)

    toplabelbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    lbls = Gtk.Label(xalign=0)
    lbls.set_text("This is the current content of ~/.config/autostart/")
    toplabelbox.append(lbls)

    files = [x.replace(".desktop", "") for x in fn.listdir(fn.autostart)]
    mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

    self.vvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    self.vvbox.set_name("vbox")

    scrolled_window.set_child(self.vvbox)
    scrolled_window.set_hexpand(True)
    scrolled_window.set_propagate_natural_height(True)
    mainbox.append(scrolled_window)

    load_autostart(self, files, base_dir)

    hbox_add_label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    lbl_add_manual = Gtk.Label(xalign=0)
    lbl_add_manual.set_markup("<b>Add a manual autostart file</b>")
    lbl_add_manual.set_margin_start(5)
    lbl_add_manual.set_margin_top(10)
    lbl_add_manual.set_margin_bottom(5)
    hbox_add_label.append(lbl_add_manual)

    lbl_name = Gtk.Label(label="Name")
    lbl_command = Gtk.Label(label="Command")
    lbl_comment = Gtk.Label(label="Comment")

    self.entry_name = Gtk.Entry()
    self.entry_command = Gtk.Entry()
    self.entry_comment = Gtk.Entry()
    self.entry_name.set_size_request(180, 0)
    self.entry_command.set_size_request(180, 0)
    self.entry_comment.set_size_request(180, 0)
    self.entry_name.connect("changed", functools.partial(on_add_entry_changed, self))
    self.entry_command.connect("changed", functools.partial(on_add_entry_changed, self))

    bbutton = Gtk.Button(label="...")
    self.abutton = Gtk.Button(label="Add")
    self.abutton.set_size_request(140, 0)
    self.abutton.set_sensitive(False)

    bbutton.connect("clicked", functools.partial(on_exec_browse, self))

    self.abutton.connect("clicked", functools.partial(on_add_autostart, self))

    vbox_name = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    vbox_command = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    vbox_comment = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    vbox_browse = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    vbox_add = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

    vbox_name.append(lbl_name)
    vbox_name.append(self.entry_name)

    vbox_command.append(lbl_command)
    vbox_command.append(self.entry_command)

    vbox_comment.append(lbl_comment)
    vbox_comment.append(self.entry_comment)

    vbox_browse.append(Gtk.Label(label=""))
    vbox_browse.append(bbutton)
    vbox_add.append(Gtk.Label(label=""))
    vbox_add.append(self.abutton)

    hbox_inputs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    vbox_name.set_margin_start(5)
    vbox_name.set_margin_end(5)
    hbox_inputs.append(vbox_name)
    hbox_inputs.append(vbox_command)
    hbox_inputs.append(vbox_browse)
    vbox_comment.set_margin_start(5)
    vbox_comment.set_margin_end(5)
    hbox_inputs.append(vbox_comment)
    vbox_add.set_margin_start(5)
    vbox_add.set_margin_end(5)
    hbox_inputs.append(vbox_add)

    mainbox.set_hexpand(True)
    mainbox.append(hbox_add_label)
    mainbox.append(hbox_inputs)

    vboxstack_autostart.append(hbox_title)
    vboxstack_autostart.append(hbox_sep)
    vboxstack_autostart.append(toplabelbox)
    vboxstack_autostart.append(mainbox)

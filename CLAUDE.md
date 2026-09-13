# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ArchLinux Tweak Tool (ATT) is a GTK4-based Python application for managing Arch-based Linux systems. It provides a graphical interface for system customization, package management, theming, services, and maintenance tasks without requiring command-line expertise.

- **Language**: Python 3.8+
- **GUI Framework**: GTK4 (4.6+)
- **Entry Point**: `usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py`
- **Desktop Launcher**: `usr/share/applications/archlinux-tweak-tool.desktop`
- **Tab count**: 31 active tabs (Accessibility, AI Tools, Arc themes, Autostart, Backup, Celestial themes, Desktop, Desktop - Wayland, Fastfetch, Icons Horst, Icons Neo Candy, Icons Surfn, ISO, Kernels, Locale, Logging, Maintenance, Network, Office, Packages, Pacman, Plymouth, Privacy, Performance, Sddm, Services, Shells, Software, System, Themer, User, Wallpaper) + 1 hidden Dev tab + 1 Kiro-only Streamline page (shown only on Kiro, alphabetically after Software) + 1 conditional Btrfs page (shown only on a btrfs root, alphabetically between Backup and Desktop). Support is no longer a page — the funding channels are reached via the `♥ Support` button in the top header bar (`funding.show_support_dialog`).

## Requirements

**Runtime:**
- Python 3.8 or later
- GTK4 libraries (version 4.6+)
- GObject Introspection (gi)
- Standard library modules: os, sys, subprocess, threading, time, shutil, json

**System Tools:**
- bash (shell execution)
- sudo (elevated operations)
- pacman (package management)
- git (version control)
- ruff (linting, development only)

**For Optional Features:**
- alacritty (terminal for package operations)
- fastfetch (system information display)
- zsh, fish, bash (shell support)
- systemctl (service management)

## Developer Objectives

These are the core principles guiding all development on this project:

1. **Fast Loading Application** - Minimize startup time through lazy-loading of heavy modules
2. **In-App Updating** - Dynamically update dropdown menus and other UI elements without full reloads
3. **Minimal Core** - Keep the main `archlinux-tweak-tool.py` file small and focused on entry point logic
4. **Modular Functions** - Separate general utilities in `functions.py` from task-specific functions
5. **Clear Structure** - Maintain strict feature-based organization (feature.py + feature_gui.py pattern)
6. **Dual Logging** - Provide both in-app notifications and console output for all operations
7. **Safe Package Operations** - Use popup terminal (Alacritty) for installations/removals with "press enter to close" workflow; never combine `alacritty --hold` with `read -p` — use one or the other; ATT preference is `read -p` at the end of the script without `--hold`; never use `subprocess.call()` to launch alacritty from a GUI callback — always use `Popen` in a daemon thread (via `_run_terminal` or equivalent) so ATT stays responsive while the terminal is open
8. **Reliability** - Never crash; handle all errors gracefully with user feedback
9. **Non-Invasive** - Respect user system state; avoid unwanted modifications
10. **User Communication** - Clearly communicate drastic changes through labels and confirmation dialogs before execution
11. **Multi-Distro Scope** - ATT targets all Arch-based systems (Kiro, Artix, Manjaro, etc.); remove Garuda and EndeavourOS *repo and package* references since ATT no longer ships those; keep `fn.distr` detection guards that conditionally show/hide UI to avoid conflicts on specific systems
12. **Data Folder Consolidation** - Transition to Kiro-only data folder; update all paths before removing other distro-specific directories
13. **Remove Dead Code** - Eliminate unused functions, imports, and legacy code left-overs; keep codebase clean and maintainable
14. **Transparency — Never a Black Box** - "What is it doing?" is the central frustration of Windows users; ATT must never reproduce that feeling. Three commitments, always: (a) tell the user what an action *will* do **before** it runs — confirmation dialog or visible label; (b) show what's *happening now* during execution — progress indicators, current step, live console output; (c) report what *was done* afterwards — success summary listing the actual changes (files written, packages installed, services touched). In `--debug` mode show source, target, result for every file operation so nothing happens silently. **Calibrate to the operation's blast radius:** a trivial toggle can flash a quick toast and move on; a multi-step action (package install + config edit + service restart) needs the full transparency treatment (confirm dialog, progress, summary). Don't dialog-spam users for every micro-action; don't silently do big things either. Aligns with the assistant-level transparency principle in [Kiro-HQ/ASSISTANT.md](/home/erik/Insync/Kiro/Kiro-HQ/ASSISTANT.md) — same rule, scale to the audience and the action size.
15. **Teach GTK4 & Python Best Practices** - When implementing or reviewing code, explain the GTK4 and Python patterns being used so the developer builds deeper understanding; link to relevant docs when non-obvious
16. **Consistent Variable Naming** - Use the same naming conventions for variables across all modules: `snake_case` for variables/functions, `PascalCase` for classes; never mix styles within equivalent constructs
17. **No Duplicate Functions** - Before writing any helper or utility function, check `functions.py` and existing modules for an equivalent; reuse and consolidate rather than duplicating logic across pages
18. **Follow GTK4 Best Practices** - Apply current GTK4 idioms: use `Gtk.Builder` for complex layouts, prefer `GObject` signals over direct calls, avoid deprecated GTK3 APIs, and follow GNOME HIG for UX consistency
19. **Teach Effective Claude Usage** - When a task is unclear or too broad, ask the developer to scope it; suggest when a plan-mode session, a sub-agent, or a focused prompt would yield better results; flag when a request risks wasted tokens
20. **Model Selection Guidance** - Recommend switching to Opus when the task requires deep multi-file reasoning, architecture decisions, or security review; stay on Sonnet for routine edits, bug fixes, and single-file changes; use Haiku for fast lookups only
21. **Use Plan Mode for Non-Trivial Work** - Invoke plan mode before any change that touches more than two files, introduces a new pattern, or has irreversible side-effects; present the plan and get confirmation before executing
22. **Project-Driven Development** - Maintain a milestone/deliverable mindset: group related changes into logical milestones, identify what constitutes a shippable/packageable state between milestones, and flag when in-progress work is blocking a release
23. **Lint, Spacing & Comments** - All Python code must pass `ruff check` (PEP 8): 4-space indentation, max line length 120, one blank line between methods, two blank lines between top-level definitions; remove inline comments that only restate a single line of code; keep comments that explain WHY (a constraint, a workaround, a non-obvious invariant); keep section dividers (`# ── Name ──────`) in long functions (50+ lines) where they aid navigation — do not add them to short functions; docstrings follow PEP 257 — public functions/methods/modules should have a one-line docstring, private functions (prefixed `_`) do not require them, never write multi-paragraph docstrings
24. **Maintain CHANGELOG.md Automatically** - After every session that changes code or project structure, update `CHANGELOG.md` without being asked; group entries by date (`YYYY.MM.DD`), use the existing structured layout (What Changed / Technical Details / Files Modified), one entry per day consolidating all changes made that day
25. **Never Change Code Without Explicit Confirmation** - Before any Edit, Write, or file deletion, state exactly what you intend to change and why, then wait for the user to approve. Never add constants, remove functions, or restructure files based on your own judgment alone — always ask first.
26. **UI Layout Consistency** - All pages must use the same layout patterns: section headers use `set_markup("<b>Section Name</b>")` (never `set_text()`); page titles use `set_name("title")` styled via CSS. When adding or editing any page, verify its section labels match this standard and fix any inconsistencies in the same change.
27. **Descriptive Variable Names — No Numbered Boxes** - Never use numbered widget names like `hbox1`, `hbox2`, `vbox3`. When touching any file that has them, rename all occurrences to descriptive names that reflect the content (e.g. `hbox_current_boot`, `hbox_pacman_log`). Rename the container, the label, and every `append()` reference in the same edit — never rename partially.
28. **Mandatory Console Output in Every Touched File** - Every file we touch must contain at least one `fn.log_*` call (`log_section`, `log_subsection`, `log_info`, `log_success`, `log_warn`, or `log_error`) so operations are always visible in the console. When touching a file that has none, add appropriate `log_*` calls to any callbacks or functions that perform user-visible actions before finishing the edit.
29. **ATT Script Standard** - Every bash script in ATT must follow the ATT Script Standard: start with `set -euo pipefail`; define `RESET`/`CYAN`/`GREEN`/`RED`/`YELLOW` via `tput`; define `separator`, `header`, `success`, `info`, `warn`, `error` helper functions; wrap every logical step in a `header` call; use `success`/`info`/`warn`/`error` for all output — never bare `echo`. Reference examples: [usr/bin/fix-sddm-conf](usr/bin/fix-sddm-conf) and [usr/share/archlinux-tweak-tool/data/bin/fix-pacman-databases-and-keys](usr/share/archlinux-tweak-tool/data/bin/fix-pacman-databases-and-keys). When touching any script that does not follow this standard, bring it into compliance in the same edit. **Frozen files — never edit without an explicit file-specific instruction: [usr/bin/archlinux-tweak-tool](usr/bin/archlinux-tweak-tool) and [setup.sh](setup.sh). No ATT Script Standard, no refactoring, no cleanup passes.**

**Generated file — [usr/bin/skell](usr/bin/skell).** This is **not** authored here and is **exempt from the ATT Script Standard**. It is a verbatim copy of `kiro-skell` from the `edu-system-files` repo, pulled by [fetch-configs.sh](fetch-configs.sh) (run by `up.sh`) — the single source of truth. It deliberately uses the `kiro-common.sh`-style inline helpers, not ATT's `header`/`separator`/`info` helpers, because the same script also ships on Kiro as `kiro-skell`. Do not hand-edit it and do not convert it to the ATT Script Standard — edit `kiro-skell` in `edu-system-files`, then re-run `fetch-configs.sh`. (It is self-contained — no `kiro-common.sh` dependency — so it runs on the non-Kiro distros ATT targets.)

## UI Vocabulary

| Term     | Meaning                   | Examples                                     |
|----------|---------------------------|----------------------------------------------|
| **Page** | Top-level sidebar entry   | Plymouth, Services, SDDM, Kernels, Packages  |
| **Tab**  | Sub-section inside a page | Audio, Bluetooth, Printing (inside Services) |

Always use "page" for sidebar items and "tab" only for sub-sections within a page — in code comments, docs, conversation, and the Dev diagnostics UI.

## Architecture

### Module Organization

The codebase follows a **feature-based module pattern** with a clear separation between logic and UI:

```text
usr/share/archlinux-tweak-tool/
├── archlinux-tweak-tool.py       # Main entry point, GTK application setup
├── functions.py                   # Central utility module (logging, subprocess, helpers)
├── gui.py                         # Main GUI container that imports all *_gui modules
├── <feature>.py                   # Business logic: icons.py, themes.py, desktopr.py, etc.
├── <feature>_gui.py              # Corresponding GUI: icons_gui.py, themes_gui.py, etc.
├── <feature>_callbacks.py         # Optional: isolated callback handlers (log_callbacks.py)
├── data/                          # System config templates and standalone scripts
│   ├── bin/                       # Standalone bash scripts launched via terminal
│   ├── chaotic/                   # Chaotic-AUR repo config
│   ├── fastfetch/                 # Fastfetch config templates
│   ├── packages/                  # Package lists
│   ├── pacman/                    # Pacman config templates
│   ├── sddm/                      # SDDM theme and config files
│   └── wallpaper/                 # Default wallpaper assets
└── images/                        # Application assets
```

### Key Modules

| Module                                  | Purpose                                                                                                                                    |
|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **functions.py**                        | Central utilities: logging (log_error, log_success, log_section), subprocess operations, file I/O, GTK helpers                             |
| **gui.py**                              | Main GUI container; imports and instantiates all *_gui modules                                                                             |
| **accessibility.py / accessibility_gui.py** | Assistive tools (Orca/Onboard/KMag), high-contrast themes, live X11 AccessX toggles (sticky/slow/bounce/mouse keys via xkbset)         |
| **icons.py / icons_gui.py**             | Icon theme management                                                                                                                      |
| **themes.py / themes_gui.py**           | GTK theme management; also owns the shared `/etc/environment` helpers (`apply_env_theme_from`, `build_env_theme_row`, `make_swatch`)       |
| **celestial.py / celestial_gui.py**     | Celestial GTK theme packages from nemesis_repo, grouped by colour family with accent swatches                                               |
| **desktopr.py / desktopr_gui.py**       | Desktop/wallpaper configuration                                                                                                            |
| **sddm.py / sddm_gui.py**               | SDDM login manager configuration                                                                                                           |
| **maintenance.py / maintenance_gui.py** | System cleanup, orphan packages, mirrors                                                                                                   |
| **performance.py / performance_gui.py** | System optimization settings                                                                                                               |
| **services.py / services_gui.py**       | systemd service management                                                                                                                 |
| **packages.py / packages_gui.py**       | Package import/export/installation                                                                                                         |
| **shell.py / shell_gui.py**             | Shell configuration and switching                                                                                                          |
| **user.py / user_gui.py**               | User account creation/management                                                                                                           |
| **fastfetch.py / fastfetch_gui.py**     | System information display configuration                                                                                                   |
| **support.py**                          | Distro detection and support utilities                                                                                                     |
| **settings.py**                         | Application settings                                                                                                                       |
| **functions_backup.py**                 | GTK config backup: copies user's GTK 3/4 config to `/root/.config` so ATT (running as root) respects the desktop theme — called at startup |
| **functions_startup.py**                | Startup init: checks pacman repo toggles and SDDM config asynchronously via `init_repos_and_sddm()` — called in `_finish_startup_init()`   |
| **functions_makedir.py**                | Directory creation: ensures `/root/.config` and all ATT user config dirs exist at startup                                                  |
| **functions_sddm.py**                   | SDDM-specific config setup (`setup_sddm_config()`): must only run on explicit user action on the SDDM page — never at startup              |

### Styling

`icons.css` (in `usr/share/archlinux-tweak-tool/`) is the sole application stylesheet, loaded at startup via `Gtk.CssProvider`. It controls sidebar label appearance, page title styling (`#title`), and icon-related layout. There is no `att.css` — any reference to it in older notes means `icons.css`.

### Reference Documents (repo root)

| File                      | Purpose                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------|
| **DISTRO_GUARDS.md**      | Documents every `fn.distr` guard in the codebase — which pages are hidden on which distros and why |
| **audit_log_coverage.py** | Dev script that scans all `*_gui.py` modules and reports any that lack `fn.log_*` calls            |

### Startup Flow

1. `archlinux-tweak-tool.py` creates the main `Gtk.Application`
2. Early imports: functions, support, utilities, desktopr_gui (splash screen)
3. GUI window created with fast display
4. **Heavy modules lazy-loaded** in `_finish_startup_init()` to keep startup time low:
   - zsh_theme, user, themer, settings, services, sddm, pacman_functions, fastfetch, maintenance, icons, themes, desktopr, autostart, packages, and all GUI modules
5. Splash screen hidden after initialization complete

## Development Patterns

### Logging & Output

All user-facing output uses **functions.py logging functions** (never `print()`):

```python
import functions as fn

fn.debug_print(message)              # Debug-only output (with --debug flag)
fn.log_section("Major Header")       # Green section header with separators
fn.log_subsection("Minor Header")    # Cyan subsection header
fn.log_info("Informational")         # Blue info message
fn.log_success("Success message")    # Green success with separators
fn.log_warn("Warning message")       # Yellow warning with separators
fn.log_error("Error message", lineno=X, cmd="command")  # Red error with details
```

### GTK4 Callbacks

All GTK button/widget callbacks **must include a `_widget` parameter** as the second argument (after `self`):

```python
def on_button_click(self, _widget):  # Note: _widget parameter
    fn.log_success("Button clicked")
```

This is required even if the widget parameter is unused. Recent GTK4 API changes require this signature.

### Markup & Special Characters

In GTK `set_markup()` calls, **ampersands must be escaped as `&amp;`** or the label silently renders nothing:

```python
# Correct
label.set_markup("Set <b>&amp;</b> configure")

# Wrong - will render as empty
label.set_markup("Set <b>&</b> configure")
```

### Async Operations

For long-running operations that could freeze the UI, use `GLib.idle_add()` to defer execution:

```python
from gi.repository import GLib

GLib.idle_add(expensive_function, priority=GLib.PRIORITY_LOW)
```

Recent fixes: thumbnail loading, file operations that previously blocked the UI.

### Terminal Actions — wait_and_refresh Pattern

When a button launches an alacritty terminal (install/remove package) and a label or button must update afterward, **always use `wait_and_refresh` in a daemon thread**. Never use a fixed timeout (`GLib.timeout_add`) — the terminal takes longer than any hardcoded delay.

The subprocess function must `return` the `Popen` object so the thread can wait on it:

```python
# In pacman_functions.py — always return the process
def install_something(self):
    fn.log_subsection("Installing something...")
    fn.show_in_app_notification(self, "Opening terminal...")
    return fn.subprocess.Popen(
        ["alacritty", "--hold", "-e", "bash", "-c", "sudo pacman -S something"],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

# In the GUI — wait for terminal close, then refresh
def wait_and_refresh(process):
    if process is None:
        fn.GLib.idle_add(refresh_labels)
        return
    fn.debug_print("Waiting for terminal to close...")
    process.wait()
    fn.debug_print("Terminal closed — refreshing labels")
    fn.GLib.idle_add(refresh_labels)

btn.connect(
    "clicked",
    lambda w: fn.threading.Thread(
        target=wait_and_refresh,
        args=(install_something(self),),
        daemon=True,
    ).start(),
)
```

### Dialog Patterns

- **File Dialogs**: Use `.connect()` + `.present()` pattern instead of `.run()`
  - Set `transient_for=self.window` for proper modality
  - Avoid deprecated GTK3 patterns like `GTK_RESPONSE_OK`, use `Gtk.ResponseType.OK`
- **Message Dialogs**: Connect to response signal; track explicit user selections rather than relying on return values

### Subprocess Management

Call system commands via `fn.subprocess_call()` or `fn.subprocess_run()` with proper error handling:

```python
result = fn.subprocess_run(["pacman", "-Sy"], check=True)
fn.subprocess_call("pacman -S package", shell=True)  # For shell syntax
```

Always log results and errors using the logging functions above.

### Package/System Operations

- **Pacman calls** must be wrapped with appropriate exception handling
- Use `fn.install_package(self, "package_name")` for interactive installation
- Network operations that could fail: retry logic and user feedback
- **Know the orphan cascade bug** (memory: Orphan Removal Bug): `pacman -Rns $(pacman -Qdtq)` can cascade-remove unrelated packages after uninstalling a dependency. Always verify operation scope first.

### User Config Directory Layout

ATT writes all user-facing data under `~/.config/archlinux-tweak-tool/` using the real user's home (via `fn.home`, never root's `~`). Every directory is created at startup by `functions_makedir.py` with `fn.permissions()` called so the user owns it.

| Directory           | Constant              | Purpose                                                                                           |
|---------------------|-----------------------|---------------------------------------------------------------------------------------------------|
| `desktop_history/`  | `fn.att_log_dir`      | Package snapshots (`pacman -Q`) written on every Desktop page action (install/remove/set default) |
| `packages/`         | `fn.att_packages_dir` | Exported package lists and install-status logs from the Packages page                             |
| `logging_sessions/` | `fn.att_sessions_dir` | ATT console session logs written at startup by `init_session_log()`                               |
| `streamline/`       | `fn.att_streamline_dir` | Saved Streamline debloat profiles (newline package lists) exported from the Streamline page    |

**Rules:**

- Never write ATT-generated files to `/var/log/` or any system path — keep everything in this config tree
- Always call `fn.permissions(path)` after creating any file or directory here so root does not own it
- New subdirectories follow the same pattern: add a constant to `functions.py`, a creation block to `functions_makedir.py`, and document it in this table

### File Operations

- Create backup files with `.bak` extension before modifying system config
- Use `shutil.copy()` for backups, not manual subprocess calls
- Always handle file not found gracefully
- Use absolute paths; avoid assumptions about working directory

## Common Tasks

### Running the Application

```bash
# Direct execution (requires sudo for system operations)
sudo python3 usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py

# Via desktop launcher (handles pkexec automatically)
archlinux-tweak-tool

# With debug output
sudo python3 usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py --debug
```

### Adding a New Feature

1. Create `<feature>.py` with business logic
2. Create `<feature>_gui.py` with GTK interface that imports from `<feature>.py`
3. Add callbacks in `<feature>_gui.py` or isolated `<feature>_callbacks.py` if complex
4. Import the `<feature>_gui` module in `gui.py` and call its GUI function
5. Follow the logging and callback patterns above
6. Test widget layout, async operations, and error handling

### Updating Data Files

Configuration files and scripts live in `usr/share/archlinux-tweak-tool/data/` in a flat topic-based structure (no distro subdirs). Use `up.sh` to pull/push updates and regenerate `nemesis_packages.txt`.

### Debugging

Use the `--debug` flag to enable `fn.debug_print()` output:

```bash
sudo python3 usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py --debug
```

Debug output includes D-Bus warnings, initialization steps, and custom debug messages.

### Dev Mode — hiding WIP/experimental UI

Use the `--dev` flag to show UI elements that are experimental or not ready for general users:

```bash
sudo python3 usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py --dev
```

Guard any WIP widget's **append call** (not its construction) with `if fn.DEV:` so the widget is still built and `self.*` attributes exist — only the visibility is gated. Pattern:

```python
if fn.DEV:
    vboxstack_page.append(hbox_experimental)
```

## Known Issues & Workarounds

- **GTK FileChooser**: Use `.connect("response")` + `.present()` instead of `.run()` (blocking deprecated)
- **FlowBox clearing**: Use `get_first_child()` + `remove()` in a loop, not deprecated `get_model()`
- **Ampersand in markup**: Always escape as `&amp;` in `set_markup()` calls
- **Double initialization**: Set initializing flag **before** first `set_active()` calls to suppress spurious logging
- **SDDM X11 display server**: Add `DisplayServer=x11` under `[General]` in `/etc/sddm.conf` (or a drop-in under `/etc/sddm.conf.d/`) to force X11 session

## Recent Work

- **Wayland WM picker, paired as Desktop / Desktop - Wayland (2026-06-29)** — a new Wayland WM picker page **"Desktop - Wayland"** is registered **adjacently** after the existing **"Desktop"** page in `gui.py` (sidebar is add-order, so they group) — surfacing the Wayland line as a first-class sibling instead of burying it at the alphabet's end. The broad page keeps the plain **"Desktop"** label (NOT "X11"): it installs Wayland-default DEs too (Plasma is Wayland-only on Kiro), so an "X11" label would be wrong. Stack IDs unchanged (`stack12`, `stack_wayland`). The picker lists all seven now-coexisting WMs (hyprland/niri/sway/river/wayfire/labwc/dwl) but **only Hyprland is selectable** — curated via the `kiro-hyprland` meta (config + full dep stack), seeding `~/.config/hypr|waybar|mako` from `/etc/skel`. niri/sway/river/wayfire/labwc are **disabled placeholders** ("no Kiro config yet") and dwl a disabled "AUR — coming soon" row — visible but not yet selectable (`set_sensitive(False)` for any `ready=False` entry), pending curated configs. New feature pair `wayland.py` (`WAYLAND_WMS` list + `install_wayland_selection()`, a multi-select wrapper that mirrors `desktopr.install_desktop`: union packages → one scoped backup → one `pkexec pacman` terminal → seed skel for curated WMs; reuses `desktopr.check_desktop`/`copy`, `fn.copy_func`/`permissions`/`makedirs`) + `wayland_gui.py` (`CheckButton` rows à la `icons_gui.py`, page skeleton à la `office_gui.py`, Hyprland preview image, nemesis_repo guard greying the Install button). **Remove selected** button (parity with Desktop page): `remove_wayland_selection` removes only Hyprland-specific pkgs (kiro-hyprland/hyprland-tweak-tool/hyprland/hyprlock/hypridle/hyprpicker/xdg-desktop-portal-hyprland — HTT included because it `Depends On: hyprland`, else `-R` fails) via plain `pacman -R` (no `-s` cascade) — shared tools kept so XFCE/chadwm aren't damaged; `~/.config` left intact; refuses to remove the running session (`pgrep -x`); sensitive only when an installed removable WM is selected. `gui.py` wires the import/vbox/deferred-builder/`add_titled`. `search_synonyms.json` gains a Wayland entry; `search_index.json` regenerated. X11 stays default — additive/opt-in.
- **New Icons Horst page (2026-06-24)** — single sidebar page in its **alphabetical** slot (between Fastfetch and Icons Neo Candy), mixing **both** colour sets: two sub-tabs **Surfn Horst** + **Neo Candy Horst**. The two existing per-set pages (Icons Surfn / Icons Neo Candy) keep their own pages; Horst variants are pulled out of "Other" into a dedicated **Horst** family. `gen-icons-list.py` gains `"Horst"` in `FAMILY_ORDER` + a `rest.startswith("horst")` classify branch (matches the 14 `surfn-horst-*` / 14 `neo-candy-horst-*` repos in `~/EDU`). `icons.py` gets `HORST_TABS` (list of `(title, set_key, [families])` since the page mixes set_keys). `icons_gui.py` refactored: extracted `_new_icon_stack()` scaffold + `_init_checks()` (hasattr-guarded so the Horst page and per-set pages can **share** a set's checkbox dict — a token only ever appears on one page), added `_build_horst_page()` + `gui_horst()`. `gui.py` adds `vboxstack_icons_horst`, a deferred builder, and the `add_titled` between Fastfetch and Icons Neo Candy. `search_synonyms.json` gains an Icons Horst entry; `surfn_families.json`/`neocandy_families.json`, thumbnails, and `search_index.json` regenerated.
- **New Accessibility page (2026-06-12)** — sidebar page placed **first** (alphabetically, above AI Tools). Three sections: (1) **Assistive tools** — Launch/Install + Remove rows for Orca / Onboard / KMag (all in `extra`); (2) **High contrast & large text** — installs `gnome-themes-extra` + "Open Themer" button (`self.att_stack` added in `gui.py` so the page can jump to Themer "stack11"); (3) **Keyboard accessibility (X11)** — Sticky/Slow/Bounce/Mouse Keys `Gtk.Switch` toggles applied **live** via `xkbset` and persisted to `~/.config/autostart/att-accessx.desktop`, each row showing its exact selectable `xkbset` line, plus a "What these do" legend. `accessibility.py` mirrors `office.py`; AccessX runs as the real user via `sudo -E -u <user>`. Switches disable with a tooltip when `get_aur_helper()` is `None` and xkbset is absent (xkbset is AUR-only). `_on_accessx_toggled` takes 6 params (`notify::active` appends `(widget, pspec)` to the 4 partial args). `search_synonyms.json` gains an Accessibility entry.
- **New Backup page (2026-06-12)** — always-shown sidebar page (alphabetically between Autostart and Btrfs) for **personal-file** backup. Informational-first: explains why personal-file backup differs from Timeshift/Snapper (system snapshots on the same disk ≠ a copy on another disk/machine), hints at off-site/cloud via BorgBackup over SSH and the 3-2-1 rule, then offers **Pika Backup** and **Vorta** with Launch/Install + Remove rows and a "use either" recommendation. `backup.py` mirrors `office.py` (install_or_launch / remove / daemon-thread wait); `backup_gui.py` mirrors `office_gui.py` (_build_row/_refresh) + `btrfs_gui.py` (info sections). No `fn.distr` guard — both packages are in Arch `extra`. `search_synonyms.json` gains a Backup entry (borg, pika, vorta, cloud, off-site, 3-2-1…); `search_index.json` regenerated.
- **Plasma one-way install enforcement (2026-05-20)** — Plasma removal blocked entirely in `on_uninstall_clicked` (early-return + `log_warn` + notification); Remove button greyed out with tooltip via `update_button_state` (with `hasattr` guard — button assigned after the function's first call during `gui()` build); `on_install_clicked` shows `Gtk.MessageDialog` (WARNING, Yes/No, nested `GLib.MainLoop`) before proceeding; `#FFA500` warning label (`set_visible` toggle) appears centered above Install button on Plasma select, collapses on other selections; notification fires simultaneously
- **Bug scan + cleanup (2026-05-20)** — systematic scan confirmed: all 176 threads have `daemon=True`, no blocking alacritty calls, no unescaped `&`, no numbered widgets, all map-signal bugs fixed; `system.py` 3x `time.sleep()` removed + `import time` dropped; all 14 `data/bin/` scripts gained `trap 'error "Command failed at line $LINENO"' ERR` after `error()` definition (inserted via Python to avoid sed quoting issues)
- **Bluetooth auto-connect + deferred-tab refresh bug sweep (2026-05-19)** — Bluetooth tab gets Auto-Connect section: `AutoEnable` switch writes `/etc/bluetooth/main.conf [Policy]`, `bluetooth-autoconnect` row installs+enables / disables+removes; deferred-tab map-signal bug fixed in services, network, performance, privacy, wallpaper, themer — `_refresh` must be called immediately at build time in addition to connecting to `map`; hblock now backs up `/etc/hosts-bak` before enabling and restores it on package remove
- **Code simplification: status label init deduplication (2026-05-18)** — `shell_gui.py` Alacritty and ATT status label init replaced duplicated if/else blocks with calls to existing `_refresh_alacritty_lbl`/`_refresh_att_lbl` helpers; `setup.sh` missing EOF newline fixed; pattern: refresh helpers should always be called at init time, not duplicated inline
- **Dev page to top + Safeguards section (2026-05-16)** — Dev page moved to first position in sidebar; Safeguards grid section added to Dev page showing all six distro guards evaluated live (Plymouth/SDDM page visibility, kernel hook, visudo, omarchy marker); Login Manager split into plasma-login + plasmalogin rows; DISTRO_GUARDS.md overhauled (Page Visibility Guards renamed, default theme entries moved to Protected Functionality, omarchy marker updated to att_settings.json); UI vocabulary Page vs Tab established in CLAUDE.md and memory
- **Full codebase review pass complete (2026-05-15)** — all 24 tabs reviewed; docstrings added/fixed throughout (PEP 257: public one-line, private none, no multi-paragraph); `# ====` banners converted to `# ──` style; page titles use `set_text()` + `set_name("title")`; `vboxstack` params and local widgets renamed from numbered to descriptive; `_widget` convention enforced; `review.md` all 24 tabs ticked
- **SDDM available themes: sort by AUR last-updated (2026-05-14)** — `fetch_aur_pkg_modified(packages)` added to `sddm.py`; queries AUR RPC v5 `/info` for all listed packages in one HTTP call; "Sort by recently updated (AUR)" switch in `sddm_gui.py` fetches lazily on first toggle and caches in closure; re-sorts dropdown newest-first; repo packages without AUR metadata fall to bottom
- **Plymouth page: dracut support (2026-05-14)** — `plymouth.is_dracut()` + `check_dracut_plymouth_enabled()` added; Install Plymouth, hook-warning fix button, Apply theme, and Reset all branch on dracut and use `dracut --regenerate-all --force` instead of `mkinitcpio -P`; hooks-order warning hidden on dracut; Early KMS section becomes informational note on dracut (pointing at `/etc/dracut.conf.d/`); fix-button writes `/etc/dracut.conf.d/att-plymouth.conf` when plymouth module is not active; verified on hardware (2026-05-16)
- **Dracut support in Kernel Manager (2026-05-14)** — `is_dracut()` + `run_dracut()` added to `kernel.py`; wired into all 5 install/remove callbacks after `run_grub_update()`; "Dracut — Initramfs Generator" GUI section with Regenerate All Initramfs button (shown only on dracut systems); Garuda entry in `kernel_distros.py` requiring `garuda-dracut-support`; verified on hardware (2026-05-16)
- **Fastfetch switch toggle: repo-aware package selection (2026-05-14)** — `on_fast_util_toggled` was hardcoded to `fastfetch-git`; now applies `check_chaotic_aur_active() or check_nemesis_repo_active()` and falls back to `fastfetch` when neither AUR repo is active — matches logic already in `on_install_fast`
- **SDDM theme dropdown + leftover dir cleanup (2026-05-12)** — `on_click_remove_simplicity` now deletes `/usr/share/sddm/themes/edu-simplicity` if pacman left it behind (happens when user applied a custom wallpaper); `pop_theme_box` moved to end of `refresh()` so dropdown always reflects filesystem
- **Plymouth: flat single page + bootloader integration (2026-05-11)** — removed show/hide wrappers; four always-visible sections; Bootloader Integration detects systemd-boot/GRUB/limine/refind; systemd-boot scans 5 ESP path variants (incl. `/boot/efi/` for Kiro); GRUB fix runs grub-mkconfig in terminal; HOOKS order warning; trap EXIT keeps terminal open on error; "Installed" label next to button; no green on status labels
- **Plymouth: distro-agnostic + per-distro reset default (2026-05-11)** — tab gated on `fn.check_package_installed("plymouth")`; `_default_theme` dict in `plymouth_gui.py` maps distro→default theme (omarchy, cachyos, prismlinux); reset button hidden on unknown distros; marker write Omarchy-only
- **SDDM tab: service-enabled guard (2026-05-11)** — `_hide_sddm` removed; replaced with `if not fn.check_service_enabled("plasma-login"):`; `fn.DEV` bypass removed; `check_service_enabled()` added to `functions.py` using `systemctl is-enabled`
- **SDDM tab guard: CachyOS+Plasma+plasma-login-manager+plasmalogin (2026-05-10)** — replaced `fn.distr != "cachyos"` with a 4-AND boolean; `--dev` still forces tab visible
- **Wallpaper: XFCE detection + xfconf-query D-Bus fix (2026-05-05)** — `_get_user_env()` reads session env from `/proc/<pid>/environ`; `_set_xfce()` runs xfconf-query as real user via `sudo -u` + D-Bus prefix; `--create` flag replaces two-step set; confirmed working on hardware (2026-05-16)
- **Shell tab: active shell indicator (2026-05-05)** — stack switcher tab for the active shell now shows "(active)"; derived from `fn.get_shell()` at GUI build time
- **Omarchy added (2026-05-05)** — startup banner updated; `DISTRO_TESTING.md` entry added (3.7.0-2); detection was already in `functions.py`
- **SDDM theme dropdown refresh (2026-05-04)** — `pop_theme_box` called inside `refresh()` after install/remove of edu-simplicity; dropdown now updates without restart
- **Kernel tab: chaotic-AUR dynamic refresh (2026-05-04)** — kernel rows rebuilt on tab map signal when chaotic status changes; no restart needed
- **Kernel tab: boot entry enrichment (2026-05-04)** — dropdown shows `title — kernel_pkg`; orphan entries filtered; `lbl_current` uses enriched string
- **M4 Feature Test complete (2026-05-03)** — all 20 tabs verified working on Kiro
- **fastfetch_gui.py cleanup (2026-05-03)** — all numbered widget names replaced with descriptive identifiers; dead `self.hbox26` and empty spacer `hbox22` removed
- **Lolcat install fix (2026-05-03)** — `on_fast_lolcat_toggled` now installs `lolcat` package via terminal if missing; previously only wrote shell config with no install
- Widget renaming pass (objective 27) — all numbered hbox/vbox names replaced with descriptive identifiers across 10+ GUI files
- Section header markup consistency (objective 26) — all pages now use `set_markup("<b>...</b>")` for section headers
- Fastfetch remove button implemented + `set_fastfetch_ui_sensitive()` for install-state control
- Kernel: boot entry title parsing fixed; non-systemd-boot fallback message added
- Desktopr: `refresh_installed_desktops()` added; called after install/remove
- Autostart: layout fix — add-entry controls moved inside mainbox
- Audio scripts migrated to `data/bin/` standalone scripts
- SDDM user context bug fixed (`fn.sudo_username` instead of `os.getenv`)

Check git log for full implementation details.

## Workflow

### Multi-Machine Development

ATT is developed across multiple machines (Kiro as primary; Omarchy, CachyOS, and other Arch-based distros as secondary). Rules:

- Always `git pull` before starting any session — never assume the working tree is current
- CHANGELOG.md, CLAUDE.md, and IDEAS.md are the most likely merge-conflict files; when conflicts occur, preserve all content from both sides — never discard either machine's entries
- Same-date CHANGELOG entries from two machines must be consolidated into one entry for that date
- CLAUDE.md "Recent Work" section: keep the union of both machines' entries, newest-first
- Code files (.py, .sh) should not conflict if machines work on separate features; if they do, read both sides with `git diff` before resolving — never blindly accept either

### Session Start Checklist

Every session, before writing a single line of code:

1. State the milestone and task: "Working on M2 — clearing arco refs in `shell_gui.py`"
2. `git status` — confirm clean working tree from last session
3. `git log --oneline -5` — remind yourself where you left off
4. If touching more than 2 files → enter plan mode first

### Session End Checklist

Before closing:

1. Run the app and confirm it still launches without errors
2. Sync memory to repo: `cp ~/.claude/projects/-home-erik-KIRO-archlinux-tweak-tool/memory/*.md .claude/memory/`
3. Sync best practices to repo: `sed -e 's|linux-lqx|<package>|g' -e 's|/home/erik/\.bin/[^ ]*|~/.bin/<your-script>|g' -e 's|erikdubois/[^ ]*|<owner>/<repo>|g' ~/.claude/best_practices.md > BEST_PRACTICES.md`
4. If a distro was tested this session, update `DISTRO_TESTING.md` with the result
5. `git add` specific files (never `git add .` — avoid accidentally staging `.env` or large binaries)
6. Commit with a clear message: `feat(shell): migrate shell_gui to Kiro paths`
7. One-line note: what was done, what is next

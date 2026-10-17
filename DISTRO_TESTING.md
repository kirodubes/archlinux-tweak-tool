# ATT Distro Testing

This file tracks compatibility testing of ArchLinux Tweak Tool (ATT) across supported Arch-based distributions. Each distro is tested against the full tab set to verify all features work without crashes or broken paths.

| Distro     | Version                       | Website                                                                                                  |
|------------|-------------------------------|----------------------------------------------------------------------------------------------------------|
| Kiro       | v26.05.01.01                  | <a href="https://sourceforge.net/projects/kiro/files/" target="_blank">sourceforge.net/projects/kiro</a> |
| Arch Linux | 2026.05.01                    | <a href="https://archlinux.org" target="_blank">archlinux.org</a>                                        |
| Omarchy    | 3.7.0-2                       | <a href="https://omarchy.org" target="_blank">omarchy.org</a>                                            |
| Nyarch     | 26.04 (KDE)                   | <a href="https://nyarchlinux.moe" target="_blank">nyarchlinux.moe</a>                                    |
| CachyOS    | 260426 (desktop)              | <a href="https://cachyos.org" target="_blank">cachyos.org</a>                                            |
| PrismLinux | 2026.05.05 (desktop)          | <a href="https://prismlinux.org" target="_blank">prismlinux.org</a>                                      |
| Garuda     | garuda-mokka linux zen 260309 | <a href="https://garudalinux.org" target="_blank">garudalinux.org</a>                                    |
| Archcraft  |                               | <a href="https://archcraft.io" target="_blank">archcraft.io</a>                                          |

## How to test — `att-check`

On the system under test, as your normal user (not root), run:

```bash
att-check              # installed package: /usr/bin/att-check
python3 usr/bin/att-check   # or straight from a git checkout
```

It walks every ATT page in sidebar order (except the developer-only Dev page) and gives each a verdict:

| Verdict | Meaning |
|---------|---------|
| PASS    | Every prerequisite is met: packages obtainable, tools and files present |
| WARN    | The page works, but some items are not obtainable (e.g. packages that need nemesis_repo or chaotic-aur), or an optional probe failed |
| FAIL    | A hard requirement is missing (e.g. no systemd, no bootloader tool), none of the page's packages are obtainable, or the page is UNMAPPED in the checker |
| UNCHECKED | The page has nothing statically checkable (no install calls or probes), so no claim is made |
| HIDDEN  | ATT hides the page on this system (distro guard, Kiro-only, plasma-login enabled) |
| (dim note) | The page does not apply here and is expected to (Btrfs on the default ext4 root): one quiet line, no verdict, left out of the summary |

It is a **static preflight**: it reads the enabled sync DBs (no `pacman -Sy`), probes tools and paths, and never
changes the system. It proves the prerequisites are there, not that every apply succeeds. It writes
`/tmp/att-check-<distro>-<YYYY.MM.DD>.md` (skip with `--no-report`); the report holds no hostname,
username or IPs, so it is safe to paste here. `--verbose` lists every package and probe, plus how many installs pick their package at runtime (from the page's
list or the user's choice); the exit code is 1 when any
page FAILs.


## Live test — developer only, test machines only

`att-check` never presses a button. [tests/run-live-att.sh](tests/run-live-att.sh) does: it opens the real window of
the **installed** ATT, drives a batch of pages and reads every change back. It is not shipped in the package
(the PKGBUILD copies only `usr/`) and it **changes the machine it runs on**, so it refuses to start unless
`/etc/att-live-test-box` exists. Create that file by hand on throwaway test boxes only.

```bash
sudo touch /etc/att-live-test-box   # once, on the test box
bash tests/run-live-att.sh          # as your normal user, while logged in to a desktop session
```

It runs from a terminal in the session or over SSH (it finds the Wayland socket or X display itself), and:

1. backs up `~/.config/autostart`, `~/.config/fastfetch`, `~/.config/fish`, `~/.bashrc`, `~/.zshrc`, `~/.fehbg`
   and the running wallpaper;
2. starts ATT as root with `PKEXEC_UID`, the way the launcher does, and runs [tests/live_att.py](tests/live_att.py):
   - **page-build sweep**: shows every page, no buttons pressed: each must build without a crash, error or dialog;
   - **Autostart**: add a test entry, toggle it off and on, remove it;
   - **Fastfetch**: Reset to ATT defaults, presets Small and All, Reset from backup (skipped without fastfetch);
   - **Shells**: apply the ATT bash (and fish, when installed) config, then Reset;
   - **Wallpaper**: apply an image from the ATT wallpaper folder;
3. reports every **root-owned file ATT left in the home folder**, then restores the backup.

Nothing installs, removes or opens a terminal: any pacman install/remove, AUR helper, terminal or
`systemctl enable/start` call is blocked and reported as a FAIL. Results go to `/tmp/att-live/report.json`
with screenshots in `/tmp/att-live/shots/`; the exit code is 1 on any FAIL. If a run is interrupted before its
restore, `bash tests/run-live-att.sh --restore` puts the backup back (a new run refuses to start until then).
To test a checkout before packaging it, point `ATT_LIVE_APP_DIR` at its `usr/share/archlinux-tweak-tool`. A FAIL is a finding about ATT, not
about the test.

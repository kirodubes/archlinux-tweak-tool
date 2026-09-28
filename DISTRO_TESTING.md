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
`att-check-<distro>-<YYYY.MM.DD>.md` to the current directory (skip with `--no-report`); the report holds no hostname,
username or IPs, so it is safe to paste here. `--verbose` lists every package and probe, plus how many installs pick their package at runtime (from the page's
list or the user's choice); the exit code is 1 when any
page FAILs.


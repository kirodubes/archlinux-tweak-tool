# DISTRO_GUARDS.md

Single source of truth for all distro-conditional logic in ATT.
Update this file whenever a guard is added, removed, or changed.

**Purpose of guards:** Prevent ATT from breaking or conflicting with how a specific distro manages its own system. Guards are not feature flags and not branding — they exist because that distro owns that area and ATT must stay out of the way.

**Rules:**

- Guards are only removed when explicitly requested during active testing on that distro — never proactively.
- The detection/re-mapping block in `functions.py` is permanently frozen — never touch it.

---

## Distro Detection & Canonical Name Resolution

**File:** `functions.py` (bottom of module, runs at import time)

These are not guards — they are identity corrections. `fn.distr` is normalized here once so that every downstream guard can key off a stable canonical name without duplicating detection logic.

| Detected as | Canonical name | Condition                                                                                 |
|-------------|----------------|-------------------------------------------------------------------------------------------|
| `manjaro`   | `biglinux`     | `/etc/os-release` contains "biglinux"                                                     |
| `arch`      | `omarchy`      | `/etc/plymouth/plymouthd.conf` contains "omarchy" OR `/etc/att/att-omarchy-marker` exists |

**Do not change this block** — all guards below depend on these names being stable.

---

## Page Visibility Guards

**File:** `gui.py`

| Page     | Hidden on    | Condition                                                                            |
|----------|--------------|--------------------------------------------------------------------------------------|
| SDDM     | `prismlinux` | `fn.distr not in _SDDM_HIDDEN_DISTROS` (set at top of `gui.py`)                      |
| SDDM     | any distro   | also hidden if `plasma-login` or `plasmalogin` service is enabled (not distro-keyed) |
| Streamline | all non-Kiro | shown ONLY on Kiro: `fn.get_distro_label() == "Kiro"` (Kiro = `IMAGE_ID=kiro` in `/etc/os-release`) |

---

## Per-Module Guards

### `kernel_distros.py`

| Distro | Effect                                                                           |
|--------|----------------------------------------------------------------------------------|
| `arch` | Requires `pacman-hook-kernel-install` (nemesis-repo) when systemd-boot is active |

### `plymouth_gui.py`

| Distro    | Effect                                                                                                                                                                                           |
|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `omarchy` | Sets `omarchy_plymouth_customized = True` in `att_settings.json` after theme apply; read back by `_omarchy_marker_set()` in `functions.py` to keep `fn.distr == "omarchy"` stable across reboots |

### `user_gui.py`

| Distro | Effect                            |
|--------|-----------------------------------|
| `arch` | Visudo section shown in User page |

---

## Protected Functionality — Not Guards

These are intentional UX behaviours that are distro-aware but are **not guards**. Do not reclassify them as guards, and do not remove or modify them without an explicit instruction.

### Plymouth — per-distro default theme (`plymouth_gui.py`)

The `_default_theme` dict maps each distro to the theme users expect when they hit "Reset to default". This is common-sense UX: users want to go back to their distro's shipped default, not some arbitrary theme.

| Distro       | Default theme           |
|--------------|-------------------------|
| `omarchy`    | `omarchy`               |
| `cachyos`    | `cachyos-bootanimation` |
| `prismlinux` | `prismlinux-theme`      |

**Do not remove or rename these entries.** New distros with a shipped Plymouth theme should be added here, not to the guards section.

---

## Quick Reference — Distro Guard Inventory

| Distro       | Guards          | Pages affected  | Modules affected                   |
|--------------|-----------------|-----------------|------------------------------------|
| `arch`       | yes             | —               | `kernel_distros.py`, `user_gui.py` |
| `archcraft`  | none            | —               | pending hardware test              |
| `artix`      | none            | —               | pending hardware test (Plymouth guard removed 2026-05-16, 7e87b39) |
| `biglinux`   | re-map only     | —               | `functions.py`                     |
| `cachyos`    | none            | —               | —                                  |
| `garuda`     | none            | —               | pending hardware test              |
| `kiro`       | yes             | Streamline (Kiro-only) | `gui.py`                    |
| `manjaro`    | none            | —               | pending hardware test              |
| `nyarch`     | none            | —               | pending hardware test              |
| `omarchy`    | re-map + marker | —               | `functions.py`, `plymouth_gui.py`  |
| `prismlinux` | yes             | SDDM hidden     | `gui.py`                           |

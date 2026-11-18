# ============================================================
# Authors: Erik Dubois
# ============================================================

import subprocess
import functions as fn


def _is_systemd_boot():
    try:
        return subprocess.run(["bootctl", "is-installed"], capture_output=True).returncode == 0
    except Exception:
        return False


DISTRO_REQUIREMENTS = {
    "arch": [
        {
            "pkg": "pacman-hook-kernel-install",
            "reason": "registers kernel-install hook for systemd-boot ESP layout",
            "repo": "chaotic-aur",
            "condition": _is_systemd_boot,
        }
    ],
}


def get_missing_requirements():
    requirements = DISTRO_REQUIREMENTS.get(fn.distr, [])
    missing = []
    for req in requirements:
        condition = req.get("condition")
        if condition is not None and not condition():
            continue
        try:
            result = subprocess.run(["pacman", "-Q", req["pkg"]], capture_output=True)
            if result.returncode != 0:
                missing.append(req)
        except Exception:
            pass
    return missing

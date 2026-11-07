# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import json
import os

import functions as fn
from att_i18n import _, ngettext

_SARDI_COUNT = 24

_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
_SURFN_FAMILIES_JSON = os.path.join(_DATA_DIR, "surfn_families.json")
_NEOCANDY_FAMILIES_JSON = os.path.join(_DATA_DIR, "neocandy_families.json")


def _load_json_table(label, json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as error:
        fn.log_error(f"Could not load {label} table: {error}")
        return {}


SURFN_FAMILIES = _load_json_table("Surfn family", _SURFN_FAMILIES_JSON)
NEOCANDY_FAMILIES = _load_json_table("Neo Candy family", _NEOCANDY_FAMILIES_JSON)

# Surfn and Neo Candy are the same kind of thing: colour-variant icon sets grouped into
# families. One generic engine drives both, keyed by set_key. "checks" is the per-window
# checkbox dict the GUI builds on self; "base" is the package every variant inherits and is
# kept out of a bulk removal unless it is the only thing selected.
ICON_SETS = {
    "surfn": {
        "families": SURFN_FAMILIES,
        "checks": "surfn_checkboxes",
        "base": "surfn-icons-git",
        "base_token": "surfn",
        "prefix": "surfn-",
        "noun": "Surfn",
    },
    "neocandy": {
        "families": NEOCANDY_FAMILIES,
        "checks": "neocandy_checkboxes",
        "base": "neo-candy-icons-git",
        "base_token": "neo-candy-icons",
        "prefix": "neo-candy-",
        "noun": "Neo Candy",
    },
}

NUMIX_FALLBACK = "numix-circle-icon-theme-git"
# Surfn Kiro is a full copy that inherits breeze, not Numix.
NUMIX_FREE = {"surfn-kiro-icons-git"}

# Which families live under each sub-tab of the Icons Surfn / Icons Neo Candy pages.
SURFN_TABS = {
    "Surfn": ["Plasma", "Numix", "Arc / Breeze", "Other"],
    "Surfn-Mint": ["Mint-X", "Mint-Y"],
    "Surfn-Papirus": ["Papirus"],
    "Surfn-Tela": ["Tela"],
}
NEOCANDY_TABS = {
    "Neo Candy": ["Numix", "Arc / Breeze", "Other"],
    "Neo Candy Mint": ["Mint-X", "Mint-Y"],
    "Neo Candy Papirus": ["Papirus"],
    "Neo Candy Tela": ["Tela"],
}

# The Icons Horst page mixes both sets: each sub-tab is (title, set_key, [families]).
HORST_TABS = [
    ("Surfn Horst", "surfn", ["Horst"]),
    ("Neo Candy Horst", "neocandy", ["Horst"]),
]


def family_title(family_label):
    """Return the text shown for a family; only the generic 'Other' bucket is translated (the rest are theme names)."""
    return _("Other") if family_label == "Other" else family_label


def _icon_families(set_key):
    return ICON_SETS[set_key]["families"]


def _icon_checks(self, set_key):
    return getattr(self, ICON_SETS[set_key]["checks"])


def _all_icon_tokens(set_key):
    return [entry["token"] for items in _icon_families(set_key).values() for entry in items]


def _icon_tab_tokens(set_key, family_labels):
    fams = _icon_families(set_key)
    return [entry["token"] for fam in family_labels for entry in fams.get(fam, [])]


def _icon_pkg(set_key, token):
    for items in _icon_families(set_key).values():
        for entry in items:
            if entry["token"] == token:
                return entry["package"]
    return token + "-icons-git"


def get_available_icon_counts():
    """Return (sardi, surfn, neocandy) installable package counts."""
    return _SARDI_COUNT, len(_all_icon_tokens("surfn")), len(_all_icon_tokens("neocandy"))


def _check_install_repos(self):
    nemesis_ok = fn.check_nemesis_repo_active()
    chaotic_ok = fn.check_chaotic_aur_active()
    if not nemesis_ok and not chaotic_ok:
        msg = "Neither nemesis_repo nor chaotic-aur is enabled — add them in the Pacman tab before installing"
        fn.log_info(msg)
        fn.show_in_app_notification(
            self,
            _("Neither {repo1} nor {repo2} is enabled — add them in the Pacman tab before installing").format(
                repo1="nemesis_repo", repo2="chaotic-aur"
            ),
        )
        return False
    if not nemesis_ok:
        msg = "nemesis_repo is not enabled — enable it in the Pacman tab for full icon theme support"
        fn.log_info(msg)
        fn.show_in_app_notification(
            self,
            _("{repo} is not enabled — enable it in the Pacman tab for full icon theme support").format(
                repo="nemesis_repo"
            ),
        )
    if not chaotic_ok:
        msg = "chaotic-aur is not enabled — enable it in the Pacman tab for full icon theme support"
        fn.log_info(msg)
        fn.show_in_app_notification(
            self,
            _("{repo} is not enabled — enable it in the Pacman tab for full icon theme support").format(
                repo="chaotic-aur"
            ),
        )
    return True


def on_click_att_sardi_icon_theming_all_selection(self, _widget):
    fn.log_subsection("All Sardi icons selected")
    fn.show_in_app_notification(self, _("We have selected all {name} icons").format(name="Sardi"))
    set_att_checkboxes_theming_sardi_icons_all(self)


def on_click_att_sardi_icon_theming_mint_selection(self, _widget):
    fn.log_subsection("Mint selection applied - Sardi icons")
    fn.show_in_app_notification(self, _("We have selected the mint selection - {name} icons").format(name="Sardi"))
    set_att_checkboxes_theming_sardi_mint_icons(self)


def on_click_att_sardi_icon_theming_mixing_selection(self, _widget):
    fn.log_subsection("Mixing selection applied - Sardi icons")
    fn.show_in_app_notification(self, _("We have selected the mixing selection - {name} icons").format(name="Sardi"))
    set_att_checkboxes_theming_sardi_mixing_icons(self)


def on_click_att_sardi_icon_theming_variations_selection(self, _widget):
    fn.log_subsection("Variations selection applied - Sardi icons")
    fn.show_in_app_notification(self, _("We have selected the variation selection - {name} icons").format(name="Sardi"))
    set_att_checkboxes_theming_sardi_icons_variations(self)


def on_click_att_sardi_icon_theming_none_selection(self, _widget):
    fn.log_subsection("No Sardi icons selected")
    fn.show_in_app_notification(self, _("We have selected no {name} icons").format(name="Sardi"))
    set_att_checkboxes_theming_sardi_icons_none(self)


def on_click_att_fam_sardi_icon_theming_sardi_selection(self, _widget):
    fn.log_subsection("Sardi family selected")
    fn.show_in_app_notification(self, _("We have selected the {name} family themes").format(name="Sardi"))
    set_att_fam_checkboxes_theming_sardi_icons(self)


def on_click_att_fam_sardi_icon_theming_sardi_flexible_selection(self, _widget):
    fn.log_subsection("Sardi flexible family selected")
    fn.show_in_app_notification(self, _("We have selected the {name} flexible family themes").format(name="Sardi"))
    set_att_fam_checkboxes_theming_sardi_flexible(self)


def on_click_att_fam_sardi_icon_theming_sardi_mono_selection(self, _widget):
    fn.log_subsection("Sardi mono family selected")
    fn.show_in_app_notification(self, _("We have selected the {name} mono family themes").format(name="Sardi"))
    set_att_fam_checkboxes_theming_sardi_mono(self)


def on_click_att_fam_sardi_icon_theming_sardi_flat_selection(self, _widget):
    fn.log_subsection("Sardi flat family selected")
    fn.show_in_app_notification(self, _("We have selected the {name} flat family themes").format(name="Sardi"))
    set_att_fam_checkboxes_theming_sardi_flat(self)


def on_click_att_fam_sardi_icon_theming_sardi_ghost_selection(self, _widget):
    fn.log_subsection("Sardi ghost family selected")
    fn.show_in_app_notification(self, _("We have selected the {name} ghost family themes").format(name="Sardi"))
    set_att_fam_checkboxes_theming_sardi_ghost(self)


def on_click_att_fam_sardi_icon_theming_sardi_orb_selection(self, _widget):
    fn.log_subsection("Sardi orb family selected")
    fn.show_in_app_notification(self, _("We have selected the {name} orb family themes").format(name="Sardi"))
    set_att_fam_checkboxes_theming_sardi_orb(self)


def on_icons_all(self, set_key, tokens, _widget):
    fn.log_subsection(f"All {ICON_SETS[set_key]['noun']} icons selected")
    fn.show_in_app_notification(self, _("We have selected all {name} icons").format(name=ICON_SETS[set_key]["noun"]))
    set_icon_checkboxes(self, set_key, True, tokens)


def on_icons_none(self, set_key, tokens, _widget):
    fn.log_subsection(f"No {ICON_SETS[set_key]['noun']} icons selected")
    fn.show_in_app_notification(self, _("We have selected no {name} icons").format(name=ICON_SETS[set_key]["noun"]))
    set_icon_checkboxes(self, set_key, False, tokens)


def on_icons_family(self, set_key, family_label, scope_tokens, _widget):
    """Tick one family (a filter button) and clear the rest within the tab."""
    fn.log_subsection(f"Select {family_label} {ICON_SETS[set_key]['noun']} icons")
    fn.show_in_app_notification(self, _("We have selected the {family} icons").format(family=family_title(family_label)))
    select_icon_family(self, set_key, family_label, scope_tokens)


def on_icons_install(self, set_key, tokens, _widget):
    fn.log_subsection(f"Installing selected {ICON_SETS[set_key]['noun']} icon themes...")
    install_icons(self, set_key, tokens)


def on_icons_remove(self, set_key, tokens, _widget):
    fn.log_subsection(f"Removing selected {ICON_SETS[set_key]['noun']} icon themes...")
    remove_icons(self, set_key, tokens)


def on_icons_find(self, set_key, tokens, _widget):
    fn.log_subsection(f"Showing installed {ICON_SETS[set_key]['noun']} icon themes...")
    fn.show_in_app_notification(self, _("We show the installed icon themes"))
    find_icons(self, set_key, tokens)


def on_install_att_sardi_icon_themes_clicked(self, _widget):
    fn.log_subsection("Installing selected Sardi icon themes...")
    install_sardi_icons(self)


def on_remove_att_sardi_icon_themes_clicked(self, _widget):
    fn.log_subsection("Removing selected Sardi icon themes...")
    remove_sardi_icons(self)


def on_find_att_sardi_icon_themes_clicked(self, _widget):
    fn.log_subsection("Showing installed Sardi icon themes...")
    fn.show_in_app_notification(self, _("We show the installed icon themes"))
    find_sardi_icons(self)


def set_att_checkboxes_theming_sardi_icons_all(self):
    self.sardi_icons_att.set_active(True)
    self.sardi_colora_variations_icons_git.set_active(True)
    self.sardi_flat_colora_variations_icons_git.set_active(True)
    self.sardi_flat_mint_y_icons_git.set_active(True)
    self.sardi_flat_mixing_icons_git.set_active(True)
    self.sardi_flexible_colora_variations_icons_git.set_active(True)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(True)
    self.sardi_flexible_mint_y_icons_git.set_active(True)
    self.sardi_flexible_mixing_icons_git.set_active(True)
    self.sardi_flexible_variations_icons_git.set_active(True)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(True)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(True)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(True)
    self.sardi_ghost_flexible_variations_icons_git.set_active(True)
    self.sardi_mint_y_icons_git.set_active(True)
    self.sardi_mixing_icons_git.set_active(True)
    self.sardi_mono_colora_variations_icons_git.set_active(True)
    self.sardi_mono_mint_y_icons_git.set_active(True)
    self.sardi_mono_mixing_icons_git.set_active(True)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(True)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(True)
    self.sardi_orb_colora_mint_y_icons_git.set_active(True)
    self.sardi_orb_colora_mixing_icons_git.set_active(True)
    self.sardi_orb_colora_variations_icons_git.set_active(True)


def set_att_checkboxes_theming_sardi_mint_icons(self):
    self.sardi_icons_att.set_active(True)
    self.sardi_colora_variations_icons_git.set_active(False)
    self.sardi_flat_colora_variations_icons_git.set_active(False)
    self.sardi_flat_mint_y_icons_git.set_active(True)
    self.sardi_flat_mixing_icons_git.set_active(False)
    self.sardi_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_mint_y_icons_git.set_active(True)
    self.sardi_flexible_mixing_icons_git.set_active(False)
    self.sardi_flexible_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(True)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(False)
    self.sardi_ghost_flexible_variations_icons_git.set_active(False)
    self.sardi_mint_y_icons_git.set_active(True)
    self.sardi_mixing_icons_git.set_active(False)
    self.sardi_mono_colora_variations_icons_git.set_active(False)
    self.sardi_mono_mint_y_icons_git.set_active(True)
    self.sardi_mono_mixing_icons_git.set_active(False)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(False)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(False)
    self.sardi_orb_colora_mint_y_icons_git.set_active(True)
    self.sardi_orb_colora_mixing_icons_git.set_active(False)
    self.sardi_orb_colora_variations_icons_git.set_active(False)


def set_att_checkboxes_theming_sardi_mixing_icons(self):
    self.sardi_icons_att.set_active(True)
    self.sardi_colora_variations_icons_git.set_active(False)
    self.sardi_flat_colora_variations_icons_git.set_active(False)
    self.sardi_flat_mint_y_icons_git.set_active(False)
    self.sardi_flat_mixing_icons_git.set_active(True)
    self.sardi_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_mint_y_icons_git.set_active(False)
    self.sardi_flexible_mixing_icons_git.set_active(True)
    self.sardi_flexible_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(False)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(True)
    self.sardi_ghost_flexible_variations_icons_git.set_active(False)
    self.sardi_mint_y_icons_git.set_active(False)
    self.sardi_mixing_icons_git.set_active(True)
    self.sardi_mono_colora_variations_icons_git.set_active(False)
    self.sardi_mono_mint_y_icons_git.set_active(False)
    self.sardi_mono_mixing_icons_git.set_active(True)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(False)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(False)
    self.sardi_orb_colora_mint_y_icons_git.set_active(False)
    self.sardi_orb_colora_mixing_icons_git.set_active(True)
    self.sardi_orb_colora_variations_icons_git.set_active(False)


def set_att_checkboxes_theming_sardi_icons_variations(self):
    self.sardi_icons_att.set_active(True)
    self.sardi_colora_variations_icons_git.set_active(True)
    self.sardi_flat_colora_variations_icons_git.set_active(True)
    self.sardi_flat_mint_y_icons_git.set_active(False)
    self.sardi_flat_mixing_icons_git.set_active(False)
    self.sardi_flexible_colora_variations_icons_git.set_active(True)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(True)
    self.sardi_flexible_mint_y_icons_git.set_active(False)
    self.sardi_flexible_mixing_icons_git.set_active(False)
    self.sardi_flexible_variations_icons_git.set_active(True)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(True)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(False)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(False)
    self.sardi_ghost_flexible_variations_icons_git.set_active(True)
    self.sardi_mint_y_icons_git.set_active(False)
    self.sardi_mixing_icons_git.set_active(False)
    self.sardi_mono_colora_variations_icons_git.set_active(True)
    self.sardi_mono_mint_y_icons_git.set_active(False)
    self.sardi_mono_mixing_icons_git.set_active(False)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(True)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(True)
    self.sardi_orb_colora_mint_y_icons_git.set_active(False)
    self.sardi_orb_colora_mixing_icons_git.set_active(False)
    self.sardi_orb_colora_variations_icons_git.set_active(True)


def set_att_checkboxes_theming_sardi_icons_none(self):
    self.sardi_icons_att.set_active(False)
    self.sardi_colora_variations_icons_git.set_active(False)
    self.sardi_flat_colora_variations_icons_git.set_active(False)
    self.sardi_flat_mint_y_icons_git.set_active(False)
    self.sardi_flat_mixing_icons_git.set_active(False)
    self.sardi_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_mint_y_icons_git.set_active(False)
    self.sardi_flexible_mixing_icons_git.set_active(False)
    self.sardi_flexible_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(False)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(False)
    self.sardi_ghost_flexible_variations_icons_git.set_active(False)
    self.sardi_mint_y_icons_git.set_active(False)
    self.sardi_mixing_icons_git.set_active(False)
    self.sardi_mono_colora_variations_icons_git.set_active(False)
    self.sardi_mono_mint_y_icons_git.set_active(False)
    self.sardi_mono_mixing_icons_git.set_active(False)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(False)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(False)
    self.sardi_orb_colora_mint_y_icons_git.set_active(False)
    self.sardi_orb_colora_mixing_icons_git.set_active(False)
    self.sardi_orb_colora_variations_icons_git.set_active(False)


def set_att_fam_checkboxes_theming_sardi_icons(self):
    self.sardi_icons_att.set_active(True)
    self.sardi_colora_variations_icons_git.set_active(True)
    self.sardi_flat_colora_variations_icons_git.set_active(False)
    self.sardi_flat_mint_y_icons_git.set_active(False)
    self.sardi_flat_mixing_icons_git.set_active(False)
    self.sardi_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_mint_y_icons_git.set_active(False)
    self.sardi_flexible_mixing_icons_git.set_active(False)
    self.sardi_flexible_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(False)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(False)
    self.sardi_ghost_flexible_variations_icons_git.set_active(False)
    self.sardi_mint_y_icons_git.set_active(False)
    self.sardi_mixing_icons_git.set_active(True)
    self.sardi_mono_colora_variations_icons_git.set_active(False)
    self.sardi_mono_mint_y_icons_git.set_active(False)
    self.sardi_mono_mixing_icons_git.set_active(False)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(False)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(False)
    self.sardi_orb_colora_mint_y_icons_git.set_active(False)
    self.sardi_orb_colora_mixing_icons_git.set_active(False)
    self.sardi_orb_colora_variations_icons_git.set_active(False)


def set_att_fam_checkboxes_theming_sardi_flexible(self):
    self.sardi_icons_att.set_active(False)
    self.sardi_colora_variations_icons_git.set_active(False)
    self.sardi_flat_colora_variations_icons_git.set_active(False)
    self.sardi_flat_mint_y_icons_git.set_active(False)
    self.sardi_flat_mixing_icons_git.set_active(False)
    self.sardi_flexible_colora_variations_icons_git.set_active(True)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(True)
    self.sardi_flexible_mint_y_icons_git.set_active(True)
    self.sardi_flexible_mixing_icons_git.set_active(True)
    self.sardi_flexible_variations_icons_git.set_active(True)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(False)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(False)
    self.sardi_ghost_flexible_variations_icons_git.set_active(False)
    self.sardi_mint_y_icons_git.set_active(False)
    self.sardi_mixing_icons_git.set_active(False)
    self.sardi_mono_colora_variations_icons_git.set_active(False)
    self.sardi_mono_mint_y_icons_git.set_active(False)
    self.sardi_mono_mixing_icons_git.set_active(False)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(False)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(False)
    self.sardi_orb_colora_mint_y_icons_git.set_active(False)
    self.sardi_orb_colora_mixing_icons_git.set_active(False)
    self.sardi_orb_colora_variations_icons_git.set_active(False)


def set_att_fam_checkboxes_theming_sardi_mono(self):
    self.sardi_icons_att.set_active(False)
    self.sardi_colora_variations_icons_git.set_active(False)
    self.sardi_flat_colora_variations_icons_git.set_active(False)
    self.sardi_flat_mint_y_icons_git.set_active(False)
    self.sardi_flat_mixing_icons_git.set_active(False)
    self.sardi_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_mint_y_icons_git.set_active(False)
    self.sardi_flexible_mixing_icons_git.set_active(False)
    self.sardi_flexible_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(False)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(False)
    self.sardi_ghost_flexible_variations_icons_git.set_active(False)
    self.sardi_mint_y_icons_git.set_active(False)
    self.sardi_mixing_icons_git.set_active(False)
    self.sardi_mono_colora_variations_icons_git.set_active(True)
    self.sardi_mono_mint_y_icons_git.set_active(True)
    self.sardi_mono_mixing_icons_git.set_active(True)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(True)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(True)
    self.sardi_orb_colora_mint_y_icons_git.set_active(False)
    self.sardi_orb_colora_mixing_icons_git.set_active(False)
    self.sardi_orb_colora_variations_icons_git.set_active(False)


def set_att_fam_checkboxes_theming_sardi_flat(self):
    self.sardi_icons_att.set_active(False)
    self.sardi_colora_variations_icons_git.set_active(False)
    self.sardi_flat_colora_variations_icons_git.set_active(True)
    self.sardi_flat_mint_y_icons_git.set_active(True)
    self.sardi_flat_mixing_icons_git.set_active(True)
    self.sardi_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_mint_y_icons_git.set_active(False)
    self.sardi_flexible_mixing_icons_git.set_active(False)
    self.sardi_flexible_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(False)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(False)
    self.sardi_ghost_flexible_variations_icons_git.set_active(False)
    self.sardi_mint_y_icons_git.set_active(False)
    self.sardi_mixing_icons_git.set_active(False)
    self.sardi_mono_colora_variations_icons_git.set_active(False)
    self.sardi_mono_mint_y_icons_git.set_active(False)
    self.sardi_mono_mixing_icons_git.set_active(False)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(False)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(False)
    self.sardi_orb_colora_mint_y_icons_git.set_active(False)
    self.sardi_orb_colora_mixing_icons_git.set_active(False)
    self.sardi_orb_colora_variations_icons_git.set_active(False)


def set_att_fam_checkboxes_theming_sardi_ghost(self):
    self.sardi_icons_att.set_active(False)
    self.sardi_colora_variations_icons_git.set_active(False)
    self.sardi_flat_colora_variations_icons_git.set_active(False)
    self.sardi_flat_mint_y_icons_git.set_active(False)
    self.sardi_flat_mixing_icons_git.set_active(False)
    self.sardi_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_mint_y_icons_git.set_active(False)
    self.sardi_flexible_mixing_icons_git.set_active(False)
    self.sardi_flexible_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(True)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(True)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(True)
    self.sardi_ghost_flexible_variations_icons_git.set_active(True)
    self.sardi_mint_y_icons_git.set_active(False)
    self.sardi_mixing_icons_git.set_active(False)
    self.sardi_mono_colora_variations_icons_git.set_active(False)
    self.sardi_mono_mint_y_icons_git.set_active(False)
    self.sardi_mono_mixing_icons_git.set_active(False)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(False)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(False)
    self.sardi_orb_colora_mint_y_icons_git.set_active(False)
    self.sardi_orb_colora_mixing_icons_git.set_active(False)
    self.sardi_orb_colora_variations_icons_git.set_active(False)


def set_att_fam_checkboxes_theming_sardi_orb(self):
    self.sardi_icons_att.set_active(False)
    self.sardi_colora_variations_icons_git.set_active(False)
    self.sardi_flat_colora_variations_icons_git.set_active(False)
    self.sardi_flat_mint_y_icons_git.set_active(False)
    self.sardi_flat_mixing_icons_git.set_active(False)
    self.sardi_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_luv_colora_variations_icons_git.set_active(False)
    self.sardi_flexible_mint_y_icons_git.set_active(False)
    self.sardi_flexible_mixing_icons_git.set_active(False)
    self.sardi_flexible_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_colora_variations_icons_git.set_active(False)
    self.sardi_ghost_flexible_mint_y_icons_git.set_active(False)
    self.sardi_ghost_flexible_mixing_icons_git.set_active(False)
    self.sardi_ghost_flexible_variations_icons_git.set_active(False)
    self.sardi_mint_y_icons_git.set_active(False)
    self.sardi_mixing_icons_git.set_active(False)
    self.sardi_mono_colora_variations_icons_git.set_active(False)
    self.sardi_mono_mint_y_icons_git.set_active(False)
    self.sardi_mono_mixing_icons_git.set_active(False)
    self.sardi_mono_numix_colora_variations_icons_git.set_active(False)
    self.sardi_mono_papirus_colora_variations_icons_git.set_active(False)
    self.sardi_orb_colora_mint_y_icons_git.set_active(True)
    self.sardi_orb_colora_mixing_icons_git.set_active(True)
    self.sardi_orb_colora_variations_icons_git.set_active(True)


def _collect_sardi_packages(self):
    pairs = [
        (self.sardi_icons_att, "sardi-icons"),
        (self.sardi_colora_variations_icons_git, "sardi-colora-variations-icons-git"),
        (self.sardi_flat_colora_variations_icons_git, "sardi-flat-colora-variations-icons-git"),
        (self.sardi_flat_mint_y_icons_git, "sardi-flat-mint-y-icons-git"),
        (self.sardi_flat_mixing_icons_git, "sardi-flat-mixing-icons-git"),
        (self.sardi_flexible_colora_variations_icons_git, "sardi-flexible-colora-variations-icons-git"),
        (self.sardi_flexible_luv_colora_variations_icons_git, "sardi-flexible-luv-colora-variations-icons-git"),
        (self.sardi_flexible_mint_y_icons_git, "sardi-flexible-mint-y-icons-git"),
        (self.sardi_flexible_mixing_icons_git, "sardi-flexible-mixing-icons-git"),
        (self.sardi_flexible_variations_icons_git, "sardi-flexible-variations-icons-git"),
        (self.sardi_ghost_flexible_colora_variations_icons_git, "sardi-ghost-flexible-colora-variations-icons-git"),
        (self.sardi_ghost_flexible_mint_y_icons_git, "sardi-ghost-flexible-mint-y-icons-git"),
        (self.sardi_ghost_flexible_mixing_icons_git, "sardi-ghost-flexible-mixing-icons-git"),
        (self.sardi_ghost_flexible_variations_icons_git, "sardi-ghost-flexible-variations-icons-git"),
        (self.sardi_mint_y_icons_git, "sardi-mint-y-icons-git"),
        (self.sardi_mixing_icons_git, "sardi-mixing-icons-git"),
        (self.sardi_mono_colora_variations_icons_git, "sardi-mono-colora-variations-icons-git"),
        (self.sardi_mono_mint_y_icons_git, "sardi-mono-mint-y-icons-git"),
        (self.sardi_mono_mixing_icons_git, "sardi-mono-mixing-icons-git"),
        (self.sardi_mono_numix_colora_variations_icons_git, "sardi-mono-numix-colora-variations-icons-git"),
        (self.sardi_mono_papirus_colora_variations_icons_git, "sardi-mono-papirus-colora-variations-icons-git"),
        (self.sardi_orb_colora_mint_y_icons_git, "sardi-orb-colora-mint-y-icons-git"),
        (self.sardi_orb_colora_mixing_icons_git, "sardi-orb-colora-mixing-icons-git"),
        (self.sardi_orb_colora_variations_icons_git, "sardi-orb-colora-variations-icons-git"),
    ]
    return [pkg for cb, pkg in pairs if cb.get_active()]


def install_sardi_icons(self):
    if not _check_install_repos(self):
        return
    packages = _collect_sardi_packages(self)
    if not packages:
        fn.log_info("No Sardi icons selected for installation")
        fn.show_in_app_notification(self, _("No {name} icons selected for installation").format(name="Sardi"))
        return
    fn.log_subsection(f"Installing {len(packages)} Sardi icon packages...")
    fn.log_info(f"  {', '.join(packages)}")
    process = fn.launch_pacman_install_in_terminal(" ".join(packages))
    fn.show_in_app_notification(
        self,
        ngettext(
            "Installing {count} {name} icon package...", "Installing {count} {name} icon packages...", len(packages)
        ).format(count=len(packages), name="Sardi"),
    )
    fn.wait_and_notify(process, self, _("{name} icons installation complete").format(name="Sardi"))


def remove_sardi_icons(self):
    packages = _collect_sardi_packages(self)
    if not packages:
        fn.log_info("No Sardi icons selected for removal")
        fn.show_in_app_notification(self, _("No {name} icons selected for removal").format(name="Sardi"))
        return
    fn.log_subsection(f"Removing {len(packages)} Sardi icon packages...")
    fn.log_info(f"  {', '.join(packages)}")
    process = fn.launch_pacman_remove_in_terminal(" ".join(packages))
    fn.show_in_app_notification(
        self,
        ngettext(
            "Removing {count} {name} icon package...", "Removing {count} {name} icon packages...", len(packages)
        ).format(count=len(packages), name="Sardi"),
    )
    fn.wait_and_notify(process, self, _("{name} icons removal complete").format(name="Sardi"))


def find_sardi_icons(self):
    set_att_checkboxes_theming_sardi_icons_none(self)

    if fn.check_package_installed("sardi-icons"):
        self.sardi_icons_att.set_active(True)
    if fn.check_package_installed("sardi-colora-variations-icons-git"):
        self.sardi_colora_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-flat-colora-variations-icons-git"):
        self.sardi_flat_colora_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-flat-mint-y-icons-git"):
        self.sardi_flat_mint_y_icons_git.set_active(True)
    if fn.check_package_installed("sardi-flat-mixing-icons-git"):
        self.sardi_flat_mixing_icons_git.set_active(True)
    if fn.check_package_installed("sardi-flexible-colora-variations-icons-git"):
        self.sardi_flexible_colora_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-flexible-luv-colora-variations-icons-git"):
        self.sardi_flexible_luv_colora_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-flexible-mint-y-icons-git"):
        self.sardi_flexible_mint_y_icons_git.set_active(True)
    if fn.check_package_installed("sardi-flexible-mixing-icons-git"):
        self.sardi_flexible_mixing_icons_git.set_active(True)
    if fn.check_package_installed("sardi-flexible-variations-icons-git"):
        self.sardi_flexible_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-ghost-flexible-colora-variations-icons-git"):
        self.sardi_ghost_flexible_colora_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-ghost-flexible-mint-y-icons-git"):
        self.sardi_ghost_flexible_mint_y_icons_git.set_active(True)
    if fn.check_package_installed("sardi-ghost-flexible-mixing-icons-git"):
        self.sardi_ghost_flexible_mixing_icons_git.set_active(True)
    if fn.check_package_installed("sardi-ghost-flexible-variations-icons-git"):
        self.sardi_ghost_flexible_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-mint-y-icons-git"):
        self.sardi_mint_y_icons_git.set_active(True)
    if fn.check_package_installed("sardi-mixing-icons-git"):
        self.sardi_mixing_icons_git.set_active(True)
    if fn.check_package_installed("sardi-mono-colora-variations-icons-git"):
        self.sardi_mono_colora_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-mono-mint-y-icons-git"):
        self.sardi_mono_mint_y_icons_git.set_active(True)
    if fn.check_package_installed("sardi-mono-mixing-icons-git"):
        self.sardi_mono_mixing_icons_git.set_active(True)
    if fn.check_package_installed("sardi-mono-numix-colora-variations-icons-git"):
        self.sardi_mono_numix_colora_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-mono-papirus-colora-variations-icons-git"):
        self.sardi_mono_papirus_colora_variations_icons_git.set_active(True)
    if fn.check_package_installed("sardi-orb-colora-mint-y-icons-git"):
        self.sardi_orb_colora_mint_y_icons_git.set_active(True)
    if fn.check_package_installed("sardi-orb-colora-mixing-icons-git"):
        self.sardi_orb_colora_mixing_icons_git.set_active(True)
    if fn.check_package_installed("sardi-orb-colora-variations-icons-git"):
        self.sardi_orb_colora_variations_icons_git.set_active(True)

    installed = _collect_sardi_packages(self)
    if installed:
        fn.log_subsection(f"Found {len(installed)} Sardi icon packages installed")
        fn.log_info(f"  {', '.join(installed)}")
        fn.show_in_app_notification(
            self,
            ngettext(
                "{count} {name} icon package installed", "{count} {name} icon packages installed", len(installed)
            ).format(count=len(installed), name="Sardi"),
        )
    else:
        fn.log_info("No Sardi icon packages installed")
        fn.show_in_app_notification(self, _("No {name} icon packages installed").format(name="Sardi"))


def set_icon_checkboxes(self, set_key, active, tokens=None):
    checks = _icon_checks(self, set_key)
    for token in tokens if tokens is not None else _all_icon_tokens(set_key):
        checks[token].set_active(active)


def select_icon_family(self, set_key, family_label, scope_tokens=None):
    """Tick the checkboxes for one family and clear the rest within scope."""
    checks = _icon_checks(self, set_key)
    scope = scope_tokens if scope_tokens is not None else _all_icon_tokens(set_key)
    family_tokens = {entry["token"] for entry in _icon_families(set_key).get(family_label, [])}
    for token in scope:
        checks[token].set_active(token in family_tokens)


def _collect_icon_packages(self, set_key, tokens=None):
    checks = _icon_checks(self, set_key)
    scope = tokens if tokens is not None else _all_icon_tokens(set_key)
    return [_icon_pkg(set_key, token) for token in scope if checks[token].get_active()]


def install_icons(self, set_key, tokens=None):
    if not _check_install_repos(self):
        return
    noun = ICON_SETS[set_key]["noun"]
    packages = _collect_icon_packages(self, set_key, tokens)
    if not packages:
        fn.log_info(f"No {noun} icons selected for installation")
        fn.show_in_app_notification(self, _("No {name} icons selected for installation").format(name=noun))
        return
    fn.log_subsection(f"Installing {len(packages)} {noun} icon packages...")
    fn.log_info(f"  {', '.join(packages)}")
    # Surfn falls back on Numix but its packages don't pull it in, and the Kiro ISO no longer ships it
    # (Surfn Kiro carries its own copies since 2026-11-07). numix-circle pulls numix in; both live in chaotic-aur.
    extra = []
    needs_numix = any(pkg not in NUMIX_FREE for pkg in packages)
    if (
        set_key == "surfn"
        and needs_numix
        and fn.check_chaotic_aur_active()
        and not fn.check_package_installed(NUMIX_FALLBACK)
    ):
        extra = [NUMIX_FALLBACK]
        fn.log_info(f"  + {NUMIX_FALLBACK} (Surfn falls back on Numix for icons it does not have)")
    process = fn.launch_pacman_install_in_terminal(" ".join(packages + extra))
    fn.show_in_app_notification(
        self,
        ngettext(
            "Installing {count} {name} icon package...", "Installing {count} {name} icon packages...", len(packages)
        ).format(count=len(packages), name=noun),
    )
    fn.wait_and_notify(process, self, _("{name} icons installation complete").format(name=noun))


def remove_icons(self, set_key, tokens=None):
    noun = ICON_SETS[set_key]["noun"]
    base = ICON_SETS[set_key]["base"]
    packages = _collect_icon_packages(self, set_key, tokens)
    if not packages:
        fn.log_info(f"No {noun} icons selected for removal")
        fn.show_in_app_notification(self, _("No {name} icons selected for removal").format(name=noun))
        return
    # Every variant inherits the base; removing it while variants remain would break them,
    # so keep the base unless it is the only thing selected.
    if base in packages and len(packages) > 1:
        packages.remove(base)
        fn.log_warn(f"Keeping {base} — other {noun} variants depend on it")
        fn.show_in_app_notification(self, _("Kept {name} (variants depend on it)").format(name=base))
    fn.log_subsection(f"Removing {len(packages)} {noun} icon packages...")
    fn.log_info(f"  {', '.join(packages)}")
    process = fn.launch_pacman_remove_in_terminal(" ".join(packages))
    fn.show_in_app_notification(
        self,
        ngettext(
            "Removing {count} {name} icon package...", "Removing {count} {name} icon packages...", len(packages)
        ).format(count=len(packages), name=noun),
    )
    fn.wait_and_notify(process, self, _("{name} icons removal complete").format(name=noun))


def find_icons(self, set_key, tokens=None):
    noun = ICON_SETS[set_key]["noun"]
    checks = _icon_checks(self, set_key)
    scope = tokens if tokens is not None else _all_icon_tokens(set_key)
    set_icon_checkboxes(self, set_key, False, scope)
    installed_map = fn.check_packages_installed([_icon_pkg(set_key, t) for t in scope])
    for token in scope:
        if installed_map.get(_icon_pkg(set_key, token)):
            checks[token].set_active(True)

    installed = _collect_icon_packages(self, set_key, scope)
    if installed:
        fn.log_subsection(f"Found {len(installed)} {noun} icon packages installed")
        fn.log_info(f"  {', '.join(installed)}")
        fn.show_in_app_notification(
            self,
            ngettext(
                "{count} {name} icon package installed", "{count} {name} icon packages installed", len(installed)
            ).format(count=len(installed), name=noun),
        )
    else:
        fn.log_info(f"No {noun} icon packages installed")
        fn.show_in_app_notification(self, _("No {name} icon packages installed").format(name=noun))

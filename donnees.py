"""
Modèle de données : persistance et statistiques.

Structure d'une entrée de stats par (jour, exercice) :
  {
    "total"      : int,    # nombre de réponses
    "reussite"   : int,    # bonnes réponses
    "temps"      : float,  # temps cumulé en secondes
    "niveau_max" : int,    # niveau numérique le plus élevé joué
    "niveau_sum" : int,    # somme des niveaux (pour calculer la moyenne)
    "classe_max" : str,    # niveau scolaire le plus élevé joué ("CP" … "CM2")
  }

Champs de session (section "session" dans le JSON) :
  {
    "classe_scolaire"  : str,       # dernier niveau scolaire choisi
    "niveau"           : int,       # dernier niveau numérique atteint
    "exercices_coches" : list[str], # NOM des exercices cochés
  }
"""

import json
from datetime import date
from pathlib import Path

from exercices.base import NIVEAUX_SCOLAIRES


SAVE_FILE = "progression_jeu.json"

_ORDRE_CLASSE = {c: i for i, c in enumerate(NIVEAUX_SCOLAIRES)}


def _entree_vide() -> dict:
    return {
        "total": 0,
        "reussite": 0,
        "temps": 0.0,
        "niveau_max": 0,
        "niveau_sum": 0,
        "classe_max": "",
    }


class Donnees:

    def __init__(self, exercices_disponibles: list[str]):
        self._exercices = exercices_disponibles
        self.score_total = 0
        self.niveau = 1
        self.badges: list[str] = []
        self.stats: dict = {}
        self.jour = date.today().isoformat()

        # ── État de session restauré au prochain démarrage ────────────────────
        # classe_scolaire   : dernier niveau scolaire choisi ("CP" … "CM2")
        # exercices_coches  : NOM des exercices cochés lors de la dernière session
        self.classe_scolaire: str = NIVEAUX_SCOLAIRES[0]
        self.exercices_coches: list[str] = list(exercices_disponibles)

        self._init_jour()

    # ── Initialisation / persistance ─────────────────────────────────────────

    def _init_jour(self) -> None:
        if self.jour not in self.stats:
            self.stats[self.jour] = {ex: _entree_vide() for ex in self._exercices}
        else:
            for ex in self._exercices:
                self.stats[self.jour].setdefault(ex, _entree_vide())
                entry = self.stats[self.jour][ex]
                entry.setdefault("niveau_max", 0)
                entry.setdefault("niveau_sum", 0)
                entry.setdefault("classe_max", "")

    def sauvegarder(self) -> None:
        data = {
            "score":   self.score_total,
            "niveau":  self.niveau,
            "badges":  self.badges,
            "stats":   self.stats,
            # ── Section session ──────────────────────────────────────────────
            "session": {
                "classe_scolaire":  self.classe_scolaire,
                "niveau":           self.niveau,
                "exercices_coches": self.exercices_coches,
            },
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def charger(self) -> None:
        if not Path(SAVE_FILE).exists():
            self._init_jour()
            return

        with open(SAVE_FILE, encoding="utf-8") as f:
            data = json.load(f)

        self.score_total = data.get("score", 0)
        self.niveau      = data.get("niveau", 1)
        self.badges      = data.get("badges", [])
        self.stats       = data.get("stats", {})

        # ── Restauration de la session ────────────────────────────────────────
        session = data.get("session", {})

        classe = session.get("classe_scolaire", NIVEAUX_SCOLAIRES[0])
        # Validation : la classe doit exister dans la liste connue
        self.classe_scolaire = classe if classe in NIVEAUX_SCOLAIRES else NIVEAUX_SCOLAIRES[0]

        self.niveau = session.get("niveau", self.niveau)

        # Filtrer les exercices cochés : ne garder que ceux encore disponibles
        coches = session.get("exercices_coches", list(self._exercices))
        self.exercices_coches = [e for e in coches if e in self._exercices]
        # Fallback : si aucun exercice valide, tout cocher
        if not self.exercices_coches:
            self.exercices_coches = list(self._exercices)

        self._init_jour()

    # ── Mise à jour de la session courante ────────────────────────────────────

    def mettre_a_jour_session(
        self,
        classe_scolaire: str,
        niveau: int,
        exercices_coches: list[str],
    ) -> None:
        """
        Appelée par la Fenetre lors de chaque démarrage de partie et
        à la fermeture, pour mémoriser l'état courant de la session.
        """
        self.classe_scolaire  = classe_scolaire
        self.niveau           = niveau
        self.exercices_coches = exercices_coches

    # ── Mise à jour des stats ─────────────────────────────────────────────────

    def enregistrer_reponse(
        self,
        nom_exercice: str,
        correct: bool,
        temps: float,
        niveau: int = 0,
        classe: str = "",
    ) -> None:
        jour = date.today().isoformat()
        if jour not in self.stats:
            self.stats[jour] = {ex: _entree_vide() for ex in self._exercices}

        s = self.stats[jour].setdefault(nom_exercice, _entree_vide())
        s["total"]  += 1
        s["temps"]  += temps
        if correct:
            s["reussite"] += 1

        if niveau > 0:
            s["niveau_max"] = max(s.get("niveau_max", 0), niveau)
            s["niveau_sum"] = s.get("niveau_sum", 0) + niveau

        if classe:
            ancien = s.get("classe_max", "")
            if not ancien or _ORDRE_CLASSE.get(classe, -1) > _ORDRE_CLASSE.get(ancien, -1):
                s["classe_max"] = classe

    # ── Accesseurs ────────────────────────────────────────────────────────────

    @property
    def exercices(self) -> list[str]:
        return list(self._exercices)

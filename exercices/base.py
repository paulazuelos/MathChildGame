"""
Module de base pour tous les exercices.
Chaque exercice hérite de la classe Exercice.
"""

from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt


# Niveaux scolaires disponibles
NIVEAUX_SCOLAIRES = ["CP", "CE1", "CE2", "CM1", "CM2"]

# Correspondance niveau scolaire -> plage de niveaux numériques
NIVEAUX_PAR_CLASSE = {
    "CP":  range(1, 3),
    "CE1": range(1, 8),
    "CE2": range(3, 6),
    "CM1": range(5, 8),
    "CM2": range(7, 11),
}


class Exercice(ABC):
    """
    Classe mère abstraite pour tous les exercices.

    Attributs de classe à définir dans chaque sous-classe :
        NOM        (str)  : identifiant interne unique  ex. "addition"
        LABEL      (str)  : nom affiché à l'utilisateur ex. "Addition"
        NIVEAUX    (list) : niveaux scolaires couverts  ex. ["CP", "CE1"]

    Cycle d'utilisation :
        1. generer(niveau)  → prépare la question
        2. widget(parent)   → retourne le QWidget à afficher
        3. verifier(saisie) → retourne (correct: bool, solution_str: str)
    """

    # ── À redéfinir dans chaque sous-classe ───────────────────────────────────
    NOM: str = ""
    LABEL: str = ""
    NIVEAUX: list[str] = []
    # ─────────────────────────────────────────────────────────────────────────

    def __init__(self):
        self._solution = None          # valeur brute attendue (int, float…)
        self._solution_affichee = ""   # représentation lisible pour feedback
        self._texte_question = ""
        self._niveau_numerique = 1
        self._classe_scolaire = ""     # ex. "CE1" — renseigné par generer()

    # ── Interface publique ────────────────────────────────────────────────────

    @abstractmethod
    def generer(self, niveau: int, classe: str = "") -> None:
        """
        Prépare une nouvelle question.

        Parameters
        ----------
        niveau  : niveau numérique courant (1-10)
        classe  : niveau scolaire sélectionné dans le menu ("CP", "CE1", …).
                  Permet à l'exercice d'adapter la difficulté à la tranche
                  scolaire en plus du niveau numérique fin.
                  Vaut "" si l'information n'est pas disponible.

        Doit renseigner self._solution, self._solution_affichee,
        self._texte_question et stocker self._classe_scolaire.
        """

    def widget(self, parent: QWidget | None = None) -> QWidget:
        """
        Retourne le QWidget à intégrer dans la vue Jeu.
        Par défaut : un QLabel + QLineEdit.
        Peut être surchargé pour un affichage spécifique à l'exercice.
        """
        return self._widget_defaut(parent)

    @abstractmethod
    def verifier(self, saisie: str) -> tuple[bool, str]:
        """
        Vérifie la saisie de l'utilisateur.
        Retourne (correct, solution_lisible).
        """

    # ── Accesseurs ────────────────────────────────────────────────────────────

    @property
    def texte_question(self) -> str:
        return self._texte_question

    @property
    def solution(self):
        return self._solution

    @property
    def solution_affichee(self) -> str:
        return self._solution_affichee

    @property
    def classe_scolaire(self) -> str:
        return self._classe_scolaire

    # ── Widget par défaut ─────────────────────────────────────────────────────

    def _widget_defaut(self, parent: QWidget | None) -> QWidget:
        """
        Widget générique : question centrée + champ de saisie.
        Stocke les références utiles sur self pour accès externe.
        """
        conteneur = QWidget(parent)
        layout = QVBoxLayout(conteneur)

        self._label_question = QLabel(self._texte_question)
        self._label_question.setAlignment(Qt.AlignCenter)
        self._label_question.setStyleSheet("font-size:28px")
        self._label_question.setWordWrap(True)

        self._champ_reponse = QLineEdit()
        self._champ_reponse.setAlignment(Qt.AlignCenter)
        self._champ_reponse.setStyleSheet("font-size:22px")

        layout.addWidget(self._label_question)
        layout.addWidget(self._champ_reponse)

        return conteneur

    def lire_saisie(self) -> str:
        """Lit la valeur du champ de saisie du widget par défaut."""
        if hasattr(self, "_champ_reponse"):
            return self._champ_reponse.text()
        return ""

    def vider_saisie(self) -> None:
        """Vide le champ de saisie et y remet le focus."""
        if hasattr(self, "_champ_reponse"):
            self._champ_reponse.clear()
            self._champ_reponse.setFocus()

    def connecter_validation(self, callback) -> None:
        """
        Connecte la touche Entrée du champ de saisie à callback.
        Appelé par la vue Jeu après avoir créé le widget.
        """
        if hasattr(self, "_champ_reponse"):
            self._champ_reponse.returnPressed.connect(callback)

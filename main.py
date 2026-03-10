"""
Fenêtre principale : orchestre les vues et charge les plugins.
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QStackedLayout
from PySide6.QtCore import Qt

from exercices.loader import charger_exercices
from donnees import Donnees
from vue_menu import Menu
from vue_jeu import Jeu
from vue_stats import Statistiques


class Fenetre(QWidget):

    def __init__(self):
        super().__init__()

        # ── 1. Charger les plugins d'exercices ────────────────────────────────
        self._catalogue = charger_exercices()

        # ── 2. Initialiser et charger les données (session incluse) ───────────
        self._data = Donnees(list(self._catalogue.keys()))
        self._data.charger()

        # ── 3. Construire les vues ────────────────────────────────────────────
        self._stack = QStackedLayout(self)

        self._menu = Menu(
            catalogue      = self._catalogue,
            start_callback = self._start_jeu,
            stats_callback = self._show_stats,
        )
        self._jeu = Jeu(self._data, self._retour_menu)

        self._stack.addWidget(self._menu)   # index 0
        self._stack.addWidget(self._jeu)    # index 1

        # ── 4. Restaurer l'état de la session précédente dans le menu ─────────
        self._menu.restaurer_session(
            classe_scolaire  = self._data.classe_scolaire,
            niveau           = self._data.niveau,
            exercices_coches = self._data.exercices_coches,
        )

        # ── 5. Paramètres fenêtre ─────────────────────────────────────────────
        self.setWindowTitle("Les Maths pour Juliette")
        self.resize(540, 520)

    # ── Transitions ──────────────────────────────────────────────────────────

    def _start_jeu(self) -> None:
        classe  = self._menu.classe_selectionnee()
        niveau  = self._menu.niveau_selectionne()
        coches  = self._menu.exercices_selectionnes()

        # Mémoriser immédiatement la session courante
        self._data.mettre_a_jour_session(classe, niveau, coches)
        self._data.niveau = niveau
        self._data.sauvegarder()

        self._stack.setCurrentWidget(self._jeu)
        self._jeu.start(
            catalogue       = self._catalogue,
            noms_actifs     = coches,
            classe_scolaire = classe,
        )

    def _show_stats(self) -> None:
        stats_widget = Statistiques(self._data, self._retour_menu)
        if self._stack.count() > 2:
            old = self._stack.widget(2)
            self._stack.removeWidget(old)
            old.deleteLater()
        self._stack.addWidget(stats_widget)
        self._stack.setCurrentWidget(stats_widget)

    def _retour_menu(self) -> None:
        self._stack.setCurrentWidget(self._menu)

    # ── Sauvegarde à la fermeture ─────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        """
        Surcharge de closeEvent : sauvegarde l'état de session
        (classe scolaire, niveau atteint, exercices cochés) avant de quitter.
        """
        self._data.mettre_a_jour_session(
            classe_scolaire  = self._menu.classe_selectionnee(),
            niveau           = self._data.niveau,
            exercices_coches = self._menu.exercices_selectionnes(),
        )
        self._data.sauvegarder()
        event.accept()


# ── Point d'entrée ────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    fen = Fenetre()
    fen.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

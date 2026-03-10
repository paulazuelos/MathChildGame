"""
Vue Statistiques.

Colonnes du tableau (une par jour) :
  - % réussite / temps moyen
  - niveau numérique max atteint
  - niveau numérique moyen
  - niveau scolaire max atteint
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from donnees import Donnees


# Nombre de sous-colonnes par journée
_COLS = ["% / tps moy", "niv. max", "niv. moy", "classe max"]


class Statistiques(QWidget):

    def __init__(self, data: Donnees, retour_callback):
        super().__init__()

        layout = QVBoxLayout(self)

        titre = QLabel("📊 Statistiques")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size:22px; font-weight:bold;")
        layout.addWidget(titre)

        exercices = data.exercices
        dates     = sorted(data.stats.keys())
        nb_cols   = len(dates) * len(_COLS)

        table = QTableWidget(len(exercices), nb_cols)
        table.setVerticalHeaderLabels(exercices)

        # En-têtes de colonnes groupées : "2025-06-01 | % / tps moy" …
        headers = []
        for jour in dates:
            for sous in _COLS:
                headers.append(f"{jour}\n{sous}")
        table.setHorizontalHeaderLabels(headers)

        for col_jour, jour in enumerate(dates):
            for row, exercice in enumerate(exercices):
                valeurs = data.stats[jour].get(exercice, {})
                total   = valeurs.get("total", 0)

                # Colonne 0 : % réussite / temps moyen
                col0 = col_jour * len(_COLS)
                if total == 0:
                    self._set(table, row, col0, "-")
                else:
                    pct   = valeurs["reussite"] / total * 100
                    t_moy = valeurs["temps"]    / total
                    self._set(table, row, col0, f"{pct:.0f}% / {t_moy:.1f}s")
                    # Colorier en vert si >= 80 %, rouge sinon
                    color = QColor("#c8f7c5") if pct >= 80 else QColor("#f7c5c5")
                    table.item(row, col0).setBackground(color)

                # Colonne 1 : niveau numérique max
                niv_max = valeurs.get("niveau_max", 0)
                self._set(table, row, col0 + 1,
                          str(niv_max) if niv_max > 0 else "-")

                # Colonne 2 : niveau numérique moyen
                niv_sum = valeurs.get("niveau_sum", 0)
                if total > 0 and niv_sum > 0:
                    self._set(table, row, col0 + 2, f"{niv_sum / total:.1f}")
                else:
                    self._set(table, row, col0 + 2, "-")

                # Colonne 3 : niveau scolaire max
                classe_max = valeurs.get("classe_max", "")
                self._set(table, row, col0 + 3, classe_max or "-")

        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(table)

        # Score total + badges
        lbl_score = QLabel(f"Score total : {data.score_total} pts")
        lbl_score.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_score)

        if data.badges:
            lbl_badges = QLabel("Badges : " + "  ".join(data.badges))
            lbl_badges.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_badges)

        btn_retour = QPushButton("← Retour")
        btn_retour.clicked.connect(retour_callback)
        layout.addWidget(btn_retour)

    @staticmethod
    def _set(table: QTableWidget, row: int, col: int, texte: str) -> None:
        item = QTableWidgetItem(texte)
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, col, item)

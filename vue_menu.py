"""
Vue Menu principal.

Flux de sélection :
  1. L'utilisateur choisit son niveau scolaire (CP … CM2).
  2. Les exercices disponibles pour ce niveau s'affichent avec cases à cocher.
  3. Le niveau numérique de départ est proposé automatiquement dans la plage
     du niveau scolaire, mais reste ajustable.
"""

from typing import Type
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QComboBox,
    QMessageBox, QFrame,
)
from PySide6.QtCore import Qt

from exercices.base import Exercice, NIVEAUX_SCOLAIRES, NIVEAUX_PAR_CLASSE


class Menu(QWidget):

    def __init__(
        self,
        catalogue: dict[str, Type[Exercice]],
        start_callback,
        stats_callback,
    ):
        super().__init__()
        self._catalogue = catalogue
        self._start_callback = start_callback
        self._checkboxes: dict[str, QCheckBox] = {}   # NOM -> QCheckBox

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # ── Titre ─────────────────────────────────────────────────────────────
        titre = QLabel("🎮 Progresser en Maths")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size:26px; color:darkblue; font-weight:bold;")
        layout.addWidget(titre)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        # ── 1. Niveau scolaire ────────────────────────────────────────────────
        row_classe = QHBoxLayout()
        row_classe.addWidget(QLabel("Niveau scolaire :"))
        self._classe_box = QComboBox()
        for classe in NIVEAUX_SCOLAIRES:
            self._classe_box.addItem(classe, classe)
        row_classe.addWidget(self._classe_box)
        layout.addLayout(row_classe)

        # ── 2. Exercices disponibles pour ce niveau scolaire ──────────────────
        lbl_ex = QLabel("Exercices à jouer :")
        layout.addWidget(lbl_ex)

        # Conteneur dynamique pour les checkboxes
        self._conteneur_ex = QWidget()
        self._conteneur_layout = QVBoxLayout(self._conteneur_ex)
        self._conteneur_layout.setContentsMargins(12, 4, 4, 4)
        layout.addWidget(self._conteneur_ex)

        # ── 3. Niveau numérique de départ ─────────────────────────────────────
        row_niveau = QHBoxLayout()
        row_niveau.addWidget(QLabel("Niveau de départ :"))
        self._niveau_box = QComboBox()
        row_niveau.addWidget(self._niveau_box)
        layout.addLayout(row_niveau)

        # Connexion + initialisation
        self._classe_box.currentIndexChanged.connect(self._on_classe_changed)
        self._on_classe_changed()

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        layout.addWidget(sep2)

        # ── Boutons ───────────────────────────────────────────────────────────
        btn_jouer = QPushButton("▶  Jouer")
        btn_jouer.setStyleSheet("font-size:18px; padding:8px;")
        btn_jouer.clicked.connect(self._lancer)

        btn_stats = QPushButton("📊 Statistiques")
        btn_stats.clicked.connect(stats_callback)

        layout.addWidget(btn_jouer)
        layout.addWidget(btn_stats)

    # ── Mise à jour dynamique ─────────────────────────────────────────────────

    def _on_classe_changed(self) -> None:
        """Rafraîchit les exercices et la plage de niveaux numériques."""
        classe = self._classe_box.currentData()

        # Vider les checkboxes précédentes
        self._checkboxes.clear()
        while self._conteneur_layout.count():
            item = self._conteneur_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        exercices_classe = sorted(
            [cls for cls in self._catalogue.values() if classe in cls.NIVEAUX],
            key=lambda c: c.LABEL,
        )
        if exercices_classe:
            for cls in exercices_classe:
                cb = QCheckBox(cls.LABEL)
                cb.setChecked(True)
                self._checkboxes[cls.NOM] = cb
                self._conteneur_layout.addWidget(cb)
        else:
            self._conteneur_layout.addWidget(QLabel("(aucun exercice disponible)"))

        # Mettre à jour la plage de niveaux numériques
        self._niveau_box.clear()
        plage = NIVEAUX_PAR_CLASSE.get(classe, range(1, 2))
        for n in plage:
            self._niveau_box.addItem(f"Niveau {n}", n)

    # ── API publique ──────────────────────────────────────────────────────────

    def classe_selectionnee(self) -> str:
        return self._classe_box.currentData()

    def niveau_selectionne(self) -> int:
        return self._niveau_box.currentData() or 1

    def exercices_selectionnes(self) -> list[str]:
        return [nom for nom, cb in self._checkboxes.items() if cb.isChecked()]

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _lancer(self) -> None:
        if not self.exercices_selectionnes():
            QMessageBox.warning(
                self,
                "Aucun exercice sélectionné",
                "Coche au moins un exercice avant de jouer !",
            )
            return
        self._start_callback()

    def restaurer_session(
        self,
        classe_scolaire: str,
        niveau: int,
        exercices_coches: list[str],
    ) -> None:
        """
        Repositionne les widgets du menu à partir de l'état sauvegardé.
        Appelée par Fenetre juste après la construction du menu.

        Parameters
        ----------
        classe_scolaire  : ex. "CE1"
        niveau           : niveau numérique (positionne la combo si valide)
        exercices_coches : liste des NOM à cocher
        """
        # 1. Sélectionner le niveau scolaire (déclenche _on_classe_changed)
        idx = self._classe_box.findData(classe_scolaire)
        if idx >= 0:
            # Bloquer le signal pour ne pas déclencher _on_classe_changed
            # avant d'avoir aussi restauré le niveau numérique
            self._classe_box.blockSignals(True)
            self._classe_box.setCurrentIndex(idx)
            self._classe_box.blockSignals(False)
            # Mettre à jour manuellement les exercices et la plage de niveaux
            self._on_classe_changed()

        # 2. Sélectionner le niveau numérique
        idx_niv = self._niveau_box.findData(niveau)
        if idx_niv >= 0:
            self._niveau_box.setCurrentIndex(idx_niv)

        # 3. Cocher uniquement les exercices de la session précédente
        for nom, cb in self._checkboxes.items():
            cb.setChecked(nom in exercices_coches)

"""
Vue Jeu : orchestre la séquence de questions.
"""

import random
import time
from datetime import date
from typing import Type

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QProgressBar, QMessageBox,
)
from PySide6.QtCore import Qt

from exercices.base import Exercice
from donnees import Donnees

NB_QUESTIONS_NIVEAU = 10


class Jeu(QWidget):

    def __init__(self, data: Donnees, fin_callback):
        super().__init__()
        self._data = data
        self._fin_callback = fin_callback

        self._catalogue: dict[str, Type[Exercice]] = {}
        self._noms_actifs: list[str] = []
        self._classe_scolaire: str = ""
        self._exercice_courant: Exercice | None = None

        self._historique: list[tuple] = []
        self._temps: list[float] = []
        self._index = 0
        self._debut = 0.0

        # ── Layout ────────────────────────────────────────────────────────────
        self._layout = QVBoxLayout(self)

        self._label_niveau = QLabel()
        self._progress = QProgressBar()
        self._progress.setMaximum(NB_QUESTIONS_NIVEAU)

        self._zone_exercice = QWidget()
        self._zone_layout = QVBoxLayout(self._zone_exercice)

        self._btn_valider = QPushButton("Valider")
        self._btn_valider.clicked.connect(self._valider)

        self._feedback = QLabel("")
        self._feedback.setAlignment(Qt.AlignCenter)
        self._feedback.setStyleSheet("font-size:20px")

        self._layout.addWidget(self._label_niveau)
        self._layout.addWidget(self._progress)
        self._layout.addWidget(self._zone_exercice)
        self._layout.addWidget(self._btn_valider)
        self._layout.addWidget(self._feedback)

    # ── API publique ──────────────────────────────────────────────────────────

    def start(
        self,
        catalogue: dict[str, Type[Exercice]],
        noms_actifs: list[str],
        classe_scolaire: str = "",
    ) -> None:
        self._catalogue       = catalogue
        self._noms_actifs     = [n for n in noms_actifs if n in catalogue]
        self._classe_scolaire = classe_scolaire
        self._historique      = []
        self._temps           = []
        self._index           = 0
        self._feedback.setText("")
        self._nouvelle_question()

    # ── Questions ─────────────────────────────────────────────────────────────

    def _nouvelle_question(self) -> None:
        self._progress.setValue(self._index)
        self._label_niveau.setText(
            f"Niveau {self._data.niveau}"
            + (f"  ({self._classe_scolaire})" if self._classe_scolaire else "")
        )

        # Tirage pondéré : favorise les exercices moins pratiqués aujourd'hui
        jour = date.today().isoformat()
        stats_jour = self._data.stats.get(jour, {})
        poids = [
            1 / (stats_jour.get(nom, {}).get("total", 0) + 1)
            for nom in self._noms_actifs
        ]

        nom_choisi = random.choices(self._noms_actifs, weights=poids, k=1)[0]
        cls = self._catalogue[nom_choisi]
        self._exercice_courant = cls()
        self._exercice_courant.generer(self._data.niveau, self._classe_scolaire)

        self._vider_zone()
        widget = self._exercice_courant.widget(self)
        self._zone_layout.addWidget(widget)
        self._exercice_courant.connecter_validation(self._valider)
        self._exercice_courant.vider_saisie()

        self._debut = time.time()

    def _vider_zone(self) -> None:
        while self._zone_layout.count():
            item = self._zone_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── Validation ────────────────────────────────────────────────────────────

    def _valider(self) -> None:
        if self._exercice_courant is None:
            return

        temps = time.time() - self._debut
        saisie = self._exercice_courant.lire_saisie()
        correct, sol_str = self._exercice_courant.verifier(saisie)

        self._temps.append(temps)
        self._historique.append((
            self._exercice_courant.texte_question,
            saisie,
            sol_str,
            correct,
            temps,
        ))

        self._data.enregistrer_reponse(
            nom_exercice=self._exercice_courant.NOM,
            correct=correct,
            temps=temps,
            niveau=self._data.niveau,
            classe=self._classe_scolaire,
        )

        if correct:
            self._feedback.setText("⭐ Bravo !")
        else:
            self._feedback.setText(f"❌ La réponse était : {sol_str}")

        self._index += 1
        if self._index >= NB_QUESTIONS_NIVEAU:
            self._fin_niveau()
        else:
            self._nouvelle_question()

    # ── Fin de niveau ─────────────────────────────────────────────────────────

    def _fin_niveau(self) -> None:
        score   = sum(1 for q in self._historique if q[3])
        moyenne = sum(self._temps) / len(self._temps) if self._temps else 0

        texte = f"Niveau terminé !\n\nScore : {score}/{NB_QUESTIONS_NIVEAU}\n"
        texte += f"Temps moyen : {moyenne:.2f}s\n\n"
        for q in self._historique:
            emoji = "✅" if q[3] else "❌"
            enonce = q[0].replace("\n", " ")
            if len(enonce) > 60:
                enonce = enonce[:57] + "…"
            texte += f"{enonce} → {q[1]} / {q[2]} {emoji} {q[4]:.1f}s\n"

        if score == NB_QUESTIONS_NIVEAU:
            self._data.badges.append("🏆 Niveau parfait")

        self._data.score_total += score
        self._data.sauvegarder()

        msg = QMessageBox(self)
        btn_continuer = msg.addButton("Continuer",      QMessageBox.AcceptRole)
        btn_menu      = msg.addButton("Menu principal", QMessageBox.RejectRole)

        if score == NB_QUESTIONS_NIVEAU:
            msg.setWindowTitle("Bravo !")
            msg.setText(texte)
            msg.setInformativeText(
                "🎉 Toutes les réponses sont correctes !\n"
                "Passage au niveau suivant."
            )
            msg.exec()
            self._data.niveau += 1
            self._data.sauvegarder()
        else:
            msg.setWindowTitle("Encore un effort !")
            msg.setText(texte)
            msg.setInformativeText(
                f"Il faut {NB_QUESTIONS_NIVEAU} bonnes réponses pour progresser.\n"
                "On recommence ce niveau ! 💪"
            )
            msg.exec()

        if msg.clickedButton() == btn_menu:
            self._fin_callback()
            return

        self._data.sauvegarder()
        self.start(self._catalogue, self._noms_actifs, self._classe_scolaire)

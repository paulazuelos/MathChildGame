"""
Exercice : Problèmes mathématiques
Niveaux  : CE1, CE2, CM1, CM2

Démontre la surcharge du widget() pour un affichage spécifique
(texte de problème dans un QTextEdit en lecture seule).
"""
import random
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit
from PySide6.QtCore import Qt

from exercices.base import Exercice


class ExerciceProbleme(Exercice):

    NOM    = "problem"
    LABEL  = "Problèmes"
    NIVEAUX = ["CE1", "CE2", "CM1", "CM2"]

    # ── Catalogue de problèmes ────────────────────────────────────────────────

    @staticmethod
    def _catalogue():
        def pb_coquillages():
            a = random.randint(10, 90)
            b = random.randint(a + 1, a + 50)
            return (
                f"Anaïs a ramassé {a} coquillages.\n"
                f"Son frère en a ramassé {b}.\n"
                f"Combien manque-t-il de coquillages à Anaïs\n"
                f"pour en avoir autant que son frère ?",
                b - a,
            )

        def pb_aquarium():
            depart = random.randint(5, 50)
            ajout  = random.randint(5, 50)
            total  = depart + ajout
            return (
                f"Un vendeur ajoute {ajout} poissons dans un aquarium.\n"
                f"Il y a maintenant {total} poissons.\n"
                f"Combien de poissons l'aquarium contenait-il au départ ?",
                depart,
            )

        def pb_pommes():
            nb = random.randint(2, 8)
            par = random.randint(3, 10)
            return (
                f"Juliette achète {nb} filets contenant\n"
                f"chacun {par} pommes.\n"
                f"Combien de pommes Juliette a-t-elle achetées en tout ?",
                nb * par,
            )

        def pb_pommes_deux():
            j = random.randint(2, 10)
            v = random.randint(2, 10)
            return (
                f"Margot achète un filet de {j} pommes jaunes\n"
                f"et un filet de {v} pommes vertes.\n"
                f"Combien de pommes en tout ?",
                j + v,
            )

        def pb_pamplemousses():
            filets = random.randint(2, 6)
            par    = random.randint(4, 8)
            return (
                f"Un filet contient {par} pamplemousses.\n"
                f"Combien en aura-t-on avec {filets} filets ?",
                filets * par,
            )

        def pb_crepes():
            filles  = random.randint(3, 8)
            garcons = random.randint(1, 5)
            crepes  = random.randint(2, 4)
            total   = filles + garcons + 1
            return (
                f"Mylène invite {filles} filles et {garcons} garçons.\n"
                f"Elle prévoit {crepes} crêpes par personne (elle incluse).\n"
                f"Combien faudra-t-il de crêpes en tout ?",
                total * crepes,
            )

        def pb_chorale():
            enfants  = random.randint(30, 60)
            nouveaux = random.randint(10, 30)
            adultes  = random.randint(5, 15)
            return (
                f"Une chorale compte {enfants} enfants et {adultes} adultes.\n"
                f"{nouveaux} enfants s'inscrivent en plus.\n"
                f"Combien d'enfants y a-t-il maintenant ?",
                enfants + nouveaux,
            )

        def pb_salle():
            r1, s1 = random.randint(3, 6), random.randint(10, 15)
            r2, s2 = random.randint(2, 4), random.randint(6, 10)
            total  = r1 * s1 + r2 * s2
            inst   = random.randint(10, total - 1)
            return (
                f"Une salle a {r1} rangées de {s1} sièges\n"
                f"et {r2} rangées de {s2} sièges.\n"
                f"{inst} personnes sont installées.\n"
                f"Combien de sièges sont encore vides ?",
                total - inst,
            )

        def pb_monnaie():
            articles = [
                ("gâteaux", random.randint(2, 6)),
                ("soda",    random.randint(1, 3)),
                ("chocolat",random.randint(3, 7)),
            ]
            total = sum(p for _, p in articles)
            billet = 5
            while billet < total:
                billet += 5
            detail = ", ".join(f"{n} à {p}€" for n, p in articles)
            return (
                f"Mathilde achète {detail}.\n"
                f"Elle paye avec un billet de {billet}€.\n"
                f"Quelle monnaie reçoit-elle ?",
                billet - total,
            )

        return [
            {"niveau": 1, "gen": pb_coquillages},
            {"niveau": 1, "gen": pb_aquarium},
            {"niveau": 2, "gen": pb_pommes_deux},
            {"niveau": 2, "gen": pb_monnaie},
            {"niveau": 3, "gen": pb_pommes},
            {"niveau": 3, "gen": pb_pamplemousses},
            {"niveau": 4, "gen": pb_crepes},
            {"niveau": 4, "gen": pb_chorale},
            {"niveau": 5, "gen": pb_salle},
        ]

    # ── Génération ────────────────────────────────────────────────────────────

    def generer(self, niveau: int, classe: str = "") -> None:
        self._niveau_numerique = niveau
        catalogue = self._catalogue()
        disponibles = [p for p in catalogue if p["niveau"] <= niveau] or catalogue[:1]
        choix = random.choice(disponibles)
        texte, solution = choix["gen"]()
        self._texte_question = texte
        self._solution = solution
        self._solution_affichee = str(solution)

    # ── Widget spécifique ─────────────────────────────────────────────────────

    def widget(self, parent=None):
        """
        Surcharge : affiche le texte du problème dans un QTextEdit
        en lecture seule pour plus de lisibilité.
        """
        conteneur = QWidget(parent)
        layout = QVBoxLayout(conteneur)

        zone_texte = QTextEdit()
        zone_texte.setReadOnly(True)
        zone_texte.setText(self._texte_question)
        zone_texte.setStyleSheet("font-size:16px; border:none; background:transparent;")
        zone_texte.setFixedHeight(150)

        label_consigne = QLabel("Écris ta réponse :")
        label_consigne.setAlignment(Qt.AlignCenter)

        self._champ_reponse = QLineEdit()
        self._champ_reponse.setAlignment(Qt.AlignCenter)
        self._champ_reponse.setStyleSheet("font-size:22px")

        layout.addWidget(zone_texte)
        layout.addWidget(label_consigne)
        layout.addWidget(self._champ_reponse)

        return conteneur

    # ── Vérification ─────────────────────────────────────────────────────────

    def verifier(self, saisie: str) -> tuple[bool, str]:
        try:
            rep = int(saisie.strip())
        except ValueError:
            return False, self._solution_affichee
        return rep == self._solution, self._solution_affichee

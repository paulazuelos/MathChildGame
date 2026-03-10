"""
Exercice : Addition
Niveaux  : CP, CE1, CE2
"""
import random
from exercices.base import Exercice


class ExerciceAddition(Exercice):

    NOM    = "addition"
    LABEL  = "Addition"
    NIVEAUX = ["CP", "CE1", "CE2"]

    def generer(self, niveau: int, classe: str = "") -> None:
        """
        Génère une addition adaptée au niveau numérique.

        Risques d'empty range dans le prototype original :
          - niveau < 2 : si ua == 9  →  randint(1, 9-9) = randint(1, 0)  CRASH
          - niveau < 3 : si ua == 10 (impossible ici) — pas de risque
          - niveau < 4 : si ua == 9 ou da == 9  →  randint(1, 0)  CRASH
          - niveau < 5 : si da == 9  →  randint(1, 0)  CRASH

        Corrections :
          - ua est borné à 8 pour les niveaux qui ont besoin de 9 - ua >= 1
          - da est borné à 8 pour les niveaux qui ont besoin de 9 - da >= 1
          - clamp systématique : max(lo, hi) garantit lo <= hi avant randint
        """
        self._niveau_numerique = niveau
        self._classe_scolaire = classe

        while True:
            ca = random.randint(0, 9)
            cb, db, ub = 0, 0, 0

            if niveau < 2:
                # Unités uniquement, sans retenue : ua + ub <= 9
                # ua doit être au plus 8 pour laisser ub >= 1
                ua = random.randint(1, 8)
                da = 0
                ub = random.randint(1, 9 - ua)          # range toujours valide

            elif niveau < 3:
                # Unités avec retenue : ua + ub >= 10
                # ua peut aller de 1 à 9 ; ub = [10-ua … 9]
                # Si ua == 9, ub doit être 1 (10-9=1) → toujours ok
                ua = random.randint(1, 9)
                da = random.randint(1, 9)
                lo = 10 - ua                             # >= 1
                ub = random.randint(lo, 9)

            elif niveau < 4:
                # Unités + dizaines, sans retenue sur aucun rang
                # ua, da bornés à 8 pour que 9 - ua >= 1 et 9 - da >= 1
                ua = random.randint(1, 8)
                da = random.randint(1, 8)
                ub = random.randint(1, 9 - ua)
                db = random.randint(1, 9 - da)

            elif niveau < 5:
                # Retenue sur unités, pas sur dizaines
                # da borné à 8 pour 9 - da >= 1
                ua = random.randint(1, 9)
                da = random.randint(1, 8)
                lo = 10 - ua                             # >= 1
                ub = random.randint(lo, 9)
                db = random.randint(1, 9 - da)

            else:
                # Unités + dizaines + centaines, résultat <= 999
                ua = random.randint(1, 9)
                da = random.randint(1, 9)
                ca = random.randint(0, 8)                # ca <= 8 pour cb >= 0
                ub = random.randint(1, 9)
                db = random.randint(1, 9)
                cb = random.randint(0, 9 - ca)

            a = ua + 10 * da + 100 * ca
            b = ub + 10 * db + 100 * cb

            if b > 0:
                break

        self._solution = a + b
        self._solution_affichee = str(self._solution)
        self._texte_question = f"{a} + {b} = ?"

    def verifier(self, saisie: str) -> tuple[bool, str]:
        try:
            rep = int(saisie.strip())
        except ValueError:
            return False, self._solution_affichee
        return rep == self._solution, self._solution_affichee

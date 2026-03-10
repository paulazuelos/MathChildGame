"""
Exercice : Soustraction
Niveaux  : CP, CE1, CE2
"""
import random
from exercices.base import Exercice


class ExerciceSoustraction(Exercice):

    NOM    = "soustraction"
    LABEL  = "Soustraction"
    NIVEAUX = ["CP", "CE1", "CE2"]

    def generer(self, niveau: int, classe: str = "") -> None:
        self._niveau_numerique = niveau

        while True:
            ca = random.randint(0, 9)
            da = random.randint(1, 9)
            ua = random.randint(1, 9)
            cb, db, ub = 0, 0, 0

            if niveau < 2:
                ub = random.randint(1, ua)
            elif niveau < 3:
                ub = random.randint(ua + 1, 9) if ua < 9 else 9
            elif niveau < 4:
                db = random.randint(1, da)
                ub = random.randint(1, ua)
            elif niveau < 5:
                db = random.randint(1, da)
                ub = random.randint(ua + 1, 9) if ua < 9 else random.randint(1, 9)
            elif niveau < 6:
                cb = random.randint(0, ca)
                db = random.randint(1, da)
                ub = random.randint(1, 9)

            a = ua + 10 * da + 100 * ca
            b = ub + 10 * db + 100 * cb

            if 0 < b < a:
                break

        self._solution = a - b
        self._solution_affichee = str(self._solution)
        self._texte_question = f"{a} - {b} = ?"

    def verifier(self, saisie: str) -> tuple[bool, str]:
        try:
            rep = int(saisie.strip())
        except ValueError:
            return False, self._solution_affichee
        return rep == self._solution, self._solution_affichee

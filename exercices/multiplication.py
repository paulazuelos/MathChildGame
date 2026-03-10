"""
Exercice : Multiplication
Niveaux  : CE1, CE2, CM1
"""
import random
from exercices.base import Exercice


class ExerciceMultiplication(Exercice):

    NOM    = "multiplication"
    LABEL  = "Multiplication"
    NIVEAUX = ["CE1", "CE2", "CM1"]

    def generer(self, niveau: int, classe: str = "") -> None:
        self._niveau_numerique = niveau
        max_table = min(10, 1 + niveau)

        a = random.randint(1, max_table)
        b = random.randint(1, max_table)

        self._solution = a * b
        self._solution_affichee = str(self._solution)
        self._texte_question = f"{a} × {b} = ?"

    def verifier(self, saisie: str) -> tuple[bool, str]:
        try:
            rep = int(saisie.strip())
        except ValueError:
            return False, self._solution_affichee
        return rep == self._solution, self._solution_affichee

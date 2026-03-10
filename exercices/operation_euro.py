"""
Exercice : Opérations en euros
Niveaux  : CE1, CE2, CM1, CM2
"""
import random
from exercices.base import Exercice


class ExerciceOperationEuro(Exercice):

    NOM    = "operationEuro"
    LABEL  = "Opérations en €"
    NIVEAUX = ["CE1", "CE2", "CM1", "CM2"]

    # ── Génération ────────────────────────────────────────────────────────────

    def generer(self, niveau: int, classe: str = "") -> None:
        self._niveau_numerique = niveau

        while True:
            a, b, operation = self._tirer_operandes(niveau)

            if operation == "soustraction" and b >= a:
                continue
            if b <= 0:
                continue
            break

        if operation == "addition":
            self._texte_question = f"{self._fmt(a)} + {self._fmt(b)} = ?"
            self._solution = a + b
        else:
            self._texte_question = f"{self._fmt(a)} - {self._fmt(b)} = ?"
            self._solution = a - b

        self._solution_affichee = self._fmt(self._solution)

    def _tirer_operandes(self, niveau: int):
        if niveau < 2:
            a = random.randint(1, 10) * 100
            b = random.randint(1, (a // 100)) * 100
            return a, b, "soustraction"

        if niveau < 3:
            a = random.randint(1, 10) * 100
            b = random.randint(1, 10) * 100
            return a, b, "addition"

        if niveau < 4:
            a = (random.randint(0, 9) * 100) + (random.randint(0, 9) * 10)
            b = (random.randint(0, 9) * 100) + (random.randint(0, 9) * 10)
            return a, b, random.choice(["addition", "soustraction"])

        if niveau < 5:
            a = random.randint(0, 19) * 100 + random.randint(0, 99)
            b = random.randint(0, 9)  * 100 + random.randint(0, 99)
            return a, b, random.choice(["addition", "soustraction"])

        a = random.randint(1, 99) * 100 + random.randint(0, 99)
        b = random.randint(1, 49) * 100 + random.randint(0, 99)
        return a, b, random.choice(["addition", "soustraction"])

    # ── Vérification ─────────────────────────────────────────────────────────

    def verifier(self, saisie: str) -> tuple[bool, str]:
        try:
            valeur = float(saisie.strip().replace(",", "."))
            rep = round(valeur * 100)
        except ValueError:
            return False, self._solution_affichee
        return rep == self._solution, self._solution_affichee

    # ── Aide ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _fmt(centimes: int) -> str:
        euros = centimes // 100
        cents = centimes % 100
        return f"{euros}€" if cents == 0 else f"{euros},{cents:02d}€"

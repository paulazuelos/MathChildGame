"""
Exercice : Numération (dizaines / centaines / unités)
Niveaux  : CP, CE1, CE2
"""
import random
from exercices.base import Exercice


class ExerciceNombres(Exercice):

    NOM    = "nombres"
    LABEL  = "Numération"
    NIVEAUX = ["CP", "CE1", "CE2"]

    def generer(self, niveau: int, classe: str = "") -> None:
        self._niveau_numerique = niveau

        if niveau < 2:
            d = random.randint(1, 9)
            u = random.randint(0, 9)
            self._texte_question = f"{d} dizaines + {u} unités = ?"
            self._solution = d * 10 + u

        elif niveau < 3:
            c = random.randint(1, 9)
            d = random.randint(0, 9)
            u = random.randint(0, 9)
            self._texte_question = f"{c} centaines + {d} dizaines + {u} unités = ?"
            self._solution = c * 100 + d * 10 + u

        elif niveau < 4:
            d = random.randint(1, 9)
            u = random.randint(0, 9)
            nombre = d * 10 + u
            q, sol = random.choice([
                (f"Combien y a-t-il de dizaines dans {nombre} ?", d),
                (f"Combien y a-t-il d'unités dans {nombre} ?",    u),
            ])
            self._texte_question = q
            self._solution = sol

        else:
            c = random.randint(1, 9)
            d = random.randint(0, 9)
            u = random.randint(0, 9)
            nombre = c * 100 + d * 10 + u
            q, sol = random.choice([
                (f"Combien y a-t-il de centaines dans {nombre} ?", c),
                (f"Combien y a-t-il de dizaines dans {nombre} ?",  d),
                (f"Combien y a-t-il d'unités dans {nombre} ?",     u),
            ])
            self._texte_question = q
            self._solution = sol

        self._solution_affichee = str(self._solution)

    def verifier(self, saisie: str) -> tuple[bool, str]:
        try:
            rep = int(saisie.strip())
        except ValueError:
            return False, self._solution_affichee
        return rep == self._solution, self._solution_affichee

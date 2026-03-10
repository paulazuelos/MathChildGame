import sys
import random
import time
import json
from pathlib import Path
from datetime import date

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QLineEdit,
    QMessageBox, QProgressBar, QStackedLayout,QComboBox,QTableWidget, QTableWidgetItem
)

from PySide6.QtCore import Qt


SAVE_FILE = "progression_jeu.json"
EXERCICES = ["addition", "soustraction", "multiplication", "nombres", "problem","operationEuro"]
NB_QUESTIONS_NIVEAU=10
class Donnees:

    def __init__(self):
        self.score_total = 0
        self.niveau = 1
        self.badges = []
        # statistiques par jour
        self.stats = {}
        self.jour = date.today().isoformat()
        # initialisation du jour
        self.init_jour()
    def init_jour(self):

        if self.jour not in self.stats:

            self.stats[self.jour] = {}

            for ex in EXERCICES:
                self.stats[self.jour][ex] = {
                    "total": 0,
                    "reussite": 0,
                    "temps": 0
                }
    def sauvegarder(self):

        data = {
            "score": self.score_total,
            "niveau": self.niveau,
            "badges": self.badges,
            "stats": self.stats
        }

        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def charger(self):

        if not Path(SAVE_FILE).exists():
            self.init_jour()
            return

        with open(SAVE_FILE) as f:
            data = json.load(f)

        self.score_total = data.get("score", 0)
        self.niveau = data.get("niveau", 1)
        self.badges = data.get("badges", [])
        self.stats = data.get("stats", {})

        # s'assurer que le jour existe
        self.init_jour()


class Menu(QWidget):

    def __init__(self, start_callback, stats_callback):
        super().__init__()

        layout = QVBoxLayout()

        titre = QLabel("🎮 Super Jeu de Calcul")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size:30px;color:darkblue")

        bouton_jouer = QPushButton("Jouer")
        bouton_stats = QPushButton("Statistiques")

        bouton_jouer.clicked.connect(start_callback)
        bouton_stats.clicked.connect(stats_callback)

        self.niveau_box = QComboBox()

        for i in range(1, 11):
            self.niveau_box.addItem(f"Niveau {i}", i)

        layout.addWidget(QLabel("Choisir le niveau"))
        layout.addWidget(self.niveau_box)

        layout.addWidget(titre)
        layout.addWidget(bouton_jouer)
        layout.addWidget(bouton_stats)

        self.setLayout(layout)


class Jeu(QWidget):

    def __init__(self, data, fin_callback):
        super().__init__()

        self.data = data
        self.fin_callback = fin_callback

        self.questions = []
        self.temps = []

        self.question_index = 0

        self.debut = None
        self.solution = 0

        layout = QVBoxLayout()

        self.label_niveau = QLabel()
        self.progress = QProgressBar()
        self.progress.setMaximum(NB_QUESTIONS_NIVEAU)

        self.question = QLabel("")
        self.question.setAlignment(Qt.AlignCenter)
        self.question.setStyleSheet("font-size:28px")

        self.reponse = QLineEdit()
        self.reponse.setAlignment(Qt.AlignCenter)
        self.reponse.returnPressed.connect(self.valider)
        
        bouton = QPushButton("Valider")
        bouton.clicked.connect(self.valider)

        self.feedback = QLabel("")
        self.feedback.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.label_niveau)
        layout.addWidget(self.progress)
        layout.addWidget(self.question)
        layout.addWidget(self.reponse)
        layout.addWidget(bouton)
        layout.addWidget(self.feedback)

        self.setLayout(layout)

    def start(self):

        self.questions = []
        self.temps = []
        self.question_index = 0
        self.feedback.setText("")
        self.jour = date.today().isoformat()

        if self.jour not in self.data.stats:
            self.data.stats[self.jour] = {
                exercice: {"total": 0, "reussite": 0, "temps": 0}
                for exercice in EXERCICES
            }

        self.nouvelle_question()

    def nouvelle_question(self):

        self.progress.setValue(self.question_index)
        self.label_niveau.setText(f"Niveau {self.data.niveau}")

        # Correspondance nom EXERCICES -> méthode
        methodes = {
            "addition"      : self.addition,
            "soustraction"  : self.soustraction,
            "multiplication": self.multiplication,
            "nombres"       : self.nombre,
            "problem"       : self.problem,
            "operationEuro" : self.operationEuro,
        }

        # Calcul du poids inverse : moins un exercice a été vu aujourd'hui,
        # plus il a de chances d'être tiré
        stats_jour = self.data.stats.get(self.jour, {})
        poids = []
        for nom in methodes:
            total = stats_jour.get(nom, {}).get("total", 0)
            poids.append(1 / (total + 1))   # +1 pour éviter la division par zéro

        exercice = random.choices(list(methodes.values()), weights=poids, k=1)[0]
        exercice()

        self.reponse.clear()
        self.debut = time.time()
        self.reponse.setFocus()

    def addition(self):
        while True:
            ca = random.randint(0, 9)
            da = random.randint(1, 9)
            ua = random.randint(1, 9)
            cb, db, ub = 0, 0, 0

            niveau = self.data.niveau

            if niveau < 2:
                # Unités uniquement, sans retenue (ua + ub <= 9)
                ub = random.randint(1, 9 - ua)

            elif niveau < 3:
                # Unités avec retenue (ua + ub >= 10)
                ub = random.randint(10 - ua, 9)

            elif niveau < 4:
                # Unités + dizaines, sans retenue
                ub = random.randint(1, 9 - ua)
                db = random.randint(1, 9 - da)

            elif niveau < 5:
                # Unités avec retenue + dizaines
                ub = random.randint(10 - ua, 9)
                db = random.randint(1, 9 - da)

            elif niveau < 6:
                # Unités + dizaines + centaines (résultat <= 999)
                ub = random.randint(1, 9)
                db = random.randint(1, 9)
                cb = random.randint(0, 9 - ca)

            a = ua + 10 * da + 100 * ca
            b = ub + 10 * db + 100 * cb

            if b > 0:
                break

        self.question.setText(f"{a} + {b} = ?")
        self.solution = a + b
        self.type = "addition"

    def soustraction(self):
        while True:
            ca = random.randint(0, 9)
            da = random.randint(1, 9)
            ua = random.randint(1, 9)
            cb, db, ub = 0, 0, 0

            niveau = self.data.niveau

            if niveau < 2:
                # Unités sans retenue : ub <= ua
                ub = random.randint(1, ua)

            elif niveau < 3:
                # Unités avec retenue : ub > ua
                ub = random.randint(ua + 1, 9) if ua < 9 else 9
                # forcer retenue : on ajustera da en conséquence si besoin

            elif niveau < 4:
                # Unités + dizaines, sans retenue
                db = random.randint(1, da)
                ub = random.randint(1, ua)

            elif niveau < 5:
                # Unités avec retenue + dizaines
                db = random.randint(1, da)
                ub = random.randint(ua + 1, 9) if ua < 9 else random.randint(1, 9)

            elif niveau < 6:
                # Unités + dizaines + centaines
                cb = random.randint(0, ca)
                db = random.randint(1, da)
                ub = random.randint(1, 9)

            a = ua + 10 * da + 100 * ca
            b = ub + 10 * db + 100 * cb

            if 0 < b < a:   # b strictement positif et strictement inférieur à a
                break

        self.question.setText(f"{a} - {b} = ?")
        self.solution = a - b
        self.type = "soustraction"

    def multiplication(self):

        max_table = min(5, 1 + self.data.niveau)

        a = random.randint(1, max_table)
        b = random.randint(1, max_table)

        self.question.setText(f"{a} × {b} = ?")
        self.solution = a * b
        self.type = "multiplication"

    def nombre(self):

        max_centaines = min(9, self.data.niveau + 1)

        c = random.randint(1, max_centaines)
        d = random.randint(0, 9)
        u = random.randint(0, 9)

        self.question.setText(
            f"{c} centaines + {d} dizaines + {u} unités = ?"
        )

        self.solution = c*100 + d*10 + u
        self.type = "nombres"

    def operationEuro(self):
        while True:
            niveau = self.data.niveau

            if niveau < 2:
                # Montants entiers, petites valeurs (1€ à 10€)
                a = random.randint(1, 10)
                b = random.randint(1, a)
                operation = "soustraction"

            elif niveau < 3:
                # Montants entiers jusqu'à 20€, addition
                a = random.randint(1, 10)
                b = random.randint(1, 10)
                operation = "addition"

            elif niveau < 4:
                # Montants avec centimes ronds (multiples de 10c), jusqu'à 10€
                a_euros = random.randint(0, 9)
                a_cents = random.randint(0, 9) * 10
                b_euros = random.randint(0, 9)
                b_cents = random.randint(0, 9) * 10
                a = a_euros * 100 + a_cents   # en centimes
                b = b_euros * 100 + b_cents
                operation = random.choice(["addition", "soustraction"])

            elif niveau < 5:
                # Montants avec centimes quelconques, jusqu'à 20€
                a_euros = random.randint(0, 19)
                a_cents = random.randint(0, 99)
                b_euros = random.randint(0, 9)
                b_cents = random.randint(0, 99)
                a = a_euros * 100 + a_cents
                b = b_euros * 100 + b_cents
                operation = random.choice(["addition", "soustraction"])

            elif niveau < 6:
                # Montants jusqu'à 100€ avec centimes
                a_euros = random.randint(1, 99)
                a_cents = random.randint(0, 99)
                b_euros = random.randint(1, 49)
                b_cents = random.randint(0, 99)
                a = a_euros * 100 + a_cents
                b = b_euros * 100 + b_cents
                operation = random.choice(["addition", "soustraction"])

            # Pour la soustraction : garantir a > b
            if operation == "soustraction" and b >= a:
                continue

            # Garantir que b > 0
            if b <= 0:
                continue

            break

        if operation == "addition":
            self.question.setText(f"{self.format_euro(a)} + {self.format_euro(b)} = ?")
            self.solution = a + b
        else:
            self.question.setText(f"{self.format_euro(a)} - {self.format_euro(b)} = ?")
            self.solution = a - b

        self.solution_display = self.format_euro(self.solution)
        self.type = "operationEuro"
        
    def format_euro(self,centimes):
        euros = centimes // 100
        cents = centimes % 100
        if cents == 0:
            return f"{euros}€"
        return f"{euros},{cents:02d}€"

    def problem(self):
        niveau = self.data.niveau
        
        # ─── Bibliothèque de problèmes ────────────────────────────────────────────
        # Chaque problème est un dict :
        #   "niveau"   : niveau minimum requis (1-5)
        #   "generate" : fonction () -> (texte, solution)
        # ─────────────────────────────────────────────────────────────────────────

        def pb_coquillages():
            a = random.randint(10, 90)
            b = random.randint(a + 1, a + 50)
            texte = (f"Anaïs a ramassé {a} coquillages. \n"
                    f"Son frère en a ramassé {b}. \n"
                    f"Combien manque-t-il de coquillages à Anaïs "
                    f"pour en avoir autant que son frère ?")
            return texte, b - a

        def pb_aquarium():
            depart = random.randint(5, 50)
            ajout  = random.randint(5, 50)
            total  = depart + ajout
            texte = (f"Un vendeur ajoute {ajout} poissons dans un aquarium. \n"
                    f"Il y a maintenant {total} poissons. \n"
                    f"Combien de poissons l'aquarium contenait-il au départ ?")
            return texte, depart

        def pb_pommes():
            nb_filets = random.randint(2, 8)
            par_filet = random.randint(3, 10)
            texte = (f"Juliette achète {nb_filets} filets contenant \n"
                    f"chacun {par_filet} pommes. \n"
                    f"Combien de pommes Juliette a-t-elle achetées en tout ?")
            return texte, nb_filets * par_filet

        def pb_pommes_deux_filets():
            jaunes = random.randint(2, 10)
            vertes = random.randint(2, 10)
            texte = (f"Margot achète un filet contenant {jaunes} pommes jaunes "
                    f"et un filet contenant {vertes} pommes vertes. "
                    f"Combien de pommes Margot a-t-elle achetées en tout ?")
            return texte, jaunes + vertes

        def pb_pamplemousses():
            filets = random.randint(2, 6)
            par_filet = random.randint(4, 8)
            texte = (f"Au supermarché, un filet de pamplemousses contient \n"
                    f"{par_filet} pamplemousses. "
                    f"Combien de pamplemousses aura-t-on "
                    f"si l'on achète {filets} filets ?")
            return texte, filets * par_filet

        def pb_crepes():
            filles   = random.randint(3, 8)
            garcons  = random.randint(1, 5)
            crepes   = random.randint(2, 4)
            invites  = filles + garcons
            total_p  = invites + 1          # invités + Mylène
            texte = (f"Mylène invite {filles} filles et {garcons} garçons "
                    f"à son anniversaire. \n"
                    f"Elle prévoit {crepes} crêpes par personne, "
                    f"pour elle et ses invités. \n"
                    f"Combien faudra-t-il de crêpes en tout ?")
            return texte, total_p * crepes

        def pb_chorale():
            enfants = random.randint(30, 60)
            adultes = random.randint(5, 15)
            nouveaux = random.randint(10, 30)
            texte = (f"Une chorale est composée de {enfants} enfants "
                    f"encadrés par {adultes} adultes. \n"
                    f"Au cours de l'année, {nouveaux} enfants de plus "
                    f"viennent s'inscrire. \n"
                    f"De combien d'enfants se compose maintenant la chorale ?")
            return texte, enfants + nouveaux

        def pb_salle_spectacle():
            r1 = random.randint(3, 6)
            s1 = random.randint(10, 15)
            r2 = random.randint(2, 4)
            s2 = random.randint(6, 10)
            total = r1 * s1 + r2 * s2
            installes = random.randint(10, total - 1)
            texte = (f"Une salle de spectacle est composée de {r1} rangées "
                    f"de {s1} sièges et {r2} rangées de {s2} sièges. \n"
                    f"Il y a {installes} personnes installées. \n"
                    f"Combien de sièges vides reste-t-il ?")
            return texte, total - installes

        def pb_monnaie():
            prix = [
                ("une boîte de gâteaux", random.randint(2, 6)),
                ("une bouteille de soda", random.randint(1, 3)),
                ("une tablette de chocolat", random.randint(3, 7)),
            ]
            total_achat = sum(p for _, p in prix)
            # Billet(s) couvrant le total
            billet = 5
            while billet < total_achat:
                billet += 5
            detail_prix = ", ".join(f"{nom} à {p}€" for nom, p in prix)
            texte = (f"Mathilde achète {detail_prix}. \n"
                    f"Elle paye avec un billet de {billet}€. \n"
                    f"Quelle somme le commerçant va-t-il lui rendre ?")
            return texte, billet - total_achat

        # ─── Table des problèmes par niveau ──────────────────────────────────────
        catalogue = [
            {"niveau": 1, "generate": pb_coquillages},
            {"niveau": 1, "generate": pb_aquarium},
            {"niveau": 2, "generate": pb_pommes_deux_filets},
            {"niveau": 2, "generate": pb_monnaie},
            {"niveau": 3, "generate": pb_pommes},
            {"niveau": 3, "generate": pb_pamplemousses},
            {"niveau": 4, "generate": pb_crepes},
            {"niveau": 4, "generate": pb_chorale},
            {"niveau": 5, "generate": pb_salle_spectacle},
        ]

        # ─── Sélection et génération ──────────────────────────────────────────────
        disponibles = [p for p in catalogue if p["niveau"] <= niveau]
        if not disponibles:
            disponibles = catalogue[:1]     # fallback niveau 1

        choix = random.choice(disponibles)
        texte, solution = choix["generate"]()

        self.question.setText(texte)
        self.solution = solution
        self.type = "problem"
    
    def valider(self):

        temps = time.time() - self.debut
        self.temps.append(temps)
        
        try:
                if self.type == "operationEuro":
                    # Accepter "3,25" ou "3.25" ou "3" (entiers en euros)
                    saisie = self.reponse.text().strip().replace(",", ".")
                    rep_euros = float(saisie)
                    rep = round(rep_euros * 100)   # conversion en centimes
                else:
                    rep = int(self.reponse.text())
        except:
            return


        correct = rep == self.solution

        self.questions.append(
            (
                self.question.text(),
                rep,
                self.solution,
                correct,
                temps
            )
        )
        stats = self.data.stats[self.jour][self.type]
        stats["total"] += 1
        stats["temps"] += temps
        if correct:
            self.feedback.setText("⭐ Bravo")
            stats["reussite"] += 1
        else:
            self.feedback.setText(f"❌ {self.solution}")

        self.question_index += 1

        if self.question_index >= NB_QUESTIONS_NIVEAU:
            self.fin_niveau()
        else:
            self.nouvelle_question()

    def fin_niveau(self):

        moyenne = sum(self.temps) / len(self.temps)

        score = sum(1 for q in self.questions if q[3])

        texte = f"Niveau terminé\n\nScore: {score}/5\n"
        texte += f"Temps moyen: {moyenne:.2f}s\n\n"

        for q in self.questions:

            emoji = "✅" if q[3] else "❌"

            texte += (
                f"{q[0]} | {q[1]} / {q[2]} {emoji} "
                f"{q[4]:.1f}s\n"
            )

        texte += f"\nProchain niveau : {self.data.niveau + 1}"
        
        if score == 5:
            self.data.badges.append("🏆 niveau parfait")

        self.data.score_total += score

        self.data.sauvegarder()
        msg = QMessageBox()
        # boutons personnalisés
        bouton_continuer = msg.addButton(
            "Continuer", QMessageBox.AcceptRole
        )

        bouton_menu = msg.addButton(
            "Menu principal", QMessageBox.RejectRole
        )
        if score == NB_QUESTIONS_NIVEAU:

            
            msg.setWindowTitle("Bravo !")
            msg.setText(texte)
            msg.setInformativeText(
                "🎉 Toutes les réponses sont correctes !\n"
                "Passage au niveau suivant."
            )
            msg.exec()

            self.data.niveau += 1
            self.data.sauvegarder()

        else:

            msg.setWindowTitle("Encore un effort")
            msg.setText(texte)
            msg.setInformativeText(
                "Pour passer au niveau suivant, il faut " + str(NB_QUESTIONS_NIVEAU)+ " bonnes réponses.\n"
                "On recommence ce niveau ! 💪"
            )
            msg.exec()

        # si retour menu
        if msg.clickedButton() == bouton_menu:
            self.fin_callback()
            return

        # sauvegarde progression
        self.data.sauvegarder()

        # démarrage du niveau suivant
        self.start()


class Statistiques(QWidget):

    def __init__(self, data, retour):
        super().__init__()

        layout = QVBoxLayout()

        titre = QLabel("📊 Statistiques")
        titre.setAlignment(Qt.AlignCenter)

        texte = "📊 Statistiques détaillées\n\n"
        
        exercices = EXERCICES
        dates = sorted(data.stats.keys())

        table = QTableWidget()
        table.setRowCount(len(exercices))
        table.setColumnCount(len(dates))

        table.setHorizontalHeaderLabels(dates)
        table.setVerticalHeaderLabels(exercices)

        for col, jour in enumerate(dates):

            for row, exercice in enumerate(exercices):

                valeurs = data.stats[jour][exercice]

                total = valeurs["total"]

                if total == 0:
                    texte = "-"
                else:
                    pourcentage = valeurs["reussite"] / total * 100
                    temps_moyen = valeurs["temps"] / total

                    texte = f"{pourcentage:.0f}% / {temps_moyen:.1f}s"

                table.setItem(row, col, QTableWidgetItem(texte))


        bouton = QPushButton("Retour")
        bouton.clicked.connect(retour)

        layout.addWidget(titre)
        layout.addWidget(table)
        layout.addWidget(bouton)

        self.setLayout(layout)


class Fenetre(QWidget):

    def __init__(self):
        super().__init__()

        self.data = Donnees()
        self.data.charger()

        self.stack = QStackedLayout()

        self.menu = Menu(self.start_jeu, self.show_stats)

        self.jeu = Jeu(self.data, self.retour_menu)

        self.stats = Statistiques(self.data, self.retour_menu)

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.jeu)
        self.stack.addWidget(self.stats)

        self.setLayout(self.stack)

        self.setWindowTitle("Les Maths pour Juliette")
        self.resize(500, 400)

    def start_jeu(self):

        niveau = self.menu.niveau_box.currentData()
        self.data.niveau = niveau

        self.stack.setCurrentWidget(self.jeu)
        self.jeu.start()

    def show_stats(self):

        self.stats = Statistiques(self.data, self.retour_menu)
        self.stack.addWidget(self.stats)
        self.stack.setCurrentWidget(self.stats)

    def retour_menu(self):

        self.stack.setCurrentWidget(self.menu)


app = QApplication(sys.argv)

fen = Fenetre()
fen.show()

app.exec()
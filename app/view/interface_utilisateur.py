"""Interface utilisateur jeu d'échec. Son but est donc purement
graphique. Celle-ci fonctionne de la manière suivante :
 * Elle est autonome.
 * Un contrôleur doit être lié en appelant la méthode
   "enregistrer_controleur" pour apporter des modifications. Un
   contrôleur doit être un objet de classe chargé de répondre aux
   actions de l'utilisateur sur la partie graphique.
 * L'interface utilisateur contient alors 2 types de méthodes :
    → Des méthodes répondants aux actions de l'utilisateur et appelant
      des méthodes du contrôleur. Le contrôleur utilisé doit donc
      contenir ces méthodes et effectuer les actions correspondantes aux
      actions de l'utilisateur.
    → Des méthodes à appeler depuis le contrôleur pour effectuer
      d'éventuels changements graphiques.
 * Remarque : le contrôleur doit être lié avant d'appeler la méthode
   "lancer_jeu", qui démarre la boucle sur la fenêtre.
 """

# -------------------------Bibliothèques---------------------------------------
# ----- Standard
import tkinter as tk
# ----- Fichiers internes
from .zone_dessin import ZoneDessin, ZoneDessinPromotion
# ----- Paramètres de jeu
from .constantes import COULEUR_INFOS, COULEUR_FOND_INFOS

# -------------------------Classes---------------------------------------------


class MainGUI:
    """Interface utilisateur principale
    """
    def __init__(self):
        # Contrôleur
        self.controleur = None

        #  Initialisation
        self.creer_main_gui()
        self.lier_souris()

    def creer_main_gui(self):
        """Créer la fenêtre, la zone de dessin, la zone d'infos et les
        boutons.
        """
        # Fenêtre
        self.window = tk.Tk()
        self.window.title("Echecs")

        # Zone de dessin
        self.zone_dessin = ZoneDessin(self.window)

        # Infos de jeu
        self.infos = tk.Label(self.window, text="Bienvenue !",
                              fg=COULEUR_INFOS, bg=COULEUR_FOND_INFOS)
        self.infos.grid(row=1, column=0, columnspan=2)

        # Boutons
        self.button1 = tk.Button(self.window, text="Nouvelle partie",
                                 command=self.gestion_nouvelle_partie)
        self.button1.grid(row=2, column=0)
        self.button2 = tk.Button(self.window, text='Quitter',
                                 command=self.gestion_quitter)
        self.button2.grid(row=2, column=1)

    def enregistrer_controleur(self, controleur):
        """Enregistre un contrôleur. Ses méthodes pourront ensuite être
        appelées pour lui indiquer que l'utilisateur veut effectuer une
        action.
        """
        self.controleur = controleur

    # Actions utilisateur

    def gestion_souris(self, evt):
        """Méthode de gestion globale de tous les évènements liés à la
        souris. Indique au contrôleur qu'un évènement de la souris a été
        déclenché.
        """
        if self.controleur is not None:
            # Clic gauche
            if evt.num == 1:
                self.controleur.gestion_clic_gauche(evt)
        else:
            raise AttributeError("Aucun controleur n'est enregistré pour la "
                                 "partie graphique.")

    def gestion_nouvelle_partie(self):
        """Indique au contrôleur que l'utilisateur souhaite lancer une
        nouvelle partie.
        """
        if self.controleur is not None:
            self.controleur.gestion_nouvelle_partie()
        else:
            raise AttributeError("Aucun controller n'est enregistré pour la "
                                 "partie graphique.")

    def gestion_quitter(self):
        """Indique au contrôleur que l'utilisateur souhaite quitter
        l'application.
        """
        if self.controleur is not None:
            self.controleur.gestion_quitter()
        else:
            raise AttributeError("Aucun controller n'est enregistré pour la "
                                 "partie graphique.")

    # Appels contrôleur

    def lancer_jeu(self):
        """Lance la boucle principale sur la fenêtre. Doit être appelée
        quand toutes les préparations au jeu ont été faites.
        """
        self.window.mainloop()

    def lier_souris(self):
        """Lie la souris au canvas principal.
        """
        self.zone_dessin.canvas.bind("<1>", self.gestion_souris)

    def desactiver_souris(self):
        """Désactive la souris sur le canvas principal.
        """
        self.zone_dessin.canvas.unbind("<1>")

    def modifier_infos(self, texte, couleur):
        """Modifie les informations de la zone de texte.
        """
        self.infos.config(text=texte, fg=couleur)

    def changer_couleur_case(self, case_x, case_y, couleur):
        """Change la couleur de la case donnée.
        """
        self.zone_dessin.changer_couleur_case(case_x, case_y, couleur)

    def reset_couleur_case(self, case_x, case_y):
        """Réinitialise la couleur de la case donnée.
        """
        self.zone_dessin.reset_couleur_case(case_x, case_y)

    def dessiner_piece_canvas(self, piece, case_x, case_y, couleur):
        """Dessine la pièce donnée sur la case donnée de la couleur
        donnée. L'argument piece doit être une str correspond au nom de
        la classe, par exemple "Pion" pour un pion.
        """
        self.zone_dessin.dessiner_piece(piece, case_x, case_y, couleur)

    def deplacer_piece(self, case_x_avant, case_y_avant, case_x_apres,
                       case_y_apres):
        """Déplace une pièce d'une case à une autre.
        """
        self.zone_dessin.deplacer_piece(case_x_avant, case_y_avant,
                                        case_x_apres, case_y_apres)

    def effacer_piece(self, case_x, case_y):
        """Efface la pièce de la case donnée.
        """
        self.zone_dessin.effacer_piece(case_x, case_y)

    def fermer_fenetre(self):
        """Détruit l'interface graphique.
        """
        self.window.destroy()

    def creer_gui_promotion(self, couleur):
        """Créer l'interface de promotion d'une pièce.
        """
        self.gui_promotion = GUIPromotion(self.controleur, self.window,
                                          couleur)
        self.window.wait_window(self.gui_promotion.window)
        # Tant que la fenêtre enfant n'est pas fermée, le programme est
        # retenu ici.

    def get_nom_piece_promotion(self, case):
        """Renvoie le nom de la pièce de la case donnée de l'interface
        de promotion .
        """
        return self.gui_promotion.get_nom_piece(case)

    def fermer_fenetre_promotion(self):
        """Détruit l'interface de promotion.
        """
        self.gui_promotion.fermer_fenetre()
        del self.gui_promotion

    def reset(self):
        """Réinitialise l'interface utilisateur.
        """
        self.modifier_infos("Bienvenue !", COULEUR_INFOS)
        self.zone_dessin.reset()


class GUIPromotion:
    """Interface de promotion d'une pièce.
    """
    def __init__(self, controleur, fenetre_parent, couleur):
        # Contrôleur
        self.controleur = controleur

        # Références
        self.fenetre_parent = fenetre_parent

        self.creer_gui_promotion(couleur)
        self.lier_souris()

    def creer_gui_promotion(self, couleur):
        """Créer la fenêtre et la zone de dessin.
        """
        # Fenêtre
        self.window = tk.Toplevel(self.fenetre_parent)
        self.window.title("Promotion")
        self.window.transient(self.fenetre_parent)  # Permet de garder
        # la fenêtre devant parent
        self.window.grab_set()  # Redirige tous les évenements vers
        # cette fenêtre, empêchant l'interaction avec la fenêtre
        # principale.

        # Zone de dessin
        self.zone_dessin = ZoneDessinPromotion(self.window, couleur)

        self.window.protocol("WM_DELETE_WINDOW", self.gestion_quitter)

        # Update pour pouvoir calculer la taille du canvas
        self.window.update()

    # Actions utilisateur

    def gestion_souris(self, evt):
        """Méthode de gestion globale de tous les évènements liés à la
        souris. Indique au contrôleur qu'un évènement de la souris a été
        déclenché.
        """
        if self.controleur is not None:
            # Clic gauche
            if evt.num == 1:
                self.controleur.gestion_clic_gauche_promotion(evt)
        else:
            raise AttributeError("Aucun controleur n'est enregistré pour la "
                                 "partie graphique.")

    def gestion_quitter(self):
        """Indique au contrôleur que l'utilisateur souhaite quitter
        la promotion de la pièce.
        """
        if self.controleur is not None:
            self.controleur.gestion_quitter_promotion()
        else:
            raise AttributeError("Aucun controleur n'est enregistré pour la "
                                 "partie graphique.")

    # Appels contrôleur

    def get_nom_piece(self, case):
        """Renvoie le nom de la pièce de la case donnée.
        """
        return self.zone_dessin.get_nom_piece(case)

    def lier_souris(self):
        """Lie la souris au canvas de promotion.
        """
        self.zone_dessin.canvas.bind("<1>", self.gestion_souris)

    def fermer_fenetre(self):
        """Détruit l'interface de promotion.
        """
        self.window.destroy()

"""Interface utilisateur jeu d'échec. Son but est donc purement graphique. Celle-ci fonctionne de la manière suivante :
 * Elle est autonome.
 * Un contrôleur doit être lié en appelant la méthode "enregistrer_controleur" pour apporter des modifications. Un
   contrôleur doit être un objet de classe chargé de répondre aux actions de l'utilisateur sur la partie graphique.
 * L'interface utilisateur contient alors 2 types de méthodes :
    → Des méthodes répondants aux actions de l'utilisateur et appelant des méthodes du contrôleur. Le contrôleur
       utilisé doit donc contenir ces méthodes et effectuer les actions correspondantes aux actions de l'utilisateur.
    → Des méthodes à appeler depuis le contrôleur pour effectuer d'éventuels changements graphiques.
 * Remarque : le contrôleur doit être lié avant d'appeler la méthode "lancer_jeu", qui démarre la boucle sur la fenêtre.
 """

### Bibliothèques ######################################################################################################
### Externes ###
import tkinter as tk
### Fichiers internes ###
from .zone_dessin import ZoneDessin, ZoneDessinPromotion
### Paramètres de jeu ###
from . import COULEUR_INFOS, COULEUR_FOND_INFOS

### Classes ############################################################################################################


class MainGUI:
    def __init__(self):
        # Contrôleur
        self.controleur = None

        #  Initialisation
        self.creer_main_gui()
        self.lier_souris()

    def creer_main_gui(self):
        # Fenêtre
        self.window = tk.Tk()
        self.window.title("Echecs")

        # Zone de dessin
        self.zone_dessin = ZoneDessin(self.window)

        # Infos de jeu
        self.infos = tk.Label(self.window, text="Bienvenue !", fg=COULEUR_INFOS, bg=COULEUR_FOND_INFOS)
        self.infos.grid(row=1, column=0, columnspan=2)

        # Boutons
        self.button1 = tk.Button(self.window, text="Nouvelle partie", command=self.gestion_nouvelle_partie)
        self.button1.grid(row=2, column=0)
        self.button2 = tk.Button(self.window, text='Quitter', command=self.gestion_quitter)
        self.button2.grid(row=2, column=1)

    def enregistrer_controleur(self, controleur):
        self.controleur = controleur

    # Actions utilisateur

    def gestion_souris(self, evt):
        if self.controleur is not None:
            # Clic gauche
            if evt.num == 1:
                self.controleur.gestion_clic_gauche(evt)
        else:
            raise AttributeError("Aucun controleur n'est enregistré pour la partie graphique.")

    def gestion_nouvelle_partie(self):
        if self.controleur is not None:
            self.controleur.gestion_nouvelle_partie()
        else:
            raise AttributeError("Aucun controller n'est enregistré pour la partie graphique.")

    def gestion_quitter(self):
        if self.controleur is not None:
            self.controleur.gestion_quitter()
        else:
            raise AttributeError("Aucun controller n'est enregistré pour la partie graphique.")

    # Appels contrôleur

    def lancer_jeu(self):
        self.window.mainloop()

    def lier_souris(self):
        self.zone_dessin.canvas.bind("<1>", self.gestion_souris)

    def desactiver_souris(self):
        self.zone_dessin.canvas.unbind("<1>")

    def modifier_infos(self, texte, couleur):
        self.infos.config(text=texte, fg=couleur)

    def changer_couleur_case(self, case_x, case_y, couleur):
        self.zone_dessin.changer_couleur_case(case_x, case_y, couleur)

    def reset_couleur_case(self, case_x, case_y):
        self.zone_dessin.reset_couleur_case(case_x, case_y)

    def dessiner_piece_canvas(self, piece, case_x, case_y, couleur):
        self.zone_dessin.dessiner_piece(piece, case_x, case_y, couleur)

    def deplacer_piece(self, case_x_avant, case_y_avant, case_x_apres, case_y_apres):
        self.zone_dessin.deplacer_piece(case_x_avant, case_y_avant, case_x_apres, case_y_apres)

    def effacer_piece(self, case_x, case_y):
        self.zone_dessin.effacer_piece(case_x, case_y)

    def fermer_fenetre(self):
        self.window.destroy()

    def creer_gui_promotion(self, couleur):
        self.gui_promotion = GUIPromotion(self.controleur, self.window, couleur)
        self.window.wait_window(self.gui_promotion.window)  # Tant que la fenêtre enfant n'est pas fermée, le programme est retenu ici

    def get_nom_piece_promotion(self, case):
        return self.gui_promotion.get_nom_piece(case)

    def fermer_fenetre_promotion(self):
        self.gui_promotion.fermer_fenetre()
        del self.gui_promotion

    def reset(self):
        self.modifier_infos("Bienvenue !", COULEUR_INFOS)
        self.zone_dessin.reset()

class GUIPromotion:
    def __init__(self, controleur, fenetre_parent, couleur):
        # Contrôleur
        self.controleur = controleur

        # Références
        self.fenetre_parent = fenetre_parent

        self.creer_gui_promotion(couleur)
        self.lier_souris()

    def creer_gui_promotion(self, couleur):
        # Fenêtre
        self.window = tk.Toplevel(self.fenetre_parent)
        self.window.title("Promotion")
        self.window.transient(self.fenetre_parent)  # Permet de garder la fenêtre devant parent
        self.window.grab_set()  # Redirige tous les évenements vers cette fenêtre, empêchant l'interaction avec la fenêtre principale

        # Zone de dessin
        self.zone_dessin = ZoneDessinPromotion(self.window, couleur)

        self.window.protocol("WM_DELETE_WINDOW", self.gestion_quitter)

        # Update pour pouvoir calculer la taille du canvas
        self.window.update()

    # Actions utilisateur

    def gestion_souris(self, evt):
        if self.controleur is not None:
            # Clic gauche
            if evt.num == 1:
                self.controleur.gestion_clic_gauche_promotion(evt)
        else:
            raise AttributeError("Aucun controleur n'est enregistré pour la partie graphique.")

    def gestion_quitter(self):
        if self.controleur is not None:
            self.controleur.gestion_quitter_promotion()
        else:
            raise AttributeError("Aucun controleur n'est enregistré pour la partie graphique.")

    # Appels contrôleur

    def get_nom_piece(self, case):
        return self.zone_dessin.get_nom_piece(case)

    def lier_souris(self):
        self.zone_dessin.canvas.bind("<1>", self.gestion_souris)

    def fermer_fenetre(self):
        self.window.destroy()

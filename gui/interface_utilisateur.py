### Bibliothèques ######################################################################################################
### Externes ###
import tkinter as tk
### Fichiers internes ###
from .damier import Damier
### Paramètres de jeu ###
from core.constantes import NB_COLONNES, NB_LIGNES, LARGEUR, HAUTEUR, NB_TYPES_PIECES, NB_LIGNES_PROMOTION, \
                       LARGEUR_PROMOTION, HAUTEUR_PROMOTION

### Classes ############################################################################################################


class MainGUI:
    def __init__(self, jeu):
        # Références
        self.jeu = jeu

        self.creer_main_gui()
        self.lier_souris()

    def creer_main_gui(self):
        # Fenêtre
        self.window = tk.Tk()
        self.window.title("Echecs")

        # Zone de dessin
        self.canvas = tk.Canvas(self.window, bg="white", width=LARGEUR, height=HAUTEUR)
        self.canvas.grid(row=0, column=0, columnspan=2)

        # Damier
        self.damier = Damier(self.canvas, NB_COLONNES, NB_LIGNES, LARGEUR, HAUTEUR)

        # Infos de jeu
        self.infos = tk.Label(self.window, text="Test")
        self.infos.grid(row=1, column=0, columnspan=2)

        # Boutons
        self.button1 = tk.Button(self.window, text="Nouvelle partie", command=self.jeu.nouvelle_partie)
        self.button1.grid(row=2, column=0)
        self.button2 = tk.Button(self.window, text='Quitter', command=self.window.destroy)
        self.button2.grid(row=2, column=1)

        self.window.update()  # .update() met à jour l'interface utilisateur avec les modifications apportées précédemment. Sans ça, le calcul de la taille du canvas est fait plus tard, dans le mainloop donc en utilisant main_canvas.winfo_width(), on obtient 1 et pas la taille réelle

    def gestion_souris(self, evt):
        # Clic gauche
        if evt.num == 1:
            self.jeu.gestion_clic_gauche(evt)

    def lier_souris(self):
        self.canvas.bind("<1>", self.gestion_souris)

    def desactiver_souris(self):
        self.canvas.unbind("<1>")

    def modifier_infos(self, texte, couleur):
        self.infos.config(text=texte, fg=couleur)

    def creer_image_canvas(self, x, y, image):
        self.canvas.create_image(x, y, image=image)

    def deplacer_objet_canvas(self, objet, x, y):
        self.canvas.coords(objet, x, y)

    def effacer_objet_canvas(self, objet):
        self.canvas.delete(objet)


class GUIPromotion:
    def __init__(self, jeu, fenetre_parent):
        # Références
        self.jeu = jeu
        self.fenetre_parent = fenetre_parent

        self.creer_gui_promotion()
        self.lier_souris()

    def creer_gui_promotion(self):
        # Fenêtre
        self.window = tk.Toplevel(self.fenetre_parent)
        self.window.title("Promotion")
        self.window.transient(self.fenetre_parent)  # Permet de garder la fenêtre devant parent
        self.window.grab_set()  # Redirige tous les évenements vers cette fenêtre, empêchant l'interaction avec la fenêtre principale

        # Zone de dessin
        self.canvas = tk.Canvas(self.window, bg="white", width=LARGEUR_PROMOTION,
                                height=HAUTEUR_PROMOTION)
        self.canvas.pack()

        # Damier
        self.damier = Damier(self.canvas, NB_TYPES_PIECES, NB_LIGNES_PROMOTION, LARGEUR_PROMOTION,
                             HAUTEUR_PROMOTION)

        self.window.protocol("WM_DELETE_WINDOW", self.jeu.annuler)

        # Update pour pouvoir calculer la taille du canvas
        self.window.update()

    def gestion_souris(self, evt):
        # Clic gauche
        if evt.num == 1:
            self.jeu.gestion_clic_gauche(evt)

    def lier_souris(self):
        self.canvas.bind("<1>", self.gestion_souris)

    def fermer_fenetre(self):
        self.window.destroy()


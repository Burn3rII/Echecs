### Bibliothéques ######################################################################################################
### Externes ###
import tkinter as tk
### Fichiers internes ###
from damier import Damier
from pieces import Piece, Pion, Tour, Cavalier, Fou, Reine
### Paramètres de jeu ###
from constantes import NB_TYPES_PIECES, NB_LIGNES_PROMOTION, LARGEUR_PROMOTION, HAUTEUR_PROMOTION, COULEUR_PIECE1, \
                       COULEUR_PIECE2


class Promotion:
    def __init__(self, parent, couleur, proprietaire):
        # Fenêtre
        self.window_promotion = tk.Toplevel(parent)
        self.window_promotion.title("Promotion")
        self.window_promotion.transient(parent)  # Permet de garder la fenêtre devant parent
        self.window_promotion.grab_set()  # Redirige tous les évenements vers cette fenêtre, empêchant l'interaction avec la fenêtre principale

        # Canvas
        self.canvas_promotion = tk.Canvas(self.window_promotion, bg="white", width=LARGEUR_PROMOTION,
                                          height=HAUTEUR_PROMOTION)
        self.canvas_promotion.pack()

        # Update du canvas pour pouvoir calculer sa taille
        self.window_promotion.update()

        # Damier
        self.damier = Damier(self.canvas_promotion, NB_TYPES_PIECES, NB_LIGNES_PROMOTION, LARGEUR_PROMOTION,
                             HAUTEUR_PROMOTION)

        # Pieces
        self.pieces = [0] * NB_TYPES_PIECES
        self.generer_pieces(couleur, proprietaire)

        # Binding
        self.canvas_promotion.bind("<1>", self.gestion_souris)

        self.choix_piece = 0

        self.window_promotion.protocol("WM_DELETE_WINDOW", lambda: self.annuler(couleur, proprietaire))

    def generer_pieces(self, couleur, proprietaire):
        j = 0  # Sert à ne pas avoir d'indice vide dans le tableau
        for i, piece in enumerate(Piece.__subclasses__()):
            if piece.__name__ not in ('Pion', 'Roi'):
                self.pieces[i - j] = piece(self.canvas_promotion, NB_TYPES_PIECES, NB_LIGNES_PROMOTION, proprietaire,
                                           couleur, i - j, 0)
            else:
                j += 1

    def gestion_souris(self, evt):
        # Clic gauche
        if evt.num == 1:
            case_x = int(evt.x * NB_TYPES_PIECES // LARGEUR_PROMOTION)
            self.selectionner_piece(self.pieces[case_x])

    def selectionner_piece(self, piece):
        self.choix_piece = piece
        self.window_promotion.destroy()

    def annuler(self, couleur, proprietaire):
        self.choix_piece = Reine(self.canvas_promotion, NB_TYPES_PIECES, NB_LIGNES_PROMOTION, proprietaire, couleur, 0,
                                 0)
        self.window_promotion.destroy()

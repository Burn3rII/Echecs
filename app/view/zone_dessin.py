### Bibliothèques ######################################################################################################
### Externes ###
import tkinter as tk
### Fichiers internes ###
from .damier import Damier
from .pieces import Piece, Pion, Tour, Cavalier, Fou, Reine, Roi
### Paramètres de jeu ###
from . import NB_COLONNES, NB_LIGNES, LARGEUR, HAUTEUR, LARGEUR_PROMOTION, HAUTEUR_PROMOTION, NB_TYPES_PIECES, \
              NB_LIGNES_PROMOTION

### Classes ############################################################################################################


class ZoneDessin:
    """Gestion du canvas principal"""

    def __init__(self, window):
        # Références
        self.window = window

        # Zone de dessin
        self.canvas = tk.Canvas(self.window, bg="white", width=LARGEUR, height=HAUTEUR)
        self.canvas.grid(row=0, column=0, columnspan=2)
        self.canvas.update()  # .update() met à jour l'interface utilisateur avec les modifications apportées
        # précédemment. Sans ça, le calcul de la taille du canvas est fait plus tard, en lançant mainloop donc en
        # utilisant main_canvas.winfo_width(), on obtient 1 et pas la taille réelle

        # Damier
        self.damier = Damier(self.canvas, NB_COLONNES, NB_LIGNES)

        # Pièces
        self.pieces = [[None] * NB_LIGNES for _ in range(NB_COLONNES)]

    def dessiner_piece(self, piece, case_x, case_y, couleur):
        """L'argument piece doit être une str correspond au nom de la classe, par exemple "Pion" pour un pion."""
        classe = globals().get(piece)  # Transformation de la str en nom de classe.
        if classe is not None and issubclass(classe, Piece):
            self.pieces[case_x][case_y] = classe(self.canvas, NB_COLONNES, NB_LIGNES, case_x, case_y, couleur)
        else:
            raise ValueError("Classe de la pièce à créer invalide")

    def changer_couleur_case(self, case_x, case_y, couleur):
        self.damier.changer_couleur_case(case_x, case_y, couleur)

    def reset_couleur_case(self, case_x, case_y):
        self.damier.reset_couleur_case(case_x, case_y)

    def effacer_piece(self, case_x, case_y):
        try:
            self.pieces[case_x][case_y].effacer_image()
            self.pieces[case_x][case_y] = None
        except AttributeError:
            # La case ne contient pas une pièce
            pass

    def deplacer_piece(self, case_x_avant, case_y_avant, case_x_apres, case_y_apres):
        if self.pieces[case_x_apres][case_y_apres] is None:
            self.pieces[case_x_avant][case_y_avant].deplacer_piece(NB_COLONNES, NB_LIGNES, case_x_apres, case_y_apres)
            self.pieces[case_x_apres][case_y_apres] = self.pieces[case_x_avant][case_y_avant]
            self.pieces[case_x_avant][case_y_avant] = None
        else:
            raise ValueError("Déplacement d'une pièce vers un emplacement contenant déjà une pièce.")

    def reset(self):
        # Pièces
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.pieces[i][j] is not None:
                    self.effacer_piece(i, j)
        # Damier
        self.damier.reset()


class ZoneDessinPromotion:
    """Gestion du canvas de la fenêtre de promotion"""

    def __init__(self, window, couleur):
        # Références
        self.window = window

        # Zone de dessin
        self.canvas = tk.Canvas(self.window, bg="white", width=LARGEUR_PROMOTION, height=HAUTEUR_PROMOTION)
        self.canvas.pack()
        self.canvas.update()  # .update() met à jour l'interface utilisateur avec les modifications apportées
        # précédemment. Sans ça, le calcul de la taille du canvas est fait plus tard, dans le mainloop donc en
        # utilisant main_canvas.winfo_width(), on obtient 1 et pas la taille réelle

        # Damier
        self.damier = Damier(self.canvas, NB_TYPES_PIECES, NB_LIGNES_PROMOTION)

        # Pieces
        self.pieces = [None] * NB_TYPES_PIECES
        self.dessiner_pieces(couleur)

    def get_nom_piece(self, case):
        """Renvoie une str du nom de classe """
        return type(self.pieces[case]).__name__

    def dessiner_piece(self, piece, case_x, case_y, couleur):
        """L'argument piece doit être une str correspond au nom de la classe, par exemple "Pion" pour un pion."""
        classe = globals().get(piece)  # Transformation de la str en nom de classe.
        if classe is not None and issubclass(classe, Piece):
            self.pieces[case_x] = classe(self.canvas, NB_TYPES_PIECES, NB_LIGNES_PROMOTION, case_x, case_y, couleur)
        else:
            raise ValueError("Classe de la pièce à créer invalide")

    def dessiner_pieces(self, couleur):
        j = 0  # Sert à ne pas avoir d'indice vide dans le tableau
        for i, piece in enumerate(Piece.__subclasses__()):
            if piece.__name__ not in ('Pion', 'Roi'):
                self.dessiner_piece(piece.__name__, i-j, 0, couleur)
            else:
                j += 1

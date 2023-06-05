### Bibliothéques ######################################################################################################
### Externes ###
from PIL import ImageTk, Image
### Paramètres de jeu ###
from constantes import *


class Piece:
    """Super classe des pièces"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y):
        largeur = canvas.winfo_width()
        hauteur = canvas.winfo_height()

        self.proprietaire = proprietaire
        self.couleur = couleur

        # Image
        x, y = (case_x + 1 / 2) * largeur / nb_colonnes, (case_y + 1 / 2) * hauteur / nb_lignes
        rayon_x = int(largeur / (2 * nb_colonnes) - 10)
        rayon_y = int(hauteur / (2 * nb_lignes) - 10)
        self.image_tk = ImageTk.PhotoImage(Image.open(image).resize((2 * rayon_x, 2 * rayon_y)))
        self.image_canvas = canvas.create_image(x, y, image=self.image_tk)  # Ici on utilise self sur image_canvas car on veut la conserver.
                                                                            # Il faut aussi le mettre sur image_tk car on doit la conserver pour image_canvas
                                                                            # On ne met pas self sur les variables qui doivent être détruite
                                                                            # à la fin de la méthode.

    def recreer_image(self, canvas, x, y):
        self.image_canvas = canvas.create_image(x, y, image=self.image_tk)


class Pion(Piece):
    """Pion"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "Images/PionB.png" if couleur == COULEUR_PIECE2 else "Images/PionN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(0, 1), (0, 2)]] if self.couleur == COULEUR_PIECE2 else [[(0, -1), (0, -2)]]
        self.attaques = [[(1, 1)], [(-1, 1)]] if self.couleur == COULEUR_PIECE2 else [[(-1, -1)], [(1, -1)]]


class Tour(Piece):
    """Tour"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "Images/TourB.png" if couleur == COULEUR_PIECE2 else "Images/TourN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                             [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                             [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                             [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]]
        self.a_bouge = False  # Pour le roque


class Cavalier(Piece):
    """Cavalier"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "Images/CavalierB.png" if couleur == COULEUR_PIECE2 else "Images/CavalierN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(1, 2)], [(2, 1)], [(1, -2)], [(2, -1)], [(-1, 2)], [(-2, 1)], [(-1, -2)], [(-2, -1)]]


class Fou(Piece):
    """Fou"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "Images/FouB.png" if couleur == COULEUR_PIECE2 else "Images/FouN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                             [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                             [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)],
                             [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]]


class Reine(Piece):
    """Reine"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "Images/ReineB.png" if couleur == COULEUR_PIECE2 else "Images/ReineN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                             [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                             [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                             [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)],
                             [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                             [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                             [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)],
                             [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]]


class Roi(Piece):
    """Roi"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "Images/RoiB.png" if couleur == COULEUR_PIECE2 else "Images/RoiN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(0, 1)], [(-1, 0)], [(0, -1)], [(1, 0)],
                             [(1, 1)], [(1, -1)], [(-1, -1)], [(-1, 1)]]
        self.a_bouge = False  # Pour le roque

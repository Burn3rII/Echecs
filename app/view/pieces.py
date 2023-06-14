### Bibliothèques ######################################################################################################
### Externes ###
from PIL import ImageTk, Image
import os
### Paramètres de jeu ###
from . import COULEUR_PIECE1

### Classes ############################################################################################################


class Piece:
    """Super classe des pièces"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, case_x, case_y, image):
        # Références
        self.canvas = canvas

        largeur_canvas = self.canvas.winfo_width()
        hauteur_canvas = self.canvas.winfo_height()

        x, y = (case_x + 1 / 2) * largeur_canvas / nb_colonnes, (case_y + 1 / 2) * hauteur_canvas / nb_lignes
        rayon_x = int(largeur_canvas / (2 * nb_colonnes) - 10)
        rayon_y = int(hauteur_canvas / (2 * nb_lignes) - 10)

        self.image_tk = ImageTk.PhotoImage(Image.open(image).resize((2 * rayon_x, 2 * rayon_y)))
        self.image_canvas = canvas.create_image(x, y, image=self.image_tk)  # Ici, on utilise self sur image_canvas car
        # on veut la conserver. Il faut aussi le mettre sur image_tk car on doit la conserver pour image_canvas. On ne
        # met pas self sur les variables qui doivent être détruite à la fin de la méthode.

    def deplacer_piece(self, nb_colonnes, nb_lignes, case_x, case_y):
        largeur_canvas = self.canvas.winfo_width()
        hauteur_canvas = self.canvas.winfo_height()

        x, y = (case_x + 1 / 2) * largeur_canvas / nb_colonnes, (case_y + 1 / 2) * hauteur_canvas / nb_lignes

        self.canvas.coords(self.image_canvas, x, y)

    def effacer_image(self):
        self.canvas.delete(self.image_canvas)  # Il faut détruire manuellement l'image dans le canvas car elle reste
        # même si l'objet est détruit (un objet de canvas existe toujours même s'il n'est plus référencé). Il est par
        # contre inutile de faire quoi que ce soit pour image_tk qui se détruit quand elle n'est plus référencée.


class Pion(Piece):
    """Pion"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, case_x, case_y, couleur):
        image_folder = os.path.join(os.path.dirname(__file__), "Images")  # Création du chemin vers le dossier Images
        image = os.path.join(image_folder, "PionB.png") if couleur != COULEUR_PIECE1 \
           else os.path.join(image_folder, "PionN.png")
        super().__init__(canvas, nb_colonnes, nb_lignes, case_x, case_y, image)


class Tour(Piece):
    """Tour"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, case_x, case_y, couleur):
        image_folder = os.path.join(os.path.dirname(__file__), "Images")  # Création du chemin vers le dossier Images
        image = os.path.join(image_folder, "TourB.png") if couleur != COULEUR_PIECE1 \
           else os.path.join(image_folder, "TourN.png")
        super().__init__(canvas, nb_colonnes, nb_lignes, case_x, case_y, image)


class Cavalier(Piece):
    """Cavalier"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, case_x, case_y, couleur):
        image_folder = os.path.join(os.path.dirname(__file__), "Images")  # Création du chemin vers le dossier Images
        image = os.path.join(image_folder, "CavalierB.png") if couleur != COULEUR_PIECE1 \
           else os.path.join(image_folder, "CavalierN.png")
        super().__init__(canvas, nb_colonnes, nb_lignes, case_x, case_y, image)


class Fou(Piece):
    """Fou"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, case_x, case_y, couleur):
        image_folder = os.path.join(os.path.dirname(__file__), "Images")  # Création du chemin vers le dossier Images
        image = os.path.join(image_folder, "FouB.png") if couleur != COULEUR_PIECE1 \
           else os.path.join(image_folder, "FouN.png")
        super().__init__(canvas, nb_colonnes, nb_lignes, case_x, case_y, image)


class Reine(Piece):
    """Reine"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, case_x, case_y, couleur):
        image_folder = os.path.join(os.path.dirname(__file__), "Images")  # Création du chemin vers le dossier Images
        image = os.path.join(image_folder, "ReineB.png") if couleur != COULEUR_PIECE1 \
           else os.path.join(image_folder, "ReineN.png")
        super().__init__(canvas, nb_colonnes, nb_lignes, case_x, case_y, image)


class Roi(Piece):
    """Roi"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, case_x, case_y, couleur):
        image_folder = os.path.join(os.path.dirname(__file__), "Images")  # Création du chemin vers le dossier Images
        image = os.path.join(image_folder, "RoiB.png") if couleur != COULEUR_PIECE1 \
           else os.path.join(image_folder, "RoiN.png")
        super().__init__(canvas, nb_colonnes, nb_lignes, case_x, case_y, image)

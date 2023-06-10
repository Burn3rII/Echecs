### Bibliothèques ######################################################################################################
### Externes ###
from PIL import ImageTk, Image
### Paramètres de jeu ###
from core.constantes import COULEUR_PIECE2

### Classes ############################################################################################################


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
        self.image_canvas = canvas.create_image(x, y, image=self.image_tk)  # Ici, on utilise self sur image_canvas car on veut la conserver.
                                                                            # Il faut aussi le mettre sur image_tk car on doit la conserver pour image_canvas
                                                                            # On ne met pas self sur les variables qui doivent être détruite
                                                                            # à la fin de la méthode.

    def __getstate__(self):
        """Renvoie un tuple contenant les informations nécessaires à la sérialisation de l'objet.
        Sérialiser un objet permet d'en obtenir une représentation binaire. On utilise pour cela la fonction 'pickle',
        qui appel la fonction __getstate__ dans le cas où la chose à sérialiser est un objet de classe personnalisée.
        (Pickle sait sérialiser un int (par exemple) mais il faut lui fournir la méthode pour sérialiser les classes
        personnalisées).

        Les types suivants sont 'pickable':
        -> None, True, and False;
        -> integers, floating-point numbers, complex numbers;
        -> strings, bytes, bytearrays;
        -> tuples, lists, sets, and dictionaries containing only picklable objects;
        -> functions (built-in and user-defined) accessible from the top level of a module (using def, not lambda);
        -> classes accessible from the top level of a module;
        -> instances of such classes whose the result of calling __getstate__() is picklable."""

        return (self.proprietaire, self.couleur)  # On ne prend pas en compte l'image car 2 cavaliers de même couleur (par exemple) sont considérés comme la même pièce. Si les 2 cavaliers échangent leur place, le plateau est quand même considéré comme étant le même.

    def recreer_image(self, canvas, x, y):
        self.image_canvas = canvas.create_image(x, y, image=self.image_tk)


class Pion(Piece):
    """Pion"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "../gui/Images/PionB.png" if couleur == COULEUR_PIECE2 else "../gui/Images/PionN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(0, 1), (0, 2)]] if self.couleur == COULEUR_PIECE2 else [[(0, -1), (0, -2)]]
        self.attaques = [[(1, 1)], [(-1, 1)]] if self.couleur == COULEUR_PIECE2 else [[(-1, -1)], [(1, -1)]]
        self.a_bouge = False

    def __getstate__(self):
        """Renvoie un tuple contenant les informations nécessaires à la sérialisation de l'objet. Contient également les
        informations de la super classe pour une représentation complète de la pièce."""

        state = super().__getstate__() # Appel de la méthode __getstate__ de la superclasse pour obtenir l'état sérialisable de la pièce
        state += (self.deplacements, self.attaques, self.a_bouge)  # Ajout des informations spécifiques au Pion
        return state


class Tour(Piece):
    """Tour"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "../gui/Images/TourB.png" if couleur == COULEUR_PIECE2 else "../gui/Images/TourN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                             [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                             [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                             [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]]
        self.peut_roquer = True

    def __getstate__(self):
        """Renvoie un tuple contenant les informations nécessaires à la sérialisation de l'objet. Contient également les
        informations de la super classe pour une représentation complète de la pièce."""

        state = super().__getstate__() # Appel de la méthode __getstate__ de la superclasse pour obtenir l'état sérialisable de la pièce
        state += (self.deplacements, self.peut_roquer)  # Ajout des informations spécifiques à la Tour
        return state


class Cavalier(Piece):
    """Cavalier"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "../gui/Images/CavalierB.png" if couleur == COULEUR_PIECE2 else "../gui/Images/CavalierN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(1, 2)], [(2, 1)], [(1, -2)], [(2, -1)], [(-1, 2)], [(-2, 1)], [(-1, -2)], [(-2, -1)]]

    def __getstate__(self):
        """Renvoie un tuple contenant les informations nécessaires à la sérialisation de l'objet. Contient également les
        informations de la super classe pour une représentation complète de la pièce."""

        state = super().__getstate__() # Appel de la méthode __getstate__ de la superclasse pour obtenir l'état sérialisable de la pièce
        state += (self.deplacements,)  # Ajout des informations spécifiques au Cavalier. La virgule à la fin sert à différencier un tuple d'une simple valeur
        return state

class Fou(Piece):
    """Fou"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "../gui/Images/FouB.png" if couleur == COULEUR_PIECE2 else "../gui/Images/FouN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                             [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                             [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)],
                             [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]]

    def __getstate__(self):
        """Renvoie un tuple contenant les informations nécessaires à la sérialisation de l'objet. Contient également les
        informations de la super classe pour une représentation complète de la pièce."""

        state = super().__getstate__() # Appel de la méthode __getstate__ de la superclasse pour obtenir l'état sérialisable de la pièce
        state += (self.deplacements,)  # Ajout des informations spécifiques au Fou. La virgule à la fin sert à différencier un tuple d'une simple valeur
        return state

class Reine(Piece):
    """Reine"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "../gui/Images/ReineB.png" if couleur == COULEUR_PIECE2 else "../gui/Images/ReineN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                             [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                             [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                             [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)],
                             [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                             [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                             [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)],
                             [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]]

    def __getstate__(self):
        """Renvoie un tuple contenant les informations nécessaires à la sérialisation de l'objet. Contient également les
        informations de la super classe pour une représentation complète de la pièce."""

        state = super().__getstate__() # Appel de la méthode __getstate__ de la superclasse pour obtenir l'état sérialisable de la pièce
        state += (self.deplacements,)  # Ajout des informations spécifiques à la Reine. La virgule à la fin sert à différencier un tuple d'une simple valeur
        return state

class Roi(Piece):
    """Roi"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, proprietaire, couleur, case_x, case_y):
        image = "../gui/Images/RoiB.png" if couleur == COULEUR_PIECE2 else "../gui/Images/RoiN.png"
        super().__init__(canvas, nb_colonnes, nb_lignes, proprietaire, couleur, image, case_x, case_y)
        self.deplacements = [[(0, 1)], [(-1, 0)], [(0, -1)], [(1, 0)],
                             [(1, 1)], [(1, -1)], [(-1, -1)], [(-1, 1)]]
        self.peut_roquer = True

    def __getstate__(self):
        """Renvoie un tuple contenant les informations nécessaires à la sérialisation de l'objet. Contient également les
        informations de la super classe pour une représentation complète de la pièce."""

        state = super().__getstate__() # Appel de la méthode __getstate__ de la superclasse pour obtenir l'état sérialisable de la pièce
        state += (self.deplacements, self.peut_roquer)  # Ajout des informations spécifiques au Roi
        return state

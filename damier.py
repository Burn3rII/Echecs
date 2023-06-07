### Bibliothèques ######################################################################################################
### Paramètres de jeu ###
from constantes import COULEUR_DAMIER1, COULEUR_DAMIER2

### Classes ############################################################################################################


class Damier:
    """Gestion du damier"""

    def __init__(self, canvas, nb_colonnes, nb_lignes, largeur, hauteur):
        self.canvas = canvas
        self.largeur = largeur
        self.hauteur = hauteur
        self.nb_lignes = nb_lignes
        self.nb_colonnes = nb_colonnes

        self.grille = [[0] * self.nb_lignes for _ in range(self.nb_colonnes)]
        for i in range(self.nb_colonnes):
            for j in range(self.nb_lignes):
                self.dessiner_case(i, j, COULEUR_DAMIER1 if (i + j) % 2 == 0 else COULEUR_DAMIER2, self.grille)

    def dessiner_case(self, case_x, case_y, couleur, conteneur):
        x, y = (case_x + 1 / 2) * self.largeur / self.nb_colonnes, (case_y + 1 / 2) * self.hauteur / self.nb_lignes
        rayon_x = self.largeur / (2 * self.nb_colonnes)
        rayon_y = self.hauteur / (2 * self.nb_lignes)
        conteneur[case_x][case_y] = self.canvas.create_rectangle(x - rayon_x, y - rayon_y, x + rayon_x, y + rayon_y,
                                                                 fill=couleur)

    def changer_couleur_case(self, case_x, case_y, couleur):
        self.canvas.itemconfigure(self.grille[case_x][case_y], fill=couleur)

    def reset(self):
        for i in range(self.nb_colonnes):
            for j in range(self.nb_lignes):
                self.changer_couleur_case(i, j, COULEUR_DAMIER1 if (i + j) % 2 == 0 else COULEUR_DAMIER2)

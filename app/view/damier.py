"""Classe gérant un damier. Le canvas dans lequel doit être créé le damier
est passé en argument.
"""

# -------------------------Bibliothèques---------------------------------------

# -------------------------Classes---------------------------------------------


class Damier:
    """Gestion du damier
    """

    COULEUR_DAMIER1, COULEUR_DAMIER2 = "#DAB790", "#9D551E"

    def __init__(self, canvas, nb_colonnes, nb_lignes):
        # Références
        self.canvas = canvas

        # Paramètres
        self.largeur = canvas.winfo_width()
        self.hauteur = canvas.winfo_height()
        self.nb_lignes = nb_lignes
        self.nb_colonnes = nb_colonnes

        # Cases
        self.grille = [[0] * self.nb_lignes for _ in range(self.nb_colonnes)]
        for i in range(self.nb_colonnes):
            for j in range(self.nb_lignes):
                self.dessiner_case(i, j, Damier.COULEUR_DAMIER1
                                   if (i + j) % 2 == 0
                                   else Damier.COULEUR_DAMIER2)

    def dessiner_case(self, case_x, case_y, couleur):
        """Dessine la case demandée de la couleur demandée.
        """
        centre_x = (case_x + 1 / 2) * self.largeur / self.nb_colonnes
        centre_y = (case_y + 1 / 2) * self.hauteur / self.nb_lignes
        rayon_x = self.largeur / (2 * self.nb_colonnes)
        rayon_y = self.hauteur / (2 * self.nb_lignes)
        self.grille[case_x][case_y] = self.canvas.create_rectangle(
            centre_x - rayon_x, centre_y - rayon_y,
            centre_x + rayon_x, centre_y + rayon_y, fill=couleur)

    def changer_couleur_case(self, case_x, case_y, couleur):
        """Change la couleur de la case donnée.
        """
        self.canvas.itemconfigure(self.grille[case_x][case_y], fill=couleur)

    def reset_couleur_case(self, case_x, case_y):
        """Remet la case donnée à la couleur par défaut.
        """
        couleur = (Damier.COULEUR_DAMIER1 if (case_x + case_y) % 2 == 0
                   else Damier.COULEUR_DAMIER2)
        self.canvas.itemconfigure(self.grille[case_x][case_y], fill=couleur)

    def reset(self):
        """Remet toutes les cases à leur couleur par défaut.
        """
        for i in range(self.nb_colonnes):
            for j in range(self.nb_lignes):
                self.reset_couleur_case(i, j)

### Bibliothèques ######################################################################################################
### Fichiers internes ###
from gui.interface_utilisateur import GUIPromotion
from pieces import Piece, Reine
### Paramètres de jeu ###
from core.constantes import NB_TYPES_PIECES, NB_LIGNES_PROMOTION, LARGEUR_PROMOTION

### Classes ############################################################################################################


class Promotion:
    def __init__(self, fenetre_parent, couleur, proprietaire):
        # Interface utilisateur
        self.gui = GUIPromotion(self, fenetre_parent)

        # Joueur
        self.couleur = couleur
        self.proprietaire = proprietaire

        # Pieces
        self.pieces = [0] * NB_TYPES_PIECES
        self.generer_pieces()

        self.choix_piece = 0

    def generer_pieces(self):
        j = 0  # Sert à ne pas avoir d'indice vide dans le tableau
        for i, piece in enumerate(Piece.__subclasses__()):
            if piece.__name__ not in ('Pion', 'Roi'):
                self.pieces[i - j] = piece(self.gui.canvas, NB_TYPES_PIECES, NB_LIGNES_PROMOTION, self.proprietaire,
                                           self.couleur, i - j, 0)
            else:
                j += 1

    def gestion_clic_gauche(self, evt):
        if evt.num == 1:
            case_x = int(evt.x * NB_TYPES_PIECES // LARGEUR_PROMOTION)
            self.selectionner_piece(self.pieces[case_x])
        else:
            raise ValueError("La fonction responsable du clic gauche a été appelée par un moyen qu'un clic gauche.")

    def selectionner_piece(self, piece):
        self.choix_piece = piece
        self.gui.fermer_fenetre()

    def annuler(self):
        self.choix_piece = Reine(self.gui.canvas, NB_TYPES_PIECES, NB_LIGNES_PROMOTION, self.proprietaire, self.couleur,
                                 0, 0)
        self.gui.fermer_fenetre()

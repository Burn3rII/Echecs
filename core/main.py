# TODO
#   Amélioration possible: utilisation, à la place des tableaux 2D de dictionnaires. On utiliserait alors la case (par
#   exemple 'e4' comme clé et on associerait chaque clé à la pièce (objet de type Piece) sur cette case.
#   Cela nécessite cependant de recoder beaucoup de méthodes.
#   Gestionnaire d'erreurs (par exemple pour maj_infos)
#   Fonction temps
#   Autres fonctions
#   Améliorer graphiques
#   Diviser Promotion en une fenêtre et un corps
#   Ajouter une demande si l'utilisateur quitte en utilisant la croix ou le bouton s'il veut vraiment quitter

### Bibliothèques ######################################################################################################
### Fichiers internes ###
from gui.interface_utilisateur import MainGUI
from plateau import Plateau
from gestionnaire_fin_jeu import GestionnaireConditionsVictoire, GestionnaireFinJeu
### Paramètres de jeu ###
from constantes import NB_LIGNES, NB_COLONNES, LARGEUR, HAUTEUR, COULEUR_INFOS, COULEUR_INFOS_FIN_JEU

### Classes ############################################################################################################


class Jeu:
    """Gestion générale du jeu"""

    def __init__(self):
        # Interface utilisateur
        self.gui = MainGUI(self)

        # Plateau
        self.plateau = Plateau(self.gui)

        # Attributs
        self.joueur_actif = 1
        self.nb_tours = 1

        # Gestionnaire fin de jeu
        self.gestionnaire_conditions_arret = GestionnaireConditionsVictoire(self.plateau, self.gui)

        # Lancement boucle
        self.gui.window.mainloop()

    def gestion_clic_gauche(self, evt):
        if evt.num == 1:
            adversaire = self.joueur_actif % 2 + 1
            case_x, case_y = int(evt.x * NB_COLONNES // LARGEUR), int(evt.y * NB_LIGNES / HAUTEUR)
            if self.plateau.case_active == (None, None):
                self.plateau.selectionner_piece(case_x, case_y, self.joueur_actif, adversaire)
            else:
                if self.plateau.coups_possibles[case_x][case_y] == self.plateau.d_coups["oui"]:
                    self.plateau.jouer_coup(case_x, case_y, False)
                    self.gestionnaire_conditions_arret.gerer_conditions_arret(self.joueur_actif, adversaire)
                    self.maj_infos()
                elif self.plateau.coups_possibles[case_x][case_y] == self.plateau.d_coups["roque"]:
                    self.plateau.jouer_coup(case_x, case_y, True)
                    self.gestionnaire_conditions_arret.gerer_conditions_arret(self.joueur_actif, adversaire)
                    self.maj_infos()
                else:
                    self.plateau.deselectionner_piece_active()
        else:
            raise ValueError("La fonction responsable du clic gauche a été appelée par un moyen qu'un clic gauche.")

    def maj_infos(self):
        if self.gestionnaire_conditions_arret.gestionnaire_fin_jeu.etat_jeu == GestionnaireFinJeu.JEU_CONTINUE:
            self.joueur_actif = self.joueur_actif % 2 + 1
            self.nb_tours += 1
            self.gui.modifier_infos(f"Tour {self.nb_tours} - Au joueur {self.joueur_actif} de jouer", COULEUR_INFOS)
        elif self.gestionnaire_conditions_arret.gestionnaire_fin_jeu.etat_jeu == GestionnaireFinJeu.VICTOIRE:
            self.gui.modifier_infos(f"Victoire joueur {self.joueur_actif}", COULEUR_INFOS_FIN_JEU)
        elif self.gestionnaire_conditions_arret.gestionnaire_fin_jeu.etat_jeu == GestionnaireFinJeu.PAT:
            self.gui.modifier_infos("Égalité par pat", COULEUR_INFOS_FIN_JEU)
        elif self.gestionnaire_conditions_arret.gestionnaire_fin_jeu.etat_jeu == GestionnaireFinJeu.MANQUE_MATERIEL:
            self.gui.modifier_infos("Égalité par manque de matériel", COULEUR_INFOS_FIN_JEU)
        elif self.gestionnaire_conditions_arret.gestionnaire_fin_jeu.etat_jeu == \
                GestionnaireFinJeu.CINQUANTE_TOURS_SANS_EVOLUTION:
            self.gui.modifier_infos("Égalité car les 50 derniers coups consécutifs ont été joués par chaque joueur sans"
                                    "mouvement de pion ni prise de pièce.", COULEUR_INFOS_FIN_JEU)
        elif self.gestionnaire_conditions_arret.gestionnaire_fin_jeu.etat_jeu == \
                GestionnaireFinJeu.TROIS_FOIS_MEME_POSITION:
            self.gui.modifier_infos("Égalité car cette position a été atteinte 3 fois dans la partie.",
                                    COULEUR_INFOS_FIN_JEU)
        else:
            raise ValueError("L'état du jeu est inconnu.")

    def nouvelle_partie(self):
        self.plateau.reset()
        self.gestionnaire_conditions_arret.reset()
        self.gui.lier_souris()

        self.joueur_actif = 1
        self.nb_tours = 1

        self.gui.modifier_infos(f"Tour {self.nb_tours} - Au joueur {self.joueur_actif} de jouer", COULEUR_INFOS)


### Corps ##############################################################################################################

jeu = Jeu()

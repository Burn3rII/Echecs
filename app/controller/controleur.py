"""Contrôleur jeu d'échec. Son but est de faire de lien entre la partie
graphique et le modèle du jeu. Celle-ci fonctionne de la manière
suivante :
 * Une interface utilisateur et un modèle de jeu doivent lui être liés à
 sa création.
 * Le contrôleur contient alors 2 types de méthodes :
    → Des méthodes permettant de répondre aux actions de l'utilisateur,
    recues depuis l'interface utilisateur.
    → Des méthodes correspondant à des modifications apportées dans la
    partie modèle devant impliquer un changement visuel. Des méthodes de
    l'interface utilisateur sont alors appelées pour effectuer ces
    changements.
"""

# -------------------------Bibliothèques---------------------------------------
# ----- Fichiers internes
from . import GestionnaireFinJeu
# ----- Paramètres de jeu
from . import (NB_LIGNES, NB_COLONNES, LARGEUR, HAUTEUR, COULEUR_CASE_ACTIVE,
               COULEUR_COUP_POSSIBLE1, COULEUR_COUP_POSSIBLE2, COULEUR_INFOS,
               COULEUR_INFOS_FIN_JEU, NB_TYPES_PIECES, LARGEUR_PROMOTION)

# -------------------------Classes---------------------------------------------


class Controleur:
    """Contrôleur, faisant le pont entre la partie view et la partie
    model
    """
    def __init__(self, gui, modele):
        # Références
        self.gui = gui
        self.gui.enregistrer_controleur(self)
        self.modele = modele
        self.modele.enregistrer_observateur(self)

    def lancer_jeu(self):
        """Ajuste les derniers éléments du modèle et de l'interface
        utilisateur qui ne peuvent mis en place que lorsque le lien au
        contrôleur est fait puis lance le jeu. La méthode "lancer_jeu"
        de l'interface utilisateur doit être appelée en dernier, car
        elle lance la boucle sur la fenêtre graphique.
        """
        self.modele.lancer_jeu()
        self.gui.lancer_jeu()

    # Actions utilisateur

    def gestion_clic_gauche(self, evt):
        """Répond au clic gauche utilisateur sur le canvas principal.
        """
        if evt.num == 1:
            case_x = int(evt.x * NB_COLONNES // LARGEUR)
            case_y = int(evt.y * NB_LIGNES / HAUTEUR)

            if self.modele.get_case_active() == (None, None):
                self.modele.selectionner_piece(case_x, case_y)
            else:
                if (self.modele.get_coups_possibles()[case_x][case_y] ==
                        self.modele.get_dico_coups()["oui"]):
                    self.modele.jouer_coup(case_x, case_y, False)
                    self.modele.gerer_conditions_arret()
                    self.modele.maj_infos()
                elif (self.modele.get_coups_possibles()[case_x][case_y] ==
                      self.modele.get_dico_coups()["roque"]):
                    self.modele.jouer_coup(case_x, case_y, True)
                    self.modele.gerer_conditions_arret()
                    self.modele.maj_infos()
                else:
                    self.modele.deselectionner_piece_active()
        else:
            raise ValueError("La fonction responsable du clic gauche a été "
                             "appelée par un moyen qu'un clic gauche.")

    def gestion_nouvelle_partie(self):
        """Répond à l'appel utilisateur demandant de lancer une nouvelle
        partie.
        """
        self.modele.nouvelle_partie()

    def gestion_quitter(self):
        """Répond à l'appel utilisateur demandant de quitter la
        partie.
        """
        self.gui.fermer_fenetre()

    def gestion_clic_gauche_promotion(self, evt):
        """Répond au clic gauche utilisateur sur le canvas de
        promotion.
        """
        if evt.num == 1:
            case_x_choix = int(evt.x * NB_TYPES_PIECES // LARGEUR_PROMOTION)
            piece_choisie = self.gui.get_nom_piece_promotion(case_x_choix)
            self.gui.fermer_fenetre_promotion()
            self.modele.choisir_piece_promotion(piece_choisie)
        else:
            raise ValueError("La fonction responsable du clic gauche a été "
                             "appelée par un moyen qu'un clic gauche.")

    def gestion_quitter_promotion(self):
        """Répond à l'appel utilisateur demandant de quitter la
        promotion.
        """
        self.gui.fermer_fenetre_promotion()
        self.modele.choisir_piece_promotion()

    # Appels modèle

    def infos_modifiees(self):
        """Demande au gui de mettre à jour les informations du jeu.
        """
        etat_jeu = self.modele.get_etat_jeu()
        joueur_actif = self.modele.get_joueur_actif()
        nb_tours = self.modele.get_nb_tours()

        if etat_jeu == GestionnaireFinJeu.JEU_CONTINUE:
            self.gui.modifier_infos(f"Tour {nb_tours} - Au joueur "
                                    f"{joueur_actif} de jouer", COULEUR_INFOS)
        elif etat_jeu == GestionnaireFinJeu.VICTOIRE:
            self.gui.modifier_infos(f"Victoire joueur {joueur_actif}",
                                    COULEUR_INFOS_FIN_JEU)
        elif etat_jeu == GestionnaireFinJeu.PAT:
            self.gui.modifier_infos("Égalité par pat", COULEUR_INFOS_FIN_JEU)
        elif etat_jeu == GestionnaireFinJeu.MANQUE_MATERIEL:
            self.gui.modifier_infos("Égalité par manque de matériel",
                                    COULEUR_INFOS_FIN_JEU)
        elif etat_jeu == GestionnaireFinJeu.CINQUANTE_TOURS_SANS_EVOLUTION:
            self.gui.modifier_infos(
                "Égalité car les 50 derniers coups consécutifs ont été joués "
                "par chaque joueur sans mouvement de pion ni prise de pièce.",
                COULEUR_INFOS_FIN_JEU)
        elif etat_jeu == GestionnaireFinJeu.TROIS_FOIS_MEME_POSITION:
            self.gui.modifier_infos(
                "Égalité car cette position a été atteinte 3 fois dans la "
                "partie.", COULEUR_INFOS_FIN_JEU)
        else:
            raise ValueError("L'état du jeu est inconnu.")

    def piece_creee(self, piece, case_x, case_y, couleur):
        """Demande au gui de créer une pièce sur la case donnée de la
        couleur donnée. L'argument piece doit être une str correspond au
        nom de la classe, par exemple "Pion" pour un pion.
        """
        self.gui.dessiner_piece_canvas(piece, case_x, case_y, couleur)

    def case_activee(self, case_x, case_y):
        """Demande au gui de mettre en valeur la case active en
        changeant sa couleur.
        """
        self.gui.changer_couleur_case(case_x, case_y, COULEUR_CASE_ACTIVE)

    def case_desactivee(self, case_x, case_y):
        """Demande au gui de réinitialiser la couleur de la case
        active.
        """
        self.gui.reset_couleur_case(case_x, case_y)

    def coups_possibles_calcules(self, coups_possibles):
        """Demande au gui de mettre en valeur les cases des coups
        possibles en changeant leurs couleurs.
        """
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if (coups_possibles[i][j] ==
                        self.modele.get_dico_coups()["oui"]
                        or coups_possibles[i][j] ==
                        self.modele.get_dico_coups()["roque"]):
                    self.gui.changer_couleur_case(i, j, COULEUR_COUP_POSSIBLE1
                                                  if (i + j) % 2 == 0
                                                  else COULEUR_COUP_POSSIBLE2)

    def coups_possibles_effaces(self, coups_possibles):
        """Demande au gui de réinitialiser la couleur des cases des
        coups possibles.
        """
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if (coups_possibles[i][j] !=
                        self.modele.get_dico_coups()["non"]):
                    self.gui.reset_couleur_case(i, j)

    def piece_deplacee(self, case_x_avant, case_y_avant, case_x_apres,
                       case_y_apres):
        """Demande au gui de déplacer une pièce d'une case à une
        autre.
        """
        self.gui.deplacer_piece(case_x_avant, case_y_avant, case_x_apres,
                                case_y_apres)

    def piece_mangee(self, case_x, case_y):
        """Demande au gui d'effacer une pièce.
        """
        self.gui.effacer_piece(case_x, case_y)

    def promotion_en_cours(self, couleur):
        """Demande au gui de créer l'interface de choix de pièce pour la
        promotion.
        """
        self.gui.creer_gui_promotion(couleur)

    def piece_promue(self, piece_choisie, case_x, case_y, couleur):
        """Demande au gui de remplacer l'image de la pièce de la case
        donnée par l'image de la pièce choisie.
        """
        self.piece_mangee(case_x, case_y)
        self.piece_creee(piece_choisie, case_x, case_y, couleur)

    def jeu_arrete(self):
        """Demande au gui d'empêcher l'utilisateur d'effectuer des
        actions supplémentaires.
        """
        self.gui.desactiver_souris()

    def plateau_reset(self):
        """Demande au gui de réinitialiser l'état du plateau.
        """
        self.gui.reset()

    def jeu_reset(self):
        """Demande au gui de mettre à jour les infos de jeu et de lier
        la souris pour permettre à l'utilisateur de jouer.
        """
        self.infos_modifiees()
        self.gui.lier_souris()

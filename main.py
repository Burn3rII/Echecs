# TODO
#   3x même position pendant partie = fin (deux positions sont identiques si le trait est le même et si les possibilités
#   de prise en passant et de roque sont les mêmes)
#   Fonction temps
#   Autres fonctions
#   Améliorer graphiques

### Bibliothèques ######################################################################################################
### Externes ###
import tkinter as tk
from math import copysign
### Fichiers internes ###
from damier import Damier
from promotion import Promotion
from pieces import Pion, Tour, Cavalier, Fou, Reine, Roi
### Paramètres de jeu ###
from constantes import *

### Classes ############################################################################################################


class Plateau:
    """Gestion des pièces"""

    def __init__(self):
        # Damier
        self.damier = Damier(main_canvas, NB_COLONNES, NB_LIGNES, LARGEUR, HAUTEUR)

        # Dictionnaire des coups
        self.d_coups = {"non": 0, "oui": 1, "roque": 2}

        # Génération et dessin pièces
        self.coups = [[None] * NB_LIGNES for _ in range(NB_COLONNES)]  # Système de coord.: Premier indice vers la droite et deuxième vers le bas, à partir du coin haut gauche
        self.generer_pieces()

        self.case_active = (None, None)
        self.case_prise_en_passant = (None, None)

        # Déplacements légaux (ne prend pas en compte l'échec)
        self.deplacements_possibles = [[self.d_coups["non"]] * NB_LIGNES for _ in range(NB_COLONNES)]

        # Calcul de l'échec:
        self.pos_roi_b, self.pos_roi_n = (4, 0), (4, 7)
        self.cases_controlees = [[self.d_coups["non"]] * NB_LIGNES for _ in range(NB_COLONNES)]

        # Coups possibles (déplacements légaux + pas d'échec à son propre roi)
        self.coups_possibles = [[self.d_coups["non"]] * NB_LIGNES for _ in range(NB_COLONNES)]

        self.sauv_piece_mangee_fictivement = None

        # Informations sur le tour
        self.pion_bouge_ce_tour = False
        self.piece_mangee_ce_tour = False

    def generer_pieces(self):
        indices_lignes = [0, 1, NB_LIGNES - 2, NB_LIGNES - 1]
        for i in range(NB_COLONNES):
            for j in indices_lignes:
                if j in (1, NB_LIGNES - 2):
                    self.coups[i][j] = Pion(main_canvas, NB_COLONNES, NB_LIGNES, 1 if j == 1 else 2,
                                            COULEUR_PIECE2 if j == 1 else COULEUR_PIECE1, i, j)
                elif j in (0, NB_LIGNES - 1):
                    if i in (0, NB_COLONNES - 1):
                        self.coups[i][j] = Tour(main_canvas, NB_COLONNES, NB_LIGNES, 1 if j == 0 else 2,
                                                COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1, i, j)
                    elif i in (1, NB_COLONNES - 2):
                        self.coups[i][j] = Cavalier(main_canvas, NB_COLONNES, NB_LIGNES, 1 if j == 0 else 2,
                                                    COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1, i, j)
                    elif i in (2, NB_COLONNES - 3):
                        self.coups[i][j] = Fou(main_canvas, NB_COLONNES, NB_LIGNES, 1 if j == 0 else 2,
                                               COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1, i, j)
                    elif i == 3:
                        self.coups[i][j] = Reine(main_canvas, NB_COLONNES, NB_LIGNES, 1 if j == 0 else 2,
                                                 COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1, i, j)
                    elif i == NB_COLONNES - 4:
                        self.coups[i][j] = Roi(main_canvas, NB_COLONNES, NB_LIGNES, 1 if j == 0 else 2,
                                               COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1, i, j)

    def case_contient_piece_a(self, case_x, case_y, joueur):
        if self.coups[case_x][case_y] is not None and self.coups[case_x][case_y].proprietaire == joueur:
            return True
        return False

    def selectionner_piece(self, case_x, case_y, joueur_actif, adversaire):
        """Sélectionne une pièce si elle appartient au joueur actif et calcule ses coups possibles.
        Une fois sélectionnée, un coup valide peut-être joué en appelant la méthode 'jouer_coup()'."""
        if self.case_contient_piece_a(case_x, case_y, joueur_actif):
            self.activer_piece(case_x, case_y)
            self.calculer_coups_possibles_piece_active(adversaire)
            self.changer_couleur_case_active()
            self.changer_couleur_coups_possibles()

    def deselectionner_piece_active(self):
        self.reset_couleur_case_active()
        self.reset_couleur_coups_possibles()
        self.desactiver_piece_active()
        self.effacer_tableau_coups_possibles()

    def activer_piece(self, case_x, case_y):
        self.case_active = (case_x, case_y)

    def desactiver_piece_active(self):
        self.case_active = (None, None)

    def calculer_deplacements_ou_controles_par_piece_active(self, conteneur, select):
        """Calcul les déplacements possibles ou cases contrôlées par la pièce active en fonction de select.
        Avec select = 1, calcule les déplacements possibles, avec select = 2 les cases contrôlées."""
        act_x, act_y = self.case_active
        proprietaire_piece_active = self.coups[act_x][act_y].proprietaire

        for direction in self.coups[act_x][act_y].deplacements:  # Les séparations des directions avec les différents tableaux de "deplacements" permet de gérer simplement les obstacles
            i = 0
            portee_piece = len(direction)
            # Avant obstacle
            while i < portee_piece and self.deplacement_dans_terrain(act_x, act_y, direction[i]) and \
                  self.coups[act_x + direction[i][0]][act_y + direction[i][1]] is None:  # Ne pas dépasser la portée des pièces ni le plateau PUIS "Tant que le chemin n'est pas bloqué par une pièce" (ordre important)
                if select == 1 or not isinstance(self.coups[act_x][act_y], Pion):  # Pion ne contrôle pas les cases en vertical
                    conteneur[act_x + direction[i][0]][act_y + direction[i][1]] = self.d_coups["oui"]
                i += 1
            # A l'obstacle
            if not isinstance(self.coups[act_x][act_y], Pion):  # Les pions n'ont pas le droit de manger verticalement
                if i < portee_piece and self.deplacement_dans_terrain(act_x, act_y, direction[i]):
                    if select == 2 or self.coups[act_x + direction[i][0]][act_y + direction[i][1]].proprietaire != \
                                      proprietaire_piece_active:  # Si pièce adverse (condition skip dans le cas du calcul de contrôle des cases)
                        conteneur[act_x + direction[i][0]][act_y + direction[i][1]] = self.d_coups["oui"]

        if isinstance(self.coups[act_x][act_y], Pion):  # Attaques en diagonale des pions
            for attaque in self.coups[act_x][act_y].attaques:
                if self.deplacement_dans_terrain(act_x, act_y, attaque[0]):
                    if select == 2 or (self.coups[act_x + attaque[0][0]][act_y + attaque[0][1]] is not None
                                       and not self.case_contient_piece_a(act_x + attaque[0][0], act_y + attaque[0][1],
                                                                          proprietaire_piece_active)) \
                                   or self.case_prise_en_passant == (act_x + attaque[0][0], act_y + attaque[0][1]): # Déplacement possible si pièce adverse ou si prise en passant
                        conteneur[act_x + attaque[0][0]][act_y + attaque[0][1]] = self.d_coups["oui"]

        # Roque
        if isinstance(self.coups[act_x][act_y], Roi) and not self.coups[act_x][act_y].a_bouge:
            for pos_tour in (3, -4):  # Positions relatives des tours par rapport au roi
                if isinstance(self.coups[act_x + pos_tour][act_y], Tour) and not \
                   self.coups[act_x + pos_tour][act_y].a_bouge:
                    piece_entre = False
                    for i in range(1 if pos_tour == 3 else -1, pos_tour, 1 if pos_tour == 3 else -1):
                        if self.coups[act_x + i][act_y] is not None:
                            piece_entre = True
                    if select == 1 and not piece_entre:
                        conteneur[act_x + int(copysign(2, pos_tour))][act_y] = self.d_coups["roque"]

    def calculer_cases_controlees_par(self, joueur):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.case_contient_piece_a(i, j, joueur):
                    self.activer_piece(i, j)  # Changement temporaire de pièce active
                    self.calculer_deplacements_ou_controles_par_piece_active(self.cases_controlees, 2)  # Au fur et à mesure, les cases contrôlées se surperposent et créées une map des cases contrôlées.

        self.desactiver_piece_active()

    def calculer_coups_possibles_piece_active(self, adversaire):
        sauv_case_active = self.case_active

        self.calculer_deplacements_ou_controles_par_piece_active(self.deplacements_possibles, 1)

        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.deplacements_possibles[i][j] in (self.d_coups["oui"], self.d_coups["roque"]):
                    self.deplacement_fictif_piece_active(i, j, not bool(
                        self.deplacements_possibles[i][j] != self.d_coups["roque"]))
                    self.calculer_cases_controlees_par(adversaire)
                    self.case_active = sauv_case_active
                    pos_roi_allie_x = self.pos_roi_n[0] if self.coups[i][j].couleur != COULEUR_PIECE2 else \
                                      self.pos_roi_b[0]
                    pos_roi_allie_y = self.pos_roi_n[1] if self.coups[i][j].couleur != COULEUR_PIECE2 else \
                                      self.pos_roi_b[1]
                    if self.cases_controlees[pos_roi_allie_x][pos_roi_allie_y] == self.d_coups["non"]:
                        if self.deplacements_possibles[i][j] != self.d_coups["roque"]:
                            self.coups_possibles[i][j] = self.d_coups["oui"]
                        elif self.cases_controlees[pos_roi_allie_x + int(copysign(1, 4 - pos_roi_allie_x))] \
                                                  [pos_roi_allie_y] == self.d_coups["non"]:  # Les cases de passage du roi ne doivent pas être contrôlées
                            self.coups_possibles[i][j] = self.d_coups["roque"]
                    self.retour_deplacement_fictif(i, j, not bool(
                        self.deplacements_possibles[i][j] != self.d_coups["roque"]))
                    self.case_active = sauv_case_active
                    self.effacer_cases_controlees()

        self.effacer_deplacements_possibles()

    def deplacement_dans_terrain(self, act_x, act_y, direction):
        return True if act_x + direction[0] < NB_COLONNES and act_y + direction[1] < NB_LIGNES and \
                       act_x + direction[0] >= 0 and act_y + direction[1] >= 0 else False

    def deplacement_fictif_piece_active(self, case_x, case_y, roque):
        # Sauvegarde pièce mangée
        self.sauv_piece_mangee_fictivement = self.coups[case_x][case_y]

        # Déplacement de l'objet
        self.deplacer_piece_tableau(self.case_active[0], self.case_active[1], case_x, case_y)

        # Modif pos roi
        if isinstance(self.coups[case_x][case_y], Roi):
            if self.coups[case_x][case_y].couleur == COULEUR_PIECE2:
                self.pos_roi_b = (case_x, case_y)
            else:
                self.pos_roi_n = (case_x, case_y)

        if roque:
            self.activer_piece(case_x + 1 if case_x == 6 else case_x - 2, case_y)  # On active la tour concernée
            self.deplacement_fictif_piece_active(case_x - 1 if case_x == 6 else case_x + 1, case_y, False)

    def retour_deplacement_fictif(self, case_x, case_y, roque):
        # Déplacement de l'objet
        self.coups[self.case_active[0]][self.case_active[1]] = self.coups[case_x][case_y]
        self.coups[case_x][case_y] = self.sauv_piece_mangee_fictivement

        # Modif pos roi
        if isinstance(self.coups[self.case_active[0]][self.case_active[1]], Roi):
            if self.coups[self.case_active[0]][self.case_active[1]].couleur == COULEUR_PIECE2:
                self.pos_roi_b = (self.case_active[0], self.case_active[1])
            else:
                self.pos_roi_n = (self.case_active[0], self.case_active[1])

        if roque:
            self.case_active = (case_x + 1 if case_x == 6 else case_x - 2, case_y)  # On active la tour concernée
            self.retour_deplacement_fictif(case_x - 1 if case_x == 6 else case_x + 1, case_y, False)

    def deplacer_piece_tableau(self, case_x_init, case_y_init, case_x_fin, case_y_fin):
        self.coups[case_x_fin][case_y_fin] = self.coups[case_x_init][case_y_init]
        self.coups[case_x_init][case_y_init] = None

    def jouer_coup(self, case_x, case_y, roque):
        """À appeler seulement si le coup est possible.
        Déplace la pièce active sur la case (case_x, case_y) et applique les règles.
        Met également à jour certaines informations sur le jeu."""
        self.deplacer_piece_active(case_x, case_y)
        self.gerer_deplacement_pions(case_x, case_y)
        self.deselectionner_piece_active()
        self.gerer_choses_relatives_au_roi(case_x, case_y, roque)

    def deplacer_piece_active(self, case_x, case_y):
        # Maj infos jeu
        self.piece_mangee_ce_tour = True if self.coups[case_x][case_y] is not None else False
        # Effacement image pièce mangée
        self.effacer_image(case_x, case_y)
        # Déplacement de l'objet
        self.deplacer_piece_tableau(self.case_active[0], self.case_active[1], case_x, case_y)
        # Déplacement de l'image
        self.recentrer_image_piece_sur_case(case_x, case_y)

    def gerer_deplacement_pions(self, case_x, case_y):  # Réduction portée pions après 1er déplacement + double pas + prise en passant + promotion
        prise_en_passant_possible_ce_tour = False
        if isinstance(self.coups[case_x][case_y], Pion):
            self.pion_bouge_ce_tour = True  # Maj infos de jeu
            if case_y in (0, 7):  # Promotion
                self.promotion_pion(case_x, case_y, self.coups[case_x][case_y].couleur,
                                    self.coups[case_x][case_y].proprietaire)
            elif not self.coups[case_x][case_y].a_bouge:  # Réduction portée + activation propre prise en passant
                if case_y == 3 or case_y == 4:
                    self.case_prise_en_passant = (case_x, int((self.case_active[1]+case_y)/2))
                    prise_en_passant_possible_ce_tour = True
                self.coups[case_x][case_y].deplacements = [[(0, 1)]] if self.coups[case_x][case_y].couleur == \
                                                                        COULEUR_PIECE2 else [[(0, -1)]]
                self.coups[case_x][case_y].a_bouge = True
            elif self.case_prise_en_passant == (case_x, case_y):  # Prise adverse en passant
                self.effacer_image(case_x, case_y+1 if case_y == 2 else case_y-1)
                self.coups[case_x][case_y+1 if case_y == 2 else case_y-1] = None
        else:
            self.pion_bouge_ce_tour = False  # Maj infos de jeu
        if not prise_en_passant_possible_ce_tour:
            self.case_prise_en_passant = (None, None)

    def gerer_choses_relatives_au_roi(self, case_x, case_y, roque):  # Pour le roque + modif pos roi
        if isinstance(self.coups[case_x][case_y], Tour):
            self.coups[case_x][case_y].a_bouge = True
        if isinstance(self.coups[case_x][case_y], Roi):
            self.coups[case_x][case_y].a_bouge = True
            if self.coups[case_x][case_y].couleur == COULEUR_PIECE2:
                self.pos_roi_b = (case_x, case_y)
            else:
                self.pos_roi_n = (case_x, case_y)

        if roque:
            self.case_active = (case_x + 1 if case_x == 6 else case_x - 2, case_y)  # On active la tour concernée
            self.jouer_coup(case_x - 1 if case_x == 6 else case_x + 1, case_y, False)

    def effacer_image(self, case_x, case_y):
        if self.coups[case_x][case_y] is not None:
            main_canvas.delete(self.coups[case_x][case_y].image_canvas)  # Un objet de canvas existe toujours même si il n'est plus référencé.
                                                                         # Il faut donc le détruire manuellement. Il est par contre inutile de
                                                                         # faire quoi que ce soit pour image_tk qui se détruit quand elle n'est
                                                                         # plus référencée.

    def recentrer_image_piece_sur_case(self, case_x, case_y):
        x, y = (case_x + 1 / 2) * LARGEUR / NB_COLONNES, (case_y + 1 / 2) * HAUTEUR / NB_LIGNES
        main_canvas.coords(self.coups[case_x][case_y].image_canvas, x, y)

    def promotion_pion(self, case_x, case_y, couleur, proprietaire):
        promotion = Promotion(main_window, couleur, proprietaire)
        main_window.wait_window(promotion.window_promotion)  # Tant que la fenêtre enfant n'est pas fermée, le programme est retenu ici
        main_canvas.delete(self.coups[case_x][case_y].image_canvas)
        self.coups[case_x][case_y] = promotion.choix_piece
        x, y = (case_x + 1 / 2) * LARGEUR / NB_COLONNES, (case_y + 1 / 2) * HAUTEUR / NB_LIGNES
        self.coups[case_x][case_y].recreer_image(main_canvas, x, y)  # Une image dans un canvas détruit est détruite. On la reconstruit dans la canvas principal.

    def effacer_deplacements_possibles(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.deplacements_possibles[i][j] != self.d_coups["non"]:
                    self.deplacements_possibles[i][j] = self.d_coups["non"]

    def effacer_cases_controlees(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.cases_controlees[i][j] != self.d_coups["non"]:
                    self.cases_controlees[i][j] = self.d_coups["non"]

    def effacer_tableau_coups_possibles(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups_possibles[i][j] != self.d_coups["non"]:
                    self.coups_possibles[i][j] = self.d_coups["non"]

    def changer_couleur_case_active(self):
        self.damier.changer_couleur_case(self.case_active[0], self.case_active[1], COULEUR_CASE_ACTIVE)

    def changer_couleur_coups_possibles(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups_possibles[i][j] == self.d_coups["oui"] or \
                   self.coups_possibles[i][j] == self.d_coups["roque"]:
                    self.damier.changer_couleur_case(i, j, COULEUR_COUP_POSSIBLE1 if (i + j) % 2 == 0
                                                      else COULEUR_COUP_POSSIBLE2)

    def reset_couleur_case_active(self):
        self.damier.changer_couleur_case(self.case_active[0], self.case_active[1], COULEUR_DAMIER1
                                         if (self.case_active[0] + self.case_active[1]) % 2 == 0 else COULEUR_DAMIER2)

    def reset_couleur_coups_possibles(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups_possibles[i][j] != self.d_coups["non"]:
                    self.damier.changer_couleur_case(i, j, COULEUR_DAMIER1 if (i + j) % 2 == 0 else COULEUR_DAMIER2)

    def reset(self):
        # Damier
        self.damier.reset()

        # Images pions
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups[i][j] is not None:
                    main_canvas.delete(self.coups[i][j].image_canvas)  # Un objet de canvas existe toujours même si il n'est plus référencé.
                                                                       # Il faut donc le détruire manuellement. Il est par contre inutile de
                                                                       # faire quoi que ce soit pour image_tk qui se détruit quand elle n'est
                                                                       # plus référencée.

        # Attributs
        self.coups = [[None] * NB_LIGNES for _ in self.coups]
        self.coups_possibles = [[None] * NB_LIGNES for _ in self.coups]
        self.generer_pieces()
        self.case_active = (None, None)
        self.case_prise_en_passant = (None, None)
        self.pos_roi_b, self.pos_roi_n = (4, 0), (4, 7)
        self.sauv_piece_mangee_fictivement = None


class GestionnaireConditionsVictoire:
    def __init__(self):
        # Gestionnaire état du jeu
        self.gestionnaire_fin_jeu = GestionnaireFinJeu()

        # Conditions de victoire
        self.compteur_tours_sans_evolution = 0

    def gerer_conditions_victoire(self, joueur_actif, adversaire):
        self.gestion_menaces_roi(joueur_actif, adversaire)
        self.gestion_manque_materiel(joueur_actif)
        self.gestion_50_tours_sans_evolution()

    def gestion_menaces_roi(self, joueur_actif, adversaire):
        if not self.adversaire_a_coup_possible(joueur_actif, adversaire):
            if self.adversaire_en_echec(joueur_actif):
                self.gestionnaire_fin_jeu.arreter_jeu(GestionnaireFinJeu.VICTOIRE)
            else:
                self.gestionnaire_fin_jeu.arreter_jeu(GestionnaireFinJeu.PAT)

    def adversaire_a_coup_possible(self, joueur_actif, adversaire):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if plateau.case_contient_piece_a(i, j, adversaire):
                    if self.piece_a_coup_possible(i, j, joueur_actif):
                        return True
        return False

    def piece_a_coup_possible(self, case_x, case_y, joueur_actif):
        plateau.activer_piece(case_x, case_y)
        plateau.calculer_coups_possibles_piece_active(joueur_actif)
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if plateau.coups_possibles[i][j] != plateau.d_coups["non"]:
                    plateau.desactiver_piece_active()
                    plateau.effacer_tableau_coups_possibles()
                    return True
        plateau.desactiver_piece_active()
        plateau.effacer_tableau_coups_possibles()
        return False

    def adversaire_en_echec(self, joueur_actif):
        roi_adverse_x, roi_adverse_y = plateau.pos_roi_n if joueur_actif == 1 else plateau.pos_roi_b
        plateau.calculer_cases_controlees_par(joueur_actif)
        if plateau.cases_controlees[roi_adverse_x][roi_adverse_y] != plateau.d_coups["non"]:
            plateau.effacer_cases_controlees()
            return True
        plateau.effacer_cases_controlees()
        return False

    def gestion_manque_materiel(self, joueur):
        if self.manque_materiel(joueur):
            self.gestionnaire_fin_jeu.arreter_jeu(GestionnaireFinJeu.MANQUE_MATERIEL)

    def manque_materiel(self, joueur1):
        compteur_fous_joueur1 = 0
        compteur_cavaliers_joueur1 = 0
        compteur_fous_joueur2 = 0
        compteur_cavaliers_joueur2 = 0
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if isinstance(plateau.coups[i][j], (Pion, Tour, Reine)):
                    return False
                elif isinstance(plateau.coups[i][j], Fou):
                    if plateau.coups[i][j].proprietaire == joueur1:
                        compteur_fous_joueur1 += 1
                    else:
                        compteur_fous_joueur2 += 1
                elif isinstance(plateau.coups[i][j], Cavalier):
                    if plateau.coups[i][j].proprietaire == joueur1:
                        compteur_cavaliers_joueur1 += 1
                    else:
                        compteur_cavaliers_joueur2 += 1

                if compteur_fous_joueur1 > 1 or compteur_fous_joueur2 > 1 \
                   or compteur_fous_joueur1+compteur_fous_joueur2 > 2 \
                   or compteur_cavaliers_joueur1+compteur_cavaliers_joueur2 > 2:
                    return False
        return True

    def gestion_50_tours_sans_evolution(self):
        self.maj_nb_tours_sans_evolution()
        if self.compteur_tours_sans_evolution > 49:
            self.gestionnaire_fin_jeu.arreter_jeu(GestionnaireFinJeu.CINQUANTE_TOURS_SANS_EVOLUTION)

    def maj_nb_tours_sans_evolution(self):
        if plateau.piece_mangee_ce_tour or plateau.pion_bouge_ce_tour:
            self.compteur_tours_sans_evolution = 0
        else:
            self.compteur_tours_sans_evolution += 1

    def reset(self):
        self.gestionnaire_fin_jeu.reset()


class GestionnaireFinJeu:
    """Gestion état du jeu"""

    VICTOIRE = 0
    MANQUE_TEMPS = 1
    MANQUE_MATERIEL = 2
    PAT = 3
    TROIS_FOIS_MEME_POSITION = 4
    CINQUANTE_TOURS_SANS_EVOLUTION = 5

    def __init__(self):
        self.etat_jeu = None

    def arreter_jeu(self, nouvel_etat_jeu):
        self.etat_jeu = nouvel_etat_jeu
        main_canvas.unbind("<1>")

    def reset(self):
        self.etat_jeu = None


class Jeu:
    """Gestion générale du jeu"""

    def __init__(self):
        # Binding
        main_canvas.bind("<1>", self.gestion_souris)

        # Attributs
        self.joueur_actif = 1
        self.nb_tours = 1

        # Infos de jeu
        self.infos = tk.Label(main_window, text=f"Tour {self.nb_tours} - Au joueur {self.joueur_actif} de jouer")
        self.infos.grid(row=1, column=0, columnspan=2)

        # Gestionnaire fin de jeu
        self.gestionnaire_conditions_victoire = GestionnaireConditionsVictoire()

    def gestion_souris(self, evt):
        # Clic gauche
        if evt.num == 1:
            adversaire = self.joueur_actif % 2 + 1
            case_x, case_y = int(evt.x * NB_COLONNES // LARGEUR), int(evt.y * NB_LIGNES / HAUTEUR)
            if plateau.case_active == (None, None):
                plateau.selectionner_piece(case_x, case_y, self.joueur_actif, adversaire)
            else:
                if plateau.coups_possibles[case_x][case_y] == plateau.d_coups["oui"]:
                    plateau.jouer_coup(case_x, case_y, False)
                    self.gestionnaire_conditions_victoire.gerer_conditions_victoire(self.joueur_actif, adversaire)
                    self.maj_infos()
                elif plateau.coups_possibles[case_x][case_y] == plateau.d_coups["roque"]:
                    plateau.jouer_coup(case_x, case_y, True)
                    self.gestionnaire_conditions_victoire.gerer_conditions_victoire(self.joueur_actif, adversaire)
                    self.maj_infos()
                else:
                    plateau.deselectionner_piece_active()

    def maj_infos(self):
        if self.gestionnaire_conditions_victoire.gestionnaire_fin_jeu.etat_jeu == GestionnaireFinJeu.VICTOIRE:
            self.infos.config(text=f"Victoire joueur {self.joueur_actif}", fg="red")
        elif self.gestionnaire_conditions_victoire.gestionnaire_fin_jeu.etat_jeu == GestionnaireFinJeu.PAT:
            self.infos.config(text="Égalité par pat", fg="red")
        elif self.gestionnaire_conditions_victoire.gestionnaire_fin_jeu.etat_jeu == GestionnaireFinJeu.MANQUE_MATERIEL:
            self.infos.config(text="Égalité par manque de matériel", fg="red")
        elif self.gestionnaire_conditions_victoire.gestionnaire_fin_jeu.etat_jeu == GestionnaireFinJeu.CINQUANTE_TOURS_SANS_EVOLUTION:
            self.infos.config(text="Égalité car les 50 derniers coups consécutifs ont été joués par chaque joueur sans "
                                   "mouvement de pion ni prise de pièce.", fg="red")
        else:
            self.joueur_actif = self.joueur_actif % 2 + 1
            self.nb_tours += 1
            self.infos.config(text=f"Tour {self.nb_tours} - Au joueur {self.joueur_actif} de jouer")

    def nouvelle_partie(self):
        plateau.reset()
        self.gestionnaire_conditions_victoire.reset()
        main_canvas.bind("<1>", self.gestion_souris)

        self.joueur_actif = 1
        self.nb_tours = 1

        self.infos.config(text=f"Tour {self.nb_tours} - Au joueur {self.joueur_actif} de jouer", fg="black")


### Corps ##############################################################################################################

# Fenêtre
main_window = tk.Tk()
main_window.title("Echecs")

# Zone de dessin
main_canvas = tk.Canvas(main_window, bg="white", width=LARGEUR, height=HAUTEUR)
main_canvas.grid(row=0, column=0, columnspan=2)

main_window.update()  # Sans ça, le calcul de la taille du canvas est fait plus tard donc en utilisant main_canvas.winfo_width(), on obtient 1 et pas la taille réelle

# Objets
plateau = Plateau()
jeu = Jeu()

# Boutons
button1 = tk.Button(main_window, text="Nouvelle partie", command=jeu.nouvelle_partie)
button1.grid(row=2, column=0)
button2 = tk.Button(main_window, text='Quitter', command=main_window.destroy)
button2.grid(row=2, column=1)

# Lancement boucle
main_window.mainloop()

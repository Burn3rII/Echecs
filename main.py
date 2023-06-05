# TODO
#   Manque de matériel pour finir = fin
#   3x même position pendant partie = fin (deux positions sont identiques si le trait est le même et si les possibilités
#   de prise en passant et de roque sont les mêmes)
#   50 tours + pas de pion bougé ni prise de pièce = fin
#   Fonction temps
#   Autres fonctions
#   Améliorer graphiques

### Bibliothéques ######################################################################################################
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

        # Génération et dessin pièces
        self.coups = [[0] * NB_LIGNES for _ in range(NB_COLONNES)]  # Système de coord.: Premier indice vers la droite et deuxième vers le bas, à partir du coin haut gauche
        self.generer_pieces()

        self.case_active = (-1, -1)
        self.case_prise_en_passant = (-1, -1)

        # Déplacements légaux (ne prend pas en compte l'échec)
        self.deplacements_possibles = [[0] * NB_LIGNES for _ in range(NB_COLONNES)]
        self.d_coups = {"non": 0, "oui": 1, "roque": 2}

        # Calcul de l'échec:
        self.pos_roi_b, self.pos_roi_n = (4, 0), (4, 7)
        self.cases_controlees = [[0] * NB_LIGNES for _ in range(NB_COLONNES)]

        # Coups possibles (déplacements légaux + pas d'échec à son propre roi)
        self.coups_possibles = [[0] * NB_LIGNES for _ in range(NB_COLONNES)]

        self.sauv_piece_mangee_fictivement = 0

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

    def activer_case(self, case_x, case_y, joueur_actif, adversaire):
        if self.case_contient_piece_a(case_x, case_y, joueur_actif):
            self.case_active = (case_x, case_y)
            self.damier.changer_couleur_case(case_x, case_y, COULEUR_CASE_ACTIVE)

            self.calculer_deplacements_ou_controles_par_piece_active(joueur_actif, adversaire,
                                                                     self.deplacements_possibles, 1)

            for i in range(NB_COLONNES):
                for j in range(NB_LIGNES):
                    if self.deplacements_possibles[i][j] in (self.d_coups["oui"], self.d_coups["roque"]):
                        self.deplacement_fictif_piece_active(i, j, not bool(
                            self.deplacements_possibles[i][j] != self.d_coups["roque"]))
                        self.calculer_cases_controlees_par(adversaire, joueur_actif)
                        self.case_active = (case_x, case_y)
                        pos_roi_x = self.pos_roi_n[0] if self.coups[i][j].couleur != COULEUR_PIECE2 else \
                                    self.pos_roi_b[0]
                        pos_roi_y = self.pos_roi_n[1] if self.coups[i][j].couleur != COULEUR_PIECE2 else \
                                    self.pos_roi_b[1]
                        if self.cases_controlees[pos_roi_x][pos_roi_y] == self.d_coups["non"]:
                            if self.deplacements_possibles[i][j] != self.d_coups["roque"]:
                                self.coups_possibles[i][j] = self.d_coups["oui"]
                            elif self.cases_controlees[pos_roi_x + int(copysign(1, 4 - pos_roi_x))][pos_roi_y] == \
                                 self.d_coups["non"]:  # Les cases de passage du roi ne doivent pas être contrôlées
                                self.coups_possibles[i][j] = self.d_coups["roque"]
                        self.retour_deplacement_fictif(i, j, not bool(
                            self.deplacements_possibles[i][j] != self.d_coups["roque"]))
                        self.case_active = (case_x, case_y)
                        self.effacer_cases_controlees()

            self.effacer_deplacements_possibles()

            self.changer_couleur_coups_possibles()

    def case_contient_piece_a(self, case_x, case_y, joueur):
        if self.coups[case_x][case_y] != 0 and self.coups[case_x][case_y].proprietaire == joueur:
            return True
        return False

    def calculer_deplacements_ou_controles_par_piece_active(self, proprietaire_piece_active, adversaire, conteneur, select):  # Calcul les déplacements possibles ou cases contrôlées par la pièce active en fonction de select
        act_x, act_y = self.case_active

        for direction in self.coups[act_x][act_y].deplacements:  # Les séparations des directions avec les différents tableaux de "deplacements" permet de gérer simplement les obstacles
            i = 0
            portee_piece = len(direction)
            # Avant obstacle
            while i < portee_piece and self.deplacement_dans_terrain(act_x, act_y, direction[i]) and \
                  self.coups[act_x + direction[i][0]][act_y + direction[i][1]] == 0:  # Ne pas dépasser la portée des pièces ni le plateau PUIS "Tant que le chemin n'est pas bloqué par une pièce" (ordre important)
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
                    if select == 2 or self.case_contient_piece_a(act_x + attaque[0][0], act_y + attaque[0][1],
                                                                 adversaire) \
                       or self.case_prise_en_passant == (act_x + attaque[0][0], act_y + attaque[0][1]):
                        conteneur[act_x + attaque[0][0]][act_y + attaque[0][1]] = self.d_coups["oui"]

        # Roque
        if isinstance(self.coups[act_x][act_y], Roi) and not self.coups[act_x][act_y].a_bouge:
            for pos_tour in (3, -4):  # Positions relatives des tours par rapport au roi
                if isinstance(self.coups[act_x + pos_tour][act_y], Tour) and not \
                   self.coups[act_x + pos_tour][act_y].a_bouge:
                    piece_entre = False
                    for i in range(1 if pos_tour == 3 else -1, pos_tour, 1 if pos_tour == 3 else -1):
                        if self.coups[act_x + i][act_y] != 0:
                            piece_entre = True
                    if select == 1 and not piece_entre:
                        conteneur[act_x + int(copysign(2, pos_tour))][act_y] = self.d_coups["roque"]

    def deplacement_dans_terrain(self, act_x, act_y, direction):
        return True if act_x + direction[0] < NB_COLONNES and act_y + direction[1] < NB_LIGNES and \
                       act_x + direction[0] >= 0 and act_y + direction[1] >= 0 else False

    def changer_couleur_coups_possibles(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups_possibles[i][j] == self.d_coups["oui"] or \
                   self.coups_possibles[i][j] == self.d_coups["roque"]:
                    self.damier.changer_couleur_case(i, j, COULEUR_COUP_POSSIBLE1 if (i + j) % 2 == 0
                                                      else COULEUR_COUP_POSSIBLE2)

    def desactiver_case_active(self):
        self.damier.changer_couleur_case(self.case_active[0], self.case_active[1], COULEUR_DAMIER1
                                         if (self.case_active[0] + self.case_active[1]) % 2 == 0 else COULEUR_DAMIER2)
        self.case_active = (-1, -1)

        self.effacer_coups_possibles()

    def effacer_deplacements_possibles(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.deplacements_possibles[i][j] != self.d_coups["non"]:
                    self.deplacements_possibles[i][j] = self.d_coups["non"]

    def effacer_coups_possibles(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups_possibles[i][j] != self.d_coups["non"]:
                    self.coups_possibles[i][j] = self.d_coups["non"]
                    self.damier.changer_couleur_case(i, j, COULEUR_DAMIER1 if (i + j) % 2 == 0 else COULEUR_DAMIER2)

    def jouer_coup(self, case_x, case_y, roque):
        self.deplacer_piece_active(case_x, case_y)
        self.gerer_deplacement_pions(case_x, case_y)
        self.desactiver_case_active()
        self.gerer_choses_relatives_au_roi(case_x, case_y, roque)

    def deplacer_piece_active(self, case_x, case_y):
        # Effacement image pièce mangée
        self.effacer_image(case_x, case_y)
        # Déplacement de l'objet
        self.deplacer_piece_tableau(self.case_active[0], self.case_active[1], case_x, case_y)
        # Déplacement de l'image
        self.recentrer_image_piece_sur_case(case_x, case_y)

    def effacer_image(self, case_x, case_y):
        if self.coups[case_x][case_y] != 0:
            main_canvas.delete(self.coups[case_x][case_y].image_canvas)  # Un objet de canvas existe toujours même si il n'est plus référencé.
                                                                         # Il faut donc le détruire manuellement. Il est par contre inutile de
                                                                         # faire quoi que ce soit pour image_tk qui se détruit quand elle n'est
                                                                         # plus référencée.

    def deplacer_piece_tableau(self, case_x_init, case_y_init, case_x_fin, case_y_fin):
        self.coups[case_x_fin][case_y_fin] = self.coups[case_x_init][case_y_init]
        self.coups[case_x_init][case_y_init] = 0

    def recentrer_image_piece_sur_case(self, case_x, case_y):
        x, y = (case_x + 1 / 2) * LARGEUR / NB_COLONNES, (case_y + 1 / 2) * HAUTEUR / NB_LIGNES
        main_canvas.coords(self.coups[case_x][case_y].image_canvas, x, y)

    def gerer_deplacement_pions(self, case_x, case_y):  # Réduction portée pions après 1er déplacement + double pas + prise en passant + promotion
        prise_en_passant_possible_ce_tour = False
        if isinstance(self.coups[case_x][case_y], Pion):
            if case_y in (0, 7):  # Promotion
                self.promotion_pion(case_x, case_y, self.coups[case_x][case_y].couleur,
                                    self.coups[case_x][case_y].proprietaire)
            elif not self.coups[case_x][case_y].a_bouge:  # Réduction portée + activation propre prise en passant
                if case_y == 3 or case_y == 4:
                    self.case_prise_en_passant = (case_x, int((self.case_active[1]+case_y)/2))
                    prise_en_passant_possible_ce_tour = True
                    print(self.case_active[1], case_y)
                    print(self.case_prise_en_passant)
                self.coups[case_x][case_y].deplacements = [[(0, 1)]] if self.coups[case_x][case_y].couleur == \
                                                                        COULEUR_PIECE2 else [[(0, -1)]]
                self.coups[case_x][case_y].a_bouge = True
            elif self.case_prise_en_passant == (case_x, case_y):  # Prise adverse en passant
                self.effacer_image(case_x, case_y+1 if case_y == 2 else case_y-1)
                self.coups[case_x][case_y+1 if case_y == 2 else case_y-1] = 0
        if not prise_en_passant_possible_ce_tour:
            self.case_prise_en_passant = (-1, -1)

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
    def promotion_pion(self, case_x, case_y, couleur, proprietaire):
        promotion = Promotion(main_window, couleur, proprietaire)
        main_window.wait_window(promotion.window_promotion)  # Tant que la fenêtre enfant n'est pas fermée, le programme est retenu ici
        main_canvas.delete(self.coups[case_x][case_y].image_canvas)
        self.coups[case_x][case_y] = promotion.choix_piece
        x, y = (case_x + 1 / 2) * LARGEUR / NB_COLONNES, (case_y + 1 / 2) * HAUTEUR / NB_LIGNES
        self.coups[case_x][case_y].recreer_image(main_canvas, x, y)  # Une image dans un canvas détruit est détruite. On la reconstruit dans la canvas principal.

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
            self.case_active = (case_x + 1 if case_x == 6 else case_x - 2, case_y)  # On active la tour concernée
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

    def calculer_cases_controlees_par(self, joueur, adversaire):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups[i][j] != 0 and self.coups[i][j].proprietaire == joueur:
                    self.case_active = (i, j)  # Changement temporaire de case_active
                    self.calculer_deplacements_ou_controles_par_piece_active(joueur, adversaire, self.cases_controlees,
                                                                             2) # Au fur et à mesure, les cases contrôlées se surperposent et créées une map des cases contrôlées.

        self.case_active = (-1, -1)

    def effacer_cases_controlees(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.cases_controlees[i][j] != self.d_coups["non"]:
                    self.cases_controlees[i][j] = self.d_coups["non"]

    def reset(self):
        # Damier
        self.damier.reset()

        # Images pions
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups[i][j] != 0:
                    main_canvas.delete(self.coups[i][j].image_canvas)  # Un objet de canvas existe toujours même si il n'est plus référencé.
                                                                       # Il faut donc le détruire manuellement. Il est par contre inutile de
                                                                       # faire quoi que ce soit pour image_tk qui se détruit quand elle n'est
                                                                       # plus référencée.

        # Attributs
        self.coups = [[0] * NB_LIGNES for _ in self.coups]
        self.generer_pieces()
        self.case_active = (-1, -1)
        self.case_prise_en_passant = (-1, -1)
        self.pos_roi_b, self.pos_roi_n = (4, 0), (4, 7)
        self.sauv_piece_mangee_fictivement = 0


class Jeu:
    """Gestion générale du jeu"""

    def __init__(self):
        # Binding
        main_canvas.bind("<1>", self.gestion_souris)

        # Attributs
        self.joueur_actif = 1
        self.symbole_actif = "X"
        self.nb_tours = 1
        self.victoire = False
        self.pat = False

        # Infos de jeu
        self.infos = tk.Label(main_window, text=f"Tour {self.nb_tours} - Au joueur {self.joueur_actif} de jouer")
        self.infos.grid(row=1, column=0, columnspan=2)

    def gestion_souris(self, evt):
        # Clic gauche
        if evt.num == 1:
            adversaire = self.joueur_actif % 2 + 1
            if plateau.case_active == (-1, -1):
                case_x, case_y = int(evt.x * NB_COLONNES // LARGEUR), int(evt.y * NB_LIGNES / HAUTEUR)
                plateau.activer_case(case_x, case_y, self.joueur_actif, adversaire)
            else:
                case_x, case_y = int(evt.x * NB_COLONNES // LARGEUR), int(evt.y * NB_LIGNES / HAUTEUR)
                if plateau.coups_possibles[case_x][case_y] == plateau.d_coups["oui"]:
                    plateau.jouer_coup(case_x, case_y, False)
                    self.gestion_fin_partie()
                    self.maj_infos()
                elif plateau.coups_possibles[case_x][case_y] == plateau.d_coups["roque"]:
                    plateau.jouer_coup(case_x, case_y, True)
                    self.gestion_fin_partie()
                    self.maj_infos()
                else:
                    plateau.desactiver_case_active()

    def gestion_fin_partie(self):
        self.gestion_echec()

    def gestion_echec(self):
        if not self.adversaire_a_coup_possible():
            if self.adversaire_en_echec():
                self.victoire = True
                main_canvas.unbind("<1>")
            else:
                self.pat = True
                main_canvas.unbind("<1>")
        plateau.desactiver_case_active()

    def adversaire_a_coup_possible(self):
        adversaire = self.joueur_actif % 2 + 1
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if plateau.case_contient_piece_a(i, j, adversaire):
                    if self.piece_a_coup_possible(i, j, adversaire):
                        return True
        return False

    def piece_a_coup_possible(self, x, y, adversaire):
        plateau.activer_case(x, y, adversaire, self.joueur_actif)
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if plateau.coups_possibles[i][j] != plateau.d_coups["non"]:
                    plateau.desactiver_case_active()
                    return True
        plateau.desactiver_case_active()
        return False

    def adversaire_en_echec(self):
        roi_adverse_x, roi_adverse_y = plateau.pos_roi_n if self.joueur_actif == 1 else plateau.pos_roi_b
        adversaire = self.joueur_actif % 2 + 1
        plateau.calculer_cases_controlees_par(self.joueur_actif, adversaire)
        if plateau.cases_controlees[roi_adverse_x][roi_adverse_y] != plateau.d_coups["non"]:
            return True
        return False

    """def verifier_et_gerer_victoire(self, coups):
        dim_max = max(NB_COLONNES,NB_LIGNES)
        dim_min = min(NB_COLONNES,NB_LIGNES)

        #Colonnes
        for i in range(NB_COLONNES):
            compteur_c = 0
            for j in range(NB_LIGNES):
                compteur_c = compteur_c+1 if coups[i][j] == self.joueur_actif else 0
                if compteur_c == nb_symboles_a_aligner:
                    self.gerer_victoire(("c", i, j))
                    return

        #Lignes
        for j in range(NB_LIGNES):
            compteur_l = 0
            for i in range(NB_COLONNES):
                compteur_l = compteur_l+1 if coups[i][j] == self.joueur_actif else 0
                if compteur_l == nb_symboles_a_aligner:
                    self.gerer_victoire(("l", i, j))
                    return

        #Diagonales (triangles aux coins)
        for i in range(nb_symboles_a_aligner, dim_min+1):
            compteur_d11, compteur_d12, compteur_d21, compteur_d22 = 0, 0, 0, 0 #2 diagonales primaires et 2 secondaires
            for j in range(i):
                compteur_d11 = compteur_d11+1 if coups[j][NB_LIGNES-i+j] == self.joueur_actif else 0 #Triangle inférieur gauche
                compteur_d12 = compteur_d12+1 if coups[NB_COLONNES-i+j][j] == self.joueur_actif else 0 #Triangle supérieur droit
                compteur_d21 = compteur_d21+1 if coups[NB_COLONNES-1-j][NB_LIGNES-i+j] == self.joueur_actif else 0 #Triangle inférieur droit
                compteur_d22 = compteur_d22+1 if coups[i-j-1][j] == self.joueur_actif else 0 #Triangle supérieur gauche
                if compteur_d11 == nb_symboles_a_aligner or compteur_d12 == nb_symboles_a_aligner:
                    self.gerer_victoire(("d1", j, NB_LIGNES-i+j) if compteur_d11 > compteur_d12 else ("d1", NB_COLONNES-i+j, j))
                    return
                elif compteur_d21 == nb_symboles_a_aligner or compteur_d22 == nb_symboles_a_aligner:
                    self.gerer_victoire(("d2", NB_COLONNES-1-j, NB_LIGNES-i+j) if compteur_d21 > compteur_d22 else ("d2", i-j-1, j))
                    return

        #Diagonales (du milieu)
        for i in range(dim_max-dim_min-1):
            compteur_d1, compteur_d2 = 0, 0
            for j in range(dim_min):
                if NB_LIGNES <  NB_COLONNES:
                    compteur_d1 = compteur_d1+1 if coups[j+1+i][j] == self.joueur_actif else 0 #Première diagonale
                    compteur_d2 = compteur_d2+1 if coups[dim_max-2-j-i][j] == self.joueur_actif else 0 #Deuxième diagonale
                    if compteur_d1 == nb_symboles_a_aligner or compteur_d2 == nb_symboles_a_aligner:
                        self.gerer_victoire(("d1", j+1+i, j) if compteur_d1 > compteur_d2 else ("d2", dim_max-2-j-i, j))
                        return
                else:
                    compteur_d1 = compteur_d1+1 if coups[j][j+1+i] == self.joueur_actif else 0 #Première diagonale
                    compteur_d2 = compteur_d2+1 if coups[dim_min-1-j][1+j+i] == self.joueur_actif else 0 #Deuxième diagonale
                    if compteur_d1 == nb_symboles_a_aligner or compteur_d2 == nb_symboles_a_aligner:
                        self.gerer_victoire(("d1", j, j+1+i) if compteur_d1 > compteur_d2 else ("d2", dim_min-1-j, 1+j+i))
                        return

    def gerer_victoire(self, emplacement): #Emplacement contient la direction de l'alignement et les indices du premier symbole
        self.victoire = True

        direction, colonne_debut, ligne_debut = emplacement[0], emplacement[1], emplacement[2]
        if direction == "c":
            for i in range(nb_symboles_a_aligner):
                plateau.dessiner_symbole(colonne_debut, ligne_debut-i, self.symbole_actif, "red", plateau.symboles)
        elif direction == "l":
            for i in range(nb_symboles_a_aligner):
                plateau.dessiner_symbole(colonne_debut-i, ligne_debut, self.symbole_actif, "red", plateau.symboles)
        elif direction == "d1":
            for i in range(nb_symboles_a_aligner):
                plateau.dessiner_symbole(colonne_debut-i, ligne_debut-i, self.symbole_actif, "red", plateau.symboles)
        elif direction == "d2":
            for i in range(nb_symboles_a_aligner):
                plateau.dessiner_symbole(colonne_debut+i, ligne_debut-i, self.symbole_actif, "red", plateau.symboles)

        main_canvas.unbind("<1>")"""

    def maj_infos(self):
        if self.victoire:
            self.infos.config(text=f"Victoire joueur {self.joueur_actif}", fg="red")
        elif self.pat:
            self.infos.config(text="Égalité par pat", fg="red")
        else:
            self.joueur_actif = self.joueur_actif % 2 + 1
            self.nb_tours += 1
            self.infos.config(text=f"Tour {self.nb_tours} - Au joueur {self.joueur_actif} de jouer")

    def nouvelle_partie(self):
        plateau.reset()
        main_canvas.bind("<1>", self.gestion_souris)

        self.joueur_actif = 1
        self.nb_tours = 1
        self.victoire = False
        self.pat = False

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

### Bibliothèques ######################################################################################################
### Externes ###
from math import copysign
import hashlib
import pickle
### Fichiers internes ###
from pieces import Pion, Tour, Cavalier, Fou, Reine, Roi
from promotion import Promotion
### Paramètres de jeu ###
from core.constantes import NB_LIGNES, NB_COLONNES, LARGEUR, HAUTEUR, COULEUR_DAMIER1, COULEUR_DAMIER2, COULEUR_PIECE1, \
                       COULEUR_PIECE2, COULEUR_CASE_ACTIVE, COULEUR_COUP_POSSIBLE1, COULEUR_COUP_POSSIBLE2

### Classes ############################################################################################################


class Plateau:
    """Gestion des pièces"""

    def __init__(self, gui):
        # Interface utilisateur
        self.gui = gui

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

        # Sauvegarde des différents états du plateau
        self.sauv_etats_plateau = []

    def generer_pieces(self):
        indices_lignes = [0, 1, NB_LIGNES - 2, NB_LIGNES - 1]
        for i in range(NB_COLONNES):
            for j in indices_lignes:
                if j in (1, NB_LIGNES - 2):
                    self.coups[i][j] = Pion(self.gui.canvas, NB_COLONNES, NB_LIGNES,
                                            1 if j == 1 else 2, COULEUR_PIECE2 if j == 1 else COULEUR_PIECE1, i, j)
                elif j in (0, NB_LIGNES - 1):
                    if i in (0, NB_COLONNES - 1):
                        self.coups[i][j] = Tour(self.gui.canvas, NB_COLONNES, NB_LIGNES,
                                                1 if j == 0 else 2, COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1, i, j)
                    elif i in (1, NB_COLONNES - 2):
                        self.coups[i][j] = Cavalier(self.gui.canvas, NB_COLONNES, NB_LIGNES,
                                                    1 if j == 0 else 2, COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1,
                                                    i, j)
                    elif i in (2, NB_COLONNES - 3):
                        self.coups[i][j] = Fou(self.gui.canvas, NB_COLONNES, NB_LIGNES,
                                               1 if j == 0 else 2, COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1, i, j)
                    elif i == 3:
                        self.coups[i][j] = Reine(self.gui.canvas, NB_COLONNES, NB_LIGNES,
                                                 1 if j == 0 else 2, COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1, i, j)
                    elif i == NB_COLONNES - 4:
                        self.coups[i][j] = Roi(self.gui.canvas, NB_COLONNES, NB_LIGNES,
                                               1 if j == 0 else 2, COULEUR_PIECE2 if j == 0 else COULEUR_PIECE1, i, j)

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
        if isinstance(self.coups[act_x][act_y], Roi) and self.coups[act_x][act_y].peut_roquer:
            for pos_tour in (3, -4):  # Positions relatives des tours par rapport au roi
                if isinstance(self.coups[act_x + pos_tour][act_y], Tour) and \
                   self.coups[act_x + pos_tour][act_y].peut_roquer:
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
            self.coups[case_x][case_y].peut_roquer = False
        if isinstance(self.coups[case_x][case_y], Roi):
            self.coups[case_x][case_y].peut_roquer = False
            self.desactiver_roque_tours_alliees(self.coups[case_x][case_y].proprietaire)  # Pour le calcul des etats du plateau, il faut indiquer que les possibilités de roque ont changé.
            if self.coups[case_x][case_y].couleur == COULEUR_PIECE2:
                self.pos_roi_b = (case_x, case_y)
            else:
                self.pos_roi_n = (case_x, case_y)

        if roque:
            self.case_active = (case_x + 1 if case_x == 6 else case_x - 2, case_y)  # On active la tour concernée
            self.jouer_coup(case_x - 1 if case_x == 6 else case_x + 1, case_y, False)

    def effacer_image(self, case_x, case_y):
        if self.coups[case_x][case_y] is not None:
            self.gui.effacer_objet_canvas(self.coups[case_x][case_y].image_canvas)  # Un objet de canvas existe toujours
            # même s'il n'est plus référencé. Il faut donc le détruire manuellement. Il est par contre inutile de faire
            # quoi que ce soit pour image_tk qui se détruit quand elle n'est plus référencée.

    def recentrer_image_piece_sur_case(self, case_x, case_y):
        x, y = (case_x + 1 / 2) * LARGEUR / NB_COLONNES, (case_y + 1 / 2) * HAUTEUR / NB_LIGNES
        self.gui.deplacer_objet_canvas(self.coups[case_x][case_y].image_canvas, x, y)

    def promotion_pion(self, case_x, case_y, couleur, proprietaire):
        promotion = Promotion(self.gui.window, couleur, proprietaire)
        self.gui.window.wait_window(promotion.gui.window)  # Tant que la fenêtre enfant n'est pas fermée, le programme est retenu ici
        self.gui.canvas.delete(self.coups[case_x][case_y].image_canvas)
        self.coups[case_x][case_y] = promotion.choix_piece
        x, y = (case_x + 1 / 2) * LARGEUR / NB_COLONNES, (case_y + 1 / 2) * HAUTEUR / NB_LIGNES
        self.coups[case_x][case_y].recreer_image(self.gui.canvas, x, y)  # Une image dans un canvas détruit est détruite. On la reconstruit dans la canvas principal.

    def desactiver_roque_tours_alliees(self, joueur):
        """Sert pour le calcul de l'état du plateau. En effet, si le roi bouge, comme l'état du plateau comprend les
        attributs 'peut_roquer', il faut actualiser ces attributs."""
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if isinstance(self.coups[i][j], Tour) and self.coups[i][j].proprietaire == joueur:
                    self.coups[i][j].peut_roquer = False

    def sauvegarder_etat_plateau(self, joueur_actif):
        plateau_serialise = pickle.dumps((self.coups, self.case_prise_en_passant, joueur_actif))  # Sérialiser un objet permet d'en obtenir une représentation binaire unique (les plateaux identiques produisent des représentations identiques et des plateaux différents des représentations différentes). On inclut également la case de prise en passant et le joueur actif car les possibilités de prise en passant et le joueur actif doivent être les mêmes pour que deux plateaux soient considérés identiques.
        hash_object = hashlib.sha256(plateau_serialise)  # Hachage de la séquence d'octets résultante de la sérialisation (permet d'obtenir un identifiant unique pour chaque état de plateau, avec une taille réduite)
        identifiant_etat_plateau = hash_object.hexdigest()  # Conversion du hachage en une chaine de caractères (représentation plus lisible et facilement utilisable de l'identifiant unique du tableau)
        self.sauv_etats_plateau.append(identifiant_etat_plateau)

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

    def effacer_sauv_etats_plateau(self):
        self.sauv_etats_plateau = []

    def changer_couleur_case_active(self):
        self.gui.damier.changer_couleur_case(self.case_active[0], self.case_active[1], COULEUR_CASE_ACTIVE)

    def changer_couleur_coups_possibles(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups_possibles[i][j] == self.d_coups["oui"] or \
                   self.coups_possibles[i][j] == self.d_coups["roque"]:
                    self.gui.damier.changer_couleur_case(i, j, COULEUR_COUP_POSSIBLE1 if (i + j) % 2 == 0
                                                      else COULEUR_COUP_POSSIBLE2)

    def reset_couleur_case_active(self):
        self.gui.damier.changer_couleur_case(self.case_active[0], self.case_active[1], COULEUR_DAMIER1
                                         if (self.case_active[0] + self.case_active[1]) % 2 == 0 else COULEUR_DAMIER2)

    def reset_couleur_coups_possibles(self):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.coups_possibles[i][j] != self.d_coups["non"]:
                    self.gui.damier.changer_couleur_case(i, j, COULEUR_DAMIER1 if (i + j) % 2 == 0 else COULEUR_DAMIER2)

    def reset(self):
        # Damier
        self.gui.damier.reset()

        # Images pions
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                self.effacer_image(i, j)

        # Attributs
        self.coups = [[None] * NB_LIGNES for _ in self.coups]
        self.effacer_tableau_coups_possibles()
        self.generer_pieces()
        self.case_active = (None, None)
        self.case_prise_en_passant = (None, None)
        self.pos_roi_b, self.pos_roi_n = (4, 0), (4, 7)
        self.sauv_piece_mangee_fictivement = None
        self.pion_bouge_ce_tour = False
        self.piece_mangee_ce_tour = False
        self.effacer_sauv_etats_plateau()
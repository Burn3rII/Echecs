### Bibliothèques ######################################################################################################
### Fichiers internes ###
from .pieces import Pion, Tour, Cavalier, Fou, Reine
### Paramètres de jeu ###
from . import NB_LIGNES, NB_COLONNES

### Classes ############################################################################################################


class GestionnaireConditionsArret:
    """Gestion conditions d'arrêt du jeu"""

    def __init__(self, plateau, observateurs):
        # Observateurs
        self.observateurs = observateurs

        # Plateau
        self.plateau = plateau

        """Très important: En Python, les types de données immuables comprennent :

        Nombres immuables : int (entiers), float (nombres à virgule flottante), complex (nombres complexes)
        Booléens : bool (True, False)
        Chaînes de caractères : str
        Tuples : tuple
        Frozensets : frozenset

        Ces types de données immuables ne peuvent pas être modifiés une fois qu'ils sont créés. Lorsque vous effectuez
        des opérations qui semblent modifier ces objets, en réalité, de nouvelles instances d'objets sont créées avec
        les valeurs mises à jour, et les variables sont réattribuées pour faire référence à ces nouvelles instances.
        Donc si on fait a=1 puis b=a puis a=2, a et b pointent au départ vers une même case contenant l'int 1. Quand on
        fait a=2, une nouvelle case contenant l'int est créée et a pointe dessus mais b continue de pointer vers l'int
        1.
        Rmq: si on fait alors b=3, plus rien ne pointe vers l'int 1: la case est alors détruite.

        D'un autre côté, les types de données mutables en Python comprennent :

        Listes : list
        Dictionnaires : dict
        Ensembles : set

        Ces types de données mutables peuvent être modifiés après leur création. Les opérations effectuées sur ces
        objets peuvent modifier leur contenu sans créer de nouvelles instances.
        Ici, comme plateau est une liste, si le plateau contenu dans la classe Jeu est modifié, la référence à ce
        plateau dans le gestionnaire de victoire verra ce changement. Ca n'est par ailleurs pas une copie du tableau
        donc on a pas de duplication de tableau.
        Rmq: Si on veut réellement copier un tableau, il existe plusieurs approches:

        Utiliser la méthode copy() : Vous pouvez utiliser la méthode copy() intégrée pour créer une copie de la liste. 
        Cette méthode effectue une copie superficielle, ce qui signifie que les objets contenus dans la liste ne sont 
        pas copiés, mais les références à ces objets sont copiées. Par conséquent, si les objets contenus dans la liste 
        sont également mutables, ils seront toujours partagés entre la liste d'origine et la copie.
        a = [1, 2, 3]
        b = a.copy()

        Utiliser l'opérateur de slicing ([:]) : Vous pouvez utiliser l'opérateur de slicing pour créer une copie de la 
        liste. Cela crée une nouvelle liste avec des éléments identiques à la liste d'origine. Cette méthode est 
        également une copie superficielle.
        a = [1, 2, 3]
        b = a[:]

        Utiliser la fonction list() : Vous pouvez utiliser la fonction list() pour créer une nouvelle liste à partir de 
        la liste existante. Cela crée également une copie superficielle.
        a = [1, 2, 3]
        b = list(a)

        Si vous avez besoin de créer une copie profonde de la liste, où les objets contenus dans la liste sont également
        copiés de manière indépendante, vous pouvez utiliser le module copy de Python et sa fonction deepcopy() :
        a = [1, 2, [3, 4]]
        b = copy.deepcopy(a)
        Avec deepcopy(), une copie complètement indépendante de la liste est créée, y compris les objets contenus à 
        l'intérieur. Cela garantit que les modifications apportées à la liste d'origine ne seront pas répercutées sur la
        copie, et vice versa.

        Rmq: si une classe personnalisée contient des attributs immuables et des attributs mutables, ceux-ci le
        resteront. Lorsqu'on créer une référence à un objet de classe personnalisée, il est donc conseillé de ne se
        servir de cette référence que pour lire des valeurs. Si on veut modifier des valeurs, il peut-être judicieux
        d'appeler des méthodes de la classe chargées de le faire."""

        # Gestionnaire état du jeu
        self.gestionnaire_fin_jeu = GestionnaireFinJeu(self.observateurs)

        # Conditions de victoire
        self.compteur_tours_sans_evolution = 0

    def get_etat_jeu(self):
        return self.gestionnaire_fin_jeu.get_etat_jeu()

    def gerer_conditions_arret(self, joueur_actif, adversaire):
        self.gerer_manque_materiel(joueur_actif)
        self.gerer_50_tours_sans_evolution()
        self.gerer_3x_meme_position(joueur_actif)
        self.gerer_menaces_roi(joueur_actif, adversaire)

    def gerer_manque_materiel(self, joueur):
        if self.manque_materiel(joueur):
            self.gestionnaire_fin_jeu.arreter_jeu(GestionnaireFinJeu.MANQUE_MATERIEL)

    def manque_materiel(self, joueur1):
        compteur_fous_joueur1 = 0
        compteur_cavaliers_joueur1 = 0
        compteur_fous_joueur2 = 0
        compteur_cavaliers_joueur2 = 0
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):

                if isinstance(self.plateau.coups[i][j], (Pion, Tour, Reine)):
                    return False
                elif isinstance(self.plateau.coups[i][j], Fou):
                    if self.plateau.coups[i][j].proprietaire == joueur1:
                        compteur_fous_joueur1 += 1
                    else:
                        compteur_fous_joueur2 += 1
                elif isinstance(self.plateau.coups[i][j], Cavalier):
                    if self.plateau.coups[i][j].proprietaire == joueur1:
                        compteur_cavaliers_joueur1 += 1
                    else:
                        compteur_cavaliers_joueur2 += 1

                if compteur_fous_joueur1 > 1 or compteur_fous_joueur2 > 1 \
                        or compteur_fous_joueur1 + compteur_fous_joueur2 > 2 \
                        or compteur_cavaliers_joueur1 + compteur_cavaliers_joueur2 > 2:
                    return False
        return True

    def gerer_50_tours_sans_evolution(self):
        self.maj_nb_tours_sans_evolution()
        if self.compteur_tours_sans_evolution > 49:
            self.gestionnaire_fin_jeu.arreter_jeu(GestionnaireFinJeu.CINQUANTE_TOURS_SANS_EVOLUTION)

    def maj_nb_tours_sans_evolution(self):
        if self.plateau.piece_mangee_ce_tour or self.plateau.pion_bouge_ce_tour:
            self.compteur_tours_sans_evolution = 0
        else:
            self.compteur_tours_sans_evolution += 1

    def gerer_3x_meme_position(self, joueur_actif):
        if self.compteur_tours_sans_evolution == 0:  # Si une évolution a eu lieu, on ne pourra pas retrouver de positions précédentes
            self.plateau.effacer_sauv_etats_plateau()
        self.plateau.sauvegarder_etat_plateau(joueur_actif)
        if self.trois_fois_meme_position():
            self.gestionnaire_fin_jeu.arreter_jeu(GestionnaireFinJeu.TROIS_FOIS_MEME_POSITION)

    def trois_fois_meme_position(self):
        self.plateau.sauv_etats_plateau = sorted(
            self.plateau.sauv_etats_plateau)  # Tri du tableau par ordre alphabétique
        for i in range(len(self.plateau.sauv_etats_plateau) - 2):
            if self.plateau.sauv_etats_plateau[i] == self.plateau.sauv_etats_plateau[i + 1] == \
                    self.plateau.sauv_etats_plateau[i + 2]:
                return True
        return False

    def gerer_menaces_roi(self, joueur_actif, adversaire):
        if not self.adversaire_a_coup_possible(joueur_actif, adversaire):
            if self.adversaire_en_echec(joueur_actif):
                self.gestionnaire_fin_jeu.arreter_jeu(GestionnaireFinJeu.VICTOIRE)
            else:
                self.gestionnaire_fin_jeu.arreter_jeu(GestionnaireFinJeu.PAT)

    def adversaire_a_coup_possible(self, joueur_actif, adversaire):
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.plateau.case_contient_piece_a(i, j, adversaire):
                    if self.piece_a_coup_possible(i, j, joueur_actif):
                        return True
        return False

    def piece_a_coup_possible(self, case_x, case_y, joueur_actif):
        self.plateau.activer_piece(case_x, case_y)
        self.plateau.calculer_coups_possibles_piece_active(joueur_actif)
        for i in range(NB_COLONNES):
            for j in range(NB_LIGNES):
                if self.plateau.coups_possibles[i][j] != self.plateau.d_coups["non"]:
                    self.plateau.desactiver_piece_active()
                    self.plateau.effacer_tableau_coups_possibles()
                    return True
        self.plateau.desactiver_piece_active()
        self.plateau.effacer_tableau_coups_possibles()
        return False

    def adversaire_en_echec(self, joueur_actif):
        roi_adverse_x, roi_adverse_y = self.plateau.pos_roi_n if joueur_actif == 1 else self.plateau.pos_roi_b
        self.plateau.calculer_cases_controlees_par(joueur_actif)
        if self.plateau.cases_controlees[roi_adverse_x][roi_adverse_y] != self.plateau.d_coups["non"]:
            self.plateau.effacer_cases_controlees()
            return True
        self.plateau.effacer_cases_controlees()
        return False

    def reset(self):
        self.gestionnaire_fin_jeu.reset()


class GestionnaireFinJeu:
    """Gestion état du jeu"""

    JEU_CONTINUE = 0
    VICTOIRE = 1
    MANQUE_TEMPS = 2
    MANQUE_MATERIEL = 3
    PAT = 4
    TROIS_FOIS_MEME_POSITION = 5
    CINQUANTE_TOURS_SANS_EVOLUTION = 6

    def __init__(self, observateurs):
        # Observateurs
        self.observateurs = observateurs

        self.etat_jeu = GestionnaireFinJeu.JEU_CONTINUE

    def get_etat_jeu(self):
        return self.etat_jeu

    def arreter_jeu(self, nouvel_etat_jeu):
        self.etat_jeu = nouvel_etat_jeu
        self.notifier_observateurs_jeu_arrete()

    def reset(self):
        self.etat_jeu = GestionnaireFinJeu.JEU_CONTINUE

    def notifier_observateurs_jeu_arrete(self):
        for observateur in self.observateurs:
            observateur.jeu_arrete()

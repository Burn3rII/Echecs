"""Modèle jeu d'échec. C'est ici qu'est contenue la logique du jeu.
Celui-ci fonctionne de la manière suivante :
 * Il est autonome.
 * Des observateurs peuvent lui être lié. Ces observateurs sont toutes
   les classes qui doivent être informées lorsqu'une modification
   importante a lieu sur le plateau, par exemple pour effectuer un
   changement graphique.
 * Le modèle contient 2 types de méthodes :
    → Des méthodes permettant à un utilisateur d'effectuer des actions
      sur le modèle.
    → Lorsque qu'une modification devant être notifiée aux observateurs
      a lieu, un appel à une méthode "notifier_observateurs_..." a lieu.
      Cette méthode est chargée d'appeler une méthode d'un même nom chez
      tous les observateurs. D'autres méthodes de notifications peuvent
      être créées suivant les besoins.
 * Remarque : Les observateurs doivent être enregistrés avant d'appeler
   la méthode "lancer_jeu" car dès le lancement, les pièces sont
   générées sur le plateau. Si certains observateurs ne sont pas
   enregistrés à ce moment-là, ils manqueront donc l'information qu'une
   pièce a été créée."""

# -------------------------Bibliothèques---------------------------------------
# ----- Fichiers internes
from .plateau import Plateau
from .gestionnaire_fin_jeu import (GestionnaireConditionsArret,
                                   GestionnaireFinJeu)

# -------------------------Classes---------------------------------------------


class Modele:
    """Gestion générale des règles du jeu
    """

    def __init__(self):
        # Observateurs
        self.observateurs = set()  # Utilisation d'un set au lieu d'une
        # liste car permet d'éviter les doublons et plus rapide

        # Plateau
        self.plateau = Plateau(self.observateurs)

        self.joueur_actif = 1
        self.nb_tours = 1

        # Gestionnaire fin de jeu
        self.gestionnaire_conditions_arret = GestionnaireConditionsArret(
            self.plateau, self.observateurs)

    def enregistrer_observateur(self, observateur):
        """Enregistre un observateur. Un observateur est une classe qui
        doit être informée lorsqu'une modification importante a lieu sur
        le plateau, par exemple pour effectuer un changement graphique.
        """
        self.observateurs.add(observateur)

    def effacer_observateur(self, observateur):
        """Retire l'observateur donné de la liste des observateurs.
        """
        self.observateurs.remove(observateur)

    def lancer_jeu(self):
        """Demande au plateau de générer les pièces et indique aux
        observateurs de modifier les infos.
        """
        self.plateau.lancer_jeu()
        self.notifier_observateurs_changement_infos()

    def get_joueur_actif(self):
        """Retourne le numéro du joueur actif.
        """
        return self.joueur_actif

    def get_nb_tours(self):
        """Retourne le nombre de tours.
        """
        return self.nb_tours

    def get_etat_jeu(self):
        """Retourne le numéro correspondant à l'état du jeu.
        """
        return self.gestionnaire_conditions_arret.get_etat_jeu()

    def get_case_active(self):
        """Retourne les coordonnées de la case active.
        """
        return self.plateau.case_active

    def get_dico_coups(self):
        """Retourne le dictionnaire des coups.
        """
        return self.plateau.dict_coups

    def get_coups_possibles(self):
        """Retourne le tableau représentant les coups possibles.
        """
        return self.plateau.coups_possibles

    def maj_infos(self):
        """Avance les informations sur le jeu d'un tour et en informe
        les observateurs.
        """
        if (self.gestionnaire_conditions_arret.get_etat_jeu() ==
                GestionnaireFinJeu.JEU_CONTINUE):
            self.joueur_actif = self.joueur_actif % 2 + 1
            self.nb_tours += 1
        self.notifier_observateurs_changement_infos()

    def selectionner_piece(self, case_x, case_y):
        """Sélectionne la pièce de la case demandée et calcul ses coups
        possibles.
        """
        adversaire = self.joueur_actif % 2 + 1
        self.plateau.selectionner_piece(case_x, case_y, self.joueur_actif,
                                        adversaire)

    def deselectionner_piece_active(self):
        """Désélectionne la pièce active et efface les coups possibles.
        """
        self.plateau.deselectionner_piece_active()

    def jouer_coup(self, case_x, case_y, roque):
        """Joue le coup sélectionné pour la pièce active.
        """
        self.plateau.jouer_coup(case_x, case_y, roque)

    def choisir_piece_promotion(self, piece_choisie="Reine"):
        """Choisie la pièce en laquelle promouvoir le pion en train
        d'être promu.
        """
        self.plateau.promouvoir_pion(piece_choisie)

    def gerer_conditions_arret(self):
        """Test si une condition d'arrêt du jeu est validée.
        """
        adversaire = self.joueur_actif % 2 + 1
        self.gestionnaire_conditions_arret.gerer_conditions_arret(
            self.joueur_actif, adversaire)

    def nouvelle_partie(self):
        """Réinitialise toutes les données pour remettre l'état du jeu
        par défaut.
        """
        self.plateau.reset()
        self.gestionnaire_conditions_arret.reset()

        self.joueur_actif = 1
        self.nb_tours = 1

        self.notifier_observateurs_jeu_reset()

    def notifier_observateurs_changement_infos(self):
        """Indique aux observateurs que les informations du jeu ont été
        modifiées.
        """
        for observateur in self.observateurs:
            observateur.infos_modifiees()

    def notifier_observateurs_jeu_reset(self):
        """Indique aux observateurs que le jeu a été réinitialisé.
        """
        for observateur in self.observateurs:
            observateur.jeu_reset()

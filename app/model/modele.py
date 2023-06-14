"""Modèle jeu d'échec. C'est ici qu'est contenue la logique du jeu. Celui-ci fonctionne de la manière suivante :
 * Il est autonome.
 * Des observateurs peuvent lui être lié. Ces observateurs sont toutes les classes qui doivent être informées lorsqu'une
   modification importante a lieu sur le plateau, par exemple pour effectuer un changement graphique.
 * Le modèle contient 2 types de méthodes :
    → Des méthodes permettant à un utilisateur d'effectuer des actions sur le modèle.
    → Lorsque qu'une modification devant être notifiée aux observateurs a lieu, un appel à une méthode
      "notifier_observateurs_..." a lieu. Cette méthode est chargée d'appeler une méthode d'un même nom chez tous les
      observateurs. D'autres méthodes de notifications peuvent être créées suivant les besoins.
 * Remarque : Les observateurs doivent être enregistrés avant d'appeler la méthode "lancer_jeu" car dès le lancement,
   les pièces sont générées sur le plateau. Si certains observateurs ne sont pas enregistrés à ce moment-là, ils
   manqueront donc l'information qu'une pièce a été créée."""

### Bibliothèques ######################################################################################################
### Fichiers internes ###
from .plateau import Plateau
from .gestionnaire_fin_jeu import GestionnaireConditionsArret, GestionnaireFinJeu

### Classes ############################################################################################################


class Modele:
    """Gestion générale des règles du jeu"""

    def __init__(self):
        # Observateurs
        self.observateurs = []

        # Plateau
        self.plateau = Plateau(self.observateurs)

        self.joueur_actif = 1
        self.nb_tours = 1

        # Gestionnaire fin de jeu
        self.gestionnaire_conditions_arret = GestionnaireConditionsArret(self.plateau, self.observateurs)

    def enregistrer_observateur(self, observateur):
        self.observateurs.append(observateur)

    def effacer_observateur(self, observateur):
        self.observateurs.remove(observateur)

    def lancer_jeu(self):
        self.plateau.lancer_jeu()
        self.notifier_observateurs_changement_infos()

    def get_joueur_actif(self):
        return self.joueur_actif

    def get_nb_tours(self):
        return self.nb_tours

    def get_etat_jeu(self):
        return self.gestionnaire_conditions_arret.get_etat_jeu()

    def get_case_active(self):
        return self.plateau.case_active

    def get_dico_coups(self):
        return self.plateau.d_coups

    def get_coups_possibles(self):
        return self.plateau.coups_possibles

    def maj_infos(self):
        if self.gestionnaire_conditions_arret.get_etat_jeu() == GestionnaireFinJeu.JEU_CONTINUE:
            self.joueur_actif = self.joueur_actif % 2 + 1
            self.nb_tours += 1
        self.notifier_observateurs_changement_infos()

    def selectionner_piece(self, case_x, case_y):
        adversaire = self.joueur_actif % 2 + 1
        self.plateau.selectionner_piece(case_x, case_y, self.joueur_actif, adversaire)

    def deselectionner_piece_active(self):
        self.plateau.deselectionner_piece_active()

    def jouer_coup(self, case_x, case_y, roque):
        self.plateau.jouer_coup(case_x, case_y, roque)

    def choisir_piece_promotion(self, piece_choisie="Reine"):
        self.plateau.promouvoir_pion(piece_choisie)

    def gerer_conditions_arret(self):
        adversaire = self.joueur_actif % 2 + 1
        self.gestionnaire_conditions_arret.gerer_conditions_arret(self.joueur_actif, adversaire)

    def nouvelle_partie(self):
        self.plateau.reset()
        self.gestionnaire_conditions_arret.reset()

        self.joueur_actif = 1
        self.nb_tours = 1

        self.notifier_observateurs_jeu_reset()

    def notifier_observateurs_changement_infos(self):
        for observateur in self.observateurs:
            observateur.infos_modifiees()

    def notifier_observateurs_jeu_reset(self):
        for observateur in self.observateurs:
            observateur.jeu_reset()

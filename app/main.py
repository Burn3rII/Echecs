"""Main du jeu d'échec. Créer le modèle, l'interface utilisateur, le
contrôleur puis lance le jeu.
"""

# TODO
#   Amélioration possible: utilisation, à la place des tableaux 2D de
#   dictionnaires. On utiliserait alors la case (par exemple 'e4' comme
#   clé et on associerait chaque clé à la pièce (objet de type Piece)
#   sur cette case).
#   Cela nécessite cependant de recoder beaucoup de méthodes.
#   Fonction temps
#   Améliorer graphiques
#   Ajouter une demande si l'utilisateur quitte en utilisant la croix ou
#   le bouton s'il veut vraiment quitter.
#   Possibilité de sauvegarde
#   Autres fonctions
#   _
#   Toujours vérifier dépendances, redondances, sécurité

# -------------------------Bibliothèques---------------------------------------
# ----- Fichiers internes
from app.model.modele import Modele
from app.view.interface_utilisateur import MainGUI
from app.controller.controleur import Controleur

# -------------------------Corps-----------------------------------------------

modele = Modele()
gui = MainGUI()
controleur = Controleur(gui, modele)

controleur.lancer_jeu()

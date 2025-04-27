## PROJET TICTACTOE EN LIGNE ET AVEC AGENT DRL :

Ce projet a été réalisé dans le cadre du cours "Fondement des Réseaux" à l'École Supérieure d'Économie Numérique (ESEN), Université de la Manouba (A.U 2024-2025).

## description
tictactoe est une application de morpion interactive développée en Python avec Pygame. Elle propose trois modes de jeu :  
- Joueur contre joueur (local)
- Joueur contre l’ordinateur (IA Q-learning)
- Joueur contre joueur en ligne (multijoueur réseau)

## Fonctionnalités

- **Interface graphique moderne** avec images personnalisées et boutons interactifs
- **Trois modes de jeu** : local, IA, et en ligne
- **Intelligence artificielle** basée sur Q-learning et stratégies de secours
- **Gestion réseau** pour le mode multijoueur en ligne (connexion à un serveur)
- **Détection automatique** des victoires, égalités, et gestion du score
- **Bouton de redémarrage** pour recommencer une partie à tout moment

## Installation

1. **Cloner le dépôt**  
git clone https://github.com/linarahma1/r-seaux.git
cd r-seaux


2. **Installer les dépendances**  
Python 3.7+ et Pygame sont requis.  
pip install pygame

3. **Lancer le jeu**  
python main.py



## Utilisation

- **Menu principal** : choisissez le mode de jeu souhaité.
- **Jeu local** : deux joueurs jouent à tour de rôle sur le même ordinateur.
- **Jeu contre l’IA** : affrontez une intelligence artificielle entraînée.
- **Jeu en ligne** : connectez-vous à un serveur et jouez contre un autre joueur distant.
- **Redémarrer** : utilisez le bouton « Restart » pour recommencer une partie.

## Structure du projet

├── README.md                     # Documentation utilisateur ce fichier 
├── documentation technique.md    # Documentation technique
├── main.py                       # Programme principal
├── server.py                     # Serveur multijoueur
├── q_agent.pkl                   # Modèle IA pré-entraîné
├── requirements.txt              # Dépendances
└── assets/
    ├── X.png                     # Image symbole X
    ├── O.png                     # Image symbole O
    ├── shape.png                 # Forme des boutons
    ├── texture_overlay.png       # Fond d'écran


## Remarques

- Pour le mode en ligne, un serveur compatible doit être disponible et lancé séparément.
- Le fichier `q_agent.pkl` doit être présent pour bénéficier de l’IA Q-learning ; sinon, l’IA utilisera des stratégies de secours.

## Contributions

Les contributions sont les bienvenues ! Proposez vos améliorations ou ouvrez une issue pour toute suggestion.


## Auteur

Projet développé par Ayadi Rahma et Fakhfekh Lina . 
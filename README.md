# 🎯 Morpion IA & Multijoueur  
*Un jeu de Tic Tac Toe avec intelligence artificielle et mode en ligne*  

![Game Screenshot](./assets/screenshot.png)  

## ✨ Fonctionnalités
- **3 Modes de Jeu**  
  - Joueur vs Joueur (Local)  
  - Joueur vs IA (Q-Learning)  
  - Multijoueur en ligne (TCP)  
- Interface Pygame intuitive  
- Serveur intégré (`server.py`)  

## Installation Rapide
```bash
git clone https://github.com/linarahma1/r-seaux.git
cd r-seaux
pip install -r requirements.txt
python main.py

## Comment Jouer? 

*Local : Cliquez sur les cases pour placer X/O
*IA : Affrontez l'agent RL (niveau configurable)
*En ligne :
Lancez le serveur : python server.py
Connectez deux clients via la même IP

--Structure du Projet
.
├── README.md                     # Documentation utilisateur ce fichier 
├── DOCUMENTATION_TECHNIQUE.md    # Documentation technique
├── main.py                       # Programme principal
├── server.py                     # Serveur multijoueur
├── q_agent.pkl                   # Modèle IA pré-entraîné
├── requirements.txt              # Dépendances
└── assets/
    ├── X.png                     # Image symbole X
    ├── O.png                     # Image symbole O
    ├── shape.png                 # Forme des boutons
    ├── texture_overlay.png       # Fond d'écran
    └── screenshot.png            # Capture du jeu (optionnel)
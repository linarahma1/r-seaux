Documentation Technique

# Documentation Technique – tictactoe

## 1. Présentation

tictactoe est un jeu de morpion multiplateforme en Python, doté d’une interface graphique Pygame, d’une IA Q-learning, et d’un mode multijoueur en ligne via sockets TCP. Il vise à offrir une expérience ludique, flexible et facilement extensible.

---

## 2. Architecture Générale

- **main.py** : point d’entrée, gestion du menu, des modes de jeu, et des événements.
- **Images** : fichiers PNG pour l’interface et les symboles.
- **q_agent.pkl** : table Q de l’agent IA (Pickle).
- **Gestion réseau** : communication client-serveur via sockets et JSON.

---

## 3. Dépendances

- Python ≥ 3.7
- Pygame
- pickle (standard)
- socket, threading, json (standard)

---

## 4. Description des modules principaux

### Interface graphique (Pygame)

- **Grille** : dessinée dynamiquement, centrée à l’écran.
- **Symboles** : images X et O redimensionnées à la taille des cases.
- **Bouton Restart** : image personnalisée, gestion du clic.
- **Affichage des messages** : statut du jeu, vainqueur, égalité.

### Modes de jeu

- **Joueur vs Joueur (local)**  
  Deux joueurs humains jouent à tour de rôle sur la même machine.  
  La grille est gérée par une matrice 3x3 (`markers`), chaque case valant 0 (vide), 1 (X), ou -1 (O).

- **Joueur vs IA**  
  L’IA utilise une table Q (`q_agent.pkl`).  
  Si la Q-table est absente ou incomplète, des règles stratégiques prennent le relais :  
    - Gagner si possible  
    - Bloquer l’adversaire  
    - Prendre le centre, un coin, ou un côté  
  L’IA choisit son action à chaque tour pair.

- **Joueur vs Joueur (en ligne)**  
  Connexion à un serveur via sockets TCP.  
  Les coups sont envoyés/recus en JSON.  
  Un thread dédié écoute les mises à jour du serveur.  
  Synchronisation stricte des tours et gestion d’état (attente, victoire, égalité).

### IA (Classe RLAgent)

- **Chargement du modèle** : tente de charger une Q-table ; sinon, active les règles de secours.
- **Action** : convertit l’état du plateau en chaîne, recherche la meilleure action dans la Q-table ou applique une stratégie.
- **Fallbacks** : gagne si possible, bloque, prend le centre, un coin, un côté, ou joue aléatoirement.

### Réseau

- **Connexion** : fonction `connect_to_server`, gestion des erreurs et de l’état d’attente.
- **Échange de messages** : JSON sérialisé, actions : assignation d’ID, début de partie, mouvement, fin de partie.
- **Thread de réception** : écoute en continu les mises à jour du serveur et met à jour l’état local.

---

## 5. Fonctions principales

- `draw_grid()` : dessine la grille du morpion.
- `draw_markers()` : affiche les symboles X et O selon l’état du plateau.
- `check_winner()` : vérifie la présence d’un gagnant ou d’une égalité.
- `restart_game()` : réinitialise la partie.
- `draw_button()` : affiche le bouton de redémarrage.
- `page_1()`, `page_2()`, `page_3()` : boucles principales pour chaque mode de jeu.
- `RLAgent.act()` : choix du coup IA.

---

## 6. Scénarios d’utilisation

- **Lancement** : le menu propose trois modes.
- **En jeu** : chaque clic valide une action, l’interface se met à jour.
- **Victoire/égalité** : message affiché, possibilité de recommencer.
- **Mode en ligne** : attente d’un adversaire, synchronisation des coups via le serveur.

---

## 7. Évolutions possibles

- Amélioration de l’IA (entraînement, heuristiques)
- Ajout d’un serveur intégré pour le multijoueur
- Support de grilles plus grandes
- Personnalisation des thèmes graphiques


*Pour toute question ou contribution, consultez le README ou ouvrez une issue sur GitHub.*
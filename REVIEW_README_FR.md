**Objet**
- Ce document est un compte‑rendu technique destiné aux deux développeurs en charge du projet `gomoku`. Il regroupe : constats principaux, pointeurs vers les fichiers concernés, recommandations priorisées (avec explications de nouveaux concepts et exemples concrets), puis conseils de qualité de code.

**Constats principaux**
- Performance : la recherche devient très lente car l'état du jeu est recopié intégralement à chaque nœud et l'évaluateur alloue et imprime des tableaux à chaque appel.
- Correctitude / fragilité : petites erreurs (constantes dupliquées, affectations suspectes, nombres magiques) rendent le code fragile et difficile à maintenir.
- Conception : manquent des optimisations standards pour un moteur de recherche (ordonnancement des coups, table de transposition, deepening itératif). L'usage de threads en Python n'apporte pas de gains significatifs tant que les allocations restent lourdes.

**Pointeurs de fichiers (à inspecter en priorité)**
- `thread.py` : recherche (`minmax`), génération de coups (`potential_moves`), évaluateur (`evaluate`).
- `Board.py` : règles (captures, double-three, séquences gagnantes), `play_moove`.
- `heuristic.py` : évaluation statique (bug d'indentation dans `evaluate_alignments`).
- `game.py` : gestion d'état (vérifier `set_players`).
- `capture.py` : logique de capture sur séquences gagnantes.

**Recommandations priorisées (avec explications et exemples)**

1) Actions immédiates (faible risque, gains rapides)
- Retirer les `print()` dans l'évaluateur (`thread.py:evaluate`) : l'I/O console est très coûteux lorsqu'il est appelé des milliers de fois.
- Éviter `np.pad()` dans l'évaluateur : au lieu d'allouer un tableau « padded » à chaque appel, extraire une fenêtre autour du coup ou vérifier manuellement les indices. Exemple :

```py
# Au lieu de : board = np.pad(game.board.board, ((0,5),(0,5)), ...)
H, W = game.board.board.shape
minx, maxx = max(0, x-5), min(W, x+6)
miny, maxy = max(0, y-5), min(H, y+6)
window = game.board.board[miny:maxy, minx:maxx]
```

- Remplacer nombres magiques (`18`, `19`) par `config.BOARD_SIZE - 1` ou `BOARD_SIZE`.

2) Changements de portée moyenne (important, effort moyen)
- Implémenter `make_move` / `unmake_move` (pattern make/unmake) :
  - Principe : appliquer le coup en place (muter le plateau et les compteurs), appeler la recherche récursive, puis annuler le coup pour restaurer l'état précédent. Cela évite la copie complète (`game.copy()`) par enfant.
  - Exemple minimal :

```py

  player.capture_score += len(captured)
  player.last_moves.insert(0, (x, y))
  game.player_turn = 1 if player.value == 2 else 2

  return prev

def unmake_move(game, player, x, y, prev):
  # 1) retirer la pierre jouée
  game.board.board[y, x] = 0

  # 2) restaurer les pierres capturées
  for cx, cy in prev['captured']:
    game.board.board[cy, cx] = 3 - player.value

  # 3) restaurer compteurs et listes
  player.capture_score = prev['capture_score_player']
  player.last_moves = prev['last_moves_player']
  game.player_turn = prev['player_turn']

  # 4) restaurer d'autres champs si nécessaire (winner, game_state...)
```

### Intégration dans la recherche
Remplacer la création d'un nouvel état pour chaque coup par :
```py
for move in moves:
  prev = make_move(game, player, move[0], move[1])
  val = minmax(game, depth-1, alpha, beta, not maximizing, opponent, last_move=move)
  unmake_move(game, player, move[0], move[1], prev)
  # traiter val pour alpha/beta
```

### Pourquoi c'est plus rapide

- Moins d'allocations mémoire : copier un plateau (`numpy.copy()`) alloue un nouveau tableau et copie 361 octets (pour 19x19 uint8) mais a aussi un coût d'allocation Python/C qui devient significatif quand il est fait des milliers de fois.
- Moins de travail du ramasse‑miettes (GC) : moins d'objets temporaires sont créés, donc moins de charge pour le GC.
- Meilleure localité mémoire : travailler sur le même tableau évite des lectures/écritures sur des buffers dispersés et profite du cache CPU.
- Moins d'appels Python : `game.copy()` peut appeler plusieurs deep_copy() et construire des objets Python (Player, Game) à chaque nœud — tout cela est coûteux.

### Conseils pratiques
- Démarrer par restaurer uniquement le plateau et `capture_score`, puis ajouter la restauration d'autres champs.
- Rédiger des tests unitaires basiques qui comparent l'état avant `make+unmake` et après ; ils doivent être identiques.
- Mesurer l'impact avec le script d'instrumentation ajouté (`scripts/benchmark_minmax.py`).

---

Le script d'instrumentation `scripts/benchmark_minmax.py` a été ajouté au dépôt ; il est non intrusif et peut être exécuté pour obtenir des chiffres de référence.

Fin.


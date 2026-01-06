"""
Script d'instrumentation non intrusif pour mesurer le temps d'exécution
et le nombre de nœuds visités par la fonction `minmax` définie dans
`thread.py`.

Usage :
    python3 scripts/benchmark_minmax.py [depth]

Le script :
- crée un `Game` minimal et deux `Player` (valeurs par défaut),
- monkeypatch la fonction `thread.minmax` par une enveloppe qui
  incrémente un compteur avant d'appeler l'implémentation originale ;
  comme l'original est conservé et appelé depuis l'enveloppe, les
  appels récursifs sont aussi comptés,
- exécute `minmax` sur la position courante et affiche temps, nœuds et
  nœuds/s.

Remarques :
- Le script ne modifie aucune logique des modules du projet : il ne fait
  que remplacer temporairement la référence `thread.minmax` pendant la
  mesure.
- Fournir une position plus réaliste (placer quelques pierres sur
  `game.board.board`) permet d'obtenir des mesures plus représentatives.
"""


import sys
import time
import thread
import numpy as np
from typing import Tuple

from srcs.game import Game
from srcs.player import Player
from srcs.enums.game_state_enum import GameType


def setup_game_with_sample_position() -> Tuple[Game, Tuple[int, int], Player]:
    """Crée un jeu minimal et place quelques pierres pour obtenir une
    position non triviale. Retourne (game, last_move, player_to_move).
    """
    game = Game(1)
    # créer deux joueurs (images non nécessaires ici)
    p1 = Player("", "", "P1", 1)
    p2 = Player("", "", "P2", 2)
    game.set_players(p1, p2)
    game.type = GameType.FUTURE

    # Exemple : placer quelques pierres pour créer une position
    b = game.board.board
    # une petite configuration manuelle (quelques coups)
    moves = [
        (9, 9, 1),
        (9, 10, 2),
        (10, 9, 1),
        (8, 9, 2),
        (7, 9, 1),
    ]
    for x, y, val in moves:
        b[y, x] = val

    # positionner les derniers coups (utile pour evaluate)
    p1.last_moves = [(7, 9)]
    p2.last_moves = [(8, 9)]

    # définir qui joue : P2 va jouer (par exemple)
    game.player_turn = 2

    # last_move passé au minmax doit être valide; on met le dernier coup
    last_move = p1.last_moves[0]

    player_to_move = game.get_player(game.get_player_value())

    return game, last_move, player_to_move


def benchmark(depth: int = 2):
    game, last_move, player = setup_game_with_sample_position()

    # compteur de nœuds
    counter = {"nodes": 0}

    # garder l'original
    original_minmax = thread.minmax

    def counting_minmax(*args, **kwargs):
        counter["nodes"] += 1
        return original_minmax(*args, **kwargs)

    # monkeypatch
    thread.minmax = counting_minmax

    try:
        print(f"Lancement du benchmark depth={depth} ...")
        t0 = time.perf_counter()
        score = thread.minmax(game, depth, float("-inf"), float("inf"), True, player, last_move)
        t1 = time.perf_counter()

        elapsed = t1 - t0
        nodes = counter["nodes"]
        rate = nodes / elapsed if elapsed > 0 else float("inf")

        print(f"Résultat score: {score}")
        print(f"Temps écoulé: {elapsed:.4f}s")
        print(f"Nœuds visités: {nodes}")
        print(f"Nœuds/s: {rate:.0f}")
    finally:
        # restaurer
        thread.minmax = original_minmax


if __name__ == "__main__":
    depth = 2
    if len(sys.argv) > 1:
        try:
            depth = int(sys.argv[1])
        except ValueError:
            print("Argument depth invalide, utilisation depth=2")
    benchmark(depth)

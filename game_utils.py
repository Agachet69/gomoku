from Board import Board
from game import Game
from game_state_enum import GameType, GameState
from thread import init_threads


def replay(game: Game):
    game.board = Board()
    game.winner = None
    game.player_turn = 1
    game.P1.capture_score = 0
    game.P2.capture_score = 0
    game.game_state = GameState.Playing
    if game.type == GameType.AI or game.type == GameType.FUTURE:
        init_threads(game)

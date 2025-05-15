from player import Player
from game_state_enum import GameState
class Game:
    def __init__(self, player):
        self.game_state = GameState.Creating
        self.player_turn = player
        self.winner = None

    def set_board(self, board):
        self.board = board

    def set_players(self, P1: Player, P2: Player):
        self.P1 = P1
        self.P2 = P2

    def has_played(self):
        player = self.player_turn
        self.player_turn = 1 if self.player_turn == 2 else 2
        return player
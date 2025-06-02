from player import Player
from Board import Board, BOARD_SIZE
from game_state_enum import GameState


class Game:
    def __init__(self, player):
        self.game_state = GameState.Creating
        self.player_turn = player
        self.winner = None
        self.win_if_not_captured = False
        self.program_run = True

    def set_players(self, P1: Player, P2: Player):
        self.board = Board()
        self.winner = None
        self.player_turn = 1
        self.P1 = P1
        self.P2 = P2
        self.winner = P2

    def has_played(self):
        player = self.player_turn
        self.player_turn = 1 if self.player_turn == 2 else 2
        return player
    
    def get_opponent(self):
        return 1 if self.player_turn == 2 else 2
    
    def get_me(self):
        return 1 if self.player_turn == 1 else 2

    def exit(self):
        self.program_run = False

    def replay(self):
        self.board = Board()
        self.winner = None
        self.player_turn = 1
        self.game_state = GameState.Playing

    def menu(self):
        self.game_state = GameState.Creating

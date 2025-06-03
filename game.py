from player import Player
from Board import Board, BOARD_SIZE
from game_state_enum import GameState


class Game:
    def __init__(self, player):
        self.game_state = GameState.Creating
        self.player_turn = player
        self.winner = None
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
    
    def get_opponent_value(self):
        return 1 if self.player_turn == 2 else 2
    
    def get_me_value(self):
        return 1 if self.player_turn == 1 else 2
    
    def get_player(self, player_value):
        return self.P1 if self.P1.value == player_value else self.P2

    def get_opponent(self, player_value):
        return self.P1 if self.P1.value != player_value else self.P2

    def exit(self):
        self.program_run = False

    def replay(self):
        self.board = Board()
        self.winner = None
        self.player_turn = 1
        self.P1.capture_score = 0
        self.P2.capture_score = 0
        self.game_state = GameState.Playing

    def menu(self):
        self.game_state = GameState.Creating

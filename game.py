from player import Player
from Board import Board
from game_state_enum import GameState
import numpy as np
from config import BOARD_SIZE


class Game:
    def __init__(self, player=1):
        self.game_state = GameState.Creating
        self.player_turn = player
        self.winner = None
        self.program_run = True
        self.P1 = None
        self.P2 = None
        self.board = Board()
        self.historic = []
        self.step_historic = 0
        self.last_chance_capture = None
        self.type = None
        self.team = None

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

    def get_player_value(self):
        return 2 if self.player_turn == 2 else 1

    def get_me_value(self):
        return 1 if self.player_turn == 1 else 2

    def get_player(self, player_value):
        return self.P1 if self.P1.value == player_value else self.P2

    def get_opponent(self, player_value):
        return self.P1 if self.P1.value != player_value else self.P2

    def exit(self):
        self.program_run = False

    def menu(self):
        self.game_state = GameState.Creating
        self.team = None
        self.type = None

    # Méthodes exposées pour multiprocessing
    def get_game_state(self):
        return self.game_state

    def get_program_run(self):
        return self.program_run

    def set_program_run(self, value: bool):
        self.program_run = value

    def get_board(self):
        return self.board

    def get_winner(self):
        return self.winner

    def addHistoric(self, board):
        if len(self.historic) < 1:
            self.historic.append(np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.uint8))

        if self.step_historic < len(self.historic) - 1:
            self.historic = self.historic[: self.step_historic + 1]
        self.step_historic += 1
        self.historic.append(board)

    def get_back_historic(self):
        if self.step_historic > 0:
            self.has_played()
            self.step_historic -= 1
            opponent_value = self.get_opponent_value()
            actual_opponent_count = np.count_nonzero(self.board.board == opponent_value)
            old_opponent_count = np.count_nonzero(
                self.historic[self.step_historic] == opponent_value
            )
            if old_opponent_count > actual_opponent_count:
                diff = old_opponent_count - actual_opponent_count
                player = self.get_player(1 if opponent_value == 2 else 2)
                player.capture_score -= diff
            self.board.board = self.historic[self.step_historic].copy()

    def get_front_historic(self):
        if self.step_historic < len(self.historic) - 1:
            self.has_played()
            self.step_historic += 1
            player_value = self.get_player_value()
            old_player_count = np.count_nonzero(self.board.board == player_value)
            actual_player_count = np.count_nonzero(
                self.historic[self.step_historic] == player_value
            )
            diff = old_player_count - actual_player_count
            if diff > 1:
                player = self.get_player(1 if player_value == 2 else 2)
                player.capture_score += diff
            self.board.board = self.historic[self.step_historic].copy()

    def copy(self):
        new_game = Game(self.player_turn)
        new_game.game_state = self.game_state
        new_game.winner = (
            self.P1.deep_copy()
            if self.winner == self.P1
            else self.P2.deep_copy()
            if self.winner == self.P2
            else None
        )
        new_game.program_run = self.program_run
        new_game.P1 = self.P1.deep_copy() if self.P1 else None
        new_game.P2 = self.P2.deep_copy() if self.P2 else None
        new_game.board = self.board.deep_copy()

        return new_game

from Board import Board

class Game:
    def __init__(self, player):
        self.player_turn = player
        self.moves_P1 = 0
        self.moves_P2 = 0
        self.board = Board()

    def has_played(self):
        player = self.player_turn
        self.player_turn = 1 if self.player_turn == 2 else 2
        return player
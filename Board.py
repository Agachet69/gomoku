import numpy as np
from game import Game

BOARD_SIZE = 19


class Board:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.uint8)

    def is_legal_moove(self, x, y):
        if (x < 0 or y < 0):
            return False
        if (self.board[y, x] != 0):
            return False
        return True
        # print(self.board)
        # check double-three

    def is_winner_moove(self, player, x ,y):
        self.is_winner_moove()
        print()

    def play_move(self,game : Game, x, y):
        if self.is_legal_moove(x, y):
            player = game.has_played()
            self.board[y, x] = player
            if player == 1:
                game.moves_P1 += 1
            else:
                game.moves_P2 += 1
            if self.is_winner_moove(player, x, y):
                print('victoire')
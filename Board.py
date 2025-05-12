import numpy as np


BOARD_SIZE = 19


class Board:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.uint8)

    def is_legal_moove(self, x, y):
        if (x < 0 or y < 0):
            return False
        return True
        # print(self.board)
        # check double-three

    def play_move(self, x, y):
        if self.is_legal_moove(x, y):
            self.board[y,x] = 1
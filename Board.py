import numpy as np


BOARD_SIZE = 19


class Board:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.uint8)

    def is_legal_moove(self):
        print(self.board)
        # check double-three

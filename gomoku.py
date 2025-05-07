import numpy as np


BOARD_SIZE = 19
EMPTY, PLAYER, PLAYER = 0, 1, 2

class Board:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.uint8)

    def is_legal_moove(self):
        print(self.board)
        # check double-three


def main():
    board = Board()
    board.is_legal_moove()

main()
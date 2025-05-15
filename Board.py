import numpy as np
from game import Game
from game_state_enum import GameState


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

    def is_on_board(self, x, y):
        if x < 0 or y < 0 or x >= BOARD_SIZE or y >= BOARD_SIZE:
            return False
        return True
        

    def is_winner_moove(self, player, x ,y):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for (dy, dx) in directions:
            stones = 1

            pos_y, pos_x = y + dy, x + dx
            while stones < 5 and self.is_on_board(pos_x, pos_y) and self.board[pos_y, pos_x] == player:
                stones += 1
                pos_y += dy
                pos_x += dx

            pos_y, pos_x = y - dy, x - dx
            while stones < 5 and self.is_on_board(pos_x, pos_y) and self.board[pos_y, pos_x] == player:
                stones += 1
                pos_y -= dy
                pos_x -= dx

            if stones >= 5:
                return True
            
    def play_moove(self, game : Game, x, y):
        if self.is_legal_moove(x, y):
            player = game.has_played()
            self.board[y, x] = player
            if player == 1:
                game.P1.mooves += 1
            else:
                game.P2.mooves += 1
            if self.is_winner_moove(player, x, y):
                if player == game.P1.value:
                    game.winner = game.P1
                else:
                    game.winner = game.P2
                
                print('victoire')
                game.game_state = GameState.Finish
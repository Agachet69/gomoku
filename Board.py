from __future__ import annotations
import numpy as np
from game_state_enum import GameState
from player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game

BOARD_SIZE = 19


class Board:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.uint8)
        self.human_best_moves = []

    def is_legal_moove(self, x, y, game: Game):
        if x < 0 or y < 0:
            return False
        if self.board[y, x] != 0:
            return False
        if self.is_double_three(x, y, game):
            return False
        return True

    def is_double_three(self, x, y, game: Game):
        player_value = game.get_me_value()
        opponent_value = game.get_opponent_value()
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        board = game.board.board
        three_number = 0

        for dx, dy in directions:
            can_be_three = True
            deepth = 1
            empty = 0
            # first_empty = 0
            # second_empty = 0
            stones = 1

            pos_y, pos_x = y + dy, x + dx
            while self.is_on_board(pos_x, pos_y) and empty <= 1 and deepth <= 4:
                position_value = board[pos_y, pos_x]
                
                if position_value == player_value:
                    stones += 1


                if deepth < 3 and position_value == opponent_value:
                    can_be_three = False
                    print("False double three")
                    break

                # if position_value == 0:
                #     first_empty += 1
                
                
                
                
                
                
                # if stones == 3 and board[pos_y, pos_x] == opponent_value:
                #     print('three blocked')
                #     can_be_three = False
                #     break


                deepth +=1
                pos_x += dx
                pos_y += dy

            # if stones == 3 and not self.is_on_board(pos_x, pos_y):
            #     print("three blocked")
            #     can_be_three = False

            empty = 0
            deepth = 0
            pos_y, pos_x = y - dy, x - dx
            while (
                can_be_three is True
                and self.is_on_board(pos_x, pos_y)
                and empty <= 1
                and deepth <= 4
            ):
                position_value = board[pos_y, pos_x]
                if position_value == player_value:
                    stones += 1


                if deepth < 3 and position_value == opponent_value:
                    can_be_three = False
                    print("False double three")
                    break

                # if position_value == 0:
                #     second_empty += 1

                deepth +=1
                pos_x -= dx
                pos_y -= dy

            
            
            if can_be_three is True and stones == 3:
                print(' three')
                three_number += 1
        if three_number > 1:
            print('double three')
            return True
        return False
    

    def is_on_board(self, x, y):
        if x < 0 or y < 0 or x >= BOARD_SIZE or y >= BOARD_SIZE:
            return False
        return True

    def is_capture_moove(self, game: Game, my_player, my_opponent, x, y):
        directions = [
            (1, 0),
            (0, 1),
            (1, 1),
            (1, -1),
            (-1, 0),
            (0, -1),
            (-1, -1),
            (-1, 1),
        ]
        new_board = game.board.board.copy()
        player = game.P1 if my_player == game.P1.value else game.P2

        for dy, dx in directions:
            stones = 0
            pos_y, pos_x = y + dy, x + dx
            while (
                self.is_on_board(pos_x, pos_y)
                and self.board[pos_y, pos_x] == my_opponent
            ):
                stones += 1
                pos_y += dy
                pos_x += dx

            if (
                self.is_on_board(pos_x, pos_y)
                and stones == 2
                and self.board[pos_y, pos_x] == player.value
            ):
                pos_y -= dy
                pos_x -= dx
                if not self.is_on_board(pos_x, pos_y):
                    continue
                player.capture_score += 2
                new_board[pos_y, pos_x] = 0
                new_board[pos_y - dy, pos_x - dx] = 0
                print(f"{player.value} score : {player.capture_score}")
        self.update_board(new_board)

        return player

    def can_be_captured(self, x, y, player: Player, opponent_value):
        directions = [
            (1, 0),
            (0, 1),
            (1, 1),
            (1, -1),
            (-1, 0),
            (0, -1),
            (-1, -1),
            (-1, 1),
        ]
        board = self.board
        for dx, dy in directions:
            if (
                self.is_on_board(x + 1 * dx, y + 1 * dy)
                and self.is_on_board(x - 1 * dx, y - 1 * dy)
                and self.is_on_board(x + 2 * dx, y + 2 * dy)
                and board[y + 1 * dy, x + 1 * dx] == player.value
            ):
                start_stone = board[y - 1 * dy, x - 1 * dx]
                last_stone = board[y + 2 * dy, x + 2 * dx]
                if (
                    start_stone in (0, opponent_value)
                    and last_stone in (0, opponent_value)
                    and last_stone != start_stone
                ):
                    return True
        return False

    def has_player_won(self, player_value):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y, x] != player_value:
                    continue

                for dx, dy in directions:
                    count = 1
                    for step in range(1, 5):
                        nx, ny = x + dx * step, y + dy * step
                        if (
                            0 <= nx < BOARD_SIZE
                            and 0 <= ny < BOARD_SIZE
                            and self.board[ny, nx] == player_value
                        ):
                            count += 1
                        else:
                            break
                    if count >= 5:
                        return True
        return False

    def is_winner_moove(self, player: Player, x, y, game: Game):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        if player.capture_score >= 10:
            return True

        for dy, dx in directions:
            stones = 1
            winners_stones_list = [(x, y)]

            pos_y, pos_x = y + dy, x + dx
            while (
                stones < 5
                and self.is_on_board(pos_x, pos_y)
                and self.board[pos_y, pos_x] == player.value
            ):
                stones += 1
                winners_stones_list.append((pos_x, pos_y))
                pos_y += dy
                pos_x += dx

            pos_y, pos_x = y - dy, x - dx

            while (
                stones < 5
                and self.is_on_board(pos_x, pos_y)
                and self.board[pos_y, pos_x] == player.value
            ):
                stones += 1
                winners_stones_list.append((pos_x, pos_y))
                pos_y -= dy
                pos_x -= dx
            if stones >= 5:
                for x, y in winners_stones_list:
                    if self.can_be_captured(
                        x, y, player, 1 if player.value == 2 else 2
                    ):
                        return False
                return True

        return False

    def play_moove(self, game: Game, x, y):
        if self.is_legal_moove(x, y, game):
            my_player_value = game.get_me_value()
            if my_player_value == 2:
                self.human_best_moves = []
            opponent = game.get_opponent(my_player_value)
            player = self.is_capture_moove(game, my_player_value, opponent.value, x, y)
            if self.has_player_won(opponent.value):
                game.winner = opponent
                game.game_state = GameState.Finish

            game.has_played()
            self.board[y, x] = player.value

            if self.is_winner_moove(player, x, y, game):
                game.winner = player
                game.game_state = GameState.Finish
            if np.count_nonzero(self.board == 0) == 0:
                    game.winner = opponent
                    game.game_state = GameState.Draw
        else:
            print("Illegal moove.")

    def update_board(self, new_board):
        self.board = new_board
    
    def deep_copy(self):
        new_board = Board()
        new_board.board = self.board.copy()
        return new_board

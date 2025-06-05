from __future__ import annotations
import numpy as np
from game_state_enum import GameState
from player import Player
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from game import Game

BOARD_SIZE = 19


class HumanMoveManager:
    def __init__(self, move):
        self.move = move
        self.running = True
        self.move_to_do = None
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"move={self.move!r}, "
            f"running={self.running}, "
            f"move_to_do={self.move_to_do!r})"
        )


class Board:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.uint8)
        self.human_best_moves : List[HumanMoveManager] = []

    def is_legal_moove(self, x, y, game: Game):
        if x < 0 or y < 0:
            return False
        if self.board[y, x] != 0:
            return False
        return True
    
    def is_double_three(self, x, y, game):
        player_value = game.get_me_value()
        board = game.board.board
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        patterns = [
            [0, player_value, player_value, player_value, 0, -1],  # 01110*
            [0, player_value, 0, player_value, player_value, 0],  # 010110
            [0, player_value, player_value, 0, player_value, 0],  # 011010
        ]

        board[y, x] = player_value
        free_three_count = 0


        for dx, dy in directions:
            line = []
            for i in range(-5, 6):
                nx, ny = x + dx * i, y + dy * i
                val = board[ny, nx] if self.is_on_board(nx, ny) else -1
                line.append(val)

            for i in range(len(line) - 5):
                segment = line[i : i + 6]
                if any(all(seg == pat or pat == -1 for seg, pat in zip(segment, pattern)) for pattern in patterns):
                    free_three_count += 1
                    break

            if free_three_count >= 2:
                board[y, x] = 0
                return True

        board[y, x] = 0
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
            if self.is_double_three(x, y, game):
                print("Illegal moove double three.")
                return
            game.has_played()
            self.board[y, x] = player.value

            if self.is_winner_moove(player, x, y, game):
                game.winner = player
                game.game_state = GameState.Finish
            if np.count_nonzero(self.board == 0) == 0:
                    game.winner = opponent
                    game.game_state = GameState.Draw
            player.last_moves.insert(0, (x, y))
        else:
            print("Illegal moove.")

    def update_board(self, new_board):
        self.board = new_board
    
    def deep_copy(self):
        new_board = Board()
        new_board.board = self.board.copy()
        return new_board

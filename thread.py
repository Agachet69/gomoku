import random
import sys
from typing import Literal, Tuple

import pygame
from Board import Board, HumanMoveManager
from game import Game
from game_state_enum import GameState, GameType
import threading
import time
import numpy as np

from player import Player

# from heuristic import evaluate
from concurrent.futures import ThreadPoolExecutor


BIG_LOSS = -1000000
BIG_GAIN = 1000000
NORMAL_GAIN = 100
SMALL_GAIN = 1


DEPTH_MAX = 1
NUMBER_BEST_MOVES = 4


executor = ThreadPoolExecutor(max_workers=4)  # ajuste ce nombre selon ta machine


POTENTIAL_MOVES_DIRECTIONS = [
    (-2, -2),
    (-2, -1),
    (-2, 0),
    (-2, 1),
    (-2, 2),
    (-1, -2),
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (-1, 2),
    (0, -2),
    (0, -1),
    (0, 1),
    (0, 2),
    (1, -2),
    (1, -1),
    (1, 0),
    (1, 1),
    (1, 2),
    (2, -2),
    (2, -1),
    (2, 0),
    (2, 1),
    (2, 2),
]


def init_threads(game):
    # thread1 = threading.Thread(target=thread_opponent, args=(game,))
    # thread1.start()
    move_maker_thr = threading.Thread(target=move_maker_thread, args=(game,))
    move_maker_thr.start()

    # thread2  = threading.Thread(target=thread_AI, args=(game,))
    # thread2.start()
    # return thread


# def potential_moves(game: Game, player: Player):
#     board = game.board.board
#     rows, cols = board.shape
#     player_value = player.value
#     opponent = game.get_opponent(player_value)
#     moves = set()

#     player_positions = np.argwhere(board == player_value)

#     for i, j in player_positions:
#         for dx, dy in POTENTIAL_MOVES_DIRECTIONS:
#             ni, nj = i + dy, j + dx
#             if 0 <= ni < rows and 0 <= nj < cols and board[ni, nj] == 0:
#                 if game.board.is_legal_moove(nj, ni):
#                     is_double_three = game.board.is_double_three(nj, ni, game)
#                     is_capture = game.board.check_is_capture_moove(game, player, opponent, nj, ni)
#                     if not (is_double_three and not is_capture):
#                         moves.add((nj, ni))

#     return moves


def potential_moves(game: Game, player: Player):
    board = game.board.board
    rows, cols = board.shape
    player_value = player.value
    opponent = game.get_opponent(player_value)
    moves = set()

    # Positions des deux joueurs
    player_positions = np.argwhere((board == player_value) | (board == opponent.value))

    for i, j in player_positions:
        for dx, dy in POTENTIAL_MOVES_DIRECTIONS:
            ny, nx = i + dy, j + dx
            if 0 <= ny < rows and 0 <= nx < cols and board[ny, nx] == 0:
                if (nx, ny) in moves:
                    continue
                if not game.board.is_legal_moove(nx, ny):
                    continue
                if game.board.is_double_three(nx, ny, game):
                    captured, new_board, score = game.board.check_is_capture_moove(
                        game, player, opponent, nx, ny
                    )
                    if not captured:
                        continue
                moves.add((nx, ny))
    return moves


def get_kern_col_idx(
    pos: Tuple[int, int], direction: int = 1, length: int = 5
):  # si dir = 1 alors vers le bas | si dir = -1 alors vers le haut
    return pos[0] * np.ones(length, dtype="int8"), np.arange(
        pos[1], pos[1] + direction * length, direction
    )


def get_kern_row_idx(
    pos: Tuple[int, int], direction: int = 1, length: int = 5
):  # si dir = 1 alors vers le droite | si dir = -1 alors vers la gauche
    return np.arange(pos[0], pos[0] + direction * length, direction), [
        pos[1]
    ] * np.ones(length, dtype="int8")


def get_kern_diag_idx(
    pos: Tuple[int, int], slope: Tuple[int, int] = 1, length: int = 5
):  # si slope = (1, 1) alors vers le bas droite | si dir = (-1, -1) alors vers le haut gauche | si dir = (-1, 1) alors vers le bas gauche | si dir = (1, -1) alors vers le haut droite
    return np.arange(pos[0], pos[0] + slope[0] * length, slope[0]), np.arange(
        pos[1], pos[1] + slope[1] * length, slope[1]
    )


def kern_trad(board, kern_idx) -> np.array:
    coords = np.column_stack(kern_idx)
    return board[coords[:, 1], coords[:, 0]]


def find_longest_row(board, last_move: Tuple[int, int]):
    longest = {
        1: [1],
        -1: [1],
    }
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player
    blocked = 0
    # print("last_move", last_move)
    for dir in [1, -1]:
        for length in range(2, 6):
            values = kern_trad(
                board, get_kern_row_idx(last_move, direction=dir, length=length)
            )
            number_player = np.count_nonzero(values == player)
            # print(get_kern_row_idx(last_move, direction=dir, length=length))
            # print("dir", dir, "values", values)

            longest[dir].append(number_player)

            if number_player < length:
                if values[-1] == opponent:
                    blocked += 1
                break

    return {"longest": max(longest[1]) + max(longest[-1]) - 1, "blocked": blocked}


def find_longest_col(board, last_move: Tuple[int, int]):
    longest = {
        1: [1],
        -1: [1],
    }
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player
    blocked = 0
    for dir in [1, -1]:
        for length in range(2, 6):
            values = kern_trad(
                board, get_kern_col_idx(last_move, direction=dir, length=length)
            )
            number_player = np.count_nonzero(values == player)

            longest[dir].append(number_player)

            if number_player < length:
                if values[-1] == opponent:
                    blocked += 1
                break

    return {"longest": max(longest[1]) + max(longest[-1]) - 1, "blocked": blocked}


def find_longest_diag(board, last_move):
    longest = {
        True: {1: [1], -1: [1]},
        False: {1: [1], -1: [1]},
    }
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player
    blocked = 0

    flipped_board = np.fliplr(board)
    flipped_move = (19 - last_move[0] + 4, last_move[1])
    for right in [True, False]:
        for down in [1, -1]:
            for length in range(2, 6):
                if right:
                    values = kern_trad(
                        board,
                        get_kern_diag_idx(last_move, slope=[1, down], length=length),
                    )
                else:
                    values = kern_trad(
                        flipped_board,
                        get_kern_diag_idx(flipped_move, slope=[1, down], length=length),
                    )
                number_player = np.count_nonzero(values == player)

                longest[right][down].append(number_player)

                if number_player < length:
                    if values[-1] == opponent:
                        blocked += 1
                    break

    return {
        "longest": max(
            max(longest[True][1]) + max(longest[False][-1]),
            max(longest[False][1]) + max(longest[True][-1]),
        )
        - 1,
        "blocked": blocked,
    }


def find_longest(board, last_move: Tuple[int, int]):
    longest = []

    longest.append(find_longest_row(board, last_move))
    longest.append(find_longest_col(board, last_move))
    longest.append(find_longest_diag(board, last_move))

    return max(longest, key=lambda x: x["longest"])


def find_longest_opponent_row(board, last_move: Tuple[int, int]):
    longest = {
        1: [0],
        -1: [0],
    }
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player
    for dir in [1, -1]:
        for length in range(1, 5):
            values = kern_trad(
                board,
                get_kern_row_idx(
                    [last_move[0] + dir, last_move[1]], direction=dir, length=length
                ),
            )
            number_player = np.count_nonzero(values == opponent)

            longest[dir].append(number_player)

            if number_player < length:
                break

    return max(longest[1]) + max(longest[-1])


def find_longest_opponent_col(board, last_move: Tuple[int, int]):
    longest = {
        1: [0],
        -1: [0],
    }
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player
    for dir in [1, -1]:
        for length in range(1, 5):
            values = kern_trad(
                board,
                get_kern_col_idx(
                    [last_move[0], last_move[1] + dir], direction=dir, length=length
                ),
            )
            number_player = np.count_nonzero(values == opponent)

            longest[dir].append(number_player)

            if number_player < length:
                break

    return max(longest[1]) + max(longest[-1])


def find_longest_opponent_diag(board, last_move: Tuple[int, int]):
    longest = {
        True: {1: [1], -1: [1]},
        False: {1: [1], -1: [1]},
    }
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player

    flipped_board = np.fliplr(board)
    flipped_move = (19 - last_move[0] + 4, last_move[1])
    for right in [True, False]:
        for down in [1, -1]:
            for length in range(1, 5):
                if right:
                    values = kern_trad(
                        board,
                        get_kern_diag_idx(
                            [last_move[0] + 1, last_move[1] + down],
                            slope=[1, down],
                            length=length,
                        ),
                    )
                else:
                    values = kern_trad(
                        flipped_board,
                        get_kern_diag_idx(
                            [flipped_move[0] + 1, flipped_move[1] + down],
                            slope=[1, down],
                            length=length,
                        ),
                    )
                number_player = np.count_nonzero(values == opponent)

                longest[right][down].append(number_player)

                if number_player < length:
                    break

    return (
        max(
            max(longest[True][1]) + max(longest[False][-1]),
            max(longest[False][1]) + max(longest[True][-1]),
        )
        - 1
    )


def find_longest_opponent(board, last_move: Tuple[int, int]):
    player = board[last_move[1], last_move[0]]
    longest = [1]

    longest.append(find_longest_opponent_row(board, last_move))
    longest.append(find_longest_opponent_col(board, last_move))
    longest.append(find_longest_opponent_diag(board, last_move))

    return max(longest)


def detect_captures(board, last_move):
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player
    board_shape = board.shape

    # Patterns
    attack_pattern = np.array([player, opponent, opponent, player])
    defense_pattern_1 = np.array([opponent, player, player, player])  # forward
    defense_pattern_2 = np.array([player, player, player, opponent])  # reverse

    directions = [
        (get_kern_row_idx, (1, 0)),
        (get_kern_col_idx, (0, 1)),
        (get_kern_diag_idx, (1, 1)),
        (get_kern_diag_idx, (1, -1)),
    ]

    attack_detected = False
    defense_detected = False

    for get_idx, (dx, dy) in directions:
        for sign in [1, -1]:
            for offset in [0, -3]:
                start_x = last_move[0] + offset * dx * sign
                start_y = last_move[1] + offset * dy * sign

                if get_idx is get_kern_diag_idx:
                    slope = (dx, dy * sign)
                    x_idx, y_idx = get_idx((start_x, start_y), slope=slope, length=4)
                else:
                    x_idx, y_idx = get_idx((start_x, start_y), direction=sign, length=4)

                if (
                    np.any(x_idx < 0)
                    or np.any(x_idx >= board_shape[1])
                    or np.any(y_idx < 0)
                    or np.any(y_idx >= board_shape[0])
                ):
                    continue

                window = kern_trad(board, (x_idx, y_idx))

                # Check attack pattern
                if np.array_equal(window, attack_pattern):
                    for pos in [0, 3]:
                        if x_idx[pos] == last_move[0] and y_idx[pos] == last_move[1]:
                            attack_detected = True

                # Check defense pattern
                if np.array_equal(window, defense_pattern_1) or np.array_equal(
                    window, defense_pattern_2
                ):
                    if last_move[0] in x_idx and last_move[1] in y_idx:
                        defense_detected = True

    return {"attack": attack_detected, "defense": defense_detected}


def check_neighbor(board, last_move):
    mid_col = kern_trad(board, get_kern_col_idx(np.add(last_move, (0, -1)), length=3))
    mid_row = kern_trad(board, get_kern_row_idx(np.add(last_move, (-1, 0)), length=3))

    player = mid_col[1]

    values = [mid_col[0], mid_col[2], mid_row[0], mid_row[2]]

    return values.count(player)


def evaluate(game: Game, last_move: Tuple[int, int], player):
    print(f"evaluate: [{last_move[0]}, {last_move[1]}]")

    val = 0
    board = game.board.board  # np.ndarray 2D
    player_value = player.value
    opponent_value = 3 - player_value  # Si 1 → 2 ; si 2 → 1
    rows, cols = board.shape
    x, y = last_move  # (colonne, ligne)

    directions = [1, -1]

    board = np.pad(game.board.board, ((0, 5), (0, 5)), mode="constant")

    longest, blocked = find_longest(board, last_move).values()
    longest_opponent = find_longest_opponent(board, last_move)
    attacking, defending = detect_captures(board, last_move).values()

    if blocked != 2:
        if longest == 2:
            print("longest 2")
            val += SMALL_GAIN
        elif longest == 3:
            print("longest 3")
            val += 3 * NORMAL_GAIN
        elif longest == 4:
            print("longest 4")
            val += 6 * NORMAL_GAIN

    if longest == 5:
        print("longest 5")
        val += BIG_GAIN

    if longest_opponent == 2:
        print("longest opponent 2")
        val += SMALL_GAIN
    elif longest_opponent == 3:
        print("longest opponent 3")
        val += 4 * NORMAL_GAIN
    elif longest_opponent >= 4:
        print("longest opponent 4")
        val += BIG_GAIN

    if attacking or defending:
        print("capture detected")
        val += 3 * SMALL_GAIN + NORMAL_GAIN * player.capture_score

    val += check_neighbor(board, last_move)

    print(val)

    return val


def minmax(game: Game, depth, alpha, beta, maximizingPlayer, player: Player, last_move):
    opponent = game.get_opponent(player.value)
    if not depth or game.board.is_winner_moove(
        opponent, last_move[0], last_move[1], game
    ):
        return evaluate(game, last_move, opponent)

    moves = potential_moves(game, player)

    if maximizingPlayer:
        maxEval = float("-inf")

        for move in moves:
            new_state = game.copy()

            is_capture, new_board, score = new_state.board.check_is_capture_moove(
                new_state,
                player,
                new_state.get_opponent(player.value).value,
                move[0],
                move[1],
            )

            if is_capture:
                new_state.board.update_board(new_board)
                new_state.get_player(player.value).capture_score += score

            new_state.board.board[move[1]][move[0]] = player.value

            eval_value = minmax(
                new_state,
                depth - 1,
                alpha,
                beta,
                not maximizingPlayer,
                opponent,
                last_move=move,
            )

            maxEval = max(maxEval, eval_value)
            alpha = max(alpha, eval_value)

            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = float("inf")

        for move in moves:
            new_state = game.copy()

            is_capture, new_board, score = new_state.board.check_is_capture_moove(
                new_state,
                player,
                new_state.get_opponent(player.value).value,
                move[0],
                move[1],
            )

            if is_capture:
                new_state.board.update_board(new_board)
                new_state.get_player(player.value).capture_score += score

            new_state.board.board[move[1]][move[0]] = player.value
            eval_value = minmax(
                new_state,
                depth - 1,
                alpha,
                beta,
                not maximizingPlayer,
                opponent,
                last_move=move,
            )

            minEval = min(minEval, eval_value)
            beta = min(beta, eval_value)

            if beta <= alpha:
                break
        return minEval


def move_maker_thread(game: Game):
    # last_turn = game.P1.name
    while game.program_run and game.game_state != GameState.Finish:
        if game.type != GameType.FUTURE:
            if game.player_turn == game.P1.value:
                # last_turn = game.P1.name
                time.sleep(0.1)
                continue

        player_value = game.get_player_value()
        player = game.get_player(player_value)
        opponent = game.get_opponent(player_value)
        # if last_turn == game.P1.name:
        #     last_turn = game.P2.name
        # last_move = game.P1.last_moves[0]
        last_move = None
        if len(opponent.last_moves) > 0:
            last_move = opponent.last_moves[0]
        rows, cols = game.board.board.shape

        print("Human had moved")

        if not np.any(game.board.board == player_value):
            direction = random.choice(POTENTIAL_MOVES_DIRECTIONS)

            if last_move is None:
                game.board.play_moove(
                    game, random.randint(0, 18), random.randint(0, 18)
                )
            else:
                while not (
                    game.board.is_on_board(
                        last_move[1] + direction[1], last_move[0] + direction[0]
                    )
                    # 0 <= last_move[1] + direction[1] < rows
                    # and 0 <= last_move[0] + direction[0] < cols
                ):
                    direction = random.choice(POTENTIAL_MOVES_DIRECTIONS)

                game.board.play_moove(
                    game, last_move[0] + direction[0], last_move[1] + direction[1]
                )

            print("AI Played randomly")

        elif move_calculated := next(
            (move for move in game.board.human_best_moves if move.move == last_move),
            None,
        ):
            while move_calculated.running:
                time.sleep(0.01)
                pass

            game.board.play_moove(
                game, move_calculated.move_to_do[0], move_calculated.move_to_do[1]
            )
            print("AI Played move already calculated")
        else:
            print("Start calculated next move.")
            move_manager = HumanMoveManager(last_move)

            executor.submit(thread_AI, game, move_manager, player, opponent)

            while move_manager.running:
                # print("oui")
                time.sleep(0.01)
            game.board.play_moove(
                game, move_manager.move_to_do[0], move_manager.move_to_do[1]
            )

            print("AI Played move calculated on the fly")
        time.sleep(2.1)


def thread_opponent(game: Game):
    while game.program_run and game.game_state != GameState.Finish:
        start_time = time.time()
        move_score = []

        if (
            not np.any(game.board.board == 1)
            or game.player_turn == 2
            or len(game.board.human_best_moves) == NUMBER_BEST_MOVES
        ):
            time.sleep(0.1)
            continue

        moves = potential_moves(game, game.P1)
        best_score = 0

        for move in moves:
            new_state = game.copy()
            new_state.board.board[move[1]][move[0]] = game.P1.value
            score = minmax(
                new_state, DEPTH_MAX - 1, -10000000000, 10000000000, True, game.P2, move
            )
            # game.board.play_moove(game, move[0], move[1])

            move_score.append(score)
            # if best_score < score:
            #     best_score = score
            #     best_move = move
        # print(move_score)

        game.board.human_best_moves = [
            HumanMoveManager(move)
            for move, _ in sorted(
                list(zip(moves, move_score)), key=lambda x: x[1], reverse=True
            )[:NUMBER_BEST_MOVES]
        ]

        for move in game.board.human_best_moves:
            # game.board.board[move.move[0]][move.move[1]] = 1
            # time.sleep(.1)

            executor.submit(thread_AI, game, move)

        elapsed = time.time() - start_time  # Fin du chrono
        # print(f"Temps total de l'itération : {elapsed:.3f} secondes")


def thread_AI(
    game: Game, move_manager: HumanMoveManager, player: Player, opponent: Player
):
    start_time = time.time()
    state = game.copy()
    state.board.board[move_manager.move[1], move_manager.move[0]] = opponent.value

    best_scores = []
    moves = potential_moves(state, player)

    max_score = float("-inf")

    for move in moves:
        # if game.player_turn == 2:
        #     return
        new_state = state.copy()
        new_state.board.board[move[1], move[0]] = player.value
        # print(game.P1.name)
        score = minmax(
            new_state, DEPTH_MAX - 1, -10000000000, 10000000000, True, player, move
        )
        best_scores.append({"score": score, "move": move})
        # game.board.play_moove(game, move[0], move[1])

        if max_score < score:
            max_score = score

    best_moves = [entry["move"] for entry in best_scores if entry["score"] == max_score]

    move_manager.move_to_do = random.choice(best_moves)
    move_manager.running = False

    elapsed = time.time() - start_time  # Fin du chrono
    print(
        f"[{elapsed:.3f}s] Thread AI chose move {move_manager.move_to_do} (score: {max_score:03}) in response to human move {move_manager.move}"
    )


# def thread_opponent(game):
#     while True:
#         print('hello')

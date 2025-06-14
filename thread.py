import random
import sys
from typing import Literal
from Board import Board, HumanMoveManager
from game import Game
from game_state_enum import GameState
import threading
import time
import numpy as np

from player import Player
# from heuristic import evaluate
from concurrent.futures import ThreadPoolExecutor

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
    thread1 = threading.Thread(target=thread_opponent, args=(game,))
    thread1.start()
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


BIG_LOSS = -1000000
BIG_GAIN = 1000000
NORMAL_GAIN = 100
SMALL_GAIN = 1


import numpy as np

def evaluate(game: Game, last_move, player):
    val = 0
    board = game.board.board  # np.ndarray 2D
    player_value = player.value
    opponent_value = 3 - player_value  # Si 1 → 2 ; si 2 → 1
    rows, cols = board.shape
    x, y = last_move  # (colonne, ligne)

    directions = [
        (1, 0),   # horizontal →
        (0, 1),   # vertical ↓
        (1, 1),   # diagonale ↘
        (1, -1),  # diagonale ↗
    ]

    for dx, dy in directions:
        count = 1  # pion placé

        nx, ny = x + dx, y + dy
        while 0 <= ny < rows and 0 <= nx < cols and board[ny, nx] == player_value:
            count += 1
            nx += dx
            ny += dy

        nx, ny = x - dx, y - dy
        while 0 <= ny < rows and 0 <= nx < cols and board[ny, nx] == player_value:
            count += 1
            nx -= dx
            ny -= dy

        if count >= 5:
            val += BIG_GAIN
        elif count == 4:
            val += 3 * NORMAL_GAIN
        elif count == 3:
            val += 2 * NORMAL_GAIN
        elif count == 2:
            val += NORMAL_GAIN

        for sign in [1, -1]:
            cx, cy = x + sign * dx, y + sign * dy
            cx2, cy2 = x + sign * 2 * dx, y + sign * 2 * dy
            cx3, cy3 = x + sign * 3 * dx, y + sign * 3 * dy

            if (
                0 <= cy3 < rows and 0 <= cx3 < cols
                and board[cy, cx] == opponent_value
                and board[cy2, cx2] == opponent_value
                and board[cy3, cx3] == player_value
            ):
                val += NORMAL_GAIN * 2 + NORMAL_GAIN * player.capture_score if player.capture_score != 9 else BIG_GAIN

    return val



def minmax(game: Game, depth, alpha, beta, maximizingPlayer, player: Player, last_move):
    opponent = game.get_opponent(player.value)
    if not depth or game.board.is_winner_moove(
        player, last_move[0], last_move[1], game
    ):
        # return evaluate(game, player)
        return evaluate(game, last_move, player)

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
    last_turn = game.P1.name
    while game.program_run and game.game_state != GameState.Finish:

        if game.player_turn == game.P1.value:
            last_turn = game.P1.name
            time.sleep(0.1)
            continue

        if last_turn == game.P1.name:
            last_turn = game.P2.name
            last_move = game.P1.last_moves[0]
            rows, cols = game.board.board.shape

            print("Human had moved")

            if not np.any(game.board.board == 2):
                direction = random.choice(POTENTIAL_MOVES_DIRECTIONS)

                while not (
                    game.board.is_on_board(last_move[1] + direction[1], last_move[0] + direction[0])
                    # 0 <= last_move[1] + direction[1] < rows
                    # and 0 <= last_move[0] + direction[0] < cols
                ):
                    direction = random.choice(POTENTIAL_MOVES_DIRECTIONS)

                game.board.play_moove(
                    game, last_move[0] + direction[0], last_move[1] + direction[1]
                )

                print("AI Played randomly")

            elif move_calculated := next(
                (
                    move
                    for move in game.board.human_best_moves
                    if move.move == last_move
                ),
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

                executor.submit(thread_AI, game, move_manager)

                while move_manager.running:
                    # print("oui")
                    time.sleep(0.01)
                game.board.play_moove(
                    game, move_manager.move_to_do[0], move_manager.move_to_do[1]
                )

                print("AI Played move calculated on the fly")


DEPTH_MAX = 1
NUMBER_BEST_MOVES = 4


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


def thread_AI(game: Game, move_manager: HumanMoveManager):

    start_time = time.time()
    state = game.copy()
    state.board.board[move_manager.move[1], move_manager.move[0]] = game.P1.value

    best_scores = []
    moves = potential_moves(state, game.P2)

    max_score = float("-inf")

    for move in moves:
        # if game.player_turn == 2:
        #     return
        new_state = state.copy()
        new_state.board.board[move[1], move[0]] = game.P2.value
        # print(game.P1.name)
        score = minmax(
            new_state, DEPTH_MAX - 1, -10000000000, 10000000000, True, game.P1, move
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

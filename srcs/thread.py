# thread.py
import random
import sys
import time
import threading
from typing import Any, Dict, Tuple, Optional

import numpy as np
import pygame
from concurrent.futures import ThreadPoolExecutor

from Board import Board, HumanMoveManager
from game import Game
from enums.game_state_enum import GameState, GameType
from player import Player


BIG_LOSS = -1_000_000
BIG_GAIN = 1_000_000
NORMAL_GAIN = 100
SMALL_GAIN = 1

DEPTH_MAX = 1
NUMBER_BEST_MOVES = 4

executor = ThreadPoolExecutor(max_workers=4)

POTENTIAL_MOVES_DIRECTIONS = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]

# Debug counters (optional)
NODES = 0
T0 = 0.0


def init_threads(game):
    move_maker_thr = threading.Thread(target=move_maker_thread, args=(game,))
    move_maker_thr.start()


def potential_moves(game: Game, player: Player):
    """
    Génère les coups candidats autour des pierres existantes (les deux joueurs),
    en filtrant les coups illégaux (double-three non capturant, etc.).
    IMPORTANT: cast en int pour éviter les np.int64 qui cassent parfois les règles/GUI.
    """
    board = game.board.board
    rows, cols = board.shape
    player_value = player.value
    opponent = game.get_opponent(player_value)
    moves = set()

    # positions des deux joueurs
    positions = np.argwhere((board == player_value) | (board == opponent.value))

    for iy, ix in positions:
        for dx, dy in POTENTIAL_MOVES_DIRECTIONS:
            ny = int(iy + dy)
            nx = int(ix + dx)
            if 0 <= ny < rows and 0 <= nx < cols and board[ny, nx] == 0:
                key = (nx, ny)
                if key in moves:
                    continue
                if not game.board.is_legal_moove(nx, ny):
                    continue

                # Double-three : autorisé seulement si le coup est une capture
                if game.board.is_double_three(nx, ny, game):
                    try:
                        captured, _, _ = game.board.check_is_capture_moove(
                            game, player, opponent, nx, ny
                        )
                    except TypeError:
                        captured, _, _ = game.board.check_is_capture_moove(
                            game, player, opponent.value, nx, ny
                        )
                    if not captured:
                        continue

                moves.add((int(nx), int(ny)))

    return moves


def get_kern_col_idx(pos, direction: int = 1, length: int = 5):
    return pos[0] * np.ones(length, dtype="int16"), np.arange(
        pos[1], pos[1] + direction * length, direction, dtype="int16"
    )


def get_kern_row_idx(pos, direction: int = 1, length: int = 5):
    return np.arange(pos[0], pos[0] + direction * length, direction, dtype="int16"), (
        [pos[1]] * length
    )


def get_kern_diag_idx(pos, slope=(1, 1), length: int = 5):
    return np.arange(pos[0], pos[0] + slope[0] * length, slope[0], dtype="int16"), np.arange(
        pos[1], pos[1] + slope[1] * length, slope[1], dtype="int16"
    )


def kern_trad(board: np.ndarray, kern_idx) -> Optional[np.ndarray]:
    """
    Retourne la fenêtre board[y,x] correspondant aux coords produites par (x_idx,y_idx).
    SAFE: si une coord sort du plateau -> None (évite IndexError).
    """
    x_idx, y_idx = kern_idx
    x = np.asarray(x_idx, dtype=np.int64)
    y = np.asarray(y_idx, dtype=np.int64)

    H, W = board.shape
    if np.any(x < 0) or np.any(x >= W) or np.any(y < 0) or np.any(y >= H):
        return None
    return board[y, x]


def find_longest_row(board, last_move):
    longest = {1: [1], -1: [1]}
    H, W = board.shape
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player
    blocked = 0

    for dir in [1, -1]:
        for length in range(2, 6):
            values = kern_trad(board, get_kern_row_idx(last_move, direction=dir, length=length))
            if values is None:
                blocked += 1
                break

            number_player = np.count_nonzero(values == player)
            longest[dir].append(number_player)

            if number_player < length:
                # bord / adversaire bloque
                end_x = last_move[0] + (length - 1) * dir
                if values[-1] == opponent or not (0 <= end_x < W):
                    blocked += 1
                break

    return {"longest": max(longest[1]) + max(longest[-1]) - 1, "blocked": blocked}


def find_longest_col(board, last_move):
    longest = {1: [1], -1: [1]}
    H, W = board.shape
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player
    blocked = 0

    for dir in [1, -1]:
        for length in range(2, 6):
            values = kern_trad(board, get_kern_col_idx(last_move, direction=dir, length=length))
            if values is None:
                blocked += 1
                break

            number_player = np.count_nonzero(values == player)
            longest[dir].append(number_player)

            if number_player < length:
                end_y = last_move[1] + (length - 1) * dir
                if values[-1] == opponent or not (0 <= end_y < H):
                    blocked += 1
                break

    return {"longest": max(longest[1]) + max(longest[-1]) - 1, "blocked": blocked}


def find_longest_diag(board, last_move):
    """
    Version robuste sans np.fliplr : on teste 2 diagonales (\, /) via kernels + guards.
    """
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player
    H, W = board.shape

    def diag_axis(slope):
        # slope = (1,1) ou (1,-1)
        longest = {1: [1], -1: [1]}
        blocked = {1: 0, -1: 0}

        for dir in [1, -1]:
            for length in range(2, 6):
                dx = slope[0] * dir
                dy = slope[1] * dir
                values = kern_trad(board, get_kern_diag_idx(last_move, slope=(dx, dy), length=length))
                if values is None:
                    blocked[dir] = 1
                    break

                number_player = np.count_nonzero(values == player)
                longest[dir].append(number_player)

                if number_player < length:
                    end_x = last_move[0] + (length - 1) * dx
                    end_y = last_move[1] + (length - 1) * dy
                    if values[-1] == opponent or not (0 <= end_x < W) or not (0 <= end_y < H):
                        blocked[dir] = 1
                    break

        size = max(longest[1]) + max(longest[-1]) - 1
        blk = blocked[1] + blocked[-1]
        return {"longest": size, "blocked": blk}

    d1 = diag_axis((1, 1))
    d2 = diag_axis((1, -1))
    return max([d1, d2], key=lambda x: x["longest"])


def find_longest(board, last_move):
    longest = []
    longest.append(find_longest_row(board, last_move))
    longest.append(find_longest_col(board, last_move))
    longest.append(find_longest_diag(board, last_move))
    return max(longest, key=lambda x: x["longest"])


def find_longest_opponent_row(board, last_move: Tuple[int, int]):
    longest = {1: [0], -1: [0]}
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player

    for dir in [1, -1]:
        for length in range(1, 5):
            start = [last_move[0] + dir, last_move[1]]
            values = kern_trad(board, get_kern_row_idx(start, direction=dir, length=length))
            if values is None:
                break
            number_player = np.count_nonzero(values == opponent)
            longest[dir].append(number_player)
            if number_player < length:
                break

    return max(longest[1]) + max(longest[-1])


def find_longest_opponent_col(board, last_move: Tuple[int, int]):
    longest = {1: [0], -1: [0]}
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player

    for dir in [1, -1]:
        for length in range(1, 5):
            start = [last_move[0], last_move[1] + dir]
            values = kern_trad(board, get_kern_col_idx(start, direction=dir, length=length))
            if values is None:
                break
            number_player = np.count_nonzero(values == opponent)
            longest[dir].append(number_player)
            if number_player < length:
                break

    return max(longest[1]) + max(longest[-1])


def find_longest_opponent_diag(board, last_move: Tuple[int, int]):
    """
    Fix du crash: aucun accès hors-bord (kern_trad safe + break).
    On mesure la longueur de l'adversaire à partir d'une case adjacente en diagonale.
    """
    longest = {True: {1: [1], -1: [1]}, False: {1: [1], -1: [1]}}
    player = board[last_move[1], last_move[0]]
    opponent = 3 - player

    for slope in [(1, 1), (1, -1)]:
        for down in [1, -1]:
            s = (slope[0], slope[1] * down)
            for length in range(1, 5):
                start = [last_move[0] + s[0], last_move[1] + s[1]]
                values = kern_trad(board, get_kern_diag_idx(start, slope=s, length=length))
                if values is None:
                    break
                number_player = np.count_nonzero(values == opponent)
                bucket = True if slope == (1, 1) else False
                longest[bucket][down].append(number_player)
                if number_player < length:
                    break

    return (
        max(
            max(longest[True][1]) + max(longest[True][-1]),
            max(longest[False][1]) + max(longest[False][-1]),
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

    attack_pattern = np.array([player, opponent, opponent, player])
    defense_pattern_1 = np.array([opponent, player, player, player])
    defense_pattern_2 = np.array([player, player, player, opponent])

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
                    np.any(np.asarray(x_idx) < 0)
                    or np.any(np.asarray(x_idx) >= board_shape[1])
                    or np.any(np.asarray(y_idx) < 0)
                    or np.any(np.asarray(y_idx) >= board_shape[0])
                ):
                    continue

                window = kern_trad(board, (x_idx, y_idx))
                if window is None:
                    continue

                if np.array_equal(window, attack_pattern):
                    for pos in [0, 3]:
                        if x_idx[pos] == last_move[0] and y_idx[pos] == last_move[1]:
                            attack_detected = True

                if np.array_equal(window, defense_pattern_1) or np.array_equal(window, defense_pattern_2):
                    if last_move[0] in x_idx and last_move[1] in y_idx:
                        defense_detected = True

    return {"attack": attack_detected, "defense": defense_detected}


def check_neighbor(board, last_move):
    # safe near borders
    mid_col = kern_trad(board, get_kern_col_idx(tuple(np.add(last_move, (0, -1))), length=3))
    mid_row = kern_trad(board, get_kern_row_idx(tuple(np.add(last_move, (-1, 0))), length=3))
    if mid_col is None or mid_row is None:
        return 0

    player = mid_col[1]
    values = [mid_col[0], mid_col[2], mid_row[0], mid_row[2]]
    return values.count(player)


def _apply_board_update_in_place(game, new_board: np.ndarray) -> None:
    if hasattr(game.board, "update_board"):
        game.board.update_board(new_board)
    else:
        game.board.board[:, :] = new_board


def make_move(game, player, x: int, y: int) -> Dict[str, Any]:
    board = game.board.board
    opponent = game.get_opponent(player.value)

    prev: Dict[str, Any] = {
        "player_turn": game.player_turn,
        "winner": getattr(game, "winner", None),
        "game_state": getattr(game, "game_state", None),
        "capture_score_p": player.capture_score,
        "capture_score_o": opponent.capture_score,
        "last_moves_p": list(getattr(player, "last_moves", [])),
        "last_moves_o": list(getattr(opponent, "last_moves", [])),
        "placed": (int(x), int(y)),
        "captured": [],
    }

    is_cap = False
    new_board = None
    score = 0

    try:
        is_cap, new_board, score = game.board.check_is_capture_moove(game, player, opponent.value, x, y)
    except TypeError:
        is_cap, new_board, score = game.board.check_is_capture_moove(game, player, opponent, x, y)

    if is_cap:
        captured_mask = (board == opponent.value) & (new_board == 0)
        cy, cx = np.where(captured_mask)
        prev["captured"] = list(zip(cx.tolist(), cy.tolist()))
        _apply_board_update_in_place(game, new_board)
        player.capture_score += score

    board[int(y), int(x)] = player.value

    if hasattr(player, "last_moves"):
        player.last_moves.insert(0, (int(x), int(y)))

    game.player_turn = opponent.value
    return prev


def unmake_move(game, player, prev: Dict[str, Any]) -> None:
    board = game.board.board
    opponent = game.get_opponent(player.value)

    x, y = prev["placed"]
    board[int(y), int(x)] = 0

    for cx, cy in prev.get("captured", []):
        board[int(cy), int(cx)] = opponent.value

    player.capture_score = prev["capture_score_p"]
    opponent.capture_score = prev["capture_score_o"]

    if hasattr(player, "last_moves"):
        player.last_moves = prev["last_moves_p"]
    if hasattr(opponent, "last_moves"):
        opponent.last_moves = prev["last_moves_o"]

    game.player_turn = prev["player_turn"]
    if "winner" in prev:
        game.winner = prev["winner"]
    if "game_state" in prev:
        game.game_state = prev["game_state"]


def evaluate(game: Game, last_move: Tuple[int, int], player: Player):
    val = 0
    board = game.board.board

    longest_info = find_longest(board, last_move)
    longest = longest_info["longest"]
    blocked = longest_info["blocked"]

    longest_opponent = find_longest_opponent(board, last_move)
    cap = detect_captures(board, last_move)
    attacking, defending = cap["attack"], cap["defense"]

    opponent = game.get_opponent(player.value)

    if blocked != 2:
        if longest == 2:
            val += SMALL_GAIN
        elif longest == 3:
            val += 3 * NORMAL_GAIN
        elif longest == 4:
            val += 6 * NORMAL_GAIN

    if longest >= 5:
        val += BIG_GAIN

    if longest_opponent == 2:
        val += SMALL_GAIN
    elif longest_opponent == 3:
        val += 4 * NORMAL_GAIN
    elif longest_opponent >= 4:
        val += BIG_GAIN * 1000

    if attacking:
        val += 4 * SMALL_GAIN + NORMAL_GAIN * player.capture_score
    if defending:
        val += 4 * SMALL_GAIN + NORMAL_GAIN * opponent.capture_score

    val += check_neighbor(board, last_move)

    return val


def minmax(game: Game, depth, alpha, beta, maximizingPlayer, player: Player, last_move, maximizer_value: int):
    """
    player = joueur qui DOIT jouer à ce nœud
    last_move = coup joué au parent (donc déjà posé sur le board)
    score renvoyé = toujours du point de vue du maximizer_value
    """
    global NODES, T0
    if T0 == 0.0:
        T0 = time.time()
    NODES += 1
    if NODES % 5000 == 0:
        print(f"[minmax] nodes={NODES} elapsed={time.time()-T0:.2f}s depth={depth}")

    lx, ly = int(last_move[0]), int(last_move[1])
    last_value = int(game.board.board[ly, lx])
    last_player = game.get_player(last_value)

    # Terminal: win sur last_move
    if game.board.is_winner_moove(last_player, lx, ly, game):
        return BIG_GAIN if last_value == maximizer_value else BIG_LOSS

    if depth == 0:
        raw = evaluate(game, (lx, ly), last_player)
        return raw if last_value == maximizer_value else -raw

    moves = list(potential_moves(game, player))
    opponent = game.get_opponent(player.value)

    if not moves:
        # Aucun coup: neutre
        return 0

    if maximizingPlayer:
        maxEval = float("-inf")
        for mx, my in moves:
            prev = make_move(game, player, int(mx), int(my))
            eval_value = minmax(game, depth - 1, alpha, beta, False, opponent, (int(mx), int(my)), maximizer_value)
            unmake_move(game, player, prev)

            if eval_value > maxEval:
                maxEval = eval_value
            if eval_value > alpha:
                alpha = eval_value
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = float("inf")
        for mx, my in moves:
            prev = make_move(game, player, int(mx), int(my))
            eval_value = minmax(game, depth - 1, alpha, beta, True, opponent, (int(mx), int(my)), maximizer_value)
            unmake_move(game, player, prev)

            if eval_value < minEval:
                minEval = eval_value
            if eval_value < beta:
                beta = eval_value
            if beta <= alpha:
                break
        return minEval


def move_maker_thread(game: Game):
    while game.program_run and game.game_state != GameState.Finish:
        if game.type != GameType.FUTURE:
            if game.player_turn == game.P1.value:
                time.sleep(0.1)
                continue

        # >>> Mesure "calcul + attente" (temps total côté IA jusqu'au play_moove)
        start_ai = time.time()

        player_value = game.get_player_value()
        player = game.get_player(player_value)
        opponent = game.get_opponent(player_value)

        last_move = opponent.last_moves[0] if len(opponent.last_moves) > 0 else None
        rows, cols = game.board.board.shape

        print("Human had moved")

        if not np.any(game.board.board == player_value):
            direction = random.choice(POTENTIAL_MOVES_DIRECTIONS)

            if last_move is None:
                game.board.play_moove(game, random.randint(0, 18), random.randint(0, 18))
            else:
                while not game.board.is_on_board(last_move[1] + direction[1], last_move[0] + direction[0]):
                    direction = random.choice(POTENTIAL_MOVES_DIRECTIONS)

                game.board.play_moove(
                    game,
                    int(last_move[0] + direction[0]),
                    int(last_move[1] + direction[1]),
                )

            print("AI Played randomly")

        elif move_calculated := next(
            (move for move in game.board.human_best_moves if move.move == last_move),
            None,
        ):
            while move_calculated.running:
                time.sleep(0.01)

            x, y = move_calculated.move_to_do
            game.board.play_moove(game, int(x), int(y))
            print("AI Played move already calculated")
        else:
            print("Start calculated next move.")
            move_manager = HumanMoveManager(last_move)

            executor.submit(thread_AI, game, move_manager, player, opponent)

            while move_manager.running:
                time.sleep(0.01)

            x, y = move_manager.move_to_do
            game.board.play_moove(game, int(x), int(y))
            print("AI Played move calculated on the fly")

        # >>> Stockage du temps total IA (calcul + attente)
        game.ai_last_response_time = time.time() - start_ai

        time.sleep(0.5)


def thread_AI(game: Game, move_manager: HumanMoveManager, player: Player, opponent: Player):
    """
    Calcule la réponse IA au coup humain move_manager.move.
    Robuste:
    - ne bloque jamais (finally: running=False)
    - affiche traceback en cas d'exception
    - fallback si aucun move
    """
    import traceback

    global NODES, T0
    NODES = 0
    T0 = 0.0

    start_time = time.time()
    try:
        state = game.copy()

        # IMPORTANT: utiliser les objets Player de l'état copié
        ai = state.get_player(player.value)
        human = state.get_player(opponent.value)

        # Appliquer le coup humain proprement (captures, scores, last_moves)
        hx, hy = move_manager.move
        prev_h = make_move(state, human, int(hx), int(hy))

        moves = list(potential_moves(state, ai))
        if not moves:
            # fallback: voisinage immédiat
            for dx, dy in POTENTIAL_MOVES_DIRECTIONS:
                nx, ny = int(hx + dx), int(hy + dy)
                if 0 <= nx < 19 and 0 <= ny < 19 and state.board.board[ny, nx] == 0:
                    move_manager.move_to_do = (nx, ny)
                    return
            empties = np.argwhere(state.board.board == 0)
            ey, ex = empties[random.randrange(len(empties))]
            move_manager.move_to_do = (int(ex), int(ey))
            return

        max_score = float("-inf")
        best_moves = []

        for mx, my in moves:
            prev_ai = make_move(state, ai, int(mx), int(my))

            # après le coup IA, c'est au joueur humain de jouer -> maximizingPlayer=False
            score = minmax(
                state,
                DEPTH_MAX - 1,
                -10**18,
                10**18,
                False,
                human,
                (int(mx), int(my)),
                maximizer_value=ai.value,
            )

            unmake_move(state, ai, prev_ai)

            if score > max_score:
                max_score = score
                best_moves = [(int(mx), int(my))]
            elif score == max_score:
                best_moves.append((int(mx), int(my)))

        # Annuler le coup humain
        unmake_move(state, human, prev_h)

        if not best_moves:
            empties = np.argwhere(state.board.board == 0)
            ey, ex = empties[random.randrange(len(empties))]
            move_manager.move_to_do = (int(ex), int(ey))
        else:
            move_manager.move_to_do = random.choice(best_moves)

        elapsed = time.time() - start_time
        print(
            f"[{elapsed:.3f}s] AI chose {move_manager.move_to_do} score={max_score} vs human {move_manager.move}"
        )

    except Exception:
        print("thread_AI crashed:\n", traceback.format_exc())
        # fallback safe
        empties = np.argwhere(game.board.board == 0)
        ey, ex = empties[random.randrange(len(empties))]
        move_manager.move_to_do = (int(ex), int(ey))

    finally:
        move_manager.running = False

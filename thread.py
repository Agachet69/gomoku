import sys
from typing import Literal
from Board import Board
from game import Game
from game_state_enum import GameState
import threading
import time
import numpy as np

from player import Player


POTENTIAL_MOVES_DIRECTIONS = [
    (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
    (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
    ( 0, -2), ( 0, -1),          ( 0, 1), ( 0, 2),
    ( 1, -2), ( 1, -1), ( 1, 0), ( 1, 1), ( 1, 2),
    ( 2, -2), ( 2, -1), ( 2, 0), ( 2, 1), ( 2, 2),
]


def init_threads(game):
    thread1  = threading.Thread(target=thread_opponent, args=(game,))
    thread1.start()
    # thread2  = threading.Thread(target=thread_AI, args=(game,))
    # thread2.start()
    # return thread



def potential_moves(state: Board, player: Player):

    moves = set()
    rows, cols = state.board.shape

    for i in range(rows):
        for j in range(cols):
            if state.board[i, j] == player.value:
                for dx, dy in POTENTIAL_MOVES_DIRECTIONS:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < rows and 0 <= nj < cols and state.board[ni, nj] == 0:
                        moves.add((ni, nj))
    
    return moves



def evaluate(game: Game, last_move, player):
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1),
    ]

    val = 0
    rows, cols = game.board.board.shape
    for dx, dy in directions:
        ni, nj = last_move[1] + dx, last_move[0] + dy
        if 0 <= ni < rows and 0 <= nj < cols:
            if game.board.board[ni][nj] == player.value:
                val += 10


    return val

    





def minmax(game: Game, depth, alpha, beta, maximizingPlayer, player: Player, last_move):

    if not depth or game.board.is_winner_moove(player, last_move[1], last_move[0]):
        return evaluate(game, last_move, game.P1 if game.P1.name != player.name else game.P2)
    
    moves = potential_moves(game.board, player)

    if maximizingPlayer:
        maxEval = -10000000000

        for move in moves:
            new_state = game.copy()
            new_state.board.board[move[1]][move[0]] = player.value
            eval_value = minmax(new_state, depth-1, alpha, beta, not maximizingPlayer, game.P1 if game.P1.name != player.name else game.P2, last_move=move)

            maxEval = max(maxEval, eval_value)
            alpha = max(alpha, eval_value)

            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = 10000000000

        for move in moves:
            new_state = game.copy()
            new_state.board.board[move[1]][move[0]] = player.value
            eval_value = minmax(new_state, depth-1, alpha, beta, not maximizingPlayer, game.P1 if game.P1.name != player.name else game.P2, last_move=move)

            minEval = min(minEval, eval_value)
            alpha = min(beta, eval_value)

            if beta <= alpha:
                break
        return minEval



DEPTH_MAX = 1
NUMBER_BEST_MOVES = 10



def thread_opponent(game: Game):
    while game.program_run and game.game_state != GameState.Finish:
        start_time = time.time()
        move_score = []

        if not np.any(game.board.board == 1) or game.player_turn == 2 or len(game.board.human_best_moves) == NUMBER_BEST_MOVES:
            continue


        moves = potential_moves(game.board, game.P1)
        best_score = 0

        for move in moves:
            new_state = game.copy()
            new_state.board.board[move[1]][move[0]] = game.P1.value
            # print(game.P1.name)
            score = minmax(new_state, DEPTH_MAX-1, -10000000000, 10000000000, False, game.P2, move)
            # game.board.play_moove(game, move[0], move[1])


            move_score.append(score)
            # if best_score < score:
            #     best_score = score
            #     best_move = move

            
        game.board.human_best_moves = [move for move, _ in sorted(list(zip(moves, move_score)), key=lambda x: x[1], reverse=True)[:NUMBER_BEST_MOVES]]
        print(game.board.human_best_moves)
        # print(f"Coups possibles : {coups}")
        # if best_move:
        #     print(best_move)
            # game.board.play_moove(game, best_move[0], best_move[1])

        # if best_move:

        # minmax(game.board.board)

        elapsed = time.time() - start_time  # Fin du chrono
        print(f"Temps total de l'itération : {elapsed:.3f} secondes")


def thread_AI(game: Game):
    while game.program_run and game.game_state != GameState.Finish:
        start_time = time.time()
        move_score = []

        if not np.any(game.board.board == 2) or game.player_turn == 1 or len(game.board.human_best_moves) == NUMBER_BEST_MOVES:
            time.sleep(0.1)
            continue


        moves = potential_moves(game.board, game.P1)
        best_score = 0

        for move in moves:
            new_state = game.copy()
            new_state.board.board[move[1]][move[0]] = game.P1.value
            # print(game.P1.name)
            score = minmax(new_state, DEPTH_MAX-1, -10000000000, 10000000000, False, game.P2, move)
            # game.board.play_moove(game, move[0], move[1])


            move_score.append(score)
            # if best_score < score:
            #     best_score = score
            #     best_move = move

            
        game.board.human_best_moves = [move for move, _ in sorted(list(zip(moves, move_score)), key=lambda x: x[1], reverse=True)[:NUMBER_BEST_MOVES]]
        print(game.board.human_best_moves)
        # print(f"Coups possibles : {coups}")
        # if best_move:
        #     print(best_move)
        game.board.play_moove(game, game.board.human_best_moves[0][1], game.board.human_best_moves[0][0])

        # if best_move:

        # minmax(game.board.board)

        elapsed = time.time() - start_time  # Fin du chrono
        print(f"Temps total de l'itération : {elapsed:.3f} secondes")

# def thread_opponent(game):
#     while True:
#         print('hello')


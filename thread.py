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

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)  # ajuste ce nombre selon ta machine



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
    move_maker_thr  = threading.Thread(target=move_maker_thread, args=(game,))
    move_maker_thr.start()

    
    # thread2  = threading.Thread(target=thread_AI, args=(game,))
    # thread2.start()
    # return thread



def potential_moves(game: Game, player: Player):

    moves = set()
    rows, cols = game.board.board.shape

    for i in range(rows):
        for j in range(cols):
            if game.board.board[i, j] == player.value:
                for dx, dy in POTENTIAL_MOVES_DIRECTIONS:
                    ni, nj = i + dy, j + dx
                    if 0 <= ni < rows and 0 <= nj < cols and game.board.board[ni, nj] == 0:
                        if game.board.is_legal_moove(nj, ni):
                            if not (game.board.is_double_three(nj, ni, game) and not game.board.is_capture_moove(game, player, game.get_opponent(player.value), nj, ni)):
                                moves.add((nj, ni))
    
    return moves



BIG_LOSS = -1000000
BIG_GAIN = 1000000
NORMAL_GAIN = 100
SMALL_GAIN = 1



def evaluate(game: Game, last_move, player):
    val = 0
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1),
    ]

   

    

    rows, cols = game.board.board.shape
    for dx, dy in directions:
        ni, nj = last_move[0] + dx, last_move[1] + dy
        if 0 <= ni < rows and 0 <= nj < cols:
            if game.board.board[nj][ni] == player.value:
                val += SMALL_GAIN


    return val

    





def minmax(game: Game, depth, alpha, beta, maximizingPlayer, player: Player, last_move):
    opponent = game.get_opponent(player.value)
    if not depth or game.board.is_winner_moove(
        opponent, last_move[0], last_move[1], game
    ):
        return evaluate(game, last_move, opponent)
    
    moves = potential_moves(game, player)

    if maximizingPlayer:
        maxEval = -10000000000

        for move in moves:
            new_state = game.copy()
            new_state.board.board[move[1]][move[0]] = player.value
            eval_value = minmax(new_state, depth-1, alpha, beta, not maximizingPlayer, opponent, last_move=move)

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
            eval_value = minmax(new_state, depth-1, alpha, beta, not maximizingPlayer, opponent, last_move=move)

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

                while not (0 <= last_move[1] + direction[1] < rows and 0 <= last_move[0] + direction[0] < cols):
                    direction = random.choice(POTENTIAL_MOVES_DIRECTIONS)

                game.board.play_moove(game, last_move[0] + direction[0], last_move[1] + direction[1])

                print("AI Played randomly")
            

            elif move_calculated := next((move for move in game.board.human_best_moves if move.move == last_move), None):
                while move_calculated.running:
                    pass

                game.board.play_moove(game, move_calculated.move_to_do[0], move_calculated.move_to_do[1])
                print("AI Played move already calculated")
            else:
                move_manager = HumanMoveManager(last_move)

                executor.submit(thread_AI, game, move_manager)

                while move_manager.running:
                    pass

                game.board.play_moove(game, move_manager.move_to_do[0], move_manager.move_to_do[1])

                print("AI Played move calculated on the fly")













DEPTH_MAX = 1
NUMBER_BEST_MOVES = 8



def thread_opponent(game: Game):
    while game.program_run and game.game_state != GameState.Finish:
        start_time = time.time()
        move_score = []


        if not np.any(game.board.board == 1) or game.player_turn == 2 or len(game.board.human_best_moves) == NUMBER_BEST_MOVES:
            time.sleep(0.1)
            continue


        moves = potential_moves(game, game.P1)
        best_score = 0

        for move in moves:
            new_state = game.copy()
            new_state.board.board[move[1]][move[0]] = game.P1.value
            # print(game.P1.name)
            score = minmax(new_state, DEPTH_MAX-1, -10000000000, 10000000000, True, game.P2, move)
            # game.board.play_moove(game, move[0], move[1])


            move_score.append(score)
            # if best_score < score:
            #     best_score = score
            #     best_move = move
        # print(move_score)
            
        game.board.human_best_moves = [HumanMoveManager(move) for move, _ in sorted(list(zip(moves, move_score)), key=lambda x: x[1], reverse=True)[:NUMBER_BEST_MOVES]]


        for move in game.board.human_best_moves:
            # game.board.board[move.move[0]][move.move[1]] = 1
            # time.sleep(.1)


            executor.submit(thread_AI, game, move)



        elapsed = time.time() - start_time  # Fin du chrono
        # print(f"Temps total de l'itération : {elapsed:.3f} secondes")


def thread_AI(game: Game, move_manager: HumanMoveManager):

    start_time = time.time()
    state = game.copy()
    state.board.board[move_manager.move[1]][move_manager.move[0]] = game.P2.value


    best_score = float('-inf')
    best_move = None
    moves = potential_moves(game, game.P2)



    for move in moves:
        
        # if game.player_turn == 2:
        #     return
        new_state = state.copy()
        new_state.board.board[move[1]][move[0]] = game.P2.value
        # print(game.P1.name)
        score = minmax(new_state, DEPTH_MAX-1, -10000000000, 10000000000, True, game.P1, move)
        # game.board.play_moove(game, move[0], move[1])

        if best_score < score:
            best_score = score
            best_move = move

    
    move_manager.running = False
    move_manager.move_to_do = best_move

    elapsed = time.time() - start_time  # Fin du chrono
    print(f"[{elapsed:.3f}s] Thread AI chose move {best_move} (score: {best_score:03}) in response to human move {move_manager.move}")

# def thread_opponent(game):
#     while True:
#         print('hello')


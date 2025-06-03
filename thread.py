from multiprocessing.managers import BaseManager
from game_state_enum import GameState
import multiprocessing
import time


def init_threads(game):
    p = multiprocessing.Process(target=thread_opponent, args=(game,))
    p.start()
    return p    

def thread_opponent(game):
    while game.get_game_state() != GameState.Finish:
        print('actual_board :', game.board.board)
        time.sleep(1)


# def thread_opponent(game):
#     while True:
#         print('hello')
import pygame
from Board import Board, BOARD_SIZE
from game import Game
from player import Player
from game_state_enum import GameState
import sys
import time

from config import WINDOW_SIZE, BLACK, GAME_SIZE, CELL_SIZE, GOBAN, WHITE, GRAY, RED
from draw import draw_game, draw_finish_modal, draw_menu_screen, draw_temporary_stone


def get_fonts():
    fonts = {}
    fonts["tinny"] = pygame.font.SysFont(None, 12)
    fonts["little_tinny"] = pygame.font.SysFont(None, 18)
    fonts["little"] = pygame.font.SysFont(None, 24)
    fonts["font"] = pygame.font.SysFont(None, 36)
    fonts["font_big"] = pygame.font.SysFont(None, 56)

    return fonts


def get_grid_position(mouse_pos):
    mx, my = mouse_pos
    mx -= (WINDOW_SIZE - GAME_SIZE) / 2
    my -= (WINDOW_SIZE - GAME_SIZE) / 2

    x = int(mx // CELL_SIZE)
    y = int(my // CELL_SIZE)
    if x > 18 or y > 18:
        return -1, -1
    return x, y


def init_game():
    pygame.init()

    game = Game(1)
    fonts = get_fonts()

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Gomoku AI")

    while game.get_program_run() is True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.exit()
                break

            elif game.game_state == GameState.Creating:
                draw_menu_screen(screen, fonts, game, event)
            elif (
                game.game_state == GameState.Playing
                or game.game_state == GameState.LastChance
            ):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = get_grid_position(pygame.mouse.get_pos())
                    game.board.play_moove(game, x, y)
                draw_game(screen, fonts, game, event)
                if event.type == pygame.MOUSEMOTION:
                    if hasattr(event, "pos"):
                        x, y = get_grid_position(event.pos)
                        if x != game.board.temp_stonex or y != game.board.temp_stoney:
                            if not game.board.is_legal_moove(
                                x, y
                            ) or game.board.detect_double_three_anywhere(
                                game.get_player_value(), x, y
                            ):
                                continue
                            my_player = game.get_player(game.get_me_value())
                        draw_temporary_stone(x, y, screen, my_player)
                        game.board.set_temp_stone(x, y)

                pygame.display.flip()
            elif (
                game.game_state == GameState.Finish or game.game_state == GameState.Draw
            ):
                if hasattr(event, "pos"):
                    draw_game(screen, fonts, game, event)
                    draw_finish_modal(screen, game, fonts, event)
        # if (
        #     game.game_state == GameState.Playing
        #     or game.game_state == GameState.LastChance
        # ):
        #     draw_game(screen, fonts, game, event)
        # elif game.game_state == GameState.Finish or game.game_state == GameState.Draw:
        #     draw_finish_modal(screen, game, fonts, event)
        pygame.display.flip()

    pygame.quit()

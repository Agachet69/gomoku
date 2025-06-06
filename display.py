import pygame
from Board import Board, BOARD_SIZE
from game import Game
from player import Player
from game_state_enum import GameState
import sys
import time

from thread import init_threads
from config import WINDOW_SIZE, BLACK, GAME_SIZE, CELL_SIZE, GOBAN, WHITE, GRAY, RED
from draw import draw_game

def get_fonts():
    fonts = {}
    fonts["font"] = pygame.font.SysFont(None, 36)
    fonts["little"] = pygame.font.SysFont(None, 24)
    fonts["font_big"] = pygame.font.SysFont(None, 56)

    return fonts


def draw_text(screen, text, font, x, y):
    label = font.render(text, True, BLACK)
    rect = label.get_rect(center=(x, y))
    screen.blit(label, rect)
    return rect


def get_grid_position(mouse_pos):
    mx, my = mouse_pos
    mx -= (WINDOW_SIZE - GAME_SIZE) / 2
    my -= (WINDOW_SIZE - GAME_SIZE) / 2

    x = int(mx // CELL_SIZE)
    y = int(my // CELL_SIZE)
    if x > 18 or y > 18:
        return -1, -1
    return x, y


def menu_screen(screen, font, game: Game, event):
    screen.fill(GOBAN)
    draw_text(screen, "Bienvenue sur Gomoku", font, WINDOW_SIZE // 2, WINDOW_SIZE // 4)
    rect1 = draw_text(
        screen, "1. Jouer contre une IA", font, WINDOW_SIZE // 2, WINDOW_SIZE // 2
    )
    rect2 = draw_text(
        screen,
        "2. Prevoir l'avenir",
        font,
        WINDOW_SIZE // 2,
        WINDOW_SIZE // 2 + 50,
    )
    pygame.display.flip()

    if event.type == pygame.MOUSEBUTTONDOWN:
        if rect1.collidepoint(event.pos):
            img_black = pygame.image.load("./assets/black.png").convert_alpha()
            img_white = pygame.image.load("./assets/white.png").convert_alpha()
            black = pygame.transform.smoothscale(img_black, (CELL_SIZE, CELL_SIZE))
            white = pygame.transform.smoothscale(img_white, (CELL_SIZE, CELL_SIZE))
            P1 = Player(black, "Black", 1)
            P2 = Player(white, "White", 2)
            game.set_players(P1, P2)
            game.game_state = GameState.Playing
            print("→ Lancement du jeu")
            init_threads(game)

        elif rect2.collidepoint(event.pos):
            img_marseille = pygame.image.load("./assets/marseille.png").convert_alpha()
            img_psg = pygame.image.load("./assets/psg.png").convert_alpha()
            marseille = pygame.transform.smoothscale(
                img_marseille, (CELL_SIZE, CELL_SIZE)
            )
            psg = pygame.transform.smoothscale(img_psg, (CELL_SIZE, CELL_SIZE))
            P1 = Player(marseille, "Marseille", 1)
            P2 = Player(psg, "PSG", 2)
            game.set_players(P1, P2)
            game.game_state = GameState.Playing
            print("→ Avenir en lecture..")

    # return img1, img2
    #         return
    # waiting = False
    # init_game()

    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         pygame.quit()
    #         sys.exit()
    #     elif event.type == pygame.KEYDOWN:
    #         if event.key == pygame.K_1:
    #             return "ai"
    #         elif event.key == pygame.K_2:
    #             return "friend"


def draw_finish_modal(screen, game: Game, fonts, event):
    screen_rect = screen.get_rect()
    box_width, box_height = 500, 300
    box_rect = pygame.Rect(0, 0, box_width, box_height)
    box_rect.center = screen_rect.center

    if game.game_state == GameState.Finish:
        text = f"{game.winner.name} WIN"
        text_surface = fonts["font_big"].render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(box_rect.centerx, box_rect.top + 60))
    else:
        text = "IT'S A DRAW"
        text_surface = fonts["font_big"].render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(box_rect.centerx, box_rect.top + 60))

    replay_surface = fonts["font"].render("Rejouer", True, BLACK)
    menu_surface = fonts["font"].render("Menu principal", True, BLACK)

    max_text_width = max(replay_surface.get_width(), menu_surface.get_width())
    button_width = max_text_width + 40
    button_height = replay_surface.get_height() + 20

    replay_rect = pygame.Rect(0, 0, button_width, button_height)
    replay_rect.center = (box_rect.centerx, box_rect.top + 160)

    menu_rect = pygame.Rect(0, 0, button_width, button_height)
    menu_rect.center = (box_rect.centerx, box_rect.top + 230)

    pygame.draw.rect(screen, WHITE, box_rect, border_radius=15)
    pygame.draw.rect(screen, GRAY, replay_rect, border_radius=14)
    pygame.draw.rect(screen, GRAY, menu_rect, border_radius=14)
    screen.blit(text_surface, text_rect)
    screen.blit(replay_surface, replay_surface.get_rect(center=replay_rect.center))
    screen.blit(menu_surface, menu_surface.get_rect(center=menu_rect.center))
    pygame.display.flip()

    if event.type == pygame.MOUSEBUTTONDOWN:
        if replay_rect.collidepoint(event.pos):
            game.replay()
        elif menu_rect.collidepoint(event.pos):
            game.menu()


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
                menu_screen(screen, fonts["font"], game, event)
            elif game.game_state == GameState.Playing:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = get_grid_position(pygame.mouse.get_pos())
                    game.board.play_moove(game, x, y)
                draw_game(screen, fonts, game)
                pygame.display.flip()
            elif (
                game.game_state == GameState.Finish or game.game_state == GameState.Draw
            ):
                draw_finish_modal(screen, game, fonts, event)

        pygame.display.flip()

    pygame.quit()

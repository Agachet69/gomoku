import pygame
from Board import Board, BOARD_SIZE
from game import Game
from player import Player
from game_state_enum import GameState
import sys
import time

WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
GRAY_RECT = (218, 218, 218)
BLUE = (66, 135, 245)
RED = (176, 23, 23)
GOBAN = (221, 180, 92)

CELL_SIZE = 50
GAME_SIZE = CELL_SIZE * BOARD_SIZE
WINDOW_SIZE = GAME_SIZE * 1.3
STONE_RADIUS = CELL_SIZE // 2 - 5
PADDING = (WINDOW_SIZE - GAME_SIZE) / 2


def get_fonts():
    fonts = {}
    fonts["font"] = pygame.font.SysFont(None, 36)
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


def draw_board(board: Board, screen, game: Game):
    screen.fill(GOBAN)

    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(
            screen,
            BLACK,
            (PADDING, PADDING + (CELL_SIZE * i)),
            (PADDING + CELL_SIZE * 19, PADDING + (CELL_SIZE * i)),
            1,
        )
        pygame.draw.line(
            screen,
            BLACK,
            (PADDING + (CELL_SIZE * i), PADDING),
            (PADDING + (CELL_SIZE * i), PADDING + (CELL_SIZE * 19)),
            1,
        )

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            val = board.board[y, x]
            img = None
            if val == 1:
                img = game.P1.img_path
            elif val == 2:
                img = game.P2.img_path

            if img:
                px = (WINDOW_SIZE - GAME_SIZE) / 2 + x * CELL_SIZE
                py = (WINDOW_SIZE - GAME_SIZE) / 2 + y * CELL_SIZE
                screen.blit(img, (px, py))


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
    # image = pygame.image.load("./assets/black.png").convert_alpha()
    # image2 = pygame.image.load("./assets/white.png").convert_alpha()
    # img1 = pygame.transform.smoothscale(image, (CELL_SIZE, CELL_SIZE))
    # img2 = pygame.transform.smoothscale(image2, (CELL_SIZE, CELL_SIZE))

    while game.program_run is True:
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

                draw_board(game.board, screen, game)
                message_couleur = "White" if game.player_turn == 2 else "Black"
                color = RED if message_couleur == "Red" else BLACK

                msg_capture = f"{game.P1.name} Capture score"
                msg_capture2 = f"{game.P2.name} Capture score"
                text_captures = fonts["font"].render(msg_capture, True, BLACK)
                text_captures2 = fonts["font"].render(msg_capture2, True, BLACK)

                captures_number_P1 = f"{game.P1.capture_score}"
                captures_number_P2 = f"{game.P2.capture_score}"

                number_captures_P1 = fonts["font"].render(
                    captures_number_P1, True, BLACK
                )
                number_captures_P2 = fonts["font"].render(
                    captures_number_P2, True, BLACK
                )

                texte_partie1 = fonts["font_big"].render(message_couleur, True, color)
                texte_partie2 = fonts["font_big"].render(" turn.", True, BLACK)
                width_text = texte_partie2.get_width()

                screen.blit(
                    texte_partie1, (WINDOW_SIZE / 2 - width_text, WINDOW_SIZE - 100)
                )
                screen.blit(
                    texte_partie2,
                    (
                        WINDOW_SIZE / 2 - width_text + texte_partie1.get_width(),
                        WINDOW_SIZE - 100,
                    ),
                )
                screen.blit(
                    text_captures,
                    (
                        WINDOW_SIZE / 8,
                        WINDOW_SIZE - 100,
                    ),
                )
                screen.blit(
                    number_captures_P1,
                    (
                        WINDOW_SIZE / 8,
                        WINDOW_SIZE - 70,
                    ),
                )

                screen.blit(
                    text_captures2,
                    (
                        WINDOW_SIZE * 0.8,
                        WINDOW_SIZE - 100,
                    ),
                )
                screen.blit(
                    number_captures_P2,
                    (
                        WINDOW_SIZE * 0.8,
                        WINDOW_SIZE - 70,
                    ),
                )
                pygame.display.flip()

            elif (
                game.game_state == GameState.Finish or game.game_state == GameState.Draw
            ):
                draw_finish_modal(screen, game, fonts, event)


        pygame.display.flip()
        # clock.tick(60)
        # pygame.display.flip()

    pygame.quit()

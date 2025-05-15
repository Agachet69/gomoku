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

CELL_SIZE = 50
GAME_SIZE = CELL_SIZE * BOARD_SIZE
WINDOW_SIZE = GAME_SIZE * 1.3
STONE_RADIUS = CELL_SIZE // 2 - 5
PADDING = (WINDOW_SIZE - GAME_SIZE) / 2


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
    screen.fill(WHITE)
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
            marseille = pygame.transform.smoothscale(img_marseille, (CELL_SIZE, CELL_SIZE))
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


def draw_board(board: Board, screen, game : Game):
    screen.fill(WHITE)

    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(
            screen,
            GRAY,
            (PADDING, PADDING + (CELL_SIZE * i)),
            (PADDING + CELL_SIZE * 19, PADDING + (CELL_SIZE * i)),
            1,
        )
        pygame.draw.line(
            screen,
            GRAY,
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


def init_game():
    game = Game(1)
    board = Board()
    game.set_board(board)
    print(WINDOW_SIZE)
    pygame.init()

    font = pygame.font.SysFont(None, 36)
    font_big = pygame.font.SysFont(None, 56)

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    # image = pygame.image.load("./assets/black.png").convert_alpha()
    # image2 = pygame.image.load("./assets/white.png").convert_alpha()
    # img1 = pygame.transform.smoothscale(image, (CELL_SIZE, CELL_SIZE))
    # img2 = pygame.transform.smoothscale(image2, (CELL_SIZE, CELL_SIZE))

    pygame.display.set_caption("Gomoku AI")
    run = True

    while run is True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif game.game_state == GameState.Creating:
                menu_screen(screen, font, game, event)
            elif game.game_state == GameState.Playing:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = get_grid_position(pygame.mouse.get_pos())
                    board.play_moove(game, x, y)

                message_couleur = "White" if game.player_turn == 2 else "Black"
                color = RED if message_couleur == "Red" else BLACK

                texte_partie1 = font_big.render(message_couleur, True, color)
                texte_partie2 = font_big.render(" turn.", True, BLACK)
                width_text = texte_partie2.get_width()
                draw_board(board, screen, game)
                screen.blit(texte_partie1, (WINDOW_SIZE / 2 - width_text, WINDOW_SIZE - 100))
                screen.blit(
                    texte_partie2,
                    (
                        WINDOW_SIZE / 2 - width_text + texte_partie1.get_width(),
                        WINDOW_SIZE - 100,
                    ),
                )
                pygame.display.flip()

            elif game.game_state == GameState.Finish:
                # message_couleur = "White" if game.player_turn == 2 else "Black"
                # color = RED if message_couleur == "Red" else BLACK

                texte_partie1 = font_big.render(game.winner.name, True, color)
                texte_partie2 = font_big.render(" Victoire.", True, BLACK)
                width_text = texte_partie2.get_width()
                # draw_board(board, screen, img1, img2)
                screen.blit(
                    texte_partie1, (WINDOW_SIZE / 2 - width_text, WINDOW_SIZE - 100)
                )
                screen.blit(
                    texte_partie2,
                    (
                        WINDOW_SIZE / 2 - width_text + texte_partie1.get_width(),
                        WINDOW_SIZE / 2,
                    ),
                )



            # if board.is_winning_move(x, y, player):
                # print(f"Player {player} wins!")
                # running = False
                # if mode == "friend":
                # player = P2 if player == P1 else P1
        # screen.fill(WHITE)
        # message = "Red turn." if game.player_turn == 2 else "Black turn."

        # texte_surface = font.render(message, True, BLACK)

        # padding_x = 10
        # padding_y = 5

        # total_width = texte_partie1.get_width() + texte_partie2.get_width()
        # total_height = texte_partie1.get_height()

        # Rectangle de fond plus large que le texte
        # bg_rect = pygame.Rect(
        #     PADDING - padding_x,
        #     20 - padding_y,
        #     total_width + 2 * padding_x,
        #     total_height + 2 * padding_y,
        # )
        # pygame.draw.rect(
        #     screen,
        #     GRAY_RECT,
        #     bg_rect,
        #     # texte_surface.get_rect(topleft=(PADDING, 20)),
        #     border_radius=10,
        #     # width=50
        # )
        # screen.blit(texte_surface, (PADDING, 20))
        # x, y = 50, 50
        # screen.blit(texte_surface, (50, 50))
        pygame.display.flip()
        # clock.tick(60)
        # pygame.display.flip()

    pygame.quit()

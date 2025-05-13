import pygame
from Board import Board, BOARD_SIZE
from game import Game
import sys


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


def get_grid_position(mouse_pos):
    mx, my = mouse_pos
    mx -= (WINDOW_SIZE - GAME_SIZE) / 2

    my -= (WINDOW_SIZE - GAME_SIZE) / 2

    print(mx)
    print(my)
    x = int(mx // CELL_SIZE)
    y = int(my // CELL_SIZE)
    if x > 18 or y > 18:
        return -1, -1
    return x, y


def menu_screen(screen, font):
    while True:
        screen.fill(WHITE)
        draw_text(
            screen, "Bienvenue sur Gomoku", font, WINDOW_SIZE // 2, WINDOW_SIZE // 4
        )
        draw_text(
            screen, "1. Jouer contre une IA", font, WINDOW_SIZE // 2, WINDOW_SIZE // 2
        )
        draw_text(
            screen,
            "2. Jouer contre un ami",
            font,
            WINDOW_SIZE // 2,
            WINDOW_SIZE // 2 + 50,
        )
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # print(event.key)
                # print(pygame.K_1)
                # print(pygame.K_2)
                if event.key == pygame.K_1:
                    return "ai"
                elif event.key == pygame.K_2:
                    return "friend"


def draw_board(board: Board, screen, img1 = None, img2 = None):
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
                img = img1
            elif val == 2:
                img = img2

            if img:
                px = (WINDOW_SIZE - GAME_SIZE) / 2 + x * CELL_SIZE
                py = (WINDOW_SIZE - GAME_SIZE) / 2 + y * CELL_SIZE
                screen.blit(img, (px, py))
            # if val == 1:
            #     pygame.draw.circle(
            #         screen,
            #         BLACK,
            #         (
            #             (WINDOW_SIZE - GAME_SIZE) / 2 + (x + 0.5) * CELL_SIZE,
            #             (WINDOW_SIZE - GAME_SIZE) / 2 + (y + 0.5) * CELL_SIZE,
            #         ),
            #         STONE_RADIUS,
            #     )
            # elif val == 2:
            #     pygame.draw.circle(
            #         screen,
            #         RED,
            #         (
            #             (WINDOW_SIZE - GAME_SIZE) / 2 + (x + 0.5) * CELL_SIZE,
            #             (WINDOW_SIZE - GAME_SIZE) / 2 + (y + 0.5) * CELL_SIZE,
            #         ),
            #         STONE_RADIUS,
            #     )

    # pygame.display.flip()


def init_game():
    game = Game(1)
    board = Board()
    print(WINDOW_SIZE)
    pygame.init()

    font = pygame.font.SysFont(None, 36)
    font_big = pygame.font.SysFont(None, 56)

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    image = pygame.image.load("./assets/black2.png").convert_alpha()
    image2 = pygame.image.load("./assets/white.png").convert_alpha()
    img1 = pygame.transform.smoothscale(image, (CELL_SIZE, CELL_SIZE))
    img2 = pygame.transform.smoothscale(image2, (CELL_SIZE, CELL_SIZE))
    # screen.blit(resized_img, (50, 50))
    # screen.blit(resized_img2, (150, 50))
    pygame.display.set_caption("Gomoku AI")
    # mode = menu_screen(screen, font)
    print(print(board.board))
    run = True

    while run is True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = get_grid_position(pygame.mouse.get_pos())
                print(x, y)
                # if
                board.play_move(game, x, y)

                # if board.is_winning_move(x, y, player):
                # print(f"Player {player} wins!")
                # running = False
                # if mode == "friend":
                # player = P2 if player == P1 else P1
        # screen.fill("purple")
        draw_board(board, screen, img1, img2)
        # screen.fill(WHITE)
        # message = "Red turn." if game.player_turn == 2 else "Black turn."
        message_couleur = "Red" if game.player_turn == 2 else "Black"
        color = RED if message_couleur == "Red" else BLACK

        texte_partie1 = font_big.render(message_couleur, True, color)
        texte_partie2 = font_big.render(" turn.", True, BLACK)

        # texte_surface = font.render(message, True, BLACK)

        # padding_x = 10
        # padding_y = 5

        # total_width = texte_partie1.get_width() + texte_partie2.get_width()
        width_text = texte_partie2.get_width()
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
        screen.blit(texte_partie1, (WINDOW_SIZE / 2 - width_text, WINDOW_SIZE - 100))
        screen.blit(
            texte_partie2,
            (
                WINDOW_SIZE / 2 - width_text + texte_partie1.get_width(),
                WINDOW_SIZE - 100,
            ),
        )
        # screen.blit(texte_surface, (50, 50))
        pygame.display.flip()
        # clock.tick(60)
        # pygame.display.flip()

    pygame.quit()

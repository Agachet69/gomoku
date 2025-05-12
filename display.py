import pygame
from Board import Board, BOARD_SIZE
import sys

WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
BLUE = (66, 135, 245)
RED = (245, 66, 66)

CELL_SIZE = 60
GAME_SIZE = CELL_SIZE * BOARD_SIZE
WINDOW_SIZE = GAME_SIZE * 1.1
STONE_RADIUS = CELL_SIZE // 2 - 5


def draw_text(screen, text, font, x, y):
    label = font.render(text, True, BLACK)
    rect = label.get_rect(center=(x, y))
    screen.blit(label, rect)

def get_grid_position(mouse_pos) :
    mx, my = mouse_pos
    mx -=  (WINDOW_SIZE - GAME_SIZE) / 2

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
            font, WINDOW_SIZE // 2,
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

def draw_board(board: Board, screen):
    screen.fill(WHITE)

    for i in range(BOARD_SIZE +1):
        padding = (WINDOW_SIZE - GAME_SIZE) / 2
        pygame.draw.line(
            screen,
            GRAY,
            (padding, padding + (CELL_SIZE * i)),
            (padding + CELL_SIZE * 19, padding + (CELL_SIZE * i)),
            1,
        )
        pygame.draw.line(
            screen,
            GRAY,
            (padding + (CELL_SIZE * i), padding),
            (padding + (CELL_SIZE * i), padding + (CELL_SIZE * 19)),
            1,
        )

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            val = board.board[y, x]
            if val == 1:
                pygame.draw.circle(
                    screen,
                    BLACK,
                    (
                        (WINDOW_SIZE - GAME_SIZE) / 2 + (x + 0.5) * CELL_SIZE,
                        (WINDOW_SIZE - GAME_SIZE) / 2 + (y + 0.5) * CELL_SIZE,
                    ),
                    STONE_RADIUS,
                )
            elif val == 2:
                pygame.draw.circle(
                    screen,
                    RED,
                    (
                        (WINDOW_SIZE - GAME_SIZE) / 2 + (x + 0.5) * CELL_SIZE,
                        (WINDOW_SIZE - GAME_SIZE) / 2 + (y + 0.5) * CELL_SIZE,
                    ),
                    STONE_RADIUS,
                )

    pygame.display.flip()

def init_game():
    board = Board()
    print(WINDOW_SIZE)
    pygame.init()
    
    font = pygame.font.SysFont(None, 36)

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
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
                board.play_move(x, y)
                    # if board.is_winning_move(x, y, player):
                        # print(f"Player {player} wins!")
                        # running = False
                    # if mode == "friend":
                        # player = P2 if player == P1 else P1
        # screen.fill("purple")
        draw_board(board, screen)
        # pygame.display.flip()

    pygame.quit()

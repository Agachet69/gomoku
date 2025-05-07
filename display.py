import pygame
from Board import Board, BOARD_SIZE


WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
BLUE = (66, 135, 245)
RED = (245, 66, 66)

WINDOW_SIZE = 1000
GAME_SIZE = WINDOW_SIZE * 0.96
CELL_SIZE = GAME_SIZE // BOARD_SIZE 
STONE_RADIUS = CELL_SIZE // 2 - 5


def draw_board(board: Board, screen):
    screen.fill(WHITE)
    # board.board = [
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # ]


    for i in range(BOARD_SIZE +1):

        pygame.draw.line(
            screen,
            GRAY,
            (CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2),
            (WINDOW_SIZE - CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2),
            1,
        )
        pygame.draw.line(
            screen,
            GRAY,
            (i * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2),
            (i * CELL_SIZE + CELL_SIZE // 2, WINDOW_SIZE - CELL_SIZE // 2),
            1,
        )

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            val = board.board[y, x]
            if val == 1:
                pygame.draw.circle(
                    screen,
                    BLACK,
                    (25 + (x + 0.5) * CELL_SIZE, 25 + (y + 0.5) * CELL_SIZE),
                    STONE_RADIUS,
                )
            elif val == 2:
                pygame.draw.circle(
                    screen,
                    RED,
                    (25 + (x + 0.5) * CELL_SIZE, 25 + (y + 0.5) * CELL_SIZE),
                    STONE_RADIUS,
                )

    pygame.display.flip()

def init_game():
    board = Board()

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Gomoku AI")
    print(print(board.board))
    board.board[0][0] = 1
    board.board[0][1] = 2
    print(print(board.board))
    run = True

    while run is True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # screen.fill("purple")
        draw_board(board, screen)
        # pygame.display.flip()

    pygame.quit()

import pygame
from game import Game
from Board import Board
from config import (
    WINDOW_SIZE,
    BOARD_SIZE,
    PADDING,
    BLACK,
    GAME_SIZE,
    CELL_SIZE,
    GOBAN,
    WHITE,
    GRAY,
    RED,
)


def draw_board(screen, fonts, game: Game):
    board = game.board
    screen.fill(GOBAN)

    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(
            screen,
            BLACK,
            (PADDING, PADDING + (CELL_SIZE * i)),
            (PADDING + CELL_SIZE * 19, PADDING + (CELL_SIZE * i)),
            1,
        )
        nb = fonts["font"].render(f"{i}", True, BLACK)
        pygame.draw.line(
            screen,
            BLACK,
            (PADDING + (CELL_SIZE * i), PADDING),
            (PADDING + (CELL_SIZE * i), PADDING + (CELL_SIZE * 19)),
            1,
        )
        if i < 19:
            screen.blit(
                nb,
                (
                    (PADDING + 15) + 50 * i,
                    160,
                ),
            )
            screen.blit(
                nb,
                (
                    160,
                    (PADDING + 15) + 50 * i,
                ),
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


def draw_turn(screen, fonts, game):
    message_couleur = "White" if game.player_turn == 2 else "Black"
    color = RED if message_couleur == "Red" else BLACK

    texte_partie1 = fonts["font_big"].render(message_couleur, True, color)
    texte_partie2 = fonts["font_big"].render(" turn.", True, BLACK)
    width_text = texte_partie2.get_width()
    screen.blit(texte_partie1, (WINDOW_SIZE / 2 - width_text, WINDOW_SIZE - 100))
    screen.blit(
        texte_partie2,
        (
            WINDOW_SIZE / 2 - width_text + texte_partie1.get_width(),
            WINDOW_SIZE - 100,
        ),
    )


def draw_capture_score(screen, fonts, game):
    msg_capture_P1 = f"Captures: {game.P1.capture_score}"
    msg_capture_P2 = f"Captures: {game.P2.capture_score}"

    number_captures_P1 = fonts["little"].render(msg_capture_P1, True, BLACK)
    number_captures_P2 = fonts["little"].render(msg_capture_P2, True, BLACK)

    screen.blit(
        number_captures_P2,
        (
            20,
            220,
        ),
    )
    screen.blit(
        number_captures_P1,
        (
            1160,
            220,
        ),
    )
  

def draw_title(screen, fonts):
    title = "Gomoku"
    title_screen = fonts["font_big"].render(title, True, BLACK)
    screen.blit(title_screen, (WINDOW_SIZE / 2 - 90, 50))


def draw_team_side(screen, fonts, game):
    P1_team = game.P1.name
    P2_team = game.P2.name
    P1_team_screen = fonts["font"].render(P1_team, True, BLACK)
    P2_team_screen = fonts["font"].render(P2_team, True, BLACK)

    screen.blit(
        P1_team_screen,
        (
            WINDOW_SIZE * 0.9,
            150,
        ),
    )

    screen.blit(
        P2_team_screen,
        (
            WINDOW_SIZE / 20,
            150,
        ),
    )


def draw_game(
    screen,
    fonts,
    game: Game,
):
    draw_board(screen, fonts, game)
    draw_title(screen, fonts)
    draw_turn(screen, fonts, game)
    draw_team_side(screen, fonts, game)
    draw_capture_score(screen, fonts, game)

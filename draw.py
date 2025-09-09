import pygame
import pygame.gfxdraw
from game import Game
from Board import Board
from player import Player
from game_state_enum import GameState
from game_state_enum import GameType
from thread import init_threads
from config import (
    WINDOW_SIZE,
    BOARD_SIZE,
    PADDING,
    BLACK,
    GAME_SIZE,
    CELL_SIZE,
    GOBAN,
    WHITE,
    WHITE_TRANSPARENT,
    GRAY,
    GRAY_ARROW,
    RED,
)


def draw_text(screen, text, font, x, y):
    label = font.render(text, True, BLACK)
    rect = label.get_rect(center=(x, y))
    screen.blit(label, rect)
    return rect


def get_mode(event, game, ia, simple, futur):
    if ia.collidepoint(event.pos) or simple.collidepoint(event.pos):
        img_black = pygame.image.load("./assets/black.png").convert_alpha()
        img_white = pygame.image.load("./assets/white.png").convert_alpha()
        black = pygame.transform.smoothscale(img_black, (CELL_SIZE, CELL_SIZE))
        white = pygame.transform.smoothscale(img_white, (CELL_SIZE, CELL_SIZE))
        black_hover = black.copy()
        black_hover.set_alpha(128)
        white_hover = white.copy()
        white_hover.set_alpha(128)
        P1 = Player(black, black_hover, "Black", 1)
        P2 = Player(white, white_hover, "White", 2)
        game.set_players(P1, P2)
        game.game_state = GameState.Playing
        print("→ Lancement du jeu")
        if ia.collidepoint(event.pos):
            game.type = GameType.AI
            init_threads(game)
        else:
            game.type = GameType.PvP

    elif futur.collidepoint(event.pos):
        img_marseille = pygame.image.load("./assets/marseille.png").convert_alpha()
        img_psg = pygame.image.load("./assets/psg.png").convert_alpha()
        marseille = pygame.transform.smoothscale(img_marseille, (CELL_SIZE, CELL_SIZE))
        psg = pygame.transform.smoothscale(img_psg, (CELL_SIZE, CELL_SIZE))
        marseille_hover = marseille.copy()
        marseille_hover.set_alpha(128)
        psg_hover = psg.copy()
        psg_hover.set_alpha(128)
        P1 = Player(marseille, marseille_hover, "Marseille", 1)
        P2 = Player(psg, psg_hover, "PSG", 2)
        game.set_players(P1, P2)
        game.game_state = GameState.Playing
        game.type = GameType.FUTURE
        print("→ Avenir en lecture..")
        init_threads(game)


def draw_menu_screen(screen, fonts, game: Game, event):
    screen.fill((0, 0, 0))
    screen.fill(GOBAN)
    screen_rect = screen.get_rect()
    box_width, box_height = 500, 300
    box_rect = pygame.Rect(0, 0, box_width, box_height)
    box_rect.center = screen_rect.center

    draw_text(
        screen,
        "Bienvenue sur Gomoku",
        fonts["font_big"],
        WINDOW_SIZE // 2,
        WINDOW_SIZE // 4,
    )
    text = "Choose a game mode"

    text_surface = fonts["font_big"].render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(box_rect.centerx, box_rect.top + 60))

    first_choice = fonts["font"].render("1. Play with AI", True, BLACK)
    second_choice = fonts["font"].render("2. Play with friend", True, BLACK)
    third_choice = fonts["font"].render("3. Prevoir l'avenir", True, BLACK)

    first_choice_rect = first_choice.get_rect(
        center=(box_rect.left + first_choice.get_width() / 2 + 80, box_rect.top + 130)
    )
    second_choice_rect = second_choice.get_rect(
        center=(box_rect.left + second_choice.get_width() / 2 + 80, box_rect.top + 180)
    )
    third_choice_rect = third_choice.get_rect(
        center=(box_rect.left + third_choice.get_width() / 2 + 80, box_rect.top + 230)
    )

    pygame.draw.rect(screen, WHITE, box_rect, border_radius=15)
    screen.blit(text_surface, text_rect)
    screen.blit(first_choice, first_choice_rect)
    screen.blit(second_choice, second_choice_rect)
    screen.blit(third_choice, third_choice_rect)

    pygame.display.flip()

    if event.type == pygame.MOUSEBUTTONDOWN:
        get_mode(event, game, first_choice_rect, second_choice_rect, third_choice_rect)


def draw_finish_modal(screen, game: Game, fonts, event):
    screen_rect = screen.get_rect()
    box_width, box_height = 500, 300
    box_rect = pygame.Rect(0, 0, box_width, box_height)
    box_rect.center = screen_rect.center
    modal_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)

    if game.game_state == GameState.Finish:
        text = f"{game.winner.name} WIN"
        text_surface = fonts["font_big"].render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(box_width // 2, 60))
    else:
        text = "IT'S A DRAW"
        text_surface = fonts["font_big"].render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(box_width // 2, 60))

    replay_surface = fonts["font"].render("Rejouer", True, BLACK)
    menu_surface = fonts["font"].render("Menu principal", True, BLACK)

    max_text_width = max(replay_surface.get_width(), menu_surface.get_width())
    button_width = max_text_width + 40
    button_height = replay_surface.get_height() + 20

    replay_rect = pygame.Rect(0, 0, button_width, button_height)
    replay_rect.center = (box_width // 2, 160)

    menu_rect = pygame.Rect(0, 0, button_width, button_height)
    menu_rect.center = (box_width // 2, 230)

    is_hover = None
    if hasattr(event, "pos"):
        is_hover = box_rect.collidepoint(event.pos)
    bg_color = WHITE if is_hover else WHITE_TRANSPARENT

    pygame.draw.rect(
        modal_surface, bg_color, modal_surface.get_rect(), border_radius=15
    )
    modal_surface.blit(text_surface, text_rect)
    pygame.draw.rect(modal_surface, GRAY, replay_rect, border_radius=14)
    pygame.draw.rect(modal_surface, GRAY, menu_rect, border_radius=14)
    modal_surface.blit(
        replay_surface, replay_surface.get_rect(center=replay_rect.center)
    )
    modal_surface.blit(menu_surface, menu_surface.get_rect(center=menu_rect.center))
    screen.blit(modal_surface, (box_rect.x, box_rect.y))

    if event.type == pygame.MOUSEBUTTONDOWN:
        abs_replay_rect = replay_rect.move(box_rect.topleft)
        abs_menu_rect = menu_rect.move(box_rect.topleft)
        if abs_replay_rect.collidepoint(event.pos):
            game.replay()
        elif abs_menu_rect.collidepoint(event.pos):
            game.menu()


def draw_temporary_stone(x, y, screen, player):
    px = (WINDOW_SIZE - GAME_SIZE) / 2 + x * CELL_SIZE
    py = (WINDOW_SIZE - GAME_SIZE) / 2 + y * CELL_SIZE
    screen.blit(player.img_hover, (px, py))


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
        pygame.draw.line(
            screen,
            BLACK,
            (PADDING + (CELL_SIZE * i), PADDING),
            (PADDING + (CELL_SIZE * i), PADDING + (CELL_SIZE * 19)),
            1,
        )
        nb = fonts["tinny"].render(f"{i}", True, BLACK)
        if i < 19:
            screen.blit(
                nb,
                (
                    PADDING + 15 + CELL_SIZE * i,
                    PADDING - 10,
                ),
            )
            screen.blit(
                nb,
                (
                    PADDING - 10,
                    PADDING + 15 + CELL_SIZE * i,
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
    screen.blit(texte_partie1, (WINDOW_SIZE / 2 - width_text, WINDOW_SIZE - 40))
    screen.blit(
        texte_partie2,
        (
            WINDOW_SIZE / 2 - width_text + texte_partie1.get_width(),
            WINDOW_SIZE - 40,
        ),
    )


def draw_capture_score(screen, fonts, game):
    msg_capture_P1 = f"Captures: {game.P1.capture_score}"
    msg_capture_P2 = f"Captures: {game.P2.capture_score}"

    number_captures_P1 = fonts["little_tinny"].render(msg_capture_P1, True, BLACK)
    number_captures_P2 = fonts["little_tinny"].render(msg_capture_P2, True, BLACK)

    screen.blit(
        number_captures_P2,
        (
            10,
            180,
        ),
    )
    screen.blit(
        number_captures_P1,
        (
            WINDOW_SIZE - PADDING + 10,
            180,
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
            WINDOW_SIZE - PADDING + 10,
            150,
        ),
    )

    screen.blit(
        P2_team_screen,
        (
            10,
            150,
        ),
    )


def draw_arrow(screen, color, x, y, orientation, width=30, height=25):
    """
    Dessine une flèche pointant soit vers
    la droite soit vers la gauche.
    """
    half_height = height // 2
    if orientation == "right":
        points = [
            (x, y - half_height),  # coin haut gauche
            (x + width, y),  # pointe droite
            (x, y + half_height),  # coin bas gauche
        ]
    else:
        points = [
            (x, y),  # pointe gauche
            (x + width, y - half_height),  # coin haut droit
            (x + width, y + half_height),  # coin bas droit
        ]

    pygame.gfxdraw.filled_polygon(screen, points, color)
    pygame.gfxdraw.aapolygon(screen, points, color)

    arrow_rect = pygame.Rect(
        min(p[0] for p in points),
        min(p[1] for p in points),
        max(p[0] for p in points) - min(p[0] for p in points),
        max(p[1] for p in points) - min(p[1] for p in points),
    )

    return arrow_rect


def draw_historic_arrows(screen, fonts, game: Game, event):
    screen_rect = screen.get_rect()

    left_rect = draw_arrow(
        screen,
        BLACK if game.step_historic > 0 else GRAY_ARROW,
        screen_rect.centerx - 90,
        screen_rect.height - 105,
        "left",
    )
    right_rect = draw_arrow(
        screen,
        BLACK if game.step_historic < len(game.historic) - 1 else GRAY_ARROW,
        screen_rect.centerx + 90,
        screen_rect.height - 105,
        "right",
    )

    if hasattr(event, "pos"):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if left_rect.collidepoint(event.pos):
                game.get_back_historic()
            if right_rect.collidepoint(event.pos):
                game.get_front_historic()


def draw_game(screen, fonts, game: Game, event):
    draw_board(screen, fonts, game)
    draw_title(screen, fonts)
    draw_turn(screen, fonts, game)
    draw_team_side(screen, fonts, game)
    draw_capture_score(screen, fonts, game)
    if game.type == GameType.PvP:
        draw_historic_arrows(screen, fonts, game, event)

from game import Game
from player import Player
from config import BOARD_SIZE

POTENTIAL_WIN_SCORE = 300

def is_on_board(x, y):
    if not (0 <= x < BOARD_SIZE) or not (0 <= y < BOARD_SIZE):
        return False
    return True


def count_aligned(board, player_value, x, y, dx, dy):
    aligned = 0
    while is_on_board(x, y) and board[y][x] == player_value:
        aligned += 1
        x += dx
        y += dy
    return aligned


def is_free(board, x, y):
    return is_on_board(x, y) and board[y][x] == 0


def evaluate_alignments(board, player_value: int):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    alignements_scores = {
        (5, "open"): 100000,
        (4, "open"): 10000,
        (4, "half"): 1000,
        (3, "open"): 500,
        (3, "half"): 100,
        (2, "open"): 50,
        (2, "half"): 10,
    }

    score = 0

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if board[y][x] != player_value:
                continue

            for dx, dy in directions:
                prev_x, prev_y = x - dx, y - dy

            if is_on_board(prev_x, prev_y) and board[prev_y][prev_x] == player_value:
                continue

            aligned = count_aligned(board, player_value, x, y, dx, dy)
            after_x, after_y = x + dx * aligned, y + dy * aligned
            open_ends = 0
            if is_free(board, prev_x, prev_y):
                open_ends += 1
            if is_free(board, after_x, after_y):
                open_ends += 1

            label = 'open' if open_ends == 2 else 'half' if open_ends == 1 else 'blocked'
            if (aligned, label) in alignements_scores:
                score += alignements_scores[(aligned, label)]
            
            total_space = aligned + open_ends
            if total_space >= 5 and aligned < 5:
                score += POTENTIAL_WIN_SCORE

    return score


def evaluate(game: Game, player: Player) -> int:
    board = game.board.board
    opponent = game.get_opponent(player.value)

    score = 0
    score += evaluate_alignments(board, player.value)
    # score += evaluate_potential_wins(board, player)
    # score += evaluate_freedom(board, player)
    # score += evaluate_captures(board, player)
    # score += evaluate_patterns(board, player)
    # score += evaluate_dynamics(game, player)

    opponent_score = (
        evaluate_alignments(board, opponent.value)
        # + evaluate_potential_wins(board, opponent)
        # + evaluate_freedom(board, opponent)
        # + evaluate_captures(board, opponent)
        # + evaluate_patterns(board, opponent)
        # + evaluate_dynamics(game, opponent)
    )
    return score - opponent_score

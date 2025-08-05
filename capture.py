def can_capture_from_winning_sequence(board, winning_seq, player_value, game):
    game.last_chance_capture = set(winning_seq)
    BOARD_SIZE = board.shape[0]
    opp_value = 2 if player_value == 1 else 1
    directions = [
        (0, 1), (1, 0), (1, 1), (1, -1)
    ]
    print(winning_seq)
    for (x, y) in winning_seq:
        for dx, dy in directions:
            x1, y1 = x + dx, y + dy
            x2, y2 = x1 + dx, y1 + dy
            neg_x, neg_y = x - dx, y - dy
            if (0 <= x2 < BOARD_SIZE and 0 <= y2 < BOARD_SIZE and
                0 <= neg_x < BOARD_SIZE and 0 <= neg_y < BOARD_SIZE):
                if board[y1, x1] == player_value and board[y2, x2] == opp_value and board[neg_y, neg_x] == 0:
                    return True
                elif board[y1, x1] == player_value and board[y2, x2] == 0 and board[neg_y, neg_x] == opp_value:
                    return True
            x1, y1 = x - dx, y - dy
            x2, y2 = x1 - dx, y1 - dy
            neg_x, neg_y = x + dx, y + dy
            if (0 <= x2 < BOARD_SIZE and 0 <= y2 < BOARD_SIZE and
                0 <= neg_x < BOARD_SIZE and 0 <= neg_y < BOARD_SIZE):
                if board[y1, x1] == player_value and board[y2, x2] == opp_value and board[neg_y, neg_x] == 0:
                    return True
                elif board[y1, x1] == player_value and board[y2, x2] == 0 and board[neg_y, neg_x] == opp_value:
                    return True
    return False

def can_capture_common_stone(board, winning_sequences, player_value, game):
    common_stones = set(winning_sequences[0])
    for seq in winning_sequences[1:]:
        common_stones.intersection_update(seq)
        if not common_stones:
            return False
    
    for stone in common_stones:
        if can_capture_from_winning_sequence(board, [stone], player_value, game):
            return True
    return False

def can_capture_winning_sequences(board, winning_sequences, player_value, game):
    if len(winning_sequences) > 1:    
        return can_capture_common_stone(board, winning_sequences, player_value, game)
    return can_capture_from_winning_sequence(board, winning_sequences[0], player_value, game)
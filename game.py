class Game:
    def __init__(self, player):
        self.player_turn = player

    def has_played(self):
        player = self.player_turn
        self.player_turn = 1 if self.player_turn == 2 else 2
        return player
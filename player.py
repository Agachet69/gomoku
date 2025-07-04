class Player:
    def __init__(self, path, path_hover, name, value):
        self.img_path = path
        self.img_hover = path_hover
        self.name = name
        self.mooves = 0
        self.capture_score = 0
        self.value = value
        self.last_moves = []
    
    def deep_copy(self):
        copied_player = Player(self.img_path, self.name, self.value)
        copied_player.mooves = self.mooves
        copied_player.capture_score = self.capture_score
        return copied_player

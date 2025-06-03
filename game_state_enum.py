from enum import Enum

class GameState(Enum):
    Creating = 0
    Playing = 1
    Finish = 2
    Draw = 3
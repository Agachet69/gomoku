from enum import Enum

class GameState(Enum):
    Creating = 0
    Playing = 1
    Finish = 2
    Draw = 3

class GameType(Enum):
    AI = 0
    PvP = 1
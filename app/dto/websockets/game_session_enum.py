from enum import Enum

class GameSessionEnum(str, Enum):
    LOBBY = "lobby"
    PLAYING = "playing"
    FINISHED = "finished"

    
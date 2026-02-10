from enum import Enum

class ChangeEvents(Enum):
    SONG_TITLE_CHANGED = 0
    SONG_ARTIST_CHANGED = 1
    DIE = 2
    TICK = 3
    UNKOWN = 99
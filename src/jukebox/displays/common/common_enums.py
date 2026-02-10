from enum import Enum

class DisplayStateMachineState(Enum):
    IDLE = 0
    """Not doing anything."""
    INIT = 1
    """Initializing display with new text."""
    LOOP = 2
    """Main loop for display updates."""
    TEXT_UPDATED = 3 
    """Text has been updated and needs to be redrawn."""
    BEGIN_ANIMATION = 4
    """Start any animations."""
    EMPTY = 5
    """No text to display."""
    FINISHED = 6
    """Finished displaying text (and any animation)."""
    END_ANIMATION = 7


class DisplayInfoState(Enum):
    IDLE = 0
    """Not doing anything."""
    DRAWING_ARTIST = 1
    """Drawing artist text."""
    DRAWING_TITLE = 2
    """Drawing title text."""

class DisplayInfoTypes(Enum):
    UNKNOWN = 0
    SONG_ARTIST = 1
    SONG_TITLE = 2

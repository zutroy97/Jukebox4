import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.displays.common.common_enums import  DisplayStateMachineState, DisplayInfoState
from abc import ABC, abstractmethod
from ctypes import c_uint64 as uint64 
from jukebox.animators.random_typewriter import RandomTypeWriter

class DisplayBase(ABC):
    def __init__(self, **kwargs ) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        self._stateArtist = DisplayStateMachineState.IDLE
        self._stateTitle = DisplayStateMachineState.IDLE
        self._alarmTicks = uint64(0)
        self._displayState = DisplayInfoState.DRAWING_ARTIST
        self._minDwellTicks =kwargs.get('max_dwell_ticks', 5000)
        '''Maximum time in ms to display a screen.'''
        self._moveNextDisplayStart : bool = False
        self._title :str = ""
        self._artist: str  = ""
        self._running : bool = False
        self._ticks : uint64 = uint64(0)
        '''Current time in ms, used for timing the display updates. Should be updated by the DisplayCoordinator on each tick.'''

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def artist(self) -> str:
        return self._artist
    
    def song_title_updated(self) -> None:
        self._stateTitle = DisplayStateMachineState.TEXT_UPDATED
    def song_artist_updated(self) -> None:
        self._stateArtist = DisplayStateMachineState.TEXT_UPDATED

    def update(self, **kwargs):
        '''Receives updates from the DisplayCoordinator. Subclasses can override this method to handle specific events.'''
        if 'event' in kwargs:
            event = kwargs.get('event', ChangeEvents.UNKOWN)
            value = kwargs.get('value', '')
            if event == ChangeEvents.DIE:
                self._running = False
            elif event == ChangeEvents.SONG_TITLE_CHANGED:
                self._title = value
                self.song_title_updated()
            elif event == ChangeEvents.SONG_ARTIST_CHANGED:
                self._artist = value
                self.song_artist_updated()
            elif event == ChangeEvents.TICK:
                self._tick()

    def __del__(self):
        #self.clear_screen()
        pass

    def _tick(self) -> None:
        '''Advances the internal clock of the display. Should be called by the DisplayCoordinator on each tick.'''
        self._ticks.value += 10
        self._updateDisplay()

    @abstractmethod
    def _updateDisplay(self) -> None:
        '''Subclasses can implement this method to update the display with new text'''
        pass

    @abstractmethod
    def clear_screen(self) -> None:
        '''Subclasses can implement this method to clear the display'''
        pass




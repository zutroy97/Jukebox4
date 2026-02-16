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
        #self._alarmTicks.value = self._ticks.value + self._minDwellTicks
        self._stateTitle = DisplayStateMachineState.TEXT_UPDATED
    def song_artist_updated(self) -> None:
        #self._alarmTicks.value = self._ticks.value + self._minDwellTicks
        self._stateArtist = DisplayStateMachineState.TEXT_UPDATED

    def update(self, **kwargs):
        '''Receives updates from the DisplayCoordinator. Subclasses can override this method to handle specific events.'''
        if 'event' in kwargs:
            event = kwargs.get('event', ChangeEvents.UNKOWN)
            value = kwargs.get('value', '')
            #self._logger.debug(f"Received update from observable. Event: {event} Value: {value}")
            if event == ChangeEvents.DIE:
                self._running = False
            elif event == ChangeEvents.SONG_TITLE_CHANGED:
                self._title = value
                self.song_title_updated()
            elif event == ChangeEvents.SONG_ARTIST_CHANGED:
                self._artist = value
                self.song_artist_updated()
            elif event == ChangeEvents.TICK:
                self._ticks.value += 10
                self._refresh()

    def __del__(self):
        pass

    def _refresh(self) -> None:
        #self._logger.debug(f"Ticks: {self._ticks.value} AlarmTicks: {self._alarmTicks.value}")
        # if (self._ticks.value >= self._alarmTicks.value or self._moveNextDisplayStart == True):
        #     self._alarmTicks.value = self._ticks.value + self._minDwellTicks
        #     self._moveNextDisplayStart = False
        #     if self._displayState == DisplayInfoState.DRAWING_ARTIST:
        #         self._displayState = DisplayInfoState.DRAWING_TITLE
        #         self._stateArtist = DisplayStateMachineState.INIT
        #     else:
        #         self._displayState = DisplayInfoState.DRAWING_TITLE
        #         self._displayState = DisplayInfoState.DRAWING_ARTIST
        #         self._stateTitle = DisplayStateMachineState.INIT

        self._updateDisplay()

        # if self._displayState == DisplayInfoState.DRAWING_ARTIST:
        #     if self._stateArtist == DisplayStateMachineState.FINISHED:
        #         self._moveNextDisplayStart = True
        # elif self._displayState == DisplayInfoState.DRAWING_TITLE:
        #     if self._stateTitle == DisplayStateMachineState.FINISHED:
        #         self._moveNextDisplayStart = True
        # else:
        #     self._moveNextDisplayStart = True

    @abstractmethod
    def _updateDisplay(self) -> None:
        '''Subclasses can implement this method to update the display with new text'''
        pass




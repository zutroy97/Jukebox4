import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.displays.display_observer_base import DisplayObserverBase
import asyncio
from jukebox.displays.common_enums import  DisplayStateMachineState, DisplayInfoState

from ctypes import c_uint64 as uint64 


class ConsoleDisplayBase(DisplayObserverBase):
    def __init__(self, max_dwell_ticks: int = 500) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        self._running = True
        self._stateArtist = DisplayStateMachineState.IDLE
        self._stateTitle = DisplayStateMachineState.IDLE
        self._alarmTicks = uint64(0)
        self._displayState = DisplayInfoState.DRAWING_ARTIST
        self._minDwellTicks = max_dwell_ticks
        self._moveNextDisplayStart : bool = False

    def title_updated(self) -> None:
        self._stateTitle = DisplayStateMachineState.TEXT_UPDATED
    def artist_updated(self) -> None:
        self._stateArtist = DisplayStateMachineState.TEXT_UPDATED
    
    async def draw(self) -> None:
        #self._logger.debug(f"Ticks: {self._ticks.value} AlarmTicks: {self._alarmTicks.value}")
        if (self._ticks.value >= self._alarmTicks.value or self._moveNextDisplayStart == True):
            self._alarmTicks.value = self._ticks.value + self._minDwellTicks
            self._moveNextDisplayStart = False
            if self._displayState == DisplayInfoState.DRAWING_ARTIST:
                self._displayState = DisplayInfoState.DRAWING_TITLE
                self._stateArtist = DisplayStateMachineState.INIT
            else:
                self._displayState = DisplayInfoState.DRAWING_TITLE
                self._displayState = DisplayInfoState.DRAWING_ARTIST
                self._stateTitle = DisplayStateMachineState.INIT

        if self._displayState == DisplayInfoState.DRAWING_ARTIST:
            self._stateArtist = self._drawText("Artist", self._artist, self._stateArtist)
            if self._stateArtist == DisplayStateMachineState.FINISHED:
                self._moveNextDisplayStart = True
            
        elif self._displayState == DisplayInfoState.DRAWING_TITLE:
            self._stateTitle = self._drawText("Title", self._title, self._stateTitle)
            if self._stateTitle == DisplayStateMachineState.FINISHED:
                self._moveNextDisplayStart = True
            pass

    def _drawText(self, header: str, text: str, state: DisplayStateMachineState) -> DisplayStateMachineState:
        '''Subclasses should implement this method'''
        return DisplayStateMachineState.FINISHED


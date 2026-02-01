import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.displays.display_observer_base import DisplayObserverBase
import asyncio
from jukebox.displays.common_enums import  DisplayStateMachineState, DisplayInfoState

from ctypes import c_uint64 as uint64 


class ConsoleDisplayBase(DisplayObserverBase):

    # class StringFlyingFromLeftAnimator:
    #     def __init__(self, text: str) -> None:
    #         self.text = text
    #         self.done : bool = False
    #         self.position = 0

    #     def next(self) -> str:
    #         if self.done:
    #             return ''
    #         display_text = self.text[0:self.position]
    #         self.position = self.position + 1
    #         if self.position > len(self.text):
    #             self.done = True
    #         return display_text
    #     def reset(self) -> None:
    #         self.position = 0
    #         self.done = False


    def __init__(self, min_dwell_ticks: int = 200) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        self._running = True
        self._stateArtist = DisplayStateMachineState.IDLE
        self._stateTitle = DisplayStateMachineState.IDLE
        self._alarmTicks = uint64(0)
        self._displayState = DisplayInfoState.DRAWING_ARTIST
        self._minDwellTicks = min_dwell_ticks

    def title_updated(self) -> None:
        self._stateTitle = DisplayStateMachineState.TEXT_UPDATED
    def artist_updated(self) -> None:
        self._stateArtist = DisplayStateMachineState.TEXT_UPDATED
    
    async def draw(self) -> None:
        #self._logger.debug(f"Ticks: {self._ticks.value} AlarmTicks: {self._alarmTicks.value}")
        if (self._ticks.value >= self._alarmTicks.value):
            self._alarmTicks.value = self._ticks.value + self._minDwellTicks
            if self._displayState == DisplayInfoState.DRAWING_ARTIST:
                self._displayState = DisplayInfoState.DRAWING_TITLE
                self._stateArtist = DisplayStateMachineState.INIT
            else:
                self._displayState = DisplayInfoState.DRAWING_TITLE
                self._displayState = DisplayInfoState.DRAWING_ARTIST
                self._stateTitle = DisplayStateMachineState.INIT

        if self._displayState == DisplayInfoState.DRAWING_ARTIST:
            self._stateArtist = self._drawText("Artist", self._artist, self._stateArtist)
            
        elif self._displayState == DisplayInfoState.DRAWING_TITLE:
            self._stateTitle = self._drawText("Title", self._title, self._stateTitle)
            pass

    def _drawText(self, header: str, text: str, state: DisplayStateMachineState) -> DisplayStateMachineState:
        '''Subclasses should implement this method'''
        return DisplayStateMachineState.FINISHED


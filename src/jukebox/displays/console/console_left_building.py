import logging
from jukebox.displays.common.common_enums import  DisplayStateMachineState
from jukebox.displays.console.console_display_base import ConsoleDisplayBase

from ctypes import c_uint64 as uint64 

class ConsoleLeftBuilding(ConsoleDisplayBase):
    def __init__(self) -> None:
        super().__init__()
        self._index = 0

    def _drawText(self, header: str, text: str, state: DisplayStateMachineState) -> DisplayStateMachineState: # returns true when fully drawn (text scrolled/fully displayed)
        if state == DisplayStateMachineState.INIT or state == DisplayStateMachineState.TEXT_UPDATED:
            self._index = 0
            if text == "":
                # Nothing to display, Nothing to do
                return DisplayStateMachineState.EMPTY
            self._text = f"{header}: {text}"
            self.__drawTextNextTick = uint64(0)
            return DisplayStateMachineState.ANIMATING
        elif state == DisplayStateMachineState.EMPTY:
            return DisplayStateMachineState.FINISHED
        elif state == DisplayStateMachineState.FINISHED:
            return DisplayStateMachineState.IDLE
        elif state == DisplayStateMachineState.ANIMATING:
            #self._logger.debug("in loop")
            self._animateFrame(10)
            if self._index > len(self._text):
                self.__drawTextNextTick.value = self._ticks.value + 75
                return DisplayStateMachineState.END_ANIMATION
        elif state == DisplayStateMachineState.END_ANIMATION:
            if (self._ticks.value > self.__drawTextNextTick.value):
                return DisplayStateMachineState.FINISHED

        return state
    
    def _animateFrame(self, wait_ticks : int):
        #self._logger.debug(f"ticks {self._ticks.value} __drawTextNextTick {self.__drawTextNextTick.value}")
        if (self._ticks.value < self.__drawTextNextTick.value):
            return
        animated_text = self._text[0:self._index]
        print("\033[H\033[2J", end="")  # Clear console
        print(animated_text)
        self._index = self._index + 1
        self.__drawTextNextTick.value = self._ticks.value + wait_ticks # wait this many clicks before scrolling the line


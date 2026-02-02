import logging
from jukebox.displays.common_enums import  DisplayStateMachineState
from jukebox.displays.console.console_display_base import ConsoleDisplayBase
import random

from ctypes import c_uint64 as uint64 

class RandomTypewriter(ConsoleDisplayBase):
    class Animator:
        def __init__(self, text: str, width: int = 20) -> None:
            self.text = text.strip()
            self.position = 0
            self.count = 0
            self.width = width
            self.done : bool = False

            if len(self.text) > 255:
                self.text = f"{self.text[0:255]}..."
            self._positions = list(range(0, len(self.text)))
            random.shuffle(self._positions)
            self._rendered = list(' ' * len(self.text))

        def next(self) -> str:
            x = self._positions.pop(0)
            self._rendered[x] = self.text[x]
            if len(self._positions) == 0:
                self.done = True
            return ''.join(self._rendered)

    def __init__(self, scroll_width : int = 10) -> None:
        super().__init__()
        self._scroll_width = scroll_width

    def _drawText(self, header: str, text: str, state: DisplayStateMachineState) -> DisplayStateMachineState: # returns true when fully drawn (text scrolled/fully displayed)
        if state == DisplayStateMachineState.INIT or state == DisplayStateMachineState.TEXT_UPDATED:
            if text == "":
                # Nothing to display, Nothing to do
                return DisplayStateMachineState.EMPTY
            self._header = f"{header}: "
            self._animator = self.Animator(text=text, width=self._scroll_width)
            self.__drawTextNextTick = uint64(0)
            return DisplayStateMachineState.LOOP
        elif state == DisplayStateMachineState.EMPTY:
            return DisplayStateMachineState.FINISHED
        elif state == DisplayStateMachineState.FINISHED:
            return DisplayStateMachineState.IDLE
        elif state == DisplayStateMachineState.LOOP:
            if (self._ticks.value > self.__drawTextNextTick.value):
                self._animateFrame(10)
                if self._animator.done:
                    self.__drawTextNextTick.value = self._ticks.value + 100
                    return DisplayStateMachineState.END_ANIMATION
        elif state == DisplayStateMachineState.END_ANIMATION:
            if (self._ticks.value > self.__drawTextNextTick.value):
                return DisplayStateMachineState.FINISHED

        return state
    
    def _animateFrame(self, wait_ticks : int):
        animated_text = self._animator.next()
        self.clear_screen()
        print(f"{self._header}{animated_text}")
        self.__drawTextNextTick.value = self._ticks.value + wait_ticks # wait this many clicks before scrolling the line


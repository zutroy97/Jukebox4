import logging
from jukebox.displays.common_enums import  DisplayStateMachineState
from jukebox.displays.console.console_display_base import ConsoleDisplayBase

from ctypes import c_uint64 as uint64 

class ConsoleScrollingWidth(ConsoleDisplayBase):
    class StringRepeatScrollAnimator:
        def __init__(self, text: str, width: int = 20) -> None:
            self.text = text
            self.position = 0
            self.width = width
            self.done : bool = False

        def next(self) -> str:
            if len(self.text) <= self.width:
                return self.text.ljust(self.width)
            display_text = self.text[self.position:self.position + self.width]
            self.position = (self.position + 1) % len(self.text)
            return display_text.ljust(self.width)
        
    def __init__(self, scroll_width : int = 10) -> None:
        super().__init__()
        self._scroll_width = scroll_width

    def _drawText(self, header: str, text: str, state: DisplayStateMachineState) -> DisplayStateMachineState: # returns true when fully drawn (text scrolled/fully displayed)
        if state == DisplayStateMachineState.INIT or state == DisplayStateMachineState.TEXT_UPDATED:
            if text == "":
                # Nothing to display, Nothing to do
                return DisplayStateMachineState.EMPTY
            self._animator = self.StringRepeatScrollAnimator(f"{header}: {text}", width=self._scroll_width)
            self.__drawTextNextTick = uint64(self._ticks.value)
            return DisplayStateMachineState.LOOP
        elif state == DisplayStateMachineState.EMPTY:
            return DisplayStateMachineState.FINISHED
        elif state == DisplayStateMachineState.FINISHED:
            state = DisplayStateMachineState.IDLE
        elif state == DisplayStateMachineState.LOOP:
            if (self._ticks.value > self.__drawTextNextTick.value):
                self.__drawTextNextTick.value = self._ticks.value + 10
                animated_text = self._animator.next()
                print("\033[H\033[2J", end="")  # Clear console
                print(animated_text)
                if self._animator.done:
                    return DisplayStateMachineState.FINISHED
        return DisplayStateMachineState.LOOP     

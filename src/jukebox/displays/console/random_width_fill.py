import logging
from jukebox.displays.common.common_enums import  DisplayStateMachineState
from jukebox.displays.common.display_base import DisplayBase
from jukebox.displays.console.console_display_base import ConsoleDisplayBase
import random
import textwrap

from ctypes import c_uint64 as uint64 

class RandomTypewriter(DisplayBase):
#class RandomTypewriter(ConsoleDisplayBase):
    class Animator:
        def __init__(self, text: str, width: int = 80) -> None:
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

    def __init__(self, max_text_width : int = 80) -> None:
        super().__init__()
        self._max_text_width = max_text_width

    def _drawText(self, header: str, text: str, state: DisplayStateMachineState) -> DisplayStateMachineState: # returns true when fully drawn (text scrolled/fully displayed)
        if state == DisplayStateMachineState.INIT or state == DisplayStateMachineState.TEXT_UPDATED:
            if text == "":
                # Nothing to display, Nothing to do
                return DisplayStateMachineState.FINISHED
            self._lines = textwrap.wrap(text, width=self._max_text_width, expand_tabs=False)
            self._animator = self.Animator(text=self._lines.pop(0))
            self._drawTextNextTick = uint64(0)
            self._header = header.strip()
            return DisplayStateMachineState.LOOP
        elif state == DisplayStateMachineState.LOOP:
            if (self._ticks.value > self._drawTextNextTick.value):
                self._animateFrame(50)
                if self._animator.done:
                    self._drawTextNextTick.value = self._ticks.value + 1000
                    if len(self._lines) > 0:
                        self._animator = self.Animator(text=self._lines.pop(0))
                    else:
                        return DisplayStateMachineState.END_ANIMATION
        elif state == DisplayStateMachineState.END_ANIMATION:
            if (self._ticks.value > self._drawTextNextTick.value):
                return DisplayStateMachineState.FINISHED

        return state
    def SetDelegation(self, delegate):
        self.delegate = delegate

    def _animateFrame(self, wait_ticks : int):
        self.delegate(self, wait_ticks)
        # animated_text = self._animator.next()
        # self.clear_screen()
        # print(f"{self._header}:")
        # print('-' * self._max_text_width)
        # print(animated_text)
        # self.__drawTextNextTick.value = self._ticks.value + wait_ticks # wait this many clicks before scrolling the line




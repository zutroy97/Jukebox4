import logging
from jukebox.displays.common.common_enums import  DisplayStateMachineState
from jukebox.displays.common.display_base import DisplayBase
from jukebox.displays.console.console_display_base import ConsoleDisplayBase

import textwrap

from ctypes import c_uint64 as uint64

from jukebox.displays.renderers.renderer import Renderer 

class RandomTypewriter(DisplayBase):


    # def __init__(self, renderer: Renderer) -> None:
    #     super().__init__(renderer)
        

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
                self._renderer.DrawFrame(header=header, value=self._animator.next(), display=self)
                self._drawTextNextTick.value = self._ticks.value + 5 # wait this many clicks before scrolling the line
                if self._animator.done:
                    self._drawTextNextTick.value = self._ticks.value + 100
                    if len(self._lines) > 0:
                        self._animator = self.Animator(text=self._lines.pop(0))
                    else:
                        return DisplayStateMachineState.END_ANIMATION
        elif state == DisplayStateMachineState.END_ANIMATION:
            if (self._ticks.value > self._drawTextNextTick.value):
                return DisplayStateMachineState.FINISHED
        return state




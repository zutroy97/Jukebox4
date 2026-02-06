import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.displays.common.display_observer_base import DisplayObserverBase
import asyncio
from jukebox.displays.common.common_enums import  DisplayStateMachineState, DisplayInfoState
from jukebox.displays.common.display_base import DisplayBase

from ctypes import c_uint64 as uint64 


class ConsoleDisplayBase(DisplayBase):
    def __init__(self, max_dwell_ticks: int = 5000) -> None:
        super().__init__(max_dwell_ticks)

    def __del__(self):
        super().__del__()
        self.clear_screen()

    def clear_screen(self):
        print("\033[H\033[2J", end="")  # Clear console



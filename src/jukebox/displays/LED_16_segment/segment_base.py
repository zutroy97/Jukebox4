import logging
from busio import I2C
import board
from typing import Dict, List, Optional, Tuple, Union
import asyncio
from adafruit_ht16k33 import segments
from ctypes import c_uint64 as uint64 
from enum import Enum

from jukebox.displays.common.display_base import DisplayBase

class SegmentBase(DisplayBase):
    def __init__(
            self, 
            **kwargs) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        i2c = kwargs.get('i2c', I2C(board.SCL, board.SDA))
        addr_lower = kwargs.get('addr_lower', (0x72, 0x73, 0x74))
        addr_upper = kwargs.get('addr_upper', (0x70, 0x71))
        self._display8 = segments.Seg14x4(i2c, address=addr_upper)  # uses board.SCL and board.SDA
        self._display12 = segments.Seg14x4(i2c, address=addr_lower)
        self._display8.brightness = 0.20
        self._display12.brightness = 0.20
    
    def clear_screen(self) -> None:
        self._display8.fill(0)
        self._display12.fill(0)

    def _updateDisplay(self) -> None:

        self._display8.print(f"{self.artist:<8}")
        self._display12.print(f"{self.title:<12}")

class SegmentSimple(SegmentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._lastArtist : str = ""
        self._lastTitle : str = ""

    def _updateDisplay(self) -> None:
        update_screen : bool = False
        update_screen |= self.artist != self._lastArtist
        update_screen |= self.title != self._lastTitle
        if not update_screen:
            return
        self._lastArtist = self.artist
        self._lastTitle = self.title
        self.clear_screen()
        self._display8.print(f"{self.artist[:8]:<8}")
        self._display12.print(f"{self.title[:12]:<12}")

class SegmentScroller(SegmentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._artistBuffer : str = ""
        self._titleBuffer : str = ""

    def _getBufferedString(self, value: str, size: int) -> str:
        if len(value) <= size:
            return f"{value:<{size}}"
        return value + " " * size  # add spaces to the end of the string to create a gap when scrolling 
    
    def song_title_updated(self) -> None:
        self._titleBuffer = self._getBufferedString(self.title, 12)
        #self._logger.debug(f"Updated title buffer: {self._titleBuffer}")
    def song_artist_updated(self) -> None:
        self._artistBuffer = self._getBufferedString(self.artist, 8)
        #self._logger.debug(f"Updated artist buffer: {self._artistBuffer}")
    def _updateDisplay(self) -> None:
        self._display8.non_blocking_marquee(self._artistBuffer, delay=0.3, loop=(len(self._artistBuffer) >8), space_between=0)
        self._display12.non_blocking_marquee(self._titleBuffer, delay=0.3, loop=(len(self._titleBuffer) >12), space_between=0)
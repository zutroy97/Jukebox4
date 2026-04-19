import asyncio
import logging

from busio import I2C
import board
from adafruit_ht16k33 import segments
from jukebox.displays.common.common_enums import DisplayStateMachineState
from jukebox.displays.common.display_base import DisplayBase
from typing import List, Tuple, Union

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
        self._running = True
    
    async def clear_screen(self) -> None:
        self._display8.fill(0)
        self._display12.fill(0)

    def _updateDisplay(self) -> None:
        self._display8.print(f"{self.artist[:8]:<8}")
        self._display12.print(f"{self.title[:12]:<12}")

    def print8(self, text: str) -> None:
        self._display8.print(f"{text[:8]:<8}")

    def print12(self, text: str) -> None:
        self._display12.print(f"{text[:12]:<12}")

    def write_raw8(self,index: int, bitmask: Union[int, List[int], Tuple[int, int]] ) -> None:
        self._display8.set_digit_raw(index, bitmask)

    def write_raw12(self,index: int, bitmask: Union[int, List[int], Tuple[int, int]] ) -> None:
        self._display12.set_digit_raw(index, bitmask)

    def set_brightness(self, brightness: float) -> None:
        brightness = max(0.0, min(1.0, brightness))
        self._display8.brightness = brightness
        self._display12.brightness = brightness




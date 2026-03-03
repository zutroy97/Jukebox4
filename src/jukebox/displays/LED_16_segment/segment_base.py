import logging
from busio import I2C
import board
from adafruit_ht16k33 import segments
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

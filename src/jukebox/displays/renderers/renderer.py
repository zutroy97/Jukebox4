from jukebox.displays.common.display_base import DisplayBase
from busio import I2C
import board
from adafruit_ht16k33 import segments

class Renderer:
    def DrawFrame(self, header: str, value: str, display: DisplayBase):
        pass
    def clear(self):
        pass

class ConsoleRenderer(Renderer):
    def DrawFrame(self, header: str, value: str, display: DisplayBase):
        self.clear()
        print(f"{header}:")
        print('-' * display.max_text_width)
        print(f"{value}")

    def clear(self):
        print("\033[H\033[2J", end="")  # Clear console

class Led14SegmentX14Renderer(Renderer):
    def __init__(self) -> None:
        super().__init__()
        i2c = board.I2C()
        self._display8 = segments.Seg14x4(i2c, address=(0x70, 0x71))  # uses board.SCL and board.SDA
        self._display12 = segments.Seg14x4(i2c, address=(0x72, 0x73, 0x74))
        self._display8.brightness = 0.20
        self._display12.brightness = 0.20

    def DrawFrame(self, header: str, value: str, display: DisplayBase):
        self._display8.print(f"{header:<8}")
        self._display12.print(f"{value:<12}")

    def clear(self):
        self._display8.fill(0)
        self._display12.fill(0)
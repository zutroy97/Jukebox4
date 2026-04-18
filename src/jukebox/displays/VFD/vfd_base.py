import asyncio

from jukebox.displays.common.display_base import DisplayBase

import logging
import serial

class VFDBase(DisplayBase):
    def __init__(
            self, 
            **kwargs) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        port = kwargs.get('port', '/dev/serial0')
        baud = int(kwargs.get('baud', 9600))
        self._ser = serial.Serial(port, baudrate=baud, timeout=1)
        self._last_write = None
        self._running = True
        self.set_brightness(0) # set brightness to 0 on startup to prevent display burn-in when not in use
    
    async def clear_screen(self) -> None:
        self._ser.write(b'\x1e') # clear screen

    def set_brightness(self, brightness: int) -> None:
        # brightness should be between 0 and 255
        brightness = max(0, min(255, brightness))
        self._ser.write(b'\x04' + bytes([brightness]))

    def set_position(self, column: int, row: int) -> None:
        # x should be between 0 and 19, y should be between 0 and 1
        column = max(0, min(19, column))
        row = max(0, min(1, row))
        column = column + (row * 20)
        self._ser.write(b'\x10' + bytes([column]))

    def write_bytes(self, data: bytes) -> None:
        self._ser.write(data)

    def clear_to_eol(self) -> None:
        '''This command will clear out the display from the current write-in position to the
end of the current line. The current write-in position will not change. '''
        self._ser.write(b'\x18') # clear to end of line

    def normal_display_mode(self) -> None:
        '''After writing a character, the write-in is shifted automatically to the right one
position. When the write-in is in the last position of the first row, the write-in
moves to the first position of the second row. When the write-in is in the last
position of the second row, the write-in moves to the first position of the first row. '''
        self._ser.write(b'\x11') # normal display mode

    async def loop(self) -> None:
        while self._running:
            await asyncio.sleep(1.0)

from jukebox.displays.common.display_base import DisplayBase
from jukebox.displays.common.common_enums import DisplayStateMachineState
from jukebox.animators.slide import MultilineSlide

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
        self._logger.debug(f"Opening serial port {port} with baudrate {baud}")  
        self._ser = serial.Serial(port, baudrate=baud, timeout=1)
        self._last_write = None
    
    def clear_screen(self) -> None:
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

    def _updateDisplay(self) -> None:
        x = f"{self.artist}\n\r{self.title}"
        if x != self._last_write:
            self.clear_screen()
            self._ser.write(x.encode('ascii'))
            self._last_write = x

class VFDSimple(VFDBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._stateArtist = DisplayStateMachineState.IDLE
        self._stateTitle = DisplayStateMachineState.IDLE
        self._title_anim = MultilineSlide(text="No title set"
                      , max_text_width=20
                      , delay_between_lines=500)
        self._artist_anim = MultilineSlide(text="No artist set"
                      , max_text_width=20
                      , delay_between_lines=500)
        self._bufferTitle : str = ''
        self._bufferArtist : str = ''
        self.normal_display_mode()

    def _updateDisplay(self) -> None:
        if self._stateArtist in (DisplayStateMachineState.TEXT_UPDATED, DisplayStateMachineState.INIT):
            self._logger.debug(f"_stateArtist: {self._stateArtist} : {self.artist}")
            self._artist_anim = MultilineSlide(text=self.artist
                      , max_text_width=20
                      , delay_between_lines=250)
            self._stateArtist = DisplayStateMachineState.ANIMATING
        
        if self._stateTitle in (DisplayStateMachineState.TEXT_UPDATED, DisplayStateMachineState.INIT):
            self._logger.debug(f"_stateTitle: {self._stateTitle} : {self.title}")
            self._title_anim = MultilineSlide(text=self.title
                      , max_text_width=20
                      , delay_between_lines=250)
            self._stateTitle = DisplayStateMachineState.ANIMATING

        if self._artist_anim.is_finished:
            if self._bufferArtist.strip() != self.artist:
                self._logger.debug(f"Artist animation finished but bufferArtist '{self._bufferArtist}' != artist '{self.artist}'")
                self._artist_anim.reset()
            else:
                self._stateArtist = DisplayStateMachineState.IDLE
        
        if self._stateArtist != DisplayStateMachineState.IDLE:
            this_screen_artist = self._artist_anim.next()
            if this_screen_artist != self._bufferArtist:
                self._logger.debug(f"this_screen_artist: {this_screen_artist}")
                self.set_position(0, 0)
                self._ser.write(this_screen_artist.encode('ascii'))
                #self.clear_to_eol()
                self._bufferArtist = this_screen_artist 
        
        if self._title_anim.is_finished:
            if self._bufferTitle.strip() != self.title:
                self._logger.debug(f"Title animation finished but bufferTitle '{self._bufferTitle}' != title '{self.title}'")
                self._title_anim.reset()
            else:
                self._stateTitle = DisplayStateMachineState.IDLE

        if self._stateTitle != DisplayStateMachineState.IDLE:
            this_screen_title = self._title_anim.next()
            if this_screen_title != self._bufferTitle:
                self._logger.debug(f"this_screen_title: {this_screen_title}|")
                self.set_position(0, 1)
                self._ser.write(this_screen_title.encode('ascii'))
                #self.clear_to_eol()
                self._bufferTitle = this_screen_title

import asyncio

from jukebox.displays.common.display_base import DisplayBase
from jukebox.displays.common.common_enums import DisplayStateMachineState
#from jukebox.animators.slide import MultilineSlide

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
        #self._logger.debug(f"Opening serial port {port} with baudrate {baud}")  
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
        pass
        # x = f"{self.artist}\n\r{self.title}"
        # if x != self._last_write:
        #     self.clear_screen()
        #     self._ser.write(x.encode('ascii'))
        #     self._last_write = x

from datetime import datetime, timedelta
from jukebox.animators2.text.animation_chain import AnimationChain, AnimationChainLink
from jukebox.animators2.text.slide import Slide
from jukebox.animators2.text.animator_base import TextAnimatorBase
from jukebox.animators2.text.multiline_generator import MultiLineGenerator

class VFDSimple(VFDBase):
    async def on_title_line_displayed(self, anim: TextAnimatorBase) -> bool:
        #await asyncio.sleep(1) # wait for the line to be fully displayed before starting the timer
        self._next_title_update = datetime.now() + timedelta(seconds=2) # display each line for 5 seconds
        self._stateTitle = DisplayStateMachineState.DELAY_START
        self._logger.debug(f"{ self._stateTitle}, setting next update to {self._next_title_update} ")
        return True

    # async def on_artist_line_displayed(self, anim: TextAnimatorBase) -> bool:
    #     #await asyncio.sleep(1) # wait for the line to be fully displayed before starting the timer
    #     return True


    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._stateArtist = DisplayStateMachineState.IDLE
        self._stateTitle = DisplayStateMachineState.IDLE
        self.normal_display_mode()
        self._next_title_update : datetime = datetime.now() + timedelta(minutes=3600) # set to a time in the future to force an update on the first tick
        self._next_artist_update : datetime = datetime.now() + timedelta(minutes=3600)

        self._links_title_animation = [
            AnimationChainLink(MultiLineGenerator),
            AnimationChainLink(Slide, onFinished=self.on_title_line_displayed),
        ]
        self._title_anim = AnimationChain(links=self._links_title_animation, text='', max_text_width=20)

    async def loop(self) -> None:
        while self._running:
            #self._logger.debug(f"_stateTitle: {self._stateTitle} : {self.title}")
            if self._stateTitle in (DisplayStateMachineState.TEXT_UPDATED, DisplayStateMachineState.INIT):
                self._title_anim = AnimationChain(links=self._links_title_animation, text=self.title, max_text_width=20)
                await self._title_anim.Start()
                self._next_title_update = datetime.now()
                self._stateTitle = DisplayStateMachineState.ANIMATING

            if self._next_title_update < datetime.now():
                self._logger.debug(f"TICK: {self._stateTitle} : {self._next_title_update}")
                if self._stateTitle == DisplayStateMachineState.ANIMATING:
                    if (await self._title_anim.Next()):
                        # onFinished callback just changes the state to DELAY_START
                        if self._stateTitle == DisplayStateMachineState.DELAY_START:
                            pass
                        else:
                            self.set_position(0, 0)
                            text = await self._title_anim.GetText()
                            #self._logger.debug(f"Updating title line to: {text}")
                            self._ser.write(text.encode('ascii'))
                            self._next_title_update = datetime.now() + timedelta(milliseconds=100)
                    else:
                        if len(self.title) > self._title_anim.max_text_width:
                            await self._title_anim.Start() # restart the animation
                            self._next_title_update = datetime.now() + timedelta(seconds=1)
                            #self._running = False # stop the loop for testing purposes
                elif self._stateTitle == DisplayStateMachineState.DELAY_START:
                    self._stateTitle = DisplayStateMachineState.ANIMATING

            # if self._stateArtist in (DisplayStateMachineState.TEXT_UPDATED, DisplayStateMachineState.INIT):
            #     self._artist_anim = AnimationChain(links=self._links_artist_animation, text=self.artist, max_text_width=20)
            #     await self._artist_anim.Start()
            #     self._next_artist_update = datetime.now()
            #     self._stateArtist = DisplayStateMachineState.ANIMATING

            # if self._stateArtist == DisplayStateMachineState.DELAY_START:
            #     if self._next_artist_update < datetime.now():
            #         self._stateArtist = DisplayStateMachineState.ANIMATING

            # if self._next_artist_update < datetime.now() and self._stateArtist == DisplayStateMachineState.ANIMATING:
            #     if (await self._artist_anim.Next()):
            #         self.set_position(0, 1)
            #         self._ser.write((await self._artist_anim.GetText()).encode('ascii'))
            #         self._next_artist_update = datetime.now() + timedelta(milliseconds=100)
            #     else:
            #         await self._artist_anim.Start() # restart the animation
            #         self._next_artist_update = datetime.now() + timedelta(seconds=1)
            #         #self._running = False # stop the loop for testing purposes

            await asyncio.sleep(0.010)

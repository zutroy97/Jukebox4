# Testing
import logging
from busio import I2C
import board
from typing import Dict, List, Optional, Tuple, Union
import asyncio
from adafruit_ht16k33 import segments
from ctypes import c_uint64 as uint64 
from enum import Enum


class DrawStates(Enum):
    IDLE = 0
    ARTIST = 1
    TITLE = 2

class DisplayManager:
    def __init__(self, 
        i2c: I2C,
        addr_upper: Union[int, List[int], Tuple[int, ...]] = (0x70, 0x71),
        addr_lower: Union[int, List[int], Tuple[int, ...]] = (0x72, 0x73, 0x74)) -> None:
        
        self._run = True
        self._artist = ""
        self._title = ""
        self._display8 = segments.Seg14x4(i2c, address=addr_upper)  # uses board.SCL and board.SDA
        self._display12 = segments.Seg14x4(i2c, address=addr_lower)
        self._display8.brightness = 0.20
        self._display12.brightness = 0.20
        self._timer = uint64(0)
        self._stateArtist : DisplayStates = DisplayStates.EMPTY
        self._stateTitle : DisplayStates = DisplayStates.EMPTY 
        self._logger = logging.getLogger(__name__)
        self._stateDraw : DrawStates = DrawStates.IDLE
        
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, title: str) -> None:
        if title.strip() != self._title:
            self._title = title.strip()
            self._stateTitle = DisplayStates.TEXT_UPDATED
    
    @property
    def artist(self) -> str:
        return self._artist
    
    @artist.setter
    def artist(self, artist: str) -> None:
        if artist.strip() != self._artist:
            self._artist = artist.strip()
            self._stateArtist = DisplayStates.TEXT_UPDATED

    def __del__(self):
        self._run = False

    def stop(self) -> None:
        self._run = False

    def start(self) -> None:
        self._run = True

    def _drawArtist(self) -> DisplayStates: # returns true when fully drawn (text scrolled/fully displayed)
        if self._stateArtist == DisplayStates.INIT or self._stateArtist == DisplayStates.TEXT_UPDATED:
            self._display8.fill(0)
            if self._artist == "":
                # No artist to display, Nothing to do
                self._stateArtist = DisplayStates.EMPTY
                return DisplayStates.EMPTY
            x = 'Artist'
            self._display8.print(f"{x:<8}")
            self._stateArtist = DisplayStates.LOOP
            self._display12.fill(0)
            self._display12.print(f"{self._artist:<12}")
            return DisplayStates.FINISHED
        if self._stateArtist == DisplayStates.EMPTY:
            self.clear()
            self._stateArtist = DisplayStates.LOOP
            return DisplayStates.FINISHED
        return DisplayStates.FINISHED
        
    def _drawTitle(self) -> DisplayStates:
        if self._stateTitle == DisplayStates.INIT or self._stateTitle == DisplayStates.TEXT_UPDATED:
            self._display8.fill(0)
            if self._title == "":
                # No title to display, Nothing to do
                self._stateTitle = DisplayStates.EMPTY
                return DisplayStates.EMPTY
            x = 'Title'
            self._display8.print(f"{x:<8}")
            self._display12.fill(0)
            self._display12.print(f"{self._title:<12}")
            self._stateTitle = DisplayStates.LOOP
            return DisplayStates.FINISHED
        if self._stateTitle == DisplayStates.EMPTY:
            self.clear()
            self._stateTitle = DisplayStates.LOOP
            return DisplayStates.FINISHED
        if self._stateTitle == DisplayStates.LOOP:
            return DisplayStates.FINISHED
        return DisplayStates.FINISHED
    
    async def draw(self) -> None:
        # Placeholder for any drawing logic if needed in future
        pass

    def clear(self) -> None:
        self._display8.fill(0)
        self._display12.fill(0)

    async def loop(self) -> None:
        currentDraw = DrawStates.ARTIST
        nextDisplayTime = 0 
        while self._run:
            if self._timer.value >= nextDisplayTime:
                if currentDraw == DrawStates.ARTIST:
                    self._logger.debug("Switching display to Title")
                    currentDraw = DrawStates.TITLE
                    self._stateTitle = DisplayStates.INIT
                elif currentDraw == DrawStates.TITLE:
                    self._logger.debug("Switching display to Artist")
                    currentDraw = DrawStates.ARTIST
                    self._stateArtist = DisplayStates.INIT
                nextDisplayTime = self._timer.value + 200
            if currentDraw == DrawStates.TITLE:
                ds = self._drawTitle()
            elif currentDraw == DrawStates.ARTIST:
                ds = self._drawArtist()
            else:
                self._logger.error("DisplayManager loop in unknown Draw State")
                ds = DisplayStates.IDLE
            if ds == DisplayStates.FINISHED:
                pass
            await asyncio.sleep(.010)
            self._timer.value += 1
            #print("LED_16_segment Plain Display Looping")

    
async def main():
    display = DisplayManager(i2c=board.I2C(), addr_upper=(0x70, 0x71), addr_lower=(0x72, 0x73, 0x74))
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            #task_exercise("display1", display)
            display.loop()
        )
        taskStop = tg.create_task(
            wait_and_stop(display, 6)
        )
async def wait_and_stop(display: DisplayManager, delay: float) -> None:
    display.artist = "Nirvana"
    display.title = "Smells Like Teen Spirit"
    await asyncio.sleep(delay)
    display.artist = "Guns n Roses"
    display.title = "November Rain"
    await asyncio.sleep(delay)
    display.artist = "Kiss"
    display.title = "Rock and Roll All Nite"
    await asyncio.sleep(delay)
    display.artist = "John Willams"
    display.title = "Star Wars Theme"
    await asyncio.sleep(delay)  
    display.clear() 
    display.stop()

async def test():
    display = DisplayManager(i2c=board.I2C(), addr_upper=(0x70, 0x71), addr_lower=(0x72, 0x73, 0x74))
    display.artist = "Test"
    display._display8.print("1234")
    display._display12.print("123456")
    await asyncio.sleep(2)
    display._display8.print("Natalie ")
    display._display12.print("SIMON       ")
    # display._display12.marquee("Hello World! This is a test of the 16-segment display. ", delay=0.3, loop=3)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
    #asyncio.run(test())

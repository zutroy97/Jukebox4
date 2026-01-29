from busio import I2C
import board
from typing import Dict, List, Optional, Tuple, Union
import asyncio
from adafruit_ht16k33 import segments
from ctypes import c_uint32 as uint32 
from enum import Enum

class ArtistStates(Enum):
    IDLE = 0
    INIT = 1
    LOOP = 2
    TEXT_UPDATED = 3 
    BEGIN_ANIMATION = 4

class Plain:
    def __init__(self, 
        i2c: I2C,
        addr_upper: Union[int, List[int], Tuple[int, ...]] = (0x70, 0x71),
        addr_lower: Union[int, List[int], Tuple[int, ...]] = (0x72, 0x73, 0x74)) -> None:
        
        # self._i2c = i2c
        # self._addr_upper = addr_upper
        # self._addr_lower = addr_lower
        self._run = True
        self._artist = ""
        self._title = ""
        self._display8 = segments.Seg14x4(i2c, address=addr_upper)  # uses board.SCL and board.SDA
        self._display12 = segments.Seg14x4(i2c, address=addr_lower)
        self._display8.brightness = 0.20
        self._display12.brightness = 0.20
        self._timer = uint32(0)
        self._stateArtist : ArtistStates = ArtistStates.IDLE 
        
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, title: str) -> None:
        if title != self._title:
            self._title = title
            #print(f"Title set to: '{self._title}' {len(self._title)}")
            #self._display12.print(self._title)
    
    @property
    def artist(self) -> str:
        return self._artist
    
    @artist.setter
    def artist(self, artist: str) -> None:
        if artist.strip() != self._artist:
            self._artist = artist
            self._stateArtist = ArtistStates.TEXT_UPDATED
            #print(f"Artist set to: '{self._artist}' {len(self._artist)}") 
            #self._display8.print(self._artist)

    def __del__(self):
        self._run = False

    def stop(self) -> None:
        self._run = False

    def start(self) -> None:
        self._run = True

    def _drawArtist(self) -> bool: # returns true when fully drawn
        if self._stateArtist == ArtistStates.INIT:
            self._display8.fill(0)
            x = 'Artist'
            self._display8.print(f"{x:<8}")
            self._stateArtist = ArtistStates.LOOP
            return False
        if self._stateArtist == ArtistStates.TEXT_UPDATED:
            print(f"Artist text updated to '{self._artist}'")
            self._display12.fill(0)
            self._display12.print(f"{self._artist:<12}")
            self._stateArtist = ArtistStates.LOOP
            return False
        if self._stateArtist == ArtistStates.LOOP:
            pass
        
    async def draw(self) -> None:
        # Placeholder for any drawing logic if needed in future
        pass

    def clear(self) -> None:
        self._display8.fill(0)
        self._display12.fill(0)

    async def loop(self) -> None:
        self._stateArtist = ArtistStates.INIT
        while self._run:
            self._timer.value += 1
            self._drawArtist()
            await asyncio.sleep(.015)
            #print("LED_16_segment Plain Display Looping")

    
async def main():
    display = Plain(i2c=board.I2C(), addr_upper=(0x70, 0x71), addr_lower=(0x72, 0x73, 0x74))
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            #task_exercise("display1", display)
            display.loop()
        )
        taskStop = tg.create_task(
            wait_and_stop(display, 5)
        )
async def wait_and_stop(display: Plain, delay: float) -> None:
    display.artist = "Nirvana"
    await asyncio.sleep(delay)
    display.artist = "Guns n Roses"
    #display.title = "November Rain"
    await asyncio.sleep(delay)
    display.artist = "Kiss"
    await asyncio.sleep(delay)
    display.artist = "John Willams"
    #display.title = "Rock and Roll All Nite (and Party Every Day)"
    await asyncio.sleep(delay)  
    display.clear() 
    display.stop()

async def test():
    display = Plain(i2c=board.I2C(), addr_upper=(0x70, 0x71), addr_lower=(0x72, 0x73, 0x74))
    display.artist = "Test"
    display._display8.print("1234")
    display._display12.print("123456")
    await asyncio.sleep(2)
    display._display8.print("Natalie ")
    display._display12.print("SIMON       ")
    # display._display12.marquee("Hello World! This is a test of the 16-segment display. ", delay=0.3, loop=3)


if __name__ == "__main__":
    asyncio.run(main())
    #asyncio.run(test())

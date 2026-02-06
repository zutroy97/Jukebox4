import logging
from jukebox.coordinator.display_coordinator import DisplayCoordinator
#from jukebox.displays.console.console_simple_display import SimpleConsoleDisplay
from jukebox.displays.console.console_scrolling_width import ConsoleScrollingWidth
from jukebox.displays.console.console_left_building import ConsoleLeftBuilding
from jukebox.displays.console.random_width_fill import RandomTypewriter

from busio import I2C
import board
from typing import Dict, List, Optional, Tuple, Union
import asyncio
from adafruit_ht16k33 import segments

import asyncio

async def wait_and_stop(coor: DisplayCoordinator, delay: float) -> None:
    coor.artist = "Nirvana"
    coor.title = "Smells Like Teen Spirit"
    await asyncio.sleep(delay)
    coor.artist = "Guns 'n Roses"
    coor.title = "November Rain"
    await asyncio.sleep(delay)
    coor.artist = "Kiss"
    coor.title = "Rock and Roll All Nite"
    await asyncio.sleep(delay)
    coor.artist = "John Willams"
    coor.title = "Star Wars Theme"
    await asyncio.sleep(delay)  
    coor.Die()

def ConsoleDrawFrame(rtm: RandomTypewriter, wait_ticks : int):
        animated_text = rtm._animator.next()
        print("\033[H\033[2J", end="")  # Clear console
        print(f"{rtm._header}:")
        print('-' * rtm._max_text_width)
        print(animated_text)
        rtm._drawTextNextTick.value = rtm._ticks.value + wait_ticks # wait this many clicks before scrolling the line
        
def LedDrawFrame(rtm: RandomTypewriter, wait_ticks : int):
     animated_text = rtm._animator.next()
     _display8.print(f"{rtm._header:<8}")
     _display12.print(f"{animated_text:<12}")
     rtm._drawTextNextTick.value = rtm._ticks.value + wait_ticks # wait this many clicks before scrolling the line

i2c = board.I2C()
_display8 = segments.Seg14x4(i2c, address=(0x70, 0x71))  # uses board.SCL and board.SDA
_display12 = segments.Seg14x4(i2c, address=(0x72, 0x73, 0x74))
_display8.brightness = 0.20
_display12.brightness = 0.20

async def main():
    logging.basicConfig(level=logging.DEBUG)

    subject = DisplayCoordinator()
    # consoleScrollWidth = ConsoleScrollingWidth(scroll_width=12)
    # subject.add_observer(consoleScrollWidth)
    # console = SimpleConsoleDisplay()
    # subject.add_observer(console)
    # consoleLeftBuild = ConsoleLeftBuilding()
    # subject.add_observer(consoleLeftBuild)
    randomWidthFill = RandomTypewriter(max_text_width=12)
    randomWidthFill.SetDelegation(LedDrawFrame)
    subject.add_observer(randomWidthFill)
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            #task_exercise("display1", display)
            #consoleScrollWidth.loop()
            #consoleLeftBuild.loop()
            randomWidthFill.loop()
        )
        # task2 = tg.create_task(
        #     console.loop()
        # )
        taskStop = tg.create_task(
            wait_and_stop(subject, 10)   
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())

import logging
from jukebox.coordinator.display_coordinator import DisplayCoordinator

# from busio import I2C
# import board
# from adafruit_ht16k33 import segments

#from typing import Dict, List, Optional, Tuple, Union
import asyncio

from jukebox.displays.console.random_typewriter import RandomTypewriter as ConsoleRandomTypewriter
from jukebox.displays.console.simple import Simple as ConsoleSimple

async def wait_and_stop(coor: DisplayCoordinator, delay: float) -> None:
    coor.song_artist = "Nirvana"
    coor.song_title = "Smells Like Teen Spirit"
    await asyncio.sleep(delay)

    coor.song_artist = "Guns 'n Roses"
    coor.song_title = "November Rain"
    await asyncio.sleep(delay)

    coor.song_artist = "Kiss"
    coor.song_title = "Rock and Roll All Nite"
    await asyncio.sleep(delay)

    coor.song_artist = "John Willams"
    coor.song_title = "Star Wars Theme"
    await asyncio.sleep(delay)  
    coor.Die()

async def main():
    logging.basicConfig(level=logging.DEBUG)

    subject = DisplayCoordinator()
    display = ConsoleRandomTypewriter(max_text_width=12)
    #display = ConsoleSimple(max_text_width=12)
    subject.add_observer(display)
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            subject.loop()
        )
        taskStop = tg.create_task(
            wait_and_stop(subject, 10)   
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())

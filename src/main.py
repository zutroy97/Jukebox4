import logging
from jukebox.coordinator.display_coordinator import DisplayCoordinator
from jukebox.displays.console.simple_console_display import SimpleConsoleDisplay
from jukebox.displays.console.console_scrolling_width import ConsoleScrollingWidth

import asyncio

async def wait_and_stop(coor: DisplayCoordinator, delay: float) -> None:
    coor.artist = "Nirvana"
    coor.title = "Smells Like Teen Spirit"
    await asyncio.sleep(delay)
    coor.artist = "Guns n Roses"
    coor.title = "November Rain"
    await asyncio.sleep(delay)
    coor.artist = "Kiss"
    coor.title = "Rock and Roll All Nite"
    await asyncio.sleep(delay)
    coor.artist = "John Willams"
    coor.title = "Star Wars Theme"
    await asyncio.sleep(delay)  
    coor.Die()

async def main():
    logging.basicConfig(level=logging.DEBUG)
    subject = DisplayCoordinator()
    consoleScrollWidth = ConsoleScrollingWidth(scroll_width=12)
    subject.add_observer(consoleScrollWidth)
    # console = SimpleConsoleDisplay()
    # subject.add_observer(console)
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            #task_exercise("display1", display)
            consoleScrollWidth.loop()
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

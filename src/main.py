import logging
from jukebox.coordinator.display_coordinator import DisplayCoordinator
from jukebox.displays.example_display import ExampleDisplay, ConsoleCursesDisplay

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
    # example = ExampleDisplay()
    # subject.add_observer(example)
    console = ConsoleCursesDisplay()
    subject.add_observer(console)
    async with asyncio.TaskGroup() as tg:
        # task1 = tg.create_task(
        #     #task_exercise("display1", display)
        #     example.loop()
        # )
        task2 = tg.create_task(
            console.loop()
        )
        taskStop = tg.create_task(
            wait_and_stop(subject, 6)   
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())

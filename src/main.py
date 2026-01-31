import logging
from jukebox.coordinator.display_coordinator import DisplayCoordinator
from jukebox.displays.example_display import ExampleDisplay

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    subject = DisplayCoordinator()
    example = ExampleDisplay()
    subject.add_observer(example)

    # subject.title = "New Song Title"
    # subject.artist = "New Artist Name"
    # subject.notify_observers("Manual notification without event")
    asyncio.run(wait_and_stop(subject, 2))


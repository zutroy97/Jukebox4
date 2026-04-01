import logging
from jukebox.coordinator.display_coordinator import DisplayCoordinator

# from busio import I2C
# import board
import asyncio

#from jukebox.displays.console.random_typewriter import RandomTypewriter as ConsoleRandomTypewriter
from jukebox.displays.LED_16_segment.segment_alien_intro_active_segment_only_display import SegmentAlienIntroActiveSegmentOnlyDisplay
from jukebox.displays.LED_16_segment.segment_simple import SegmentSimple
from jukebox.displays.VFD.vfd_base import VFDBase, VFDSimple
from jukebox.displays.console.random_typewriter import DisplayConsoleRandomTypewriter
from jukebox.displays.console.simple import Simple as ConsoleSimple
from jukebox.displays.LED_16_segment.segment_scroller import SegmentScroller    

subject = DisplayCoordinator()

display = SegmentAlienIntroActiveSegmentOnlyDisplay(segment_delay_ticks=5)
subject.add_observer(display)

vfd_display = VFDSimple(port='/dev/serial0', baud=9600)
subject.add_observer(vfd_display)

async def wait_and_stop(coor: DisplayCoordinator, delay: float) -> None:
    global display
    coor.song_artist = "Nirvana"
    coor.song_title = "Smells Like Teen Spirit"
    await asyncio.sleep(delay)

    # subject.remove_observer(display)
    # display = SegmentScroller()
    # subject.add_observer(display)
    coor.song_artist = "Guns 'n Roses"
    coor.song_title = "November Rain"
    await asyncio.sleep(delay)

    # subject.remove_observer(display)
    # display = SegmentSimple()
    # subject.add_observer(display)
    coor.song_artist = "Kiss"
    coor.song_title = "Rock and Roll All Nite"
    await asyncio.sleep(delay)

    coor.song_artist = "John Willams"
    coor.song_title = "Star Wars Theme"
    await asyncio.sleep(delay)  
    coor.Die()

async def main():
    logging.basicConfig(level=logging.DEBUG)

    
    #display = DisplayConsoleRandomTypewriter(max_text_width=12)
    #display = SegmentSimple()
    #display = SegmentScroller()
    #display = ConsoleSimple(max_text_width=12)
    
    
    #subject.add_observer(led_display)
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

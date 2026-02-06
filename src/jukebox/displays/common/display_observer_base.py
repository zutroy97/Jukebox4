from jukebox.coordinator.change_events import ChangeEvents
import asyncio
from ctypes import c_uint64 as uint64 

class DisplayObserverBase:
    def __init__(self) -> None:
        self._title :str = ""
        self._artist: str  = ""
        self._running : bool = False
        self._ticks : uint64 = uint64(0)
    
    async def draw(self) -> None:
        pass
    
    def title_updated(self) -> None:
        pass
    def artist_updated(self) -> None:
        pass

    def __del__(self):
        pass # subclasses to define

    async def loop(self) -> None:
        while self._running:
            await self.draw()
            await asyncio.sleep(0.001)
            self._ticks.value += 1

    def update(self, observable, *args, **kwargs):
        if 'event' in kwargs:
            event = kwargs['event']
            value = kwargs.get('value', '')
            if event == ChangeEvents.DIE:
                self._running = False
            elif event == ChangeEvents.TITLE_CHANGED:
                self._title = value
                self.title_updated()
            elif event == ChangeEvents.ARTIST_CHANGED:
                self._artist = value
                self.artist_updated()
import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.displays.common.display_base import DisplayBase
import asyncio
from ctypes import c_uint64 as uint64 

class DisplayCoordinator:
    def __init__(self):
        self.observers = []
        self._title = ""
        self._artist = ""
        self._logger = logging.getLogger(__class__.__name__)
        self._running = True

    def add_observer(self, observer: DisplayBase):
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer: DisplayBase):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self, **kwargs):
        for observer in self.observers:
            observer.update(**kwargs)

    async def loop(self) -> None:
        self._running = True
        while self._running:
            await asyncio.sleep(0.010)
            self.notify_observers(event=ChangeEvents.TICK)

    @property
    def song_title(self) -> str:
        return self._title
    
    @song_title.setter
    def song_title(self, title: str) -> None:
        if title.strip() != self._title:
            self._title = title.strip()
            self._logger.debug(f"Title updated to: {self._title}")
            self.notify_observers(event=ChangeEvents.SONG_TITLE_CHANGED, value=self._title)
    
    @property
    def song_artist(self) -> str:
        return self._artist
    
    @song_artist.setter
    def song_artist(self, artist: str) -> None:
        if artist.strip() != self._artist:
            self._artist = artist.strip()
            self.notify_observers(event=ChangeEvents.SONG_ARTIST_CHANGED, value=self._artist)

    def Die(self):
        self.notify_observers(event=ChangeEvents.DIE, value=self._artist)
        self._running = False










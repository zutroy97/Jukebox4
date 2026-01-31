import logging
from jukebox.coordinator.change_events import ChangeEvents
import asyncio

class DisplayCoordinator:
    def __init__(self):
        self.observers = []
        self._title = ""
        self._artist = ""
        self._logger = logging.getLogger(__class__.__name__)

    def add_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(self, *args, **kwargs)

    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, title: str) -> None:
        if title.strip() != self._title:
            self._title = title.strip()
            self.notify_observers("Title changed", event=ChangeEvents.TITLE_CHANGED, value=self._title)
    
    @property
    def artist(self) -> str:
        return self._artist
    
    @artist.setter
    def artist(self, artist: str) -> None:
        if artist.strip() != self._artist:
            self._artist = artist.strip()
            self.notify_observers("Artist changed", event=ChangeEvents.ARTIST_CHANGED, value=self._artist)

    def Die(self):
        self.notify_observers("Die", event=ChangeEvents.DIE, value=self._artist)

class DisplayObserver:
    def __init__(self) -> None:
        self._title = ""
        self._artist = ""
        self._running = False
    
    async def draw(self) -> None:
        pass
    
    def title_updated(self) -> None:
        pass
    def artist_updated(self) -> None:
        pass

    async def loop(self) -> None:
        while self._running:
            await self.draw()
            await asyncio.sleep(0.010)

    def update(self, observable, *args, **kwargs):
        if 'event' in kwargs:
            event = kwargs['event']
            if event == ChangeEvents.DIE:
                self._running = False
            elif event == ChangeEvents.TITLE_CHANGED:
                self._title = kwargs.get('value')
                self.title_updated()
            elif event == ChangeEvents.ARTIST_CHANGED:
                self._artist = kwargs.get('value')
                self.artist_updated()








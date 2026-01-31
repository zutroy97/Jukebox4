import logging
from jukebox.coordinator.change_events import ChangeEvents

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


class DisplayObserver:
    def update(self, observable, *args, **kwargs):
        pass  # Implement specific update logic here




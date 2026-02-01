import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.displays.display_observer_base import DisplayObserverBase

class SimpleConsoleDisplay(DisplayObserverBase):
    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        self._running = True

    def title_updated(self) -> None:
        self._logger.info(f"Title updated to: {self._title}")
    def artist_updated(self) -> None:
        self._logger.info(f"Artist updated to: {self._artist}")
    
    async def draw(self) -> None:
        pass
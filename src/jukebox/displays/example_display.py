import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.coordinator.display_coordinator import DisplayObserver
import asyncio

class ExampleDisplay(DisplayObserver):
    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        self._running = True

    def title_updated(self) -> None:
        self._logger.info(f"Title updated to: {self._title}")
    def artist_updated(self) -> None:
        self._logger.info(f"Artist updated to: {self._artist}")
    
    async def draw(self) -> None:
        while self._running:
            if self._artist:
                self._logger.debug(f"Artist: {self._artist}")
            await asyncio.sleep(2)
            if self._title:
                self._logger.debug(f"Title: {self._title}")
            await asyncio.sleep(2)

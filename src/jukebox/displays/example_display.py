import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.coordinator.display_coordinator import DisplayObserver
import asyncio
from enum import Enum
import curses
from ctypes import c_uint64 as uint64 

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
        pass

class ConsoleCursesDisplay(DisplayObserver):
    class StringAnimator:
        def __init__(self, text: str, width: int = 20) -> None:
            self.text = text
            self.position = 0
            self.width = width

        def next(self) -> str:
            if len(self.text) <= self.width:
                return self.text.ljust(self.width)
            display_text = self.text[self.position:self.position + self.width]
            self.position = (self.position + 1) % len(self.text)
            return display_text.ljust(self.width)
    
    class State(Enum):
        IDLE = 0
        """Not doing anything."""
        INIT = 1
        """Initializing display with new text."""
        LOOP = 2
        """Main loop for display updates."""
        TEXT_UPDATED = 3 
        """Text has been updated and needs to be redrawn."""
        BEGIN_ANIMATION = 4
        """Start any animations."""
        EMPTY = 5
        """No text to display."""
        FINISHED = 6
        """Finished displaying text (and any animation)."""
    class DisplayState(Enum):
        IDLE = 0
        """Not doing anything."""
        DRAWING_ARTIST = 1
        """Drawing artist text."""
        DRAWING_TITLE = 2
        """Drawing title text."""
    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        self._running = True
        self._stateArtist = self.State.IDLE
        self._stateTitle = self.State.IDLE
        # self._stdscr = curses.initscr()
        # self._stdscr.clear()
        self._alarmTicks = uint64(0)
        self._displayState = self.DisplayState.DRAWING_ARTIST
        self._animator = self.StringAnimator('')

    def title_updated(self) -> None:
        #self._logger.debug(f"Title updated to: {self._title}")
        self._stateTitle = self.State.TEXT_UPDATED
    def artist_updated(self) -> None:
        #self._logger.debug(f"Artist updated to: {self._artist}")
        self._stateArtist = self.State.TEXT_UPDATED
    
    async def draw(self) -> None:
        #self._logger.debug(f"Ticks: {self._ticks.value} AlarmTicks: {self._alarmTicks.value}")
        if (self._ticks.value > self._alarmTicks.value):
            self._alarmTicks.value = self._ticks.value + 200
            if self._displayState == self.DisplayState.DRAWING_ARTIST:
                self._displayState = self.DisplayState.DRAWING_TITLE
                self._stateArtist = self.State.INIT
            else:
                self._displayState = self.DisplayState.DRAWING_TITLE
                self._displayState = self.DisplayState.DRAWING_ARTIST
                self._stateTitle = self.State.INIT

        if self._displayState == self.DisplayState.DRAWING_ARTIST:
            self._stateArtist = self._drawText("Artist", self._artist, self._stateArtist)
            
        elif self._displayState == self.DisplayState.DRAWING_TITLE:
            self._stateTitle = self._drawText("Title", self._title, self._stateTitle)
            pass

    def _drawText(self, header: str, text: str, state: State) -> State: # returns true when fully drawn (text scrolled/fully displayed)
        if state == self.State.INIT or state == self.State.TEXT_UPDATED:
            if text == "":
                # No artist to display, Nothing to do
                return self.State.EMPTY
            self._animator = self.StringAnimator(f"{header}: {text}", width=10)
            self.__drawTextNextTick = uint64(self._ticks.value + 10)
            return self.State.LOOP
        elif state == self.State.EMPTY:
            return self.State.FINISHED
        elif state == self.State.FINISHED:
            state = self.State.IDLE
        elif state == self.State.LOOP:
            if (self._ticks.value > self.__drawTextNextTick.value):
                self.__drawTextNextTick.value = self._ticks.value + 10
                animated_text = self._animator.next()
                print("\033[H\033[2J", end="")  # Clear console
                print(animated_text)
        return self.State.LOOP

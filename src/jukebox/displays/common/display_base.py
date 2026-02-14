import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.displays.common.common_enums import  DisplayStateMachineState, DisplayInfoState, DisplayInfoTypes
from abc import ABC, abstractmethod
from ctypes import c_uint64 as uint64 
from jukebox.animators.random_typewriter import RandomTypeWriter

class DisplayBase(ABC):
    def __init__(self, **kwargs ) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        self._stateArtist = DisplayStateMachineState.IDLE
        self._stateTitle = DisplayStateMachineState.IDLE
        self._alarmTicks = uint64(0)
        self._displayState = DisplayInfoState.DRAWING_ARTIST
        self._minDwellTicks =kwargs.get('max_dwell_ticks', 5000)
        '''Maximum time in ms to display a screen.'''
        self._moveNextDisplayStart : bool = False
        self._title :str = ""
        self._artist: str  = ""
        self._running : bool = False
        self._ticks : uint64 = uint64(0)
        self._max_text_width = kwargs.get('max_text_width',80)
        self.max_widths = {}
        self.max_widths[DisplayInfoTypes.SONG_TITLE] = kwargs.get('max_song_title_width',80)
        self.max_widths[DisplayInfoTypes.SONG_ARTIST] = kwargs.get('max_song_artist_width',80)
        #self._song_artist_animator : Animator 

    @property
    def max_text_width(self) -> int:
        return self._max_text_width

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def artist(self) -> str:
        return self._artist
    
    # def set_song_artist_animator(self, ani : Animator) -> None:
    #     self._stateArtist = DisplayStateMachineState.INIT
    #     self._song_artist_animator = ani
    
    def song_title_updated(self) -> None:
        self._alarmTicks.value = self._ticks.value + self._minDwellTicks
        self._stateTitle = DisplayStateMachineState.TEXT_UPDATED
    def song_artist_updated(self) -> None:
        self._alarmTicks.value = self._ticks.value + self._minDwellTicks
        self._stateArtist = DisplayStateMachineState.TEXT_UPDATED

    def update(self, **kwargs):
        '''Receives updates from the DisplayCoordinator. Subclasses can override this method to handle specific events.'''
        if 'event' in kwargs:
            event = kwargs.get('event', ChangeEvents.UNKOWN)
            value = kwargs.get('value', '')
            #self._logger.debug(f"Received update from observable. Event: {event} Value: {value}")
            if event == ChangeEvents.DIE:
                self._running = False
            elif event == ChangeEvents.SONG_TITLE_CHANGED:
                self._title = value
                self.song_title_updated()
            elif event == ChangeEvents.SONG_ARTIST_CHANGED:
                self._artist = value
                self.song_artist_updated()
            elif event == ChangeEvents.TICK:
                self._ticks.value += 10
                self._refresh()

    def __del__(self):
        pass

    def _refresh(self) -> None:
        #self._logger.debug(f"Ticks: {self._ticks.value} AlarmTicks: {self._alarmTicks.value}")
        if (self._ticks.value >= self._alarmTicks.value or self._moveNextDisplayStart == True):
            self._alarmTicks.value = self._ticks.value + self._minDwellTicks
            self._moveNextDisplayStart = False
            if self._displayState == DisplayInfoState.DRAWING_ARTIST:
                self._displayState = DisplayInfoState.DRAWING_TITLE
                self._stateArtist = DisplayStateMachineState.INIT
            else:
                self._displayState = DisplayInfoState.DRAWING_TITLE
                self._displayState = DisplayInfoState.DRAWING_ARTIST
                self._stateTitle = DisplayStateMachineState.INIT

        self._updateDisplay()

        if self._displayState == DisplayInfoState.DRAWING_ARTIST:
            if self._stateArtist == DisplayStateMachineState.FINISHED:
                self._moveNextDisplayStart = True
        elif self._displayState == DisplayInfoState.DRAWING_TITLE:
            if self._stateTitle == DisplayStateMachineState.FINISHED:
                self._moveNextDisplayStart = True
        else:
            self._moveNextDisplayStart = True

    @abstractmethod
    # def _drawText(self, header: str, text: str, state: DisplayStateMachineState) -> DisplayStateMachineState:
    #     '''Subclasses should implement this method'''
    #     pass

    def _updateDisplay(self) -> None:
        '''Subclasses can implement this method to update the display with new text'''
        pass

class DisplaySimpleConsole(DisplayBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._lastArtist = ""
        self._lastTitle = ""

    def __del__(self):
        super().__del__()

    def clear_screen(self):
        print("\033[H\033[2J", end="")  # Clear console

    def _updateDisplay(self) -> None:
        if self._artist == self._lastArtist and self._title == self._lastTitle:
            return
        self._lastArtist = self._artist
        self._lastTitle = self._title
        self.clear_screen()
        print(f"Artist: {self._artist}")
        print("-" * self.max_widths[DisplayInfoTypes.SONG_TITLE])
        print(f"Title: {self._title}")


class DisplayConsoleRandomTypewriter(DisplayBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._artist_animator : RandomTypeWriter
        self._title_animator : RandomTypeWriter
        self._lastArtist = ""
        self._lastTitle = ""
        self._next_frame_ticks = uint64(self._ticks.value + 100)
    
    def clear_screen(self):
        print("\033[H\033[2J", end="")  # Clear console

    def _updateDisplay(self) -> None:
        if self._artist != self._lastArtist:
            self._artist_animator = RandomTypeWriter(self._artist, max_text_width=self.max_widths[DisplayInfoTypes.SONG_ARTIST])
            self._stateArtist = DisplayStateMachineState.ANIMATING
            self._lastArtist = self._artist
            self._next_frame_ticks = self._ticks # act immediately on artist change, don't wait for the next tick
        
        if self._title != self._lastTitle:
            self._title_animator = RandomTypeWriter(self._title, max_text_width=self.max_widths[DisplayInfoTypes.SONG_TITLE])
            self._stateTitle = DisplayStateMachineState.ANIMATING
            self._lastTitle = self._title
            self._next_frame_ticks = self._ticks # act immediately on artist change, don't wait for the next tick

        if self._ticks.value < self._next_frame_ticks.value:
            return
        self._next_frame_ticks = uint64(self._ticks.value + 100)
        self.clear_screen()

        if self._artist_animator is not None and self._stateArtist == DisplayStateMachineState.ANIMATING:
            print(f"Artist: {self._artist_animator.next()}")
            if self._artist_animator.is_finished:
                self._stateArtist = DisplayStateMachineState.FINISHED
        else:
            print(f"Artist: {self._artist}")
            self._stateArtist = DisplayStateMachineState.FINISHED

        print("-" * max(self.max_widths[DisplayInfoTypes.SONG_ARTIST], self.max_widths[DisplayInfoTypes.SONG_TITLE]))

        if self._title_animator is not None and self._stateTitle == DisplayStateMachineState.ANIMATING:
            print(f"Title: {self._title_animator.next()}")
            if self._title_animator.is_finished:
                self._stateTitle = DisplayStateMachineState.FINISHED
        else:
            print(f"Title: {self._title}")
            self._stateTitle = DisplayStateMachineState.FINISHED
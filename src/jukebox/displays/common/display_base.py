import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.displays.common.common_enums import  DisplayStateMachineState, DisplayInfoState
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
        '''Current time in ms, used for timing the display updates. Should be updated by the DisplayCoordinator on each tick.'''

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def artist(self) -> str:
        return self._artist
    
    def song_title_updated(self) -> None:
        #self._alarmTicks.value = self._ticks.value + self._minDwellTicks
        self._stateTitle = DisplayStateMachineState.TEXT_UPDATED
    def song_artist_updated(self) -> None:
        #self._alarmTicks.value = self._ticks.value + self._minDwellTicks
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
        # if (self._ticks.value >= self._alarmTicks.value or self._moveNextDisplayStart == True):
        #     self._alarmTicks.value = self._ticks.value + self._minDwellTicks
        #     self._moveNextDisplayStart = False
        #     if self._displayState == DisplayInfoState.DRAWING_ARTIST:
        #         self._displayState = DisplayInfoState.DRAWING_TITLE
        #         self._stateArtist = DisplayStateMachineState.INIT
        #     else:
        #         self._displayState = DisplayInfoState.DRAWING_TITLE
        #         self._displayState = DisplayInfoState.DRAWING_ARTIST
        #         self._stateTitle = DisplayStateMachineState.INIT

        self._updateDisplay()

        # if self._displayState == DisplayInfoState.DRAWING_ARTIST:
        #     if self._stateArtist == DisplayStateMachineState.FINISHED:
        #         self._moveNextDisplayStart = True
        # elif self._displayState == DisplayInfoState.DRAWING_TITLE:
        #     if self._stateTitle == DisplayStateMachineState.FINISHED:
        #         self._moveNextDisplayStart = True
        # else:
        #     self._moveNextDisplayStart = True

    @abstractmethod
    def _updateDisplay(self) -> None:
        '''Subclasses can implement this method to update the display with new text'''
        pass

class DisplaySimpleConsole(DisplayBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._max_text_width = kwargs.get('max_text_width', 80)
        self._lastArtist = ""
        self._lastTitle = ""

    def __del__(self):
        super().__del__()

    def clear_screen(self):
        print("\033[H\033[2J", end="")  # Clear console

    def _updateDisplay(self) -> None:
        if self.artist == self._lastArtist and self._title == self._lastTitle:
            return
        self._lastArtist = self.artist
        self._lastTitle = self._title
        self._drawConsole()

    def _drawConsole(self):
        self.clear_screen()
        print(f"Artist: {self.artist}")
        print("-" * self._max_text_width)
        print(f"Title: {self._title}")

class DisplayConsoleRandomTypewriter(DisplaySimpleConsole):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._update_every_ms = kwargs.get('update_every_ms', 100)
        self._segment_finished_delay_ms = kwargs.get('segment_finished_delay_ms', 2000)
        self._artist_animator : RandomTypeWriter
        self._title_animator : RandomTypeWriter
        self._next_frame_ticks_artist = uint64(self._ticks.value)
        self._next_frame_ticks_title = uint64(self._ticks.value)
        self._buffer_artist = ""
        self._buffer_title = ""
        self._stateArtist = DisplayStateMachineState.INIT
        self._stateTitle = DisplayStateMachineState.INIT

    def _updateDisplay(self) -> None:
        if self._stateArtist == DisplayStateMachineState.TEXT_UPDATED \
            or self._stateArtist == DisplayStateMachineState.INIT:
            self._artist_animator = RandomTypeWriter(self.artist, max_text_width=self._max_text_width)
            self._artist_animator.add_observer(self, target_name="artist")
            self._stateArtist = DisplayStateMachineState.ANIMATING
            self._next_frame_ticks_artist.value = self._ticks.value # act immediately on artist change, don't wait for the next tick
        
        if self._stateTitle == DisplayStateMachineState.TEXT_UPDATED \
            or self._stateTitle == DisplayStateMachineState.INIT:
            self._title_animator = RandomTypeWriter(self._title, max_text_width=self._max_text_width)
            self._title_animator.add_observer(self, target_name="title")
            self._stateTitle = DisplayStateMachineState.ANIMATING
            self._next_frame_ticks_title.value = self._ticks.value # act immediately on artist change, don't wait for the next tick

        self._drawConsole()

    def animation_update(self, **kwargs):
        #print(f"Received animation update from animator. Kwargs: {kwargs}")
        target_name = kwargs.get('target_name', '')
        if 'event' in kwargs:
            event = kwargs.get('event', '')
            if event == "segment_finished":
                #print(f"pre segment_finished: target_name: {target_name} _stateArtist: {self._stateArtist} _stateTitle: {self._stateTitle}")
                if target_name == "artist":
                    self._next_frame_ticks_artist.value = self._ticks.value + self._segment_finished_delay_ms
                    self._stateArtist = DisplayStateMachineState.DELAY_START
                elif target_name == "title":
                    self._next_frame_ticks_title.value = self._ticks.value + self._segment_finished_delay_ms
                    self._stateTitle = DisplayStateMachineState.DELAY_START
                #print(f"post segment_finished: target_name: {target_name} _stateArtist: {self._stateArtist} _stateTitle: {self._stateTitle}")

    def _drawConsole(self):
        
        #print(f"_stateArtist: {self._stateArtist} _stateTitle: {self._stateTitle}")
        screen_update : bool= False
        if self._buffer_artist == self.artist:
            # Artist is fully drawn and matches the current artist, nothing to do
            self._stateArtist = DisplayStateMachineState.FINISHED
        elif self._stateArtist == DisplayStateMachineState.DELAY_START:
            self._next_frame_ticks_artist.value = self._ticks.value + self._segment_finished_delay_ms
            self._stateArtist = DisplayStateMachineState.DELAY
        elif self._stateArtist == DisplayStateMachineState.DELAY:
            if self._ticks.value >= self._next_frame_ticks_artist.value:
                self._stateArtist = DisplayStateMachineState.ANIMATING
        elif self._stateArtist == DisplayStateMachineState.ANIMATING:
            if self._ticks.value >= self._next_frame_ticks_artist.value:
                self._buffer_artist = self._artist_animator.next()
                screen_update |= True
                self._next_frame_ticks_artist.value = self._ticks.value + self._update_every_ms
            if self._artist_animator.is_finished:
                self._stateArtist = DisplayStateMachineState.END_ANIMATION
                self._next_frame_ticks_artist.value = self._ticks.value + self._segment_finished_delay_ms
            elif self._stateArtist == DisplayStateMachineState.END_ANIMATION:
                if self._ticks.value >= self._next_frame_ticks_artist.value:
                    self._stateArtist = DisplayStateMachineState.INIT

        if self._buffer_title == self.title:
            # Title is fully drawn and matches the current title, nothing to do
            self._stateTitle = DisplayStateMachineState.FINISHED
        elif self._stateTitle == DisplayStateMachineState.DELAY_START:
            self._next_frame_ticks_title.value = self._ticks.value + self._segment_finished_delay_ms
            self._stateTitle = DisplayStateMachineState.DELAY
        elif self._stateTitle == DisplayStateMachineState.DELAY:
            if self._ticks.value >= self._next_frame_ticks_title.value:
                self._stateTitle = DisplayStateMachineState.ANIMATING
                self._next_frame_ticks_title.value = self._ticks.value
        elif self._stateTitle == DisplayStateMachineState.ANIMATING:
            if self._ticks.value >= self._next_frame_ticks_title.value:
                self._buffer_title = self._title_animator.next()
                screen_update |= True
                self._next_frame_ticks_title.value = self._ticks.value + self._update_every_ms
            if self._title_animator.is_finished:
                self._stateTitle = DisplayStateMachineState.END_ANIMATION
                self._next_frame_ticks_title.value = self._ticks.value + self._segment_finished_delay_ms
        elif self._stateTitle == DisplayStateMachineState.END_ANIMATION:
            if self._ticks.value >= self._next_frame_ticks_title.value:
                self._stateTitle = DisplayStateMachineState.INIT

        if screen_update:
            self.clear_screen()
            print(f"Artist: {self._buffer_artist}")
            print("-" * (self._max_text_width + 8))
            print(f"Title: {self._buffer_title}")


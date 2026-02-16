from jukebox.displays.common.common_enums import  DisplayStateMachineState
from jukebox.displays.console.simple import Simple as ConsoleSimple
from ctypes import c_uint64 as uint64 
from jukebox.animators.random_typewriter import RandomTypeWriter

class RandomTypewriter(ConsoleSimple):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._update_every_ms = kwargs.get('update_every_ms', 100)
        self._segment_finished_delay_ms = kwargs.get('segment_finished_delay_ms', 2000)
        self._max_text_width = kwargs.get('max_text_width', 80)
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


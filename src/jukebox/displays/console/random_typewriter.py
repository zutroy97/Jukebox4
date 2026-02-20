from jukebox.displays.common.common_enums import  DisplayStateMachineState
from jukebox.displays.console.simple import Simple as ConsoleSimple
from ctypes import c_uint64 as uint64 
from jukebox.animators.random_typewriter import RandomTypeWriter

class DisplayConsoleRandomTypewriter(ConsoleSimple):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._update_every_ms = kwargs.get('update_every_ms', 100)
        self._segment_finished_delay_ms = kwargs.get('segment_finished_delay_ms', 2000)
        self._max_text_width = kwargs.get('max_text_width', 80)
        self._artist_state : DisplayState = DisplayState(self)
        self._title_state : DisplayState = DisplayState(self)

    def song_title_updated(self) -> None:
        self._title_state.updateValue(self._title)
    def song_artist_updated(self) -> None:
        self._artist_state.updateValue(self._artist)

    def _drawConsole(self):
        self.clear_screen()
        print(f"Artist: {self._artist_state.buffer}")
        print(" " * 8 + "-" * (self._max_text_width ))
        print(f"Title:  {self._title_state.buffer}")

    def _updateDisplay(self) -> None:
        update_screen : bool = False
        update_screen |= self._artist_state.is_updated()
        update_screen |= self._title_state.is_updated()
        if update_screen:
            self._drawConsole()

class DisplayState:
    def __init__(self, parent: DisplayConsoleRandomTypewriter, **kwargs) -> None:
        self.parent = parent
        self.animator : RandomTypeWriter
        self.next_frame_ticks : uint64 = uint64()
        self.buffer : str = ""
        self.state : DisplayStateMachineState = kwargs.get('state', DisplayStateMachineState.INIT)
        self.value : str = ""
    def set_next_frame_ticks(self, ticks: uint64) -> None:
        self.next_frame_ticks = ticks
    def add_next_frame_ticks(self, delta_ms: int) -> None:
        self.next_frame_ticks.value = self.parent._ticks.value + delta_ms
    def has_next_frame_ticks_expired(self) -> bool:
        return self.parent._ticks.value >= self.next_frame_ticks.value

    def updateValue(self, value: str) -> None:
        self.value = value
        self.state = DisplayStateMachineState.TEXT_UPDATED
    def is_updated(self) -> bool:
        if self.state == DisplayStateMachineState.TEXT_UPDATED \
            or self.state == DisplayStateMachineState.INIT:
            self.animator = RandomTypeWriter(self.value, max_text_width=self.parent._max_text_width)
            self.animator.add_observer(self)
            self.state = DisplayStateMachineState.ANIMATING
            self.add_next_frame_ticks(0) # act immediately on artist change, don't wait for the next tick
        
        screen_update : bool= False
        if self.buffer.strip() == self.value:
            # Value is fully drawn and matches the current value, nothing to do
            self.state = DisplayStateMachineState.FINISHED
        elif self.state == DisplayStateMachineState.DELAY_START:
            self.add_next_frame_ticks(self.parent._segment_finished_delay_ms)
            self.state = DisplayStateMachineState.DELAY
        elif self.state == DisplayStateMachineState.DELAY:
            if self.has_next_frame_ticks_expired():
                self.state = DisplayStateMachineState.ANIMATING
        elif self.state == DisplayStateMachineState.ANIMATING:
            if self.has_next_frame_ticks_expired():
                self.buffer = self.animator.next()
                screen_update |= True
                self.add_next_frame_ticks(self.parent._update_every_ms)
            if self.animator.is_finished:
                self.state = DisplayStateMachineState.END_ANIMATION
                self.add_next_frame_ticks(self.parent._segment_finished_delay_ms)
        elif self.state == DisplayStateMachineState.END_ANIMATION:
            if self.has_next_frame_ticks_expired():
                self.state = DisplayStateMachineState.INIT
        return screen_update

    def animation_update(self, **kwargs):
        if 'event' in kwargs:
            event = kwargs.get('event', '')
            if event == "segment_finished":
                self.add_next_frame_ticks(self.parent._segment_finished_delay_ms)
                self.state = DisplayStateMachineState.DELAY_START


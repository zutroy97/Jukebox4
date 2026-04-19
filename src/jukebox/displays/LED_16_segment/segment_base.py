import asyncio
import logging

from busio import I2C
import board
from adafruit_ht16k33 import segments
from jukebox.animators2.led16.animator_base import Led16AlienIntro, Led16AnimatorBase, Led16StaticText
from jukebox.animators2.text.animator_base import TextAnimatorBase
from jukebox.displays.common.common_enums import DisplayStateMachineState
from jukebox.displays.common.display_base import DisplayBase
from typing import Awaitable, Callable, List, Tuple, Type, Union

class SegmentBase(DisplayBase):
    def __init__(
            self, 
            **kwargs) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        i2c = kwargs.get('i2c', I2C(board.SCL, board.SDA))
        addr_lower = kwargs.get('addr_lower', (0x72, 0x73, 0x74))
        addr_upper = kwargs.get('addr_upper', (0x70, 0x71))
        self._display8 = segments.Seg14x4(i2c, address=addr_upper)  # uses board.SCL and board.SDA
        self._display12 = segments.Seg14x4(i2c, address=addr_lower)
        self._display8.brightness = 0.20
        self._display12.brightness = 0.20
        self._running = True
    
    async def clear_screen(self) -> None:
        self._display8.fill(0)
        self._display12.fill(0)

    def _updateDisplay(self) -> None:
        self._display8.print(f"{self.artist[:8]:<8}")
        self._display12.print(f"{self.title[:12]:<12}")

    def print8(self, text: str) -> None:
        self._display8.print(f"{text[:8]:<8}")

    def print12(self, text: str) -> None:
        self._display12.print(f"{text[:12]:<12}")

    def write_raw8(self,index: int, bitmask: Union[int, List[int], Tuple[int, int]] ) -> None:
        self._display8.set_digit_raw(index, bitmask)

    def write_raw12(self,index: int, bitmask: Union[int, List[int], Tuple[int, int]] ) -> None:
        self._display12.set_digit_raw(index, bitmask)

    def set_brightness(self, brightness: float) -> None:
        brightness = max(0.0, min(1.0, brightness))
        self._display8.brightness = brightness
        self._display12.brightness = brightness

class SegmentStaticText(SegmentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._title_animator : Led16AnimatorBase
        self._artist_animator: Led16AnimatorBase 

    async def loop(self) -> None:
        while self._running:
            if self._stateTitle ==DisplayStateMachineState.TEXT_UPDATED:
                self._title_animator = Led16StaticText(text=self.title, max_text_width=12)
                await self._title_animator.Start()
                self._stateTitle = DisplayStateMachineState.ANIMATING
                self.print12(self.title)

            if self._stateArtist == DisplayStateMachineState.TEXT_UPDATED:
                self._artist_animator = Led16StaticText(text=self.artist, max_text_width=8)
                await self._artist_animator.Start()
                self._stateArtist = DisplayStateMachineState.ANIMATING
                self.print8(self.artist)
            await asyncio.sleep(0.1)


from jukebox.displays.LED_16_segment.segment_base import SegmentBase
from jukebox.displays.common.common_enums import DisplayStateMachineState
from datetime import datetime, timedelta
from enum import Enum
from jukebox.animators2.text.multiline_generator import MultiLineGenerator

class SegmentMultiLine(SegmentBase):
    class AnimationState(Enum):
        IDLE = 0
        """Not doing anything."""
        INIT = 1
        """Initializing display with new text."""
        ANIMATING = 2
        """Main loop for display updates."""
        ANIMATED_LINE_CALLBACK = 3
        """Callback after a line has been fully animated, waiting for the callback to return true before animating the next line.""" 
        DELAY = 8
        """Waiting for a delay to pass before starting next animation."""
        DELAY_START = 9

    class SegmentLineAnimator():
        async def on_line_animated(self) -> bool:
            #await asyncio.sleep(1) # wait for the line to be fully displayed before starting the timer
            self._next_update_after = datetime.now() + timedelta(seconds=2) # display each line for 5 seconds
            self._state = SegmentMultiLine.AnimationState.DELAY_START
            return True

        def __init__(self, display: segments.Seg14x4):
            self._next_update_after : datetime = datetime.now() + timedelta(days=3600)
            self._display = display
            self._max_text_width = len(display.i2c_device) * 4
            self._lineGenerator : MultiLineGenerator = MultiLineGenerator(text='', max_text_width=self._max_text_width) 
            self._anim_type : Type[Led16AnimatorBase] = Led16AlienIntro
            self._anim : Led16AnimatorBase 
            self._state = SegmentMultiLine.AnimationState.IDLE
            self._text = ""
            self._logger = logging.getLogger(f"{__class__.__name__}_{id(self)}")
            self._on_line_animated_callback : Callable[[Led16AnimatorBase], Awaitable[bool]] = self._default_on_line_animated_callback
        
        async def _default_on_line_animated_callback(self, anim: Led16AnimatorBase) -> bool:
            print(f"_default_on_line_animated_callback finished for animation: {anim.__class__.__name__} {anim.text}")
            await asyncio.sleep(2) # wait for the line to be fully displayed before starting the timer
            return True 
        
        def on_line_animated_callback(self, callback: Callable[[Led16AnimatorBase], Awaitable[bool]]) -> None:
            self._on_line_animated_callback = callback

        def set_text(self, text: str) -> None:
            self._text = text
            self._state = SegmentMultiLine.AnimationState.INIT
            self._next_update_after = datetime.now() - timedelta(seconds=1)
   
        def set_animator(self, anim_type: Type[Led16AnimatorBase]) -> None:
            self._anim_type = anim_type

        async def setup_multiline(self) -> None:
            self._lineGenerator = MultiLineGenerator(text=self._text, max_text_width=self._max_text_width) 
            await self._lineGenerator.Start()

        async def setup_animation(self) -> None:
            if not await self._lineGenerator.Next():
                await self.setup_multiline()
            t = await self._lineGenerator.GetText()
            self._anim = self._anim_type(text=t, max_text_width=self._max_text_width)
            await self._anim.Start()

        async def loop(self) -> None:
            if self._next_update_after < datetime.now():
                if self._state == SegmentMultiLine.AnimationState.INIT:
                    await self.setup_multiline()
                    await self.setup_animation()
                    self._state = SegmentMultiLine.AnimationState.ANIMATING
                
                elif self._state == SegmentMultiLine.AnimationState.ANIMATED_LINE_CALLBACK:
                    if not await self._on_line_animated_callback(self._anim):
                        return
                    if await self._lineGenerator.Next():
                        await self.setup_animation()
                        self._state = SegmentMultiLine.AnimationState.ANIMATING
                    elif len(self._text) <= self._anim.max_text_width:
                        self._state = SegmentMultiLine.AnimationState.IDLE
                        return # no more lines to animate and the text fits on one line, so we're done
                    else:
                        await self.setup_animation() # restart the animation
                        self._state = SegmentMultiLine.AnimationState.ANIMATING
                
                elif self._state == SegmentMultiLine.AnimationState.ANIMATING:
                    #print(f"Checking if animation has next frame for text: {self._text}")
                    if (await self._anim.Next()):
                        bitmasks = await self._anim.GetSegments()
                        #print(f"Updating display with bitmasks: {bitmasks}")
                        self._display.fill(0) # clear the display before writing the new frame
                        for i, bitmask in enumerate(bitmasks):
                            if i > self._max_text_width:
                                break
                            #print(f"Setting digit {i} to bitmask {bitmask}")
                            self._display.set_digit_raw(i, bitmask)
                        self._next_update_after = datetime.now() + timedelta(milliseconds=100)
                    else:
                        self._state = SegmentMultiLine.AnimationState.ANIMATED_LINE_CALLBACK
                        return

                elif self._state == SegmentMultiLine.AnimationState.DELAY_START:
                    self._logger.debug("Transitioning to ANIMATING")

                    self._state = SegmentMultiLine.AnimationState.ANIMATING
            

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_brightness(.1)
        self._title_animator = self.SegmentLineAnimator(self._display12)
        self._artist_animator = self.SegmentLineAnimator(self._display8)

    async def loop(self) -> None:
        while self._running:
            if self._stateTitle == DisplayStateMachineState.TEXT_UPDATED:
                self._title_animator.set_text(self.title)
                self._stateTitle = DisplayStateMachineState.ANIMATING
            if self._stateArtist == DisplayStateMachineState.TEXT_UPDATED:
                self._artist_animator.set_text(self.artist)
                self._stateArtist = DisplayStateMachineState.ANIMATING
            await self._title_animator.loop()
            await self._artist_animator.loop()
            await asyncio.sleep(0.010)


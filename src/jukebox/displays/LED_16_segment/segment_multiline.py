import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Awaitable, Callable, Optional, Type

from adafruit_ht16k33 import segments
from jukebox.animators2.led16.animator_base import Led16AnimatorBase
from jukebox.animators2.led16.led16_alien_intro import Led16AlienIntro
from jukebox.animators2.text.multiline_generator import MultiLineGenerator
from jukebox.displays.common.common_enums import DisplayStateMachineState
from jukebox.displays.LED_16_segment.segment_base import SegmentBase


class SegmentMultiLine(SegmentBase):
    class AnimationState(Enum):
        IDLE = 0
        """Not doing anything."""
        INIT = 1
        """Initializing display with new text."""
        ANIMATING = 2
        """Main loop for display updates."""
        ON_ANIMATED_LINE_COMPLETE_CALLBACK = 3
        """Callback after a line has been fully animated, waiting for the callback to return true before animating the next line.""" 
        ON_TEXT_CHANGED_CALLBACK = 4
        """Callback after the text has been fully changed, waiting for the callback to return true before starting to animate the new text."""
        DELAY = 8
        """Waiting for a delay to pass before starting next animation."""
        DELAY_START = 9

    class NonBlockingDelay():
        def __init__(self, delay_seconds: float):
            self._delay_seconds = delay_seconds
            self._next_update_time: Optional[datetime] = None

        async def isDelayFinished(self, anim: Led16AnimatorBase) -> bool:
            if self._next_update_time is None:
                self._next_update_time = datetime.now() + timedelta(seconds=self._delay_seconds)
            if self._next_update_time < datetime.now():
                self._next_update_time = None
                return True
            return False

    class SegmentLineAnimator():
        async def on_line_animated(self) -> bool:
            self._next_update_after = datetime.now() + timedelta(seconds=2)
            self._state = SegmentMultiLine.AnimationState.DELAY_START
            return True

        def __init__(self, display: segments.Seg14x4):
            self._next_update_after: datetime = datetime.now() + timedelta(days=3600)
            self._display = display
            self._max_text_width = len(display.i2c_device) * 4
            self._lineGenerator: MultiLineGenerator = MultiLineGenerator(text='', max_text_width=self._max_text_width)
            self._anim_type: Type[Led16AnimatorBase] = Led16AlienIntro
            self._anim: Led16AnimatorBase
            self._state = SegmentMultiLine.AnimationState.IDLE
            self._text = ""
            self._logger = logging.getLogger(f"{__class__.__name__}_{id(self)}")
            self._on_line_animated_callback: Callable[[Led16AnimatorBase], Awaitable[bool]] = self._default_on_line_animated_callback
            self._on_text_changed_callback: Callable[[Optional[Led16AnimatorBase], str], Awaitable[bool]] = self._default_on_text_changed_callback

        async def _default_on_text_changed_callback(self, anim: Optional[Led16AnimatorBase], text: str) -> bool:
            return True

        async def _default_on_line_animated_callback(self, anim: Led16AnimatorBase) -> bool:
            return True

        def on_line_animated_callback(self, callback: Callable[[Led16AnimatorBase], Awaitable[bool]]) -> None:
            self._on_line_animated_callback = callback

        def set_text(self, text: str) -> None:
            self._text = text
            self._state = SegmentMultiLine.AnimationState.ON_TEXT_CHANGED_CALLBACK

        def set_animator(self, anim_type: Type[Led16AnimatorBase]) -> None:
            self._anim_type = anim_type

        async def _setup_multiline(self) -> None:
            self._lineGenerator = MultiLineGenerator(text=self._text, max_text_width=self._max_text_width)
            await self._lineGenerator.Start()

        async def _setup_animation(self) -> None:
            if not await self._lineGenerator.Next():
                await self._setup_multiline()
            t = await self._lineGenerator.GetText()
            self._anim = self._anim_type(text=t, max_text_width=self._max_text_width)
            await self._anim.Start()

        async def loop(self) -> None:
            if self._state == SegmentMultiLine.AnimationState.ON_TEXT_CHANGED_CALLBACK:
                anim = self._anim if hasattr(self, '_anim') else None
                if not await self._on_text_changed_callback(anim, self._text):
                    return
                self._state = SegmentMultiLine.AnimationState.INIT
                self._next_update_after = datetime.now() - timedelta(seconds=1)

            if self._next_update_after < datetime.now():
                if self._state == SegmentMultiLine.AnimationState.INIT:
                    await self._setup_multiline()
                    await self._setup_animation()
                    self._state = SegmentMultiLine.AnimationState.ANIMATING

                elif self._state == SegmentMultiLine.AnimationState.ON_ANIMATED_LINE_COMPLETE_CALLBACK:
                    if not await self._on_line_animated_callback(self._anim):
                        return
                    if await self._lineGenerator.Next():
                        await self._setup_animation()
                        self._state = SegmentMultiLine.AnimationState.ANIMATING
                    elif len(self._text) <= self._anim.max_text_width:
                        self._state = SegmentMultiLine.AnimationState.IDLE
                        return
                    else:
                        await self._setup_animation()
                        self._state = SegmentMultiLine.AnimationState.ANIMATING

                elif self._state == SegmentMultiLine.AnimationState.ANIMATING:
                    if await self._anim.Next():
                        bitmasks = await self._anim.GetSegments()
                        self._display.fill(0)
                        for i, bitmask in enumerate(bitmasks):
                            if i > self._max_text_width:
                                break
                            self._display.set_digit_raw(i, bitmask)
                        self._next_update_after = datetime.now() + timedelta(milliseconds=100)
                    else:
                        self._state = SegmentMultiLine.AnimationState.ON_ANIMATED_LINE_COMPLETE_CALLBACK
                        return

                elif self._state == SegmentMultiLine.AnimationState.DELAY_START:
                    self._logger.debug("Transitioning to ANIMATING")
                    self._state = SegmentMultiLine.AnimationState.ANIMATING

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_brightness(.1)
        self._title_animator = self.SegmentLineAnimator(self._display12)
        _title_line_animated_callback = self.NonBlockingDelay(2)
        self._title_animator.on_line_animated_callback(_title_line_animated_callback.isDelayFinished)

        self._artist_animator = self.SegmentLineAnimator(self._display8)
        _artist_line_animated_callback = self.NonBlockingDelay(2)
        self._artist_animator.on_line_animated_callback(_artist_line_animated_callback.isDelayFinished)

    async def loop(self) -> None:
        while self._running:
            if self._stateTitle == DisplayStateMachineState.TEXT_UPDATED:
                self._title_animator.set_text(self.title)
                self._stateTitle = DisplayStateMachineState.ANIMATING
            await self._title_animator.loop()
            if self._stateArtist == DisplayStateMachineState.TEXT_UPDATED:
                self._artist_animator.set_text(self.artist)
                self._stateArtist = DisplayStateMachineState.ANIMATING
            await self._artist_animator.loop()
            await asyncio.sleep(0.010)

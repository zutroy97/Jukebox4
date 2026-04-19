import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Awaitable, Optional, Type

from adafruit_ht16k33 import segments
from jukebox.animators2.led16.animator_base import Led16AnimatorBase
from jukebox.animators2.led16.led16_static_text import Led16StaticText
from jukebox.animators2.text.multiline_generator import MultiLineGenerator
from jukebox.displays.LED_16_segment.segment_multiline_handlers import LineAnimationCompleteEvent, LineAnimationCompleteAbstractHandler, NonBlockingDelay
from jukebox.displays.LED_16_segment.segment_text_changed import TextChangedEvent, TextChangedAbstractHandler, TextChangedNoOpHandler


class SegmentLineAnimator:
    class AnimatorState(Enum):
        IDLE = 0
        INIT = 1
        ANIMATING = 2
        ON_ANIMATED_LINE_COMPLETE_CALLBACK = 3
        ON_TEXT_CHANGED_CALLBACK = 4
        DELAY = 8
        DELAY_START = 9

    def __init__(self, display: segments.Seg14x4):
        self._next_update_after: datetime = datetime.now() + timedelta(days=3600)
        self._display = display
        self._max_text_width = len(display.i2c_device) * 4
        self._lineGenerator: MultiLineGenerator = MultiLineGenerator(text='', max_text_width=self._max_text_width)
        self._anim_type: Type[Led16AnimatorBase] = Led16StaticText
        self._anim: Led16AnimatorBase = self._anim_type(text='', max_text_width=self._max_text_width)
        self._state = SegmentLineAnimator.AnimatorState.IDLE
        self._text = ""
        self._logger = logging.getLogger(f"{__class__.__name__}_{id(self)}")
        self._on_line_animated_handler: LineAnimationCompleteAbstractHandler = NonBlockingDelay(2)
        self._on_text_changed_callback: TextChangedAbstractHandler = TextChangedNoOpHandler()

    def on_line_animated_handler(self, handler: LineAnimationCompleteAbstractHandler) -> None:
        self._on_line_animated_handler = handler

    def set_text(self, text: str) -> None:
        self._text = text
        self._state = SegmentLineAnimator.AnimatorState.ON_TEXT_CHANGED_CALLBACK

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
        if self._state == SegmentLineAnimator.AnimatorState.ON_TEXT_CHANGED_CALLBACK:
            if not await self._on_text_changed_callback.shouldContinue(TextChangedEvent(orgText=self._anim.text, newText=self._text, animator=self)):
                return
            if self._on_line_animated_handler is not None:
                await self._on_line_animated_handler.cancel()
            self._state = SegmentLineAnimator.AnimatorState.INIT
            self._next_update_after = datetime.now() - timedelta(seconds=1)

        if self._next_update_after < datetime.now():
            if self._state == SegmentLineAnimator.AnimatorState.INIT:
                await self._setup_multiline()
                await self._setup_animation()
                self._state = SegmentLineAnimator.AnimatorState.ANIMATING

            elif self._state == SegmentLineAnimator.AnimatorState.ON_ANIMATED_LINE_COMPLETE_CALLBACK:
                if self._on_line_animated_handler is not None and not await self._on_line_animated_handler.shouldAnimateNextLine(LineAnimationCompleteEvent(self._anim)):
                    return
                if await self._lineGenerator.Next():
                    await self._setup_animation()
                    self._state = SegmentLineAnimator.AnimatorState.ANIMATING
                elif len(self._text) <= self._anim.max_text_width:
                    self._state = SegmentLineAnimator.AnimatorState.IDLE
                    return
                else:
                    await self._setup_animation()
                    self._state = SegmentLineAnimator.AnimatorState.ANIMATING

            elif self._state == SegmentLineAnimator.AnimatorState.ANIMATING:
                if await self._anim.Next():
                    bitmasks = await self._anim.GetSegments()
                    self._display.fill(0)
                    for i, bitmask in enumerate(bitmasks):
                        if i > self._max_text_width:
                            break
                        self._display.set_digit_raw(i, bitmask)
                    self._next_update_after = datetime.now() + timedelta(milliseconds=100)
                else:
                    self._state = SegmentLineAnimator.AnimatorState.ON_ANIMATED_LINE_COMPLETE_CALLBACK
                    return

            elif self._state == SegmentLineAnimator.AnimatorState.DELAY_START:
                self._logger.debug("Transitioning to ANIMATING")
                self._state = SegmentLineAnimator.AnimatorState.ANIMATING

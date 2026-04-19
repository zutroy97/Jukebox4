import asyncio
import logging

from jukebox.animators2.led16.animator_base import Led16AnimatorBase
from jukebox.animators2.led16.led16_static_text import Led16StaticText
from jukebox.displays.common.common_enums import DisplayStateMachineState
from jukebox.displays.LED_16_segment.segment_base import SegmentBase


class SegmentStaticText(SegmentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._title_animator: Led16AnimatorBase
        self._artist_animator: Led16AnimatorBase

    async def loop(self) -> None:
        while self._running:
            if self._stateTitle == DisplayStateMachineState.TEXT_UPDATED:
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

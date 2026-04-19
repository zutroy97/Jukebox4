from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from jukebox.animators2.led16.animator_base import Led16AnimatorBase


class LineAnimationCompleteEvent:
    def __init__(self, anim: Led16AnimatorBase):
        self.anim = anim

    @property
    def Animation(self) -> Led16AnimatorBase:
        return self.anim


class LineAnimationCompleteAbstractHandler(ABC):
    @abstractmethod
    async def shouldAnimateNextLine(self, event: LineAnimationCompleteEvent) -> bool:
        '''Callback that is called when a line has been fully animated. The callback should return true if the next line should be animated, or false if the animation should stop.'''
        pass

    @abstractmethod
    async def cancel(self) -> None:
        pass


class NonBlockingDelay(LineAnimationCompleteAbstractHandler):
    def __init__(self, delay_seconds: float):
        self._delay_seconds = delay_seconds
        self._next_update_time: Optional[datetime] = None

    async def shouldAnimateNextLine(self, event: LineAnimationCompleteEvent) -> bool:
        if self._next_update_time is None:
            self._next_update_time = datetime.now() + timedelta(seconds=self._delay_seconds)
        if self._next_update_time < datetime.now():
            self._next_update_time = None
            return True
        return False

    async def cancel(self) -> None:
        self._next_update_time = None

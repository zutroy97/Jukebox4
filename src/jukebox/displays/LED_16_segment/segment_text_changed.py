from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jukebox.displays.LED_16_segment.segment_line_animator import SegmentLineAnimator


class TextChangedEvent:
    def __init__(self, orgText: str, newText: str, animator: 'SegmentLineAnimator'):
        self._orgText = orgText
        self._newText = newText

    @property
    def OriginalText(self) -> str:
        return self._orgText

    def NewText(self) -> str:
        return self._newText


class TextChangedAbstractHandler(ABC):
    @abstractmethod
    async def shouldContinue(self, event: TextChangedEvent) -> bool:
        pass


class TextChangedNoOpHandler(TextChangedAbstractHandler):
    async def shouldContinue(self, event: TextChangedEvent) -> bool:
        return True

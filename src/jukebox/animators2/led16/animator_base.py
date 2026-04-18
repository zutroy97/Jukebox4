from enum import Enum
from abc import abstractmethod, ABC
import logging
import asyncio
from adafruit_ht16k33 import segments
from typing import List


class Led16AnimatorBase(ABC):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._logger = logging.getLogger()
        self._text = kwargs.get('text', '')
        self._done : bool = False
        self._max_text_width = kwargs.get('max_text_width', 20)

    @staticmethod
    def get_char_pattern(char: str) -> int:
        if not 32 <= ord(char) <= 127:
            return 0
        # TODO: Handle decimal points and commas, which are not currently supported by this mapping
        character = ord(char) * 2 - 64
        return (segments.CHARS[character]<<8)| segments.CHARS[1 +character]
    
    @staticmethod
    def string_to_char_mask(s: str) -> List[int]:
        return [Led16AnimatorBase.get_char_pattern(ch) for ch in s]

    @property
    def max_text_width(self) -> int:
        return self._max_text_width
    
    @property
    def text(self) -> str:
        return self._text

    @abstractmethod
    async def GetSegments(self) -> list[int]:
        '''Returns the segments to be displayed'''
        return []
    
    @abstractmethod
    async def Next(self) -> bool:
        '''Returns true if more data is available'''
        return False
    
    @abstractmethod
    async def Start(self) -> None:
        '''Start/Restarts the animation'''
        pass
    
class Led16StaticText(Led16AnimatorBase):
    async def GetSegments(self) -> list[int]:
        return self.string_to_char_mask(self.text)
    
    async def Next(self) -> bool:
        return False
    
    async def Start(self) -> None:
        pass

class Led16AlienIntro(Led16AnimatorBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.i = 0
    async def GetSegments(self) -> list[int]:
        #print(f"Getting segments for text: {self.text}")
        return self.string_to_char_mask(self.text)
    
    async def Next(self) -> bool:
        self.i += 1
        return self.i == 1 # only one frame of animation, so return true on the first call and false thereafter
    
    async def Start(self) -> None:
        self.i = 0
        return
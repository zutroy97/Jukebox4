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
        '''Converts a character to a segment bitmask. The bitmask represents the segments that should be lit for the corresponding character. Characters that are not in the supported range (32-127) will be represented as blank (0).   The mapping is based on the adafruit_ht16k33 library's character mapping, which supports a subset of ASCII characters. The mapping does not currently support decimal points and commas, which are commonly used in 16-segment displays. '''
        if not 32 <= ord(char) <= 127:
            return 0
        # TODO: Handle decimal points and commas, which are not currently supported by this mapping
        character = ord(char) * 2 - 64
        return (segments.CHARS[character]<<8)| segments.CHARS[1 +character]
    
    @staticmethod
    def string_to_char_mask(s: str) -> List[int]:
        '''Converts a string to a list of segment bitmasks. Each bitmask represents the segments that should be lit for the corresponding character in the string.  Characters that are not in the supported range (32-127) will be represented as blank (0).   The mapping is based on the adafruit_ht16k33 library's character mapping, which supports a subset of ASCII characters. The mapping does not currently support decimal points and commas, which are commonly used in 16-segment displays.'''
        return [Led16AnimatorBase.get_char_pattern(ch) for ch in s]

    @property
    def max_text_width(self) -> int:
        '''Returns the maximum text width that should be used for this animation.'''
        return self._max_text_width
    
    @property
    def text(self) -> str:
        '''Returns the text to be displayed.'''
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

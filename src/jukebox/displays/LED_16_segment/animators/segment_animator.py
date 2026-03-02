import random
from time import sleep
from jukebox.animators import animation
from jukebox.animators.multi_line_generator import MultiLineGenerator   
from abc import abstractmethod
from typing import List
from enum import Enum

class SegmentAnimatorBase(animation.Animation):
    def __init__(self,  **kwargs) -> None:
        super().__init__(**kwargs)

    @staticmethod
    def get_char_pattern(char: str) -> int:
        if not 32 <= ord(char) <= 127:
            return 0
        # TODO: Handle decimal points and commas, which are not currently supported by this mapping
        character = ord(char) * 2 - 64
        return (SegmentAnimatorBase.CHARS[character]<<8)|SegmentAnimatorBase.CHARS[1 +character]
    
    @staticmethod
    def string_to_char_mask(s: str) -> List[int]:
        return [SegmentAnimatorBase.get_char_pattern(ch) for ch in s]

    @abstractmethod
    def nextSegments(self) -> List[int]:
        '''Returns the new state to be written to the segmenta'''
        pass

    CHARS = (
        0b00000000, 0b00000000,
        0b01000000, 0b00000110,  # !
        0b00000010, 0b00100000,  # "
        0b00010010, 0b11001110,  # #
        0b00010010, 0b11101101,  # $
        0b00001100, 0b00100100,  # %
        0b00100011, 0b01011101,  # &
        0b00000100, 0b00000000,  # '
        0b00100100, 0b00000000,  # (
        0b00001001, 0b00000000,  # )
        0b00111111, 0b11000000,  # *
        0b00010010, 0b11000000,  # +
        0b00001000, 0b00000000,  # ,
        0b00000000, 0b11000000,  # -
        0b00000000, 0b00000000,  # .
        0b00001100, 0b00000000,  # /
        0b00001100, 0b00111111,  # 0
        0b00000000, 0b00000110,  # 1
        0b00000000, 0b11011011,  # 2
        0b00000000, 0b10001111,  # 3
        0b00000000, 0b11100110,  # 4
        0b00100000, 0b01101001,  # 5
        0b00000000, 0b11111101,  # 6
        0b00000000, 0b00000111,  # 7
        0b00000000, 0b11111111,  # 8
        0b00000000, 0b11101111,  # 9
        0b00010010, 0b00000000,  # :
        0b00001010, 0b00000000,  # ;
        0b00100100, 0b01000000,  # <
        0b00000000, 0b11001000,  # =
        0b00001001, 0b10000000,  # >
        0b01100000, 0b10100011,  # ?
        0b00000010, 0b10111011,  # @
        0b00000000, 0b11110111,  # A
        0b00010010, 0b10001111,  # B
        0b00000000, 0b00111001,  # C
        0b00010010, 0b00001111,  # D
        0b00000000, 0b11111001,  # E
        0b00000000, 0b01110001,  # F
        0b00000000, 0b10111101,  # G
        0b00000000, 0b11110110,  # H
        0b00010010, 0b00000000,  # I
        0b00000000, 0b00011110,  # J
        0b00100100, 0b01110000,  # K
        0b00000000, 0b00111000,  # L
        0b00000101, 0b00110110,  # M
        0b00100001, 0b00110110,  # N
        0b00000000, 0b00111111,  # O
        0b00000000, 0b11110011,  # P
        0b00100000, 0b00111111,  # Q
        0b00100000, 0b11110011,  # R
        0b00000000, 0b11101101,  # S
        0b00010010, 0b00000001,  # T
        0b00000000, 0b00111110,  # U
        0b00001100, 0b00110000,  # V
        0b00101000, 0b00110110,  # W
        0b00101101, 0b00000000,  # X
        0b00010101, 0b00000000,  # Y
        0b00001100, 0b00001001,  # Z
        0b00000000, 0b00111001,  # [
        0b00100001, 0b00000000,  # \
        0b00000000, 0b00001111,  # ]
        0b00001100, 0b00000011,  # ^
        0b00000000, 0b00001000,  # _
        0b00000001, 0b00000000,  # `
        0b00010000, 0b01011000,  # a
        0b00100000, 0b01111000,  # b
        0b00000000, 0b11011000,  # c
        0b00001000, 0b10001110,  # d
        0b00001000, 0b01011000,  # e
        0b00000000, 0b01110001,  # f
        0b00000100, 0b10001110,  # g
        0b00010000, 0b01110000,  # h
        0b00010000, 0b00000000,  # i
        0b00000000, 0b00001110,  # j
        0b00110110, 0b00000000,  # k
        0b00000000, 0b00110000,  # l
        0b00010000, 0b11010100,  # m
        0b00010000, 0b01010000,  # n
        0b00000000, 0b11011100,  # o
        0b00000001, 0b01110000,  # p
        0b00000100, 0b10000110,  # q
        0b00000000, 0b01010000,  # r
        0b00100000, 0b10001000,  # s
        0b00000000, 0b01111000,  # t
        0b00000000, 0b00011100,  # u
        0b00100000, 0b00000100,  # v
        0b00101000, 0b00010100,  # w
        0b00101000, 0b11000000,  # x
        0b00100000, 0b00001100,  # y
        0b00001000, 0b01001000,  # z
        0b00001001, 0b01001001,  # {
        0b00010010, 0b00000000,  # |
        0b00100100, 0b10001001,  # }
        0b00000101, 0b00100000,  # ~
        0b00111111, 0b11111111,
    )


class SegmentAlienIntroActiveSegmentOnlyAnimation(SegmentAnimatorBase):
    class States(Enum):
        UNKNOWN = 0
        WORD_DELAY = 1
        ANIMATING = 2
        FINISHED = 3

    class SegmentCharData:
        def __init__(self, char : str) -> None:
            self.mask : List[int] = []
            self.buffer = 0
            self.character : str = char
            self.pattern = SegmentAnimatorBase.get_char_pattern(char=self.character)
            for i in range(15):
                this_mask = 1 << i
                if this_mask & self.pattern:
                    self.mask.append(this_mask)
            random.shuffle(self.mask)

        def next(self) -> bool:
            if len(self.mask) == 0:
                return False
            self.buffer |= (self.mask.pop(0) & self.pattern)
            return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._args = kwargs
        self._char_data = []
        self._delaySegmentTicks = kwargs.get('segment_delay_ticks', 10)
        '''Number of elapsed ticks between animation updates'''
        self._delaySegmentCnt : int = 0

        self._max_text_width = kwargs.get('max_text_width', 4)
        '''Number of Character/Digits in the display'''
        self._generator = MultiLineGenerator(**kwargs)
        
        self._delayLineTicks = kwargs.get('delay_line_ticks', 200)
        '''Number of ticks between displaying new lines on the display'''
        self._delayLineCnt : int = 0

        self._loop : bool = kwargs.get('loop_number', True)
        '''Contiunelessly loop the message'''
        self._state = self.States.ANIMATING
        self._init(self._generator.next())
        

    def _init(self, text: str) -> None:
        text = text.ljust(self._max_text_width, ' ')
        self._char_data = self.str_to_SegmentCharData(text)


    def str_to_SegmentCharData(self, input : str) -> List[SegmentCharData]:
        x = [self.SegmentCharData(char) for char in list(input)]
        return x

    def next(self) -> str:
        return ''

    def nextSegments(self)  -> List[int]:
        if self._state == self.States.ANIMATING:
            if self._delaySegmentCnt > 0:
                self._delaySegmentCnt -= 1
                return []
            else:
                self._delaySegmentCnt = self._delaySegmentTicks
            render_cnt = 0
            segments = []
            for ren in self._char_data:
                if ren.next():
                    render_cnt += 1
                segments.append(ren.buffer)

            if render_cnt > 0:
                return segments
            else:
                self.notify_observers(event="segment_finished" )
                self._state = self.States.WORD_DELAY
                self._delayLineCnt = self._delayLineTicks
                if self._generator.is_finished:
                    if self._loop and (self._max_text_width < len(self.text)):
                        self._generator = MultiLineGenerator(**self._args)
                    else:
                        self._done = True
                        self._state = self.States.FINISHED
        elif self._state == self.States.WORD_DELAY:
            if self._delayLineCnt > 0:
                self._delayLineCnt -= 1
            else:
                self._init(self._generator.next())
                self._state = self.States.ANIMATING
                self._delaySegmentCnt = -1
        return []







class SegmentAlienIntroAnimation(SegmentAnimatorBase):
    class States(Enum):
        UNKNOWN = 0
        WORD_DELAY = 1
        ANIMATING = 2
        FINISHED = 3

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._args = kwargs
        self._mask : List[int] = []
        '''Bitmask representing which characters in the current line have been revealed. Should be updated as the animation progresses.'''
        self._segment_queue : List[int] = []
        self._delaySegmentTicks = kwargs.get('delay_ticks', 5)
        '''Number of elapsed ticks between animation updates'''
        self._delaySegmentCnt : int = 0

        self._max_text_width = kwargs.get('max_text_width', 4)
        '''Number of Character/Digits in the display'''
        self._generator = MultiLineGenerator(**kwargs)
        
        self._delayLineTicks = kwargs.get('delay_line_ticks', 200)
        '''Number of ticks between displaying new lines on the display'''
        self._delayLineCnt : int = 0

        self._loop : bool = kwargs.get('loop_number', True)
        '''Contiunelessly loop the message'''
        self._state = self.States.ANIMATING
        self._init(self._generator.next())
        

    def _init(self, text: str) -> None:
        text = text.strip()[:self._max_text_width].ljust(self._max_text_width)
        self._mask = self.string_to_char_mask(text) # 
        self._buffer = [0] * self._max_text_width # reset the buffer for the new line
        self._segment_queue = list(range(0, 15)) # queue of character segments to reveal, shuffled to create the random effect
        random.shuffle(self._segment_queue)   

    def next(self) -> str:
        return ''

    def nextSegments(self)  -> List[int]:
        if self._state == self.States.ANIMATING:
            if self._delaySegmentCnt > 0:
                self._delaySegmentCnt -= 1
                return []
            else:
                self._delaySegmentCnt = self._delaySegmentTicks

            this_mask = 1 << self._segment_queue.pop(0)
            for pos in range (self._max_text_width):
                self._buffer[pos] |= (self._mask[pos] & this_mask)
            if len(self._segment_queue) == 0:
                self.notify_observers(event="segment_finished" )
                self._state = self.States.WORD_DELAY
                self._delayLineCnt = self._delayLineTicks
                if self._generator.is_finished:
                    if self._loop and (self._max_text_width < len(self.text)):
                        self._generator = MultiLineGenerator(**self._args)
                    else:
                        self._done = True
                        self._state = self.States.FINISHED
        elif self._state == self.States.WORD_DELAY:
            if self._delayLineCnt > 0:
                self._delayLineCnt -= 1
                return []
            else:
                self._init(self._generator.next())
                self._state = self.States.ANIMATING
                self._delaySegmentCnt = -1
        return self._buffer

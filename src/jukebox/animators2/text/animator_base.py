from enum import Enum
from abc import abstractmethod, ABC
import logging


class TextAnimatorBase(ABC):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)
        self._text = kwargs.get('text', '')
        self._done : bool = False
        self._max_text_width = kwargs.get('max_text_width', 20)

    @property
    def max_text_width(self) -> int:
        return self._max_text_width
    
    @property
    def text(self) -> str:
        return self._text

    @abstractmethod
    def GetText(self) -> str:
        '''Returns the text to be displayed'''
        return ""
    
    @abstractmethod
    def Next(self) -> bool:
        '''Returns true if more data is available'''
        return False
    
    @abstractmethod
    def Restart(self) -> None:
        '''Restarts the animation'''
        pass
    
import textwrap

class MultiLineGenerator(TextAnimatorBase):
    '''Animates text by splitting it into multiple lines and displaying each line one at a time.'''
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Restart()

    def Restart(self) -> None:
        self._lines = textwrap.wrap(self.text, width=self.max_text_width, expand_tabs=False, drop_whitespace=True)
        self._done = False

    def Next(self) -> bool:
        '''Returns true if more data is available'''
        return len(self._lines) > 0

    def GetText(self) -> str:
        '''Returns the text to be displayed'''
        return self._lines.pop(0)

# if __name__ == "__main__":
#     anim = MultiLineGenerator(text="Hello there! My name is Slim Shady. This is a test of the multiline slide animation. It should display the text one line at a time."
#         , max_text_width=20)
#     while anim.Next():
#         print('-' * anim.max_text_width)
#         print(anim.GetText())

import random
class RandomTypeWriter(TextAnimatorBase):
    def __init__(self,  **kwargs) -> None:
        super().__init__(**kwargs)
        self._character_queue = []
        self._frameBuffer : list[str] = []
        self.Restart()
        
    def Restart(self) -> None:
        self._text = self.text[:self.max_text_width] # truncate text to max width if necessary
        self._character_queue = list(range(0, len(self.text)))
        random.shuffle(self._character_queue)
        self._frameBuffer = list(' ' * len(self.text)) # empty string of the same length as text, to be filled in as the animation progresses   

    def Next(self) -> bool:
        '''Returns true if more data is available'''
        return len(self._character_queue) > 0

    def GetText(self) -> str:
        '''Returns the text to be displayed'''
        x = self._character_queue.pop(0)
        self._frameBuffer[x] = self.text[x]
        return ''.join(self._frameBuffer)
    
# if __name__ == "__main__":
#     anim = RandomTypeWriter(text="This is a test. This animation should display the text one character at a time, in a random order."
#         , max_text_width=15)
#     cnt = 0
#     while anim.Next():
#         print(f"Frame {cnt:>3}: {anim.GetText()}")
#         cnt += 1
#     print(f"Text Length: {len(anim.text)} Frames: {cnt}")

class Slide(TextAnimatorBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Restart()
    
    def Restart(self) -> None:
        self._position = 1
        self._text = self.text[:self.max_text_width] # truncate text to max width if necessary

    def Next(self) -> bool:
        '''Returns true if more data is available'''
        return self._position <= len(self.text)

    def GetText(self) -> str:
        '''Returns the text to be displayed'''
        result = self.text[:self._position].ljust(self._max_text_width)
        self._position += 1
        return result 

# if __name__ == "__main__":
#     anim = Slide(text="0123456789ABCDEF", max_text_width=10)
#     while anim.Next():
#         print(anim.GetText())
#     print('-' * anim.max_text_width)

class TestAnimation(TextAnimatorBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._args = kwargs
        self._mlGenerator : TextAnimatorBase = MultiLineGenerator(**kwargs)
        self._slide : TextAnimatorBase = Slide(**kwargs)
        self.Restart()

    def Restart(self) -> None:
        self._mlGenerator = MultiLineGenerator(**self._args)
        self._slide = Slide(max_text_width = self.max_text_width, text=self._mlGenerator.GetText())

    def Next(self) -> bool:
        '''Returns true if more data is available'''
        return self._mlGenerator.Next() or self._slide.Next()

    def GetText(self) -> str:
        if self._slide.Next():
            text = self._slide.GetText()
            return f"|{text}|"
        if self._mlGenerator.Next():
            self._slide = Slide(max_text_width = self.max_text_width, text=self._mlGenerator.GetText())
            text = self._slide.GetText()
            return f"`{text}`"
        return '*'
        
if __name__ == "__main__":
    anim = TestAnimation(text="Hello there! My name is Slim Shady.", max_text_width=10)
    while anim.Next():
        print(anim.GetText())
    print('-' * anim.max_text_width)        
import random
from abc import ABC, abstractmethod
import textwrap
from enum import Enum
from time import sleep

class Animator(ABC):
    def __init__(self):
        self.observers = []
        self.done : bool = False

    @abstractmethod
    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        pass
    
    @property
    def is_finished(self) -> bool:
        '''Returns True if the animation is finished, False otherwise.'''
        return self.done

    def add_observer(self, observer, **kwargs):
        if observer not in self.observers:
            observer_name = kwargs.get('target_name', 'unknown')
            self.observers.append((observer, observer_name))

    def remove_observer(self, observer, **kwargs):
        if observer in self.observers:
            observer_name = kwargs.get('target_name', 'unknown')
            self.observers.remove((observer, observer_name))

    def notify_observers(self, **kwargs):
        for observer in self.observers:
            kwargs['target_name'] = observer[1]
            observer[0].animation_update(**kwargs)

class RandomTypeWriter(Animator):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__()
        self.text = ''
        self._max_text_width = kwargs.get('max_text_width', 80)
        self.position = 0
        self.count = 0
        self._lines = textwrap.wrap(text.strip(), width=self._max_text_width, expand_tabs=False)
        self.___init_queue(self._lines.pop(0))

    def ___init_queue(self, text: str) -> None:
        self.text = text.strip()
        self.__character_queue = list(range(0, len(self.text)))

        random.shuffle(self.__character_queue)
        self._frameBuffer = list(' ' * len(self.text)) # empty string of the same length as text, to be filled in as the animation progresses   
        #print(f"Initialized animator for line: {text} with character queue: {self.__character_queue}")

    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        
        x = self.__character_queue.pop(0)
        self._frameBuffer[x] = self.text[x]
        buf = ''.join(self._frameBuffer)
        if len(self.__character_queue) == 0:
            self.notify_observers(event="segment_finished" )
            #print(f"_frameBuffer='{self._frameBuffer}'")
            #print(f"Finished animating line: {''.join(self._frameBuffer)}")
            if len(self._lines) > 0:
                # Finished animating the current line, move on to the next line
                self.___init_queue(self._lines.pop(0))
            else:
                self.done = True
                #print(f"Finished animating all lines for text: {self.text}")
        return buf # makes _rendered into a string

class CharacterWipe(Animator):
    class CharacterWipeStates(Enum):
        INIT = 0
        START_FILL_ANIMATION_1 = 1
        RUNNING_FILL_ANIMATION_1 = 2
        FINISHED_FILL_ANIMATION_1 = 3

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._char = kwargs.get('wipe_char', '*')
        self._max_text_width = kwargs.get('max_text_width', 80)
        self._preText = kwargs.get('pre_text', ' ')
        self._postText = kwargs.get('post_text', ' ')
        self._state : CharacterWipe.CharacterWipeStates = self.CharacterWipeStates.START_FILL_ANIMATION_1
        self._buffer = self.__make_buffer_string(self._preText)
        self._is_first_pass : bool = True
        
    def __make_buffer_string(self, text: str) -> list[str]:
        return list(text.ljust(self._max_text_width, ' '))

    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        if self._state == self.CharacterWipeStates.START_FILL_ANIMATION_1:
            self.position = 0
            self.count = 0
            self._state = self.CharacterWipeStates.RUNNING_FILL_ANIMATION_1
        if self._state == self.CharacterWipeStates.RUNNING_FILL_ANIMATION_1:
            if self._is_first_pass:
                self._buffer[self.position] = self._char
            elif self._postText is not None:
                self._buffer[self.position] = self.__make_buffer_string(self._postText)[self.position]
            self.position += 1
            if self.position >= self._max_text_width:
                self._state = self.CharacterWipeStates.FINISHED_FILL_ANIMATION_1
        result = ''.join(self._buffer)
        if self._state == self.CharacterWipeStates.FINISHED_FILL_ANIMATION_1:
            if self._is_first_pass:
                self._is_first_pass = False
                self._state = self.CharacterWipeStates.START_FILL_ANIMATION_1
            else:
                self.done = True
        return result
    
if __name__ == "__main__":
    anim = CharacterWipe(pre_text="Hello", post_text='World!', max_text_width=20)
    print("Hello")
    while not anim.is_finished:
        print("\033[H\033[2J", end="")  # Clear console
        print(anim.next())
        sleep(0.03)
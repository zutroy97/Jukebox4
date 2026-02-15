import random
from abc import ABC, abstractmethod
import textwrap

class Animator(ABC):
    def __init__(self):
        self.observers = []

    @abstractmethod
    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        pass

    @property
    @abstractmethod
    def is_finished(self) -> bool:
        '''Returns True if the animation is finished, False otherwise.'''
        pass

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
        self.done : bool = False

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

    @property
    def is_finished(self) -> bool:
        '''Returns True if the animation is finished, False otherwise.'''
        return self.done

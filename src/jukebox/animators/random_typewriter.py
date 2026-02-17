import random
import textwrap
from time import sleep
import animation

class RandomTypeWriter2(animation.Animation):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__()
        self.position = 0
        self.count = 0
        self.text = text.strip()
        self._character_queue = list(range(0, len(self.text)))
        random.shuffle(self._character_queue)
        self._frameBuffer = list(' ' * len(self.text)) # empty string of the same length as text, to be filled in as the animation progresses   

    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        x = self._character_queue.pop(0)
        self._frameBuffer[x] = self.text[x]
        buf = ''.join(self._frameBuffer)
        if len(self._character_queue) == 0:
            self.notify_observers(event="segment_finished" )
            self.done = True
        return buf # makes _rendered into a string
    
class RandomTypeWriter(animation.Animation):
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

if __name__ == "__main__":
    width = 20
    anim = RandomTypeWriter2("Hello There, Scott Simon")
    while not anim.is_finished:
        print("\033[H\033[2J", end="")  # Clear console
        print(anim.next())
        print('-' * width)
        sleep(0.05)

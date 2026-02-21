import random
from time import sleep
from jukebox.animators import animation
from jukebox.animators.multi_line_generator import MultiLineGenerator   

class RandomTypeWriter(animation.Animation):
    def __init__(self,  **kwargs) -> None:
        super().__init__(**kwargs)
        self._character_queue = []
        self._generator = MultiLineGenerator(**kwargs)
        self._current_line : str = ''
        self._init_queue(self._generator.next())
        
    def _init_queue(self, text: str) -> None:
        self._current_line = text.strip()
        self._character_queue = list(range(0, len(self._current_line)))
        random.shuffle(self._character_queue)
        self._frameBuffer = list(' ' * self.max_text_width) # empty string of the same length as text, to be filled in as the animation progresses   

    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        x = self._character_queue.pop(0)
        self._frameBuffer[x] = self._current_line[x]
        buf = ''.join(self._frameBuffer)
        if len(self._character_queue) == 0:
            self.notify_observers(event="segment_finished" )
            if self._generator.is_finished:
                # Finished animating the current line, move on to the next line
                self._done = True
            else:
                self._init_queue(self._generator.next())
        return buf # makes _rendered into a string

if __name__ == "__main__":
    width = 75
    #anim = RandomTypeWriter2("Hello There, Scott Simon")
    #anim = RandomTypeWriterMultiLine("Hello There, Scott Simon. This is a test of the random typewriter animation. It should display the text in a random order, one character at a time, and then move on to the next line when finished.", max_text_width=width)
    anim = RandomTypeWriter(text="Hello There, Scott Simon")
    while not anim.is_finished:
        print("\033[H\033[2J", end="")  # Clear console
        print(anim.next())
        print('-' * width)
        sleep(0.05)

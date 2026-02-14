import random

class RandomTypeWriter:
    def __init__(self, text: str, **kwargs) -> None:
        self.text = text.strip()
        self._max_text_width = kwargs.get('max_text_width', 80)
        self.position = 0
        self.count = 0
        self.done : bool = False

        if len(self.text) > self._max_text_width:
            self.text = f"{self.text[0:self._max_text_width-3]}..."
        self._frames = list(range(0, len(self.text)))
        random.shuffle(self._frames)
        self._frameBuffer = list(' ' * len(self.text)) # empty string of the same length as text, to be filled in as the animation progresses

    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        x = self._frames.pop(0)
        self._frameBuffer[x] = self.text[x]
        if len(self._frames) == 0:
            self.done = True
        return ''.join(self._frameBuffer) # makes _rendered into a string

    @property
    def is_finished(self) -> bool:
        '''Returns True if the animation is finished, False otherwise.'''
        return self.done
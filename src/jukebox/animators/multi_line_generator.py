import textwrap
from jukebox.animators import animation

class MultiLineGenerator(animation.Animation):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.reset()

    def reset(self) -> None:
        self._lines = textwrap.wrap(self.text, width=self.max_text_width, expand_tabs=False)
        self._done = False

    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        buf = self._lines.pop(0)
        if len(self._lines) == 0:
            self._done = True
        return buf # makes _rendered into a string
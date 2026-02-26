import animation
from time import sleep


class Scroll(animation.Animation):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._position = 0
        self._count = 0
        self._num_trailing_spaces = kwargs.get('num_trailing_spaces', self._max_text_width)
        self._repeat :bool = kwargs.get('repeat', False)
        self._buffer = (' ' * self._max_text_width) + self.text
        self._buffer += (' ' * self._num_trailing_spaces)  # Add spacing when scrolling

    def next(self) -> str:
        if len(self._buffer) <= self._max_text_width:
            return self._buffer.ljust(self._max_text_width)
        
        display_text = self._buffer[self._position:self._position + self._max_text_width]
        self._position = (self._position + 1) % len(self._buffer)

        self._count += 1
        if self._repeat and self._count >= len(self._buffer):
            self._done = True
        return display_text.ljust(self._max_text_width)  
    
if __name__ == "__main__":
    anim = Scroll(text="Hello there! My name is Slim Shady.", max_text_width=12,repeat=True)
    while not anim.is_finished:
        print("\033[H\033[2J", end="")  # Clear console
        print(anim.next())
        sleep(0.1)

    anim = Scroll(text="Scott Simon", max_text_width=12,repeat=True)
    while not anim.is_finished:
        print("\033[H\033[2J", end="")  # Clear console
        print(anim.next())
        sleep(0.1)        

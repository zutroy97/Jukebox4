from time import sleep
from datetime import datetime, timedelta

from jukebox.animators import animation
from jukebox.animators.multi_line_generator import MultiLineGenerator  

class Slide(animation.Animation):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._position = 0

    def reset(self) -> None:
        self._position = 0
        self._done = False
    def next(self) -> str:
        if self._position >= len(self.text):
            self._done = True
            return self.text.ljust(self._max_text_width)

        result = self.text[:self._position].ljust(self._max_text_width)
        self._position += 1
        return result

class MultilineSlide(animation.Animation):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._generator = MultiLineGenerator(**kwargs)
        self._delay_between_lines = kwargs.get('delay_between_lines', 500) # in milliseconds
        self._line_timer : datetime = datetime.now()
        self.reset()


    def reset(self) -> None:
        self._generator.reset()
        self._current_animation = Slide(text=self._generator.next(), max_text_width=self.max_text_width)
        self._done = False
        self._buffer = ''

    def next(self) -> str:
        if self._current_animation.is_finished:
            if self._generator.is_finished:
                self._done = True
                return self._buffer
            self._current_animation = Slide(text=self._generator.next(), max_text_width=self.max_text_width)
            self._line_timer = datetime.now() + timedelta(milliseconds=self._delay_between_lines)
            return self._buffer
        if datetime.now() < self._line_timer:
            return self._buffer
        self._buffer = self._current_animation.next()
        return self._buffer

if __name__ == "__main__":
#    anim = Slide(text="Hello there! My name is Slim Shady.", max_text_width=25,repeat=False)
    anim = MultilineSlide(text="Hello there! My name is Slim Shady. This is a test of the multiline slide animation. It should display the text one line at a time, sliding each line in from the left, and then move on to the next line when finished.", max_text_width=25)
    while True:
        while not anim.is_finished:
            print("\033[H\033[2J", end="")  # Clear console
            print(anim.next())
            print(f"Position: {anim._current_animation._position}")
            sleep(0.1)
        anim.reset()
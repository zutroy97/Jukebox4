import random

class Animator:
    def __init__(self, text: str, **kwargs) -> None:
        self.text = text.strip()
        self._max_text_width = kwargs.get('max_text_width', 80)
        self.position = 0
        self.count = 0
        self.done : bool = False

        if len(self.text) > self._max_text_width:
            self.text = f"{self.text[0:self._max_text_width-3]}..."
        self._positions = list(range(0, len(self.text)))
        random.shuffle(self._positions)
        self._rendered = list(' ' * len(self.text))

    def next(self) -> str:
        x = self._positions.pop(0)
        self._rendered[x] = self.text[x]
        if len(self._positions) == 0:
            self.done = True
        return ''.join(self._rendered)

    @property
    def is_finished(self) -> bool:
        return self.done
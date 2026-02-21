from jukebox.displays.common.display_base import DisplayBase

class Simple(DisplayBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._lastArtist = ""
        self._lastTitle = ""

    def __del__(self):
        super().__del__()

    def clear_screen(self):
        print("\033[H\033[2J", end="")  # Clear console

    def _updateDisplay(self) -> None:
        if self.artist == self._lastArtist and self._title == self._lastTitle:
            return
        self._lastArtist = self.artist
        self._lastTitle = self._title
        self._drawConsole()

    def _drawConsole(self):
        self.clear_screen()
        print(f"Artist: {self.artist}")
        print(f"Title: {self._title}")
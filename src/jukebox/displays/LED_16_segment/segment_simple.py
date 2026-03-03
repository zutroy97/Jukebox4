from jukebox.displays.LED_16_segment.segment_base import SegmentBase

class SegmentSimple(SegmentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._lastArtist : str = ""
        self._lastTitle : str = ""

    def _updateDisplay(self) -> None:
        update_screen : bool = False
        update_screen |= self.artist != self._lastArtist
        update_screen |= self.title != self._lastTitle
        if not update_screen:
            return
        self._lastArtist = self.artist
        self._lastTitle = self.title
        self.clear_screen()
        self._display8.print(f"{self.artist[:8]:<8}")
        self._display12.print(f"{self.title[:12]:<12}")
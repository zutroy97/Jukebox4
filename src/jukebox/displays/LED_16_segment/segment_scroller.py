
from jukebox.displays.LED_16_segment.segment_base import SegmentBase

class SegmentScroller(SegmentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._artistBuffer : str = ""
        self._titleBuffer : str = ""

    def _getBufferedString(self, value: str, size: int) -> str:
        if len(value) <= size:
            return f"{value:<{size}}"
        return value + " " * size  # add spaces to the end of the string to create a gap when scrolling 
    
    def song_title_updated(self) -> None:
        self._titleBuffer = self._getBufferedString(self.title, 12)
        #self._logger.debug(f"Updated title buffer: {self._titleBuffer}")
    def song_artist_updated(self) -> None:
        self._artistBuffer = self._getBufferedString(self.artist, 8)
        #self._logger.debug(f"Updated artist buffer: {self._artistBuffer}")
    def _updateDisplay(self) -> None:
        self._display8.non_blocking_marquee(self._artistBuffer, delay=0.3, loop=(len(self._artistBuffer) >8), space_between=0)
        self._display12.non_blocking_marquee(self._titleBuffer, delay=0.3, loop=(len(self._titleBuffer) >12), space_between=0)

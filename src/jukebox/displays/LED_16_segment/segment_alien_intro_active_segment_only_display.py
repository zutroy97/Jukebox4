from jukebox.displays.LED_16_segment.animators.segment_animator import SegmentAlienIntroAnimation, SegmentAlienIntroActiveSegmentOnlyAnimation
from jukebox.displays.LED_16_segment.segment_base import SegmentBase
from jukebox.displays.common.common_enums import DisplayStateMachineState

class SegmentAlienIntroActiveSegmentOnlyDisplay(SegmentBase):
    '''Fill in random segments until the text is displayed'''
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._animatorArtist : SegmentAlienIntroActiveSegmentOnlyAnimation
        self._animatorTitle : SegmentAlienIntroActiveSegmentOnlyAnimation
    
    def _updateDisplay(self) -> None:
        if self._stateArtist in (DisplayStateMachineState.TEXT_UPDATED, DisplayStateMachineState.INIT):
            self._logger.debug(f"_stateArtist: {self._stateArtist} : {self.artist}")
            self._animatorArtist = SegmentAlienIntroActiveSegmentOnlyAnimation(text = self.artist, max_text_width=8)
            self._stateArtist = DisplayStateMachineState.ANIMATING

        data = self._animatorArtist.nextSegments()
        if len(data):
            for pos in range (len(data)):
                self._display8.set_digit_raw(pos, data[pos])

        if self._stateTitle in (DisplayStateMachineState.TEXT_UPDATED, DisplayStateMachineState.INIT):
            #self._logger.debug(f"_stateTitle: {self._stateTitle} : {self.title}")
            self._animatorTitle = SegmentAlienIntroActiveSegmentOnlyAnimation(text = self.title, max_text_width=12)
            self._stateTitle = DisplayStateMachineState.ANIMATING

        data = self._animatorTitle.nextSegments()
        if len(data):
            for pos in range (len(data)):
                self._display12.set_digit_raw(pos, data[pos])   

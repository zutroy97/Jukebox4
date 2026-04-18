import asyncio

from jukebox.displays.VFD.vfd_base import VFDBase
from jukebox.displays.common.display_base import DisplayBase
from jukebox.displays.common.common_enums import DisplayStateMachineState
from datetime import datetime, timedelta
from jukebox.animators2.text.animation_chain import AnimationChain, AnimationChainLink
from jukebox.animators2.text.slide import Slide
from jukebox.animators2.text.animator_base import TextAnimatorBase
from jukebox.animators2.text.multiline_generator import MultiLineGenerator

class VFDSimple(VFDBase):
    async def on_title_line_displayed(self, anim: TextAnimatorBase) -> bool:
        self._next_title_update = datetime.now() + timedelta(seconds=2) # display each line for 5 seconds
        self._stateTitle = DisplayStateMachineState.DELAY_START
        self._logger.debug(f"{ self._stateTitle}, setting next update to {self._next_title_update} ")
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._stateArtist = DisplayStateMachineState.IDLE
        self._stateTitle = DisplayStateMachineState.IDLE
        self.normal_display_mode()
        self._next_title_update : datetime = datetime.now() + timedelta(minutes=3600) # set to a time in the future to force an update on the first tick
        self._next_artist_update : datetime = datetime.now() + timedelta(minutes=3600)

        self._links_title_animation = [
            AnimationChainLink(MultiLineGenerator),
            AnimationChainLink(Slide, onFinished=self.on_title_line_displayed),
        ]
        self._title_anim = AnimationChain(links=self._links_title_animation, text='', max_text_width=20)

    async def loop(self) -> None:
        while self._running:
            #self._logger.debug(f"_stateTitle: {self._stateTitle} : {self.title}")
            if self._stateTitle in (DisplayStateMachineState.TEXT_UPDATED, DisplayStateMachineState.INIT):
                self._title_anim = AnimationChain(links=self._links_title_animation, text=self.title, max_text_width=20)
                await self._title_anim.Start()
                self._next_title_update = datetime.now()
                self._stateTitle = DisplayStateMachineState.ANIMATING

            if self._next_title_update < datetime.now():
                self._logger.debug(f"TICK: {self._stateTitle} : {self._next_title_update}")
                if self._stateTitle == DisplayStateMachineState.ANIMATING:
                    if (await self._title_anim.Next()):
                        # onFinished callback just changes the state to DELAY_START
                        if self._stateTitle == DisplayStateMachineState.DELAY_START:
                            pass
                        else:
                            self.set_position(0, 0)
                            text = await self._title_anim.GetText()
                            #self._logger.debug(f"Updating title line to: {text}")
                            self._ser.write(text.encode('ascii'))
                            self._next_title_update = datetime.now() + timedelta(milliseconds=100)
                    else:
                        if len(self.title) > self._title_anim.max_text_width:
                            await self._title_anim.Start() # restart the animation
                            self._next_title_update = datetime.now() + timedelta(seconds=1)
                            #self._running = False # stop the loop for testing purposes
                elif self._stateTitle == DisplayStateMachineState.DELAY_START:
                    self._stateTitle = DisplayStateMachineState.ANIMATING
            await asyncio.sleep(0.010)
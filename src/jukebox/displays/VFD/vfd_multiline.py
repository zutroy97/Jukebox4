import asyncio
from typing import Type

from jukebox.animators2.text.random_typewriter import RandomTypeWriter
from jukebox.displays.VFD.vfd_base import VFDBase
from jukebox.displays.common.display_base import DisplayBase
from jukebox.displays.common.common_enums import DisplayStateMachineState
from datetime import datetime, timedelta
from jukebox.animators2.text.animation_chain import AnimationChain, AnimationChainLink
from jukebox.animators2.text.slide import Slide
from jukebox.animators2.text.animator_base import TextAnimatorBase
from jukebox.animators2.text.multiline_generator import MultiLineGenerator

class VFDMultiLine(VFDBase):
    class VFDLineAnimator():
        async def _on_line_displayed(self, anim: TextAnimatorBase) -> bool:
            #await asyncio.sleep(1) # wait for the line to be fully displayed before starting the timer
            self._next_update_after = datetime.now() + timedelta(seconds=2) # display each line for 5 seconds
            self._state = DisplayStateMachineState.DELAY_START
            return True
            
        def __init__(self, vfd: VFDBase, line: int):
            self._vfd : VFDBase = vfd
            self._line : int = line
            self._next_update_after : datetime = datetime.now() + timedelta(days=3600)
            self._final_text_anim : Type[TextAnimatorBase] = Slide
            self._links_animation = [
                AnimationChainLink(MultiLineGenerator),
                AnimationChainLink(self._final_text_anim, onFinished=self._on_line_displayed),
            ]
            
            self._state = DisplayStateMachineState.IDLE
            self._text = ""
        
        def set_text(self, text: str) -> None:
            self._text = text
            self._state = DisplayStateMachineState.INIT
   
        def set_animator(self, anim_type: Type[TextAnimatorBase]) -> None:
            self._final_text_anim = anim_type
            self._links_animation[1] = AnimationChainLink(self._final_text_anim, onFinished=self._on_line_displayed)

        async def loop(self) -> None:
            if self._state == DisplayStateMachineState.INIT:
                self._anim = AnimationChain(links=self._links_animation, text=self._text, max_text_width=20)
                await self._anim.Start()
                self._next_update_after = datetime.now()
                self._state = DisplayStateMachineState.ANIMATING

            if self._next_update_after < datetime.now():
                if self._state == DisplayStateMachineState.ANIMATING:
                    if (await self._anim.Next()):
                        # onFinished callback just changes the state to DELAY_START
                        if self._state == DisplayStateMachineState.DELAY_START:
                            pass
                        else:
                            self._vfd.set_position(0, self._line)
                            text = await self._anim.GetText()
                            #self._logger.debug(f"Updating title line to: {text}")
                            self._vfd.write_bytes(text.encode('ascii'))
                            self._next_update_after = datetime.now() + timedelta(milliseconds=100)
                    else:
                        if len(self._text) > self._anim.max_text_width:
                            await self._anim.Start() # restart the animation
                            self._next_update_after = datetime.now() + timedelta(seconds=1)
                elif self._state == DisplayStateMachineState.DELAY_START:
                    self._state = DisplayStateMachineState.ANIMATING
            

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_brightness(0)
        self.normal_display_mode()
        self._title_animator = self.VFDLineAnimator(self, 0)
        self._title_animator.set_animator(RandomTypeWriter)
        self._artist_animator = self.VFDLineAnimator(self, 1)

    async def loop(self) -> None:
        while self._running:
            if self._stateTitle == DisplayStateMachineState.TEXT_UPDATED:
                self._title_animator.set_text(self.title)
                self._stateTitle = DisplayStateMachineState.ANIMATING
            if self._stateArtist == DisplayStateMachineState.TEXT_UPDATED:
                self._artist_animator.set_text(self.artist)
                self._stateArtist = DisplayStateMachineState.ANIMATING
            await self._title_animator.loop()
            await self._artist_animator.loop()
            await asyncio.sleep(0.010)

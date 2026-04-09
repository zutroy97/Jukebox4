import asyncio
import logging

from jukebox.animators2.text.animation_chain import AnimationChain, AnimationChainLink
from jukebox.animators2.text.animator_base import TextAnimatorBase
from jukebox.animators2.text.multiline_generator import MultiLineGenerator
from jukebox.animators2.text.slide import Slide


async def on_multiline_finished(anim: TextAnimatorBase) -> bool:
    print("MultiLineGenerator finished!")
    return True 

async def on_slide_finished(anim: TextAnimatorBase) -> bool:
    print("Slide finished!")
    return True

anim = AnimationChain(links=[
    AnimationChainLink(MultiLineGenerator, onFinished=on_multiline_finished),
    AnimationChainLink(Slide, onFinished=on_slide_finished),
], text="This is a test of the animation chain", max_text_width=20) 

async def main():
    await anim.Start()
    while await anim.Next():
        print(await anim.GetText())
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())


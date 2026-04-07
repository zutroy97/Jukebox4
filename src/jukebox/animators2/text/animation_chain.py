from typing import Type, TypeVar, Awaitable
from collections.abc import Callable

from animator_base import TextAnimatorBase
import asyncio

class AnimationChainLink():
    def __init__(self, anim_type: Type[TextAnimatorBase], onFinished: Callable[[TextAnimatorBase], Awaitable[bool]] | None = None) -> None:
        if onFinished is not None and not callable(onFinished):
            raise TypeError("onFinished must be callable or None")
        self._anim_type = anim_type
        self._onFinished = onFinished

class AnimationChain(TextAnimatorBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._links : list[AnimationChainLink] = kwargs.get('links', [])
        self._args = kwargs
        self._animators : list[TextAnimatorBase] = []

    async def Start(self) -> None:
        self._animators = []
        anim = self._links[0]._anim_type(text=self.text, max_text_width=self.max_text_width)
        await anim.Start()
        self._animators.append(anim)
        await self._initAnimation(1)

    async def Next(self) -> bool:
        '''Returns true if more data is available'''
        #return any(await anim.Next() async for anim in self._animators)
        for anim in self._animators:
            if await anim.Next():
                return True
        return False


    async def GetText(self) -> str:
        return await self._fetchNextText(len(self._animators)-1)

    async def _fetchNextText(self, index :int) -> str | None:
        if index < 0:
            return None
        anim = self._animators[index]
        if False == await anim.Next():
            link = self._links[index]
            if link._onFinished:
                result = await link._onFinished(anim)
                if False == result:
                    return None
            parentText = await self._fetchNextText(index-1)
            if parentText == None:
                return None
            anim = self._links[index]._anim_type(text=parentText, max_text_width=self.max_text_width)
            self._animators[index]=anim
        return await anim.GetText()

    async def _initAnimation(self, index: int) -> None:
        if index < len(self._links):
            anim = self._links[index]._anim_type(text= await self._animators[index-1].GetText()
                , max_text_width=self.max_text_width)
            await anim.Start()
            self._animators.append(anim)
            await self._initAnimation(index+1)
        return


from time import sleep
from multiline_generator import MultiLineGenerator
from random_typewriter import RandomTypeWriter
from slide import Slide

async def main():
    async def on_multiline_finished(anim: TextAnimatorBase) -> bool:
        print("MultiLineGenerator finished!")
        return True

    async def on_random_typewriter_finished(anim: TextAnimatorBase) -> bool:
        print("Slide finished!")
        await asyncio.sleep(1) # wait a bit before starting the next animation
        return True

    links = [
        AnimationChainLink(MultiLineGenerator, onFinished=on_multiline_finished),
        AnimationChainLink(Slide, onFinished=on_random_typewriter_finished),
    ]

    anim = AnimationChain(links=links, text="Hello there! My name is Slim Shady.", max_text_width=12)
    await anim.Start()
    while await anim.Next():
        print(await anim.GetText())
        await asyncio.sleep(0.1)

    print('-' * anim.max_text_width)

if __name__ == "__main__":
    asyncio.run(main())        
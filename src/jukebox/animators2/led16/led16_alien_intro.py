from jukebox.animators2.led16.animator_base import Led16AnimatorBase


class Led16AlienIntro(Led16AnimatorBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.i = 0

    async def GetSegments(self) -> list[int]:
        #print(f"Getting segments for text: {self.text}")
        return self.string_to_char_mask(self.text)

    async def Next(self) -> bool:
        self.i += 1
        return self.i == 1

    async def Start(self) -> None:
        self.i = 0
        return

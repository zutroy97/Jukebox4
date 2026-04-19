from jukebox.animators2.led16.animator_base import Led16AnimatorBase


class Led16StaticText(Led16AnimatorBase):
    async def GetSegments(self) -> list[int]:
        return self.string_to_char_mask(self.text)

    async def Next(self) -> bool:
        return False

    async def Start(self) -> None:
        pass

from enum import Enum
from time import sleep
from jukebox.animators import animation

class CharacterWipe(animation.Animation):
    class CharacterWipeStates(Enum):
        INIT = 0
        START_FILL_ANIMATION_1 = 1
        RUNNING_FILL_ANIMATION_1 = 2
        FINISHED_FILL_ANIMATION_1 = 3

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._char = kwargs.get('wipe_char', '*')
        self._max_text_width = kwargs.get('max_text_width', 80)
        self._preText = kwargs.get('pre_text', ' ')
        self._postText = kwargs.get('post_text', ' ')
        self._state : CharacterWipe.CharacterWipeStates = self.CharacterWipeStates.START_FILL_ANIMATION_1
        self._buffer = self.__make_buffer_string(self._preText)
        self._is_first_pass : bool = True
        
    def __make_buffer_string(self, text: str) -> list[str]:
        return list(text.ljust(self._max_text_width, ' '))

    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        if self._state == self.CharacterWipeStates.START_FILL_ANIMATION_1:
            self.position = 0
            self.count = 0
            self._state = self.CharacterWipeStates.RUNNING_FILL_ANIMATION_1
        if self._state == self.CharacterWipeStates.RUNNING_FILL_ANIMATION_1:
            if self._is_first_pass:
                self._buffer[self.position] = self._char
            elif self._postText is not None:
                self._buffer[self.position] = self.__make_buffer_string(self._postText)[self.position]
            self.position += 1
            if self.position >= self._max_text_width:
                self._state = self.CharacterWipeStates.FINISHED_FILL_ANIMATION_1
        result = ''.join(self._buffer)
        if self._state == self.CharacterWipeStates.FINISHED_FILL_ANIMATION_1:
            if self._is_first_pass:
                self._is_first_pass = False
                self._state = self.CharacterWipeStates.START_FILL_ANIMATION_1
            else:
                self.done = True
        return result
    
if __name__ == "__main__":
    anim = CharacterWipe(post_text="Hello", max_text_width=20)
    while not anim.is_finished:
        print("\033[H\033[2J", end="")  # Clear console
        print(anim.next())
        sleep(0.03)
    sleep(1)
    anim = CharacterWipe(pre_text="Hello", post_text='World!', max_text_width=20)
    while not anim.is_finished:
        print("\033[H\033[2J", end="")  # Clear console
        print(anim.next())
        sleep(0.03)        
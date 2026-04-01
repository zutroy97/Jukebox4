from jukebox.animators.slide import MultilineSlide
from time import sleep
import serial

#    anim = Slide(text="Hello there! My name is Slim Shady.", max_text_width=25,repeat=False)
# anim = MultilineSlide(text="Hello there! My name is Slim Shady. This is a test of the multiline slide animation. It should display the text one line at a time, sliding each line in from the left, and then move on to the next line when finished."
#                       , max_text_width=25
#                       , delay_between_lines=1000)
# #while True:
# while not anim.is_finished:
#     print("\033[H\033[2J", end="")  # Clear console
#     print(anim.next())
#     print('-' * 25)
#     print(f"Position: {anim._current_animation._position}")
#     sleep(0.1)
#     #anim.reset()

ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

def set_position(column: int, row: int) -> None:
    # x should be between 0 and 19, y should be between 0 and 1
    column = max(0, min(19, column))
    row = max(0, min(1, row))
    column = column + (row * 20)
    ser.write(b'\x10' + bytes([column]))


ser.write(b'\x1e') # clear screen
#            -----------------
#ser.write(b'\x10\x15') 
set_position(7,1)
ser.write(b'Hello, World!')
#ser.write(b'This is a test of the VFD display.')

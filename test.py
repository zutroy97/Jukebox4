import board
import busio as io
import adafruit_ht16k33.segments

i2c = io.I2C(board.SCL, board.SDA)
#display = adafruit_ht16k33.segments.Seg14x4(i2c)

display = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x74)


display.fill(0)
display.show()

display.print('CPY!')
display.show()
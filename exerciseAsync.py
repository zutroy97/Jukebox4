import board
from adafruit_ht16k33 import segments
import asyncio
import aiomqtt

title = ''
artist = ''

# Create the display object.
# Display connected to STEMMA QT connector.
# display = segments.Seg14x4(board.STEMMA_I2C())
# Display connected to I2C pins.
display = segments.Seg14x4(board.I2C(), address=(0x70, 0x71))  # uses board.SCL and board.SDA
display2 = segments.Seg14x4(board.I2C(), address=(0x72, 0x73, 0x74))
display.brightness = 0.20
display2.brightness = 0.20

async def task_mqtt():
    global title, artist
    async with aiomqtt.Client("127.0.0.1") as client:
        await client.subscribe("/Jukebox4/#")
        async for message in client.messages:
            if message.topic.matches("/+/title"):
                title = message.payload.decode('UTF-8')
                print("Title: ", title)
            elif message.topic.matches("/+/artist"):
                print("Artist: ", message.payload)
                artist = message.payload.decode('UTF-8')
            elif message.topic.matches("/+/album"):
                print("Album: ", message.payload)                
            else:
                print("Other Topic: ", message.topic,"\t\tPayload: ", message.payload)

# async def task_updateLeds2():
#     global title, artist
    
#     while(True):
#         didWait = False
#         if title:
#             didWait = True
#             display.print("Title   ")
#             timer = 700
#             while (timer > 0):
#                 scrollWhenNeeded2(title)
#                 timer = timer - 1
#                 await asyncio.sleep(.01)
#         if artist:
#             didWait = True
#             display.print("Artist  ")
#             timer = 700
#             while (timer > 0):
#                 scrollWhenNeeded2(artist)
#                 timer = timer - 1
#                 await asyncio.sleep(.01)
#         if not didWait:
#             await asyncio.sleep(.5)

# def scrollWhenNeeded2(message, displaySize = 12):
#     if len(message) > displaySize:
#         message = message + (' ' * displaySize)
#         display2.non_blocking_marquee(message, space_between=True)
#     else:
#         message = message + (' ' * (displaySize - len(message)))  
#         display2.print(message)


def getString(message, displaySize = 12):
    if len(message) > displaySize:
        message = message + (' ' * displaySize)
    else:
        message = message + (' ' * (displaySize - len(message)))  
    return message

def getTicks(message):
    if len(message) <= 12:
        return 500
    return (len(message)-1) * .25 * 100


async def task_updateLeds():
    global title, artist
    
    while(True):
        didWait = False
        if title:
            didWait = True
            display.print("Title   ")
            message = getString(title)
            timer = getTicks(message)
            display2.non_blocking_marquee(text=' ', delay=0.0, loop=False, space_between=False)
            while (timer > 0):
                if len(message) == 12:
                    display2.print(message)
                else:
                    display2.non_blocking_marquee(text=message, delay=0.25, loop=False, space_between=False)
                timer = timer - 1
                await asyncio.sleep(.01)
        if artist:
            didWait = True
            display.print("Artist  ")
            message = getString(artist)
            timer = getTicks(message)
            display2.non_blocking_marquee(text=' ', delay=0.0, loop=False, space_between=False)
            while (timer > 0):
                if len(message) == 12:
                    display2.print(message)
                else:
                    display2.non_blocking_marquee(text=message, delay=0.25, loop=False, space_between=False)
                timer = timer - 1
                await asyncio.sleep(.01)
        if not didWait:
            await asyncio.sleep(.5)



async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            #task_exercise("display1", display)
            task_updateLeds()
        )
        taskmqtt = tg.create_task(
            task_mqtt()
        )
asyncio.run(main())
#asy
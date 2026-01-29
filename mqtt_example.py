import asyncio
import aiomqtt


async def main():
    async with aiomqtt.Client("jukebox4.home.lan") as client:
        await client.subscribe("/Jukebox4/#")
        async for message in client.messages:
            if message.topic.matches("/+/title"):
                print("Title: ", message.payload.decode('UTF-8'))
            elif message.topic.matches("/+/artist"):
                print("Artist: ", message.payload)
            elif message.topic.matches("/+/album"):
                print("Album: ", message.payload)                
            else:
                print("Other Topic: ", message.topic,"\t\tPayload: ", message.payload)

asyncio.run(main())
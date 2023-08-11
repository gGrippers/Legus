import asyncio
from websockets.server import serve


room_to_socket = {}


async def consumer_handler(websocket):
    async for message in websocket:
        await handle_message(message, websocket)
        
async def producer_handler(websocket):
    while True:
        message = await producer(websocket)
        await websocket.send(message)
        await asyncio.sleep(0) # avoid .send blocking
             
        
async def handle_message(message: str):
    pass

async def producer(websocket):
    return 

async def blokus_server(websocket):
    await asyncio.gather(
        consumer_handler(websocket),
        producer_handler(websocket),
    )

async def main():
    async with serve(blokus_server, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
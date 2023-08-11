import asyncio
from websockets.server import WebSocketServerProtocol, serve
from dataclasses import dataclass
import json

room_to_sockets: dict[str, list[WebSocketServerProtocol]] = {}
rooms = {}


async def send_to_room(room_id: str, message: str):
    for socket in room_to_sockets[room_id]:
        await socket.send(message)


async def consumer_handler(websocket):
    async for message in websocket:
        await handle_message(message, websocket)


async def producer_handler(websocket):
    while True:
        message = await producer(websocket)
        await websocket.send(message)
        await asyncio.sleep(0)  # avoid .send blocking


async def handle_message(message: str, websocket):
    json_msg: dict = json.loads(message)
    if json_msg.get("method") == "createRoom":
        user = json_msg["payload"]["user"]
        new_room_id = json_msg["payload"]["roomId"]
        if new_room_id in rooms:
            room_already_exists_error = json.dumps(
                {"method": "roomError", "errorType": "RoomAlreadyExists"}
            )
            return await websocket.send(room_already_exists_error)
        rooms[new_room_id] = {"players": [user], "creator": user}
        room_to_sockets[new_room_id] = [websocket]
        return await websocket.send(
            json.loads({"method": "roomResponse", "payload": rooms[new_room_id]})
        )

    elif json_msg.get("method") == "joinRoom":
        user = json_msg["payload"]["user"]
        room_id = json_msg["payload"]["roomId"]
        if room_id not in rooms:
            room_does_not_exist_error = json.dumps(
                {"method": "roomError", "errorType": "RoomDoesNotExist"}
            )
            return await websocket.send(room_does_not_exist_error)
        rooms[room_id]["players"].append(user)

        await websocket.send(
            json.loads({"method": "roomResponse", "payload": rooms[room_id]})
        )  # let the player know they were able to join

        player_joined_message = {"method": "roomUpdate", "type": "join", "user": user}
        await send_to_room(
            room_id, player_joined_message
        )  # tell the others a player joined
        room_to_sockets[room_id].append(websocket)  # add the user's socket to the room


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

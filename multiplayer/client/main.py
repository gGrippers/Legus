#!/usr/bin/env python

import asyncio
import websockets
from getkey import getkey, keys

class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __dict__(self):
        return {"id": self.id, "name": self.name}

    @staticmethod
    def from_dict(dict):
        return User(dict["id"], dict["name"])

class Game:
    pass

user = User(0, "Juanito")
room = None
game = Game()

async def create_room_request(code: str):
    return {"method": "createRoom", "payload": {"roomId": code, "user": user.__dict__()}}

async def join_room_request(code: str):
    return {"method": "joinRoom", "payload": {"roomId": code, "user": user.__dict__()}}

def handle_room_message(message):
    if message["method"] == "roomUpdate":
        if message["type"] == "join":
            room["players"].append(message["user"])
        else:
            room["players"] = filter(lambda user: user.id != message["user"].id, room["players"])

def handle_room_error(error):
    error_type = error["errorType"]
    if error_type == "RoomAlreadyExists":
        print("Room already exists")
    elif error_type == "RoomDoesNotExist":
        print("Room does not exist")

def parse_room_from_response(response):
    global room
    if response["method"] != "roomResponse":
        print("Invalid response")
        return
    room = response["payload"]

def show_room_screen():
    print("Q: to exit")

async def listen_in_room(websocket):
    while True:
        message = await websocket.recv()
        handle_room_message(message)
        
async def handle_user_input_in_room(websocket):
    global room
    while True:
        key = getkey(False)
        asyncio.sleep(0) # ensure the loop doesn't hog the event loop
        # User leaves room -> they pressed q
        if key == "q":
            room = None
            return
        #Room master starts game -> they pressed s

async def main():

    while True:
        print("Welcome to Blokus")
        print("Press C to create a room or J to join a room")
        key = getkey(True)
        request = ""
        if key == "C":
            roomCode = input("Type the name of your room: ")
            request = await create_room_request(roomCode)
        elif key == "J":
            roomCode = input("Type the name of the room you'd like to join: ")
            request = await join_room_request(roomCode)
        else:
            continue
        # We want to try to get them to join a room
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            await websocket.send(request)
            room_response: str = await websocket.recv()
            if room_response["method"] == "roomError": #handle room join failure
                handle_room_error(room_response)
                continue # go back to start screen
            room = parse_room_from_response(room_response)
            # a room has been created on the server and the user now has info about it
            # now we want to listen for updates from players who join and players who leave
            show_room_screen(room) # also show any controls 
            websocket_listener = asyncio.create_task(listen_in_room(websocket))
            input_listener = asyncio.create_task(handle_user_input_in_room(websocket))

            done, pending = await asyncio.wait(
            [websocket_listener, input_listener],
            return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            
            if room is None:
                continue # go back to the beginning, the user has left the building
            
            print("TODO")
            #At this point, the user should have a room, otherwise we probably fucked up somehow
                        
                
                
        
        
   

if __name__ == "__main__":
    asyncio.run(main())
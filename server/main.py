from fastapi import FastAPI, WebSocket
from databases import Database

app = FastAPI()

@app.get("/")
async def get():
    return {"msg": "Welcome to Ziegelus!"}


@app.post("/rooms")
def create_room(room_name: str, creator_id: int):
    return {}

@app.post("/rooms/{room_id}")
def join_room(room_id: int, user_id: int):
    # assume room exists
    # tell them their color
    return {}


@app.post("/rooms/{room_id}/game")
def join_game(room_id: int, user_id: int):
    return {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await websocket.send_text(f"Message received was: {data}")

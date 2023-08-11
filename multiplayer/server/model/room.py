from typing import Dict, List, Optional
from pydantic import BaseModel

from server.model.user import Player
from server.model.enums import PlayerColor

class Room(BaseModel):
    id: int
    name: str
    creator_id: str
    players: List[Player]
    password: str

class CreateRoomRequest(BaseModel):
    room_name: str
    creator_id: int
    password: str
    
class JoinRoomRequest(BaseModel):
    user_id: int
    room_id: int
    password: str
    
    
class RoomResponse(BaseModel):
    room_id: int
    player_color: PlayerColor
    creator_id: int
    


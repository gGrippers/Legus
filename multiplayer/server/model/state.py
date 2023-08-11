from typing import List, Tuple
from pydantic import BaseModel
from enums import PlayerColor

class GridItem(BaseModel):
    piece_id: int
    owner: PlayerColor
    
class Move(BaseModel):
    owner: PlayerColor
    piece_id: int
    units_occupied: List[Tuple[int, int]]
    turn: int

class State(BaseModel):
    room_id: int
    turn: int
    board: List[List[GridItem | None]]
    currentPlayer: PlayerColor
    moves_played: List[Move]

    

from typing import List
from pydantic import BaseModel

class Piece(BaseModel):
    id: int
    name: str
    shape: List[List[bool]]
    
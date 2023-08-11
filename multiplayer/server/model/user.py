from pydantic import BaseModel

from server.model.enums import PlayerColor

class Player(BaseModel):
    id: int
    name: str
    color: PlayerColor
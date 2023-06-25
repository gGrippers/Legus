from enum import Enum
from pydantic import BaseModel


class PlayerColor(str, Enum):
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
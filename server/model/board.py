

from typing import Tuple
from pydantic import BaseModel


class Board(BaseModel):
    dimensions: Tuple[int, int]
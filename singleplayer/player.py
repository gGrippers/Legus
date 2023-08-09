from enums import Color
from piece import pieces
from player_piece import PlayerPiece

class Player:
    def __init__(self, name: str, color: Color, player_pieces: list[PlayerPiece]=None):
        if player_pieces is None:
            player_pieces = [PlayerPiece(i) for i in range(len(pieces))]
        self.name = name
        self.color = color
        self.pieces = player_pieces

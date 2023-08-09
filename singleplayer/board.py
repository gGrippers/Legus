from enums import Color
from player_piece import PlayerPiece, PieceShard
from player import Player
import numpy as np


class GridItem:

  def __init__(self, piece_id: int, owner_color: Color):
    self.piece_id = piece_id
    self.owner_color = owner_color


class Board:
  grid_size = 20

  def __init__(self, grid_items: list[list[GridItem]] = None):
    if grid_items is None:
      grid_items = [[None for j in range(Board.grid_size)]
                    for i in range(Board.grid_size)]
    self.grid_items = grid_items

  def print(self):
    print("\n".join([
      " ".join([
        "." if grid_item is None else grid_item.owner_color.value
        for grid_item in row
      ]) for row in self.grid_items
    ]))

  def print_mock(self, piece_shards: list[PieceShard], color: Color):
    valid = self.validate(piece_shards, color)
    mock = [["." if y is None else y.owner_color.value for y in x]
            for x in self.grid_items]
    for shard in piece_shards:
      i, j = shard.position[0], shard.position[1]
      mock[i][j] = color.value.lower() if valid else "x"
    print("\n".join([" ".join(x) for x in mock]))

  def out_of_bounds(self, piece_shards: list[PieceShard]) -> bool:
    for shard in piece_shards:
      i, j = shard.position[0], shard.position[1]
      if i < 0 or j < 0 or i >= len(self.grid_items) or j >= len(
          self.grid_items[0]):
        return True
    return False

  def out_of_bounds_offset(self, piece_shards: list[PieceShard]) -> tuple[int]:
    offset_i, offset_j = 0, 0
    for shard in piece_shards:
      i, j = shard.position[0], shard.position[1]
      if i < 0:
        offset_i = min(i, offset_i)
      elif i >= len(self.grid_items):
        offset_i = max(i - len(self.grid_items) + 1, offset_i)
      if j < 0:
        offset_j = min(j, offset_j)
      elif j >= len(self.grid_items):
        offset_j = max(j - len(self.grid_items) + 1, offset_j)
    return (offset_i, offset_j)

  def position_out_of_bounds(self, i: int, j: int) -> bool:
    return i < 0 or j < 0 or i >= len(self.grid_items) or j >= len(
      self.grid_items[0])

  def unit_is_color(self, i: int, j: int, color: Color):
    return not self.position_out_of_bounds(i, j) and self.grid_items[i][
      j] is not None and self.grid_items[i][j].owner_color == color

  def first_move(self, color: Color) -> bool:
    for row in self.grid_items:
      for grid_item in row:
        if grid_item is not None and grid_item.owner_color == color:
          return False
    return True

  def validate(self, piece_shards: list[PieceShard], color: Color) -> bool:
    if self.out_of_bounds(piece_shards):
      return False

    is_first_move = self.first_move(color)
    touches_corner = False
    is_corner = False
    touches_side = False
    intersects = False

    for shard in piece_shards:
      i, j = shard.position[0], shard.position[1]
      if self.grid_items[i][j] is not None:
        intersects = True
        break
      if is_first_move and (i == 0 and j == 0
                            or i == 0 and j == len(self.grid_items[0]) - 1
                            or i == len(self.grid_items) - 1 and j == 0
                            or i == len(self.grid_items) - 1
                            and j == len(self.grid_items[0]) - 1):
        is_corner = True
      if not is_first_move and (self.unit_is_color(i + 1, j, color)
                                or self.unit_is_color(i - 1, j, color)
                                or self.unit_is_color(i, j + 1, color)
                                or self.unit_is_color(i, j - 1, color)):
        touches_side = True
        break
      if not is_first_move and (self.unit_is_color(i + 1, j + 1, color)
                                or self.unit_is_color(i - 1, j + 1, color)
                                or self.unit_is_color(i + 1, j - 1, color)
                                or self.unit_is_color(i - 1, j - 1, color)):
        touches_corner = True

    return (is_first_move and is_corner or not is_first_move and touches_corner
            and not touches_side) and not intersects

  def find_possible_corners(self, player: Player):
    possible_corners = np.zeros([Board.grid_size, Board.grid_size])
    for row in range(Board.grid_size):
      for col in range(Board.grid_size):
        free_square = self.grid_items[row][col] is None
        same_color_corner = (
          self.unit_is_color(row + 1, col + 1, player.color)
          or self.unit_is_color(row - 1, col + 1, player.color)
          or self.unit_is_color(row + 1, col - 1, player.color)
          or self.unit_is_color(row - 1, col - 1, player.color))
        same_color_side = (self.unit_is_color(row + 1, col, player.color)
                           or self.unit_is_color(row - 1, col, player.color)
                           or self.unit_is_color(row, col + 1, player.color)
                           or self.unit_is_color(row, col - 1, player.color))
        if (free_square and same_color_corner and not same_color_side):
          for rOff in range(-2, 3):
            for cOff in range(-2, 3):
              nRow = min(max(row + rOff, 0), Board.grid_size - 1)
              nCol = min(max(col + cOff, 0), Board.grid_size - 1)
              possible_corners[nRow, nCol] = 1
    return possible_corners

  def any_valid_move_piece(self, piece: PlayerPiece, color: Color,
                           possible_corners):
    for a in range(2):
      for b in range(4):
        for i in range(Board.grid_size):
          for j in range(Board.grid_size):
            if possible_corners[i, j] == 1 and self.validate(
                piece.split((i, j)), color):
              return True
        piece.rotate_90()
      piece.flip_horizontal()
    return False

  def any_valid_move(self, player: Player):
    if self.first_move(player.color):
      return [True for piece in player.pieces]

    possible_corners = self.find_possible_corners(player)
    return [
      self.any_valid_move_piece(piece, player.color, possible_corners)
      for piece in player.pieces
    ]

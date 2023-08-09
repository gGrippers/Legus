from enums import Color
from player_piece import PlayerPiece
from state import State
from board import Board
from piece import pieces
from getkey import getkey, keys
import os
import math
import time

clear = "cls" if os.name == "nt" else "clear"

character_limit = 48

state = State()
page = "start"
page_data = {}
alerts = []
valid_moves = [True for piece in pieces]


def character_limiter(x, limit, append=""):
  count = 0
  i = 0
  while i < len(x):
    count += 1
    if count > limit:
      if x[i] == " ":
        x = x[:i] + "\n" + append + x[i + 1:]
        count = len(append)
        i += count
    if x[i] == "\n":
      count = 0
    i += 1
  return x


def get_printable_piece(piece: PlayerPiece, color: Color, valid: bool):
  result = []
  for i in range(len(piece.shape)):
    result.append(" ".join([
      " " if y == 0 else color.value if valid else "X" for y in piece.shape[i]
    ]))
  return result


def handle_goto_flags(flags):
  if "any_valid_moves" in flags:
    global valid_moves
    player_index = state.turn % len(state.players)
    if state.pass_tracker[player_index]:
      valid_moves = [False for piece in state.players[player_index].pieces]
      state.pass_turn()
      goto("pieces", {"index": 0, "num_buffer": ""}, ["any_valid_moves"])
      raise_alert("No valid moves so turn was skipped")
    valid_moves = state.board.any_valid_move(state.players[player_index])
    if not any(valid_moves):
      state.pass_turn()
      goto("pieces", {"index": 0, "num_buffer": ""}, ["any_valid_moves"])
      raise_alert("No valid moves so turn was skipped")


def goto(x: int, data: dict = None, flags=None):
  global page, page_data
  if data is None:
    data = {}
  if flags is None:
    flags = []
  page = x
  page_data = data
  handle_goto_flags(flags)


def display_page():
  global valid_moves
  player = state.players[state.turn % len(state.players)]
  if page == "start":
    print(
      character_limiter(
        "Welcome to Blokus!\n\nPlace your tetrominoes on the board, corner-to-corner, blocking your opponents. Maximize territory to win!\n\nPress enter to start the game.",
        character_limit))

  elif page == "board":
    print(f"Turn #{state.turn+1}: {player.name}'s Turn")
    state.board.print()

  elif page == "pieces":
    print(f"Turn #{state.turn+1}: {player.name}'s Turn")
    printable_pieces = []
    for i in range(len(player.pieces)):
      piece_num_string = f"Piece #{i+1}"
      printable_piece = get_printable_piece(player.pieces[i], player.color,
                                            valid_moves[i])
      piece_num_string += " " * (len(printable_piece[0]) -
                                 len(piece_num_string))
      printable_pieces.append([piece_num_string] + printable_piece)
    width = math.ceil(math.sqrt(len(player.pieces)))
    s = ""
    for i in range(0, len(printable_pieces), width):
      for n in range(width):
        s += (("+" + "-" * len(printable_pieces[0][0]) +
               "+") if i + n == page_data['index']
              or i + n == page_data['index'] + width else " " *
              (len(printable_pieces[0][0]) + 2))
      s += "\n"
      for j in range(len(printable_pieces[0])):
        for n in range(width):
          if i + n < len(printable_pieces):
            separator = ("|" if i + n == page_data['index'] else " ")
            s += separator + printable_pieces[i + n][j] + separator
        s += "\n"
      if i < len(printable_pieces) <= i + width:
        for n in range(width):
          s += (("+" + "-" * len(printable_pieces[0][0]) +
                 "+") if i + n == page_data['index'] else " " *
                (len(printable_pieces[0][0]) + 2))
        s += "\n"
    print(s)
    if page_data["num_buffer"] != "":
      print(f"Selecting... {page_data['num_buffer']}")

  elif page == "piece":
    piece = player.pieces[page_data["index"]]
    print(f"Turn #{state.turn+1}: {player.name}'s Turn")
    state.board.print_mock(piece.split(page_data["position"]), player.color)

  elif page == "place_piece":
    print(f"Turn #{state.turn+1}: {player.name}'s Turn")
    state.board.print_mock(
      player.pieces[page_data["index"]].split(page_data["position"]),
      player.color)
    print("Confirm piece position? (Y/n) ")

  elif page == "menu":
    s = "Menu:\n"
    for i, action in enumerate(
      ["Continue", "View Instructions", "View Help", "Exit Game"]):
      indicator = ">" if page_data["select"] == i else " "
      s += indicator + " " + action + "\n"
    print(s)

  elif page == "help":
    target = page_data["page"]
    print("Help:")
    if target == "pieces":
      print(
        character_limiter(
          " -Press WASD to move the cursor\n"
          " -Press B to view the board\n"
          " -Press any number to select piece by number\n"
          " -Press Enter to select the piece\n", character_limit, "  "))
    elif target == "board":
      print(
        character_limiter(" -Press B to go back to your pieces\n",
                          character_limit, "  "))
    elif target == "piece":
      print(
        character_limiter(
          " -Press WASD to move the piece\n"
          " -Press Q/E to rotate the piece\n"
          " -Press Z to flip the piece vertically\n"
          " -Press X to flip the piece horizontally\n"
          " -Press P to view your pieces\n"
          " -Press < or > to swap the current piece\n"
          " -Press 1, 2, 3, 4 to position the piece in a quadrant\n"
          " -Press 0 to reset the piece's position\n"
          " -Press Enter to place the piece\n", character_limit, "  "))
    else:
      pass

  elif page == "instructions":
    print(
      character_limiter(
        "Instructions:\n"
        " 1. Players: Blokus is designed for 4 players.\n"
        " 2. Board: The game is played on a square grid board with 20x20 cells.\n"
        " 3. Pieces: Each player has a set of differently shaped and colored pieces called \"tetrominoes\".\n"
        " 4. Objective: The goal is to strategically place your pieces on the board while blocking your opponents, maximizing your territory.\n"
        " 5. Placing Pieces: Players take turns placing one of their pieces on the board. Pieces must touch their own at a corner but not along edges.\n"
        " 6. Blocking: Pieces cannot touch other players' pieces, except at corners.\n"
        " 7. Passing: If a player cannot legally place a piece, they must pass their turn.\n"
        " 8. End of Game: The game ends when no player can make a legal move.\n"
        " 9. Scoring: Players count occupied cells; the one with the fewest remaining wins.\n",
        character_limit, "    "))


def raise_alert(text: str):
  alerts.append("Alert: " + text)


def update_screen():
  os.system(clear)
  if len(alerts) > 0:
    print("\n".join(alerts))
    alerts.clear()
  display_page()


update_screen()
while True:
  try:
    winner = state.check_win()
    if winner is not None:
      os.system(clear)
      print(f"{winner.name} has won!")
      state.board.print()
      if input("Would you like to play again? (Y/n) ").upper() == "Y":
        state = State()
        page = "board"
        page_data = {}
        alerts = []
        continue
      else:
        break

    player = state.players[state.turn % len(state.players)]
    key = getkey()

    if page == "start":
      if key == keys.ENTER:
        goto("pieces", {"index": 0, "num_buffer": ""})
        update_screen()

    elif page == "pieces":
      width = math.ceil(math.sqrt(len(player.pieces)))
      if key == "w":
        if page_data.get("index") > width:
          page_data["index"] -= width
        else:
          page_data["index"] = 0
        page_data["num_buffer"] = ""
      elif key == "s":
        if page_data.get("index") < len(player.pieces) - width:
          page_data["index"] += width
        else:
          page_data["index"] = len(player.pieces) - 1
        page_data["num_buffer"] = ""
      elif key == "a":
        if page_data.get("index") > 0:
          page_data["index"] -= 1
        else:
          page_data["index"] = 0
        page_data["num_buffer"] = ""
      elif key == "d":
        if page_data.get("index") < len(player.pieces) - 1:
          page_data["index"] += 1
        else:
          page_data["index"] = len(player.pieces) - 1
        page_data["num_buffer"] = ""
      elif key.isdecimal():
        buffer = int(page_data["num_buffer"] + key)
        if 0 < buffer <= len(player.pieces):
          page_data["num_buffer"] += key
          page_data["index"] = buffer - 1
      elif key == keys.BACKSPACE:
        if page_data["num_buffer"] != "":
          page_data["num_buffer"] = page_data["num_buffer"][:-1]
          if page_data["num_buffer"] != "":
            page_data["index"] = int(page_data["num_buffer"]) - 1
      elif key == keys.ENTER:
        if valid_moves[page_data["index"]]:
          goto(
            "piece", {
              "index": page_data["index"],
              "position": (Board.grid_size // 2, Board.grid_size // 2)
            })
        else:
          raise_alert("No valid moves for this piece")
      elif key == "b":
        goto(
          "board", {
            "index": page_data.get("index"),
            "num_buffer": page_data.get("num_buffer")
          })
      elif key == keys.ESCAPE:
        goto("menu", {"page": page, "data": page_data, "select": 0})
      else:
        continue
      update_screen()

    elif page == "board":
      if key == "b":
        goto(
          "pieces", {
            "index": page_data.get("index"),
            "num_buffer": page_data.get("num_buffer")
          })
      elif key == keys.ESCAPE:
        goto("menu", {"page": page, "data": page_data, "select": 0})
      else:
        continue
      update_screen()

    elif page == "piece":
      piece = player.pieces[page_data["index"]]
      i, j = page_data["position"]
      if key == "w":
        if not state.board.out_of_bounds(piece.split((i - 1, j))):
          page_data["position"] = (i - 1, j)
      elif key == "s":
        if not state.board.out_of_bounds(piece.split((i + 1, j))):
          page_data["position"] = (i + 1, j)
      elif key == "a":
        if not state.board.out_of_bounds(piece.split((i, j - 1))):
          page_data["position"] = (i, j - 1)
      elif key == "d":
        if not state.board.out_of_bounds(piece.split((i, j + 1))):
          page_data["position"] = (i, j + 1)
      elif key == "0":
        page_data["position"] = (Board.grid_size // 2, Board.grid_size // 2)
      elif key in ["1", "2", "3", "4"]:
        positions = [(Board.grid_size // 4, Board.grid_size // 4),
                     (Board.grid_size // 4, Board.grid_size * 3 // 4),
                     (Board.grid_size * 3 // 4, Board.grid_size // 4),
                     (Board.grid_size * 3 // 4, Board.grid_size * 3 // 4)]
        page_data["position"] = positions[int(key) - 1]
      elif key == "q":
        piece.rotate_neg_90()
        offset = state.board.out_of_bounds_offset(
          piece.split(page_data["position"]))
        page_data["position"] = (page_data["position"][0] - offset[0],
                                 page_data["position"][1] - offset[1])
      elif key == "e":
        piece.rotate_90()
        offset = state.board.out_of_bounds_offset(
          piece.split(page_data["position"]))
        page_data["position"] = (page_data["position"][0] - offset[0],
                                 page_data["position"][1] - offset[1])
      elif key == "x":
        piece.flip_horizontal()
        offset = state.board.out_of_bounds_offset(
          piece.split(page_data["position"]))
        page_data["position"] = (page_data["position"][0] - offset[0],
                                 page_data["position"][1] - offset[1])
      elif key == "z":
        piece.flip_vertical()
        offset = state.board.out_of_bounds_offset(
          piece.split(page_data["position"]))
        page_data["position"] = (page_data["position"][0] - offset[0],
                                 page_data["position"][1] - offset[1])
      elif key == "p":
        goto("pieces", {"index": page_data.get("index"), "num_buffer": ""})
      elif key == keys.LEFT:
        while True:
          if page_data["index"] > 0:
            page_data["index"] -= 1
          else:
            page_data["index"] = len(player.pieces) - 1
          if valid_moves[page_data["index"]]:
            break
        offset = state.board.out_of_bounds_offset(
          player.pieces[page_data["index"]].split(page_data["position"]))
        page_data["position"] = (page_data["position"][0] - offset[0],
                                 page_data["position"][1] - offset[1])
      elif key == keys.RIGHT:
        while True:
          if page_data["index"] < len(player.pieces) - 1:
            page_data["index"] += 1
          else:
            page_data["index"] = 0
          if valid_moves[page_data["index"]]:
            break
        offset = state.board.out_of_bounds_offset(
          player.pieces[page_data["index"]].split(page_data["position"]))
        page_data["position"] = (page_data["position"][0] - offset[0],
                                 page_data["position"][1] - offset[1])
      elif key == keys.ENTER:
        if state.board.validate(piece.split(page_data["position"]),
                                player.color):
          state.place_piece(player, piece, page_data["position"])
          goto("pieces", {"index": 0, "num_buffer": ""}, ["any_valid_moves"])
        else:
          raise_alert("Piece is in an invalid position")
      elif key == keys.ESCAPE:
        goto("menu", {"page": page, "data": page_data, "select": 0})
      else:
        continue
      update_screen()

    elif page == "menu":
      actions = ["continue", "instructions", "help", "exit"]
      if key == "w":
        if page_data["select"] > 0:
          page_data["select"] -= 1
      elif key == "s":
        if page_data["select"] < len(actions) - 1:
          page_data["select"] += 1
      elif key == keys.ENTER:
        action = actions[page_data["select"]]
        if action == "continue":
          goto(page_data["page"], page_data["data"])
        elif action == "exit":
          break
        else:
          goto(
            action, {
              "page": page_data["page"],
              "data": page_data["data"],
              "select": page_data["select"]
            })
      elif key == keys.ESCAPE:
        goto(page_data["page"], page_data["data"])
      else:
        continue
      update_screen()

    elif page == "instructions" or page == "help":
      if key == keys.ESCAPE:
        goto(
          "menu", {
            "page": page_data["page"],
            "data": page_data["data"],
            "select": page_data["select"]
          })
        update_screen()

  except Exception as e:
    raise_alert(f"Error has occurred, {str(e)}")

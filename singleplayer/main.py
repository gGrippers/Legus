from enums import Color
from player_piece import PlayerPiece
from state import State
from board import Board
from getkey import getkey,key
import os
import math
import time

clear = "cls" if os.name == "nt" else "clear"

character_limit = 48

state = State()
page = "start"
page_data = {}
alerts = []


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


def get_printable_piece(piece: PlayerPiece, color: Color):
  result = []
  for i in range(len(piece.shape)):
    result.append(" ".join(
      [" " if y == 0 else color.value for y in piece.shape[i]]))
  return result


def print_target_piece(piece: PlayerPiece, color: Color):
  result = "      |    \n"
  for i in range(len(piece.shape)):
    result += ("--" if i == 2 else "  ") + " ".join(
      [" " if y == 0 else color.value
       for y in piece.shape[i]]) + ("--" if i == 2 else "") + "\n"
  result += "      |    "
  print(result)


def parse_position(position_code):
  if len(position_code) != 2:
    return (-1, -1)
  return (ord(position_code[0].upper()) - ord("A"),
          ord(position_code[1].upper()) - ord("A"))


def goto(x: int, data: dict = None):
  global page, page_data
  if data is None:
    data = {}
  page = x
  page_data = data


def display_page():
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
      piece_num_string = f"Pc #{i+1}"
      printable_piece = get_printable_piece(player.pieces[i], player.color)
      piece_num_string += " " * (len(printable_piece[0]) -
                                 len(piece_num_string))
      if i == page_data['index']:
        piece_num_string = piece_num_string[:-1] + "X"
      printable_pieces.append([piece_num_string] + printable_piece)
    width = 5  #math.ceil(math.sqrt(len(player.pieces)))
    s = ""
    for i in range(0, len(printable_pieces), width):
      for j in range(len(printable_pieces[0])):
        for n in range(width):
          if i + n < len(printable_pieces):
            s += printable_pieces[i + n][j] + "  "
        s += "\n"
    print(s)
    if page_data["num_buffer"] != "":
      print(f"Buffer... {page_data['num_buffer']}")
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
  elif page == "help":
    print(
      character_limiter(
        "Help:\n"
        " -instructions: Show the game's instructions\n"
        " -board: Show the game board\n"
        " -pieces: Show your current pieces\n"
        " -piece [x]: Focus on a specific piece\n"
        " -rotate [+/-]+: Rotate the focused piece\n"
        " -flip [h/v]: Flip the focused piece\n"
        " -place [RowCol]: Place the focused piece\n"
        " -pass: Pass your turn onto the next player\n"
        " -exit: Exit the game\n", character_limit, "  "))
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
    player = state.players[state.turn % len(state.players)]

    if state.pass_tracker[state.turn % len(
        state.players)] or not state.board.any_valid_move(player):
      state.pass_turn()
      goto("pieces", {"index": 0, "num_buffer": ""})
      raise_alert("You have no valid moves")
      update_screen()
      continue

    key = getkey()

    if page == "start":
      if key == keys.ENTER:
        goto("pieces", {"index": 0, "num_buffer": ""})
        update_screen()
    elif page == "pieces":
      if key == "w":
        if page_data.get("index") > 5:
          page_data["index"] -= 5
        else:
          page_data["index"] = 0
        page_data["num_buffer"] = ""
        update_screen()
      elif key == "s":
        if page_data.get("index") < len(player.pieces) - 5:
          page_data["index"] += 5
        else:
          page_data["index"] = len(player.pieces) - 1
        page_data["num_buffer"] = ""
        update_screen()
      elif key == "a":
        if page_data.get("index") > 0:
          page_data["index"] -= 1
        else:
          page_data["index"] = 0
        page_data["num_buffer"] = ""
        update_screen()
      elif key == "d":
        if page_data.get("index") < len(player.pieces) - 1:
          page_data["index"] += 1
        else:
          page_data["index"] = len(player.pieces) - 1
        page_data["num_buffer"] = ""
        update_screen()
      elif key.isdecimal():
        buffer = int(page_data["num_buffer"] + key)
        if 0 < buffer <= len(player.pieces):
          page_data["num_buffer"] += key
          page_data["index"] = buffer - 1
          update_screen()
      elif key == keys.BACKSPACE:
        if page_data["num_buffer"] != "":
          page_data["num_buffer"] = page_data["num_buffer"][:-1]
          if page_data["num_buffer"] != "":
            page_data["index"] = int(page_data["num_buffer"]) - 1
          else:
            page_data["index"] = 0
          update_screen()
      elif key == keys.ENTER:
        goto(
          "piece", {
            "index": page_data["index"],
            "position": (Board.grid_size // 2, Board.grid_size // 2)
          })
        update_screen()
      elif key == "b":
        goto(
          "board", {
            "index": page_data.get("index"),
            "num_buffer": page_data.get("num_buffer")
          })
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
      elif key == "q":
        piece.rotate_neg_90()
      elif key == "e":
        piece.rotate_90()
      elif key == "x":
        piece.flip_horizontal()
      elif key == "z":
        piece.flip_vertical()
      elif key == "p":
        goto("pieces", {"index": page_data.get("index"), "num_buffer": ""})
      elif key == keys.LEFT:
        if page_data["index"] > 0:
          page_data["index"] -= 1
        else:
          page_data["index"] = len(player.pieces) - 1
      elif key == keys.RIGHT:
        if page_data["index"] < len(player.pieces) - 1:
          page_data["index"] += 1
        else:
          page_data["index"] = 0
      elif key == keys.ENTER:
        if state.board.validate(piece.split(page_data["position"]),
                                player.color):
          state.place_piece(player, piece, page_data["position"])
          goto("pieces", {"index": 0, "num_buffer": ""})
      else:
        continue
      update_screen()
    # elif command == "board":
    #   goto("board")
    # elif command == "pieces":
    #   goto("pieces")
    # elif command.startswith("piece "):
    #   index = int(command[len("piece "):]) - 1
    #   if index >= 0 and index < len(player.pieces):
    #     goto("piece", {"piece": player.pieces[index]})
    #   else:
    #     raise_alert("Invalid piece index")
    # elif page == "piece" and command.startswith("rotate "):
    #   for c in command[len("rotate "):]:
    #     if c == "+":
    #       page_data["piece"].rotate_90()
    #     elif c == "-":
    #       page_data["piece"].rotate_neg_90()
    # elif page == "piece" and command.startswith("place "):
    #   if state.board.validate(
    #       page_data["piece"].split(parse_position(command[len("piece "):])),
    #       player.color):
    #     goto(
    #       "place_piece", {
    #         "position": parse_position(command[len("piece "):]),
    #         "piece": page_data["piece"]
    #       })
    #   else:
    #     raise_alert("Piece cannot be placed in that location")
    # elif page == "piece" and command.startswith("flip "):
    #   dir = command[len("flip "):]
    #   if dir == "horizontal" or dir == "h":
    #     page_data["piece"].flip_horizontal()
    #   elif dir == "vertical" or dir == "v":
    #     page_data["piece"].flip_vertical()
    #   else:
    #     raise_alert("Piece cannot be flipped in that direction")
    # elif page == "place_piece" and command.upper() == "Y":
    #   if state.place_piece(player, page_data["piece"], page_data["position"]):
    #     raise_alert("Piece was placed")
    #     goto("board")
    #   else:
    #     raise_alert("Piece was not placed")
    # elif page == "place_piece" and command.lower() == "n":
    #   goto("piece", {"piece": page_data["piece"]})
    # elif command == "pass":
    #   state.pass_turn()
    #   raise_alert("Player has passed")
    #   goto("board")
    # elif command == "help":
    #   goto("help")
    # elif command == "instructions":
    #   goto("instructions")
    # elif command == "exit":
    #   break
    # else:
    #   raise_alert("Invalid command")

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
      else:
        break
  except:
    raise_alert("Error has occurred")
  finally:
    time.sleep(1 / 20)

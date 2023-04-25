from enum import Enum, auto
from random import choice
from time import sleep
import socket as sock

from constants import ADDRESS
from tile_bag import TileBag
from player import Player
from board import Board

class Server:
    def __init__(self) -> None:
        self.socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.socket.bind(ADDRESS)
        self.socket.listen(2)

        self.board = Board()
        self.tile_bag = TileBag()
        self.turn = 0

    def run(self) -> None:
        self.listen()
        print("Closing sockets...")
        for player in self.players:
            player.disconnect()
        self.socket.close()
        print("Socket closed.")

    def listen(self) -> None:
        print("Listening for connections...")
        self.players = [Player(self, 1, *self.socket.accept()), Player(self, 2, *self.socket.accept())]
        print("Both players have connected!")
        print("Creating receive threads...")
        for player in self.players:
            player.create_thread()
        print("Both threads have been created!")

        sleep(0.02)
        for player in self.players:
            player.send({"type": MessageType.REPLENISH.name, "message": [self.tile_bag.get() for _ in range(7)]})

        sleep(0.02)
        first_player = choice(self.players)
        first_player.send({"type": MessageType.TURN.name, "message": None})
        self.turn = self.players.index(first_player)

        while all([player.alive for player in self.players]):
            for player in self.players:
                if player.messages.empty(): continue
                message = player.messages.get()
                handler = getattr(self, f"message_type_{message['type'].lower()}")
                handler(player, message)

    def message_type_place(self, player: Player, message: dict):
        print(f"Player {player.id} made a move: {message['message']}")

        old_board = [row[:] for row in self.board.data]
        for pos, letter in message["message"].items():
            self.board[pos] = letter

        if not self.validate_placement(message["message"]):
            print(f"Player {player.id} made an invalid move")
            self.board.data = old_board
            player.send({"type": MessageType.INVALID.name, "message": None})
            return

        for other in self.players:
            if other is player: continue
            other.send(message)

        tiles_used = len(message["message"])
        print(f"Granting player {player.id} {tiles_used} tiles")
        player.send({"type": MessageType.REPLENISH.name, "message": [self.tile_bag.get() for _ in range(tiles_used)]})

        sleep(0.02)
        self.turn = (self.turn + 1) % 2
        self.players[self.turn].send({"type": MessageType.TURN.name, "message": None})

    def validate_placement(self, tiles: dict[tuple[int, int], str]) -> bool:
        horizontal = len(set([pos[1] for pos in tiles])) == 1 # All y coord equal
        vertical = len(set([pos[0] for pos in tiles])) == 1   # All x coord equal
        if not horizontal and not vertical:
            return False

        # One letter placement
        if horizontal and vertical:
            pos = next(iter(tiles))
            if self.board[(pos[0] - 1, pos[1])] or self.board[(pos[0] + 1, pos[1])]:
                # more stuff coming here? (store word)
                return True
            if self.board[(pos[0], pos[1] - 1)] or self.board[(pos[0], pos[1] + 1)]:
                # more stuff coming here? (store word)
                return True

        first_move = (8, 8) in tiles

        if horizontal: # Horizontal word
            start = next(iter(tiles))
            found = connected = 1

            left = start[0] - 1
            while self.board[(left, start[1])]:
                connected += 1
                found += (left, start[1]) in tiles
                left -= 1

            right = start[0] + 1
            while self.board[(right, start[1])]:
                connected += 1
                found += (right, start[1]) in tiles
                right += 1

            # If the placement is disconnected from everything
            if connected == found and not first_move:
                return False
            return found == len(tiles)

        else: # Vertical word
            start = next(iter(tiles))
            found = connected = 1

            top = start[1] - 1
            while self.board[(start[0], top)]:
                connected += 1
                found += (start[0], top) in tiles
                top -= 1

            bottom = start[1] + 1
            while self.board[(start[0], bottom)]:
                connected += 1
                found += (start[0], bottom) in tiles
                bottom += 1

            # If the placement is disconnected from everything
            if connected == found and not first_move:
                return False
            return found == len(tiles)

# All types of messages that can be sent to or received from a client
class MessageType(Enum):
    PLACE = auto()
    REPLENISH = auto()
    TURN = auto()
    INVALID = auto()
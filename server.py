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
        self.invalid_reason = ""

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

        if not self.validate_placement(message["message"]) and not self.validate_words(message["message"]):
            print(f"Player {player.id} made an invalid move")
            self.board.data = old_board
            player.send({"type": MessageType.INVALID.name, "message": self.invalid_reason})
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

        # Neither vertical nor horizontal: not in a straight line
        if not horizontal and not vertical:
            self.invalid_reason = InvalidReason.NotInStraightLine.value
            return False

        if horizontal:
            left = min(tiles, key=lambda pos: pos[0])[0]
            right = max(tiles, key=lambda pos: pos[0])[0]
            y = next(iter(tiles))[1]
            for x in range(left, right):
                if not self.board[(x, y)]:
                    self.invalid_reason = InvalidReason.SeparateWords.value
                    return False
        elif vertical:
            top = min(tiles, key=lambda pos: pos[1])[1]
            bottom = max(tiles, key=lambda pos: pos[1])[1]
            x = next(iter(tiles))[0]
            for y in range(top, bottom):
                if not self.board[(x, y)]:
                    self.invalid_reason = InvalidReason.SeparateWords.value
                    return False

        return True

# All types of messages that can be sent to or received from a client
class MessageType(Enum):
    PLACE = auto()
    REPLENISH = auto()
    TURN = auto()
    INVALID = auto()

class InvalidReason(Enum):
    NotInStraightLine = "All tiles must be placed on the same row or column!"
    SeparateWords = "All tiles must be placed to form the same word!"
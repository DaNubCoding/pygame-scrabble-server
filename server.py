from enum import Enum, auto
from random import choice
from time import sleep
import socket as sock

from constants import ADDRESS
from tile_bag import TileBag
from player import Player

class Server:
    def __init__(self) -> None:
        self.socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.socket.bind(ADDRESS)
        self.socket.listen(2)

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
        print(f"Player {player.id} made a move")
        for other in self.players:
            if other is player: continue
            other.send(message)

        tiles_used = len(message["message"])
        print(f"Granting player {player.id} {tiles_used} tiles")
        player.send({"type": MessageType.REPLENISH.name, "message": [self.tile_bag.get() for _ in range(tiles_used)]})

        sleep(0.02)
        self.turn = (self.turn + 1) % 2
        self.players[self.turn].send({"type": MessageType.TURN.name, "message": None})

# All types of messages that can be sent to or received from a client
class MessageType(Enum):
    PLACE = auto()
    REPLENISH = auto()
    TURN = auto()
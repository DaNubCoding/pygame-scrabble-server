import socket as sock

from constants import ADDRESS
from player import Player

class Server:
    def __init__(self) -> None:
        self.socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.socket.bind(ADDRESS)
        self.socket.listen(2)

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

        while all([player.alive for player in self.players]):
            for player in self.players:
                if player.messages.empty(): continue
                self.handle_message(player)

    def handle_message(self, player: Player):
        message = player.messages.get()
        print(f"Player {player.id} made a move")
        for other in self.players:
            if other is player: continue
            other.send(message)
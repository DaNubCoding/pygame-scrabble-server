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
        print("Closing server socket...")
        self.socket.close()
        print("Socket closed, program will exit.")

    def listen(self) -> None:
        print("Listening for connections...")
        self.player1 = Player(self, 1, *self.socket.accept())
        self.player2 = Player(self, 2, *self.socket.accept())
        print("Both players have connected!")
        print("Creating receive threads...")
        self.player1.create_thread()
        self.player2.create_thread()
        print("Both threads have been created!")

        while self.player1.alive and self.player2.alive:
            if not self.player1.messages.empty():
                message = self.player1.messages.get()
                print(f"Player 1: {message}")
                self.player2.send(message)
            if not self.player2.messages.empty():
                message = self.player2.messages.get()
                print(f"Player 2: {message}")
                self.player1.send(message)
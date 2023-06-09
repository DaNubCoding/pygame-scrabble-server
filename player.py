from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server import Server

from threading import Thread
from queue import Queue
from typing import Any
import socket as sock
import pickle

class Player:
    def __init__(self, server: Server, _id: int, socket: sock.socket, address: tuple[str, int]) -> None:
        self.server = server
        self.id = _id
        self.socket = socket
        self.address = address
        self.messages = Queue()
        self.dead = False

        self.log("Connected")

    def log(self, message: str) -> None:
        print(f"[Player {self.id}] {message}")

    def receive(self) -> None:
        try:
            pickled = self.socket.recv(1024)
        except ConnectionResetError:
            self.quit_queue.put(True)
            self.log("Connection lost")
        except ConnectionAbortedError:
            self.quit_queue.put(True)
            self.log("Forcibly disconnected")
        else:
            self.messages.put(pickle.loads(pickled))

    def forever_receive(self) -> None:
        self.log("Receive thread started")
        while self.quit_queue.empty():
            self.receive()
        self.log("Receive thread ended")

    def create_thread(self) -> None:
        self.quit_queue = Queue(maxsize=1)
        self.receive_thread = Thread(target=self.forever_receive)
        self.receive_thread.start()

    def send(self, message: Any) -> None:
        pickled = pickle.dumps(message)
        self.socket.send(pickled)

    @property
    def alive(self) -> bool:
        return self.quit_queue.empty()

    def disconnect(self) -> None:
        self.socket.close()
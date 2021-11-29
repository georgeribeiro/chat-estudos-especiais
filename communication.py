import socket


class Client:
    def __init__(self, connection: socket.socket) -> None:
        self.conn = connection
        self.username: str = None

    def auth(self, username: str):
        self.username = username

    def __eq__(self, o: "Client") -> bool:
        return self.conn == o.conn

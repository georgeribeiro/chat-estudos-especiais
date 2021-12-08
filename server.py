import socket
from typing import List, Any
import threading

"""
https://www.geeksforgeeks.org/simple-chat-room-using-python/
"""


class Client:
    def __init__(self, conn: socket.socket, addr: Any, username: str = None) -> None:
        self.conn = conn
        self.addr = addr
        self.username = username


class Server:
    def __init__(self, host: str, port: int) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))
        self._clients: List[Client] = []

    def auth(self, conn: socket.socket, username: str) -> bool:
        for c in self._clients:
            if c.conn == conn:
                c.username = username
                return True
        return False

    def listen(self, max_connections):
        self._sock.listen(max_connections)
        while True:
            conn, addr = self._sock.accept()
            c = Client(conn, addr)
            self._clients.append(c)
            threading.Thread(target=self._clientthread, args=(c))

    def _response(self, c: Client, code: str, message: str = ""):
        data = " ".join([s for s in (code, message) if s])
        c.conn.send(data.encode())

    def _clientthread(self, c: Client):
        while True:
            try:
                data = c.conn.recv(2048)
                if data:
                    message = data.decode()
                    match message.split():
                        case ["AUTH", username]:
                            c.username = username
                            self._response(c, "OK")
                        case _:
                            self._response(c, "ERROR", "invalid action")
            except Exception as e:
                print(e)
                continue


def main():
    server = Server("", 5555)
    print(f"Server running in port 5555")
    server.listen(100)


if __name__ == "__main__":
    main()

import socket
from typing import List, Tuple, Any
import threading

"""
https://www.geeksforgeeks.org/simple-chat-room-using-python/
"""

HOST = "127.0.0.1"
PORT = 5555


class Client:
    def __init__(self, conn: socket.socket, addr: Any, username: str = None) -> None:
        self.conn = conn
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

    def listen(self):
        self._sock.listen(100)
        while True:
            conn, addr = self._sock.accept()
            c = Client(conn, addr)
            self._clients.append(c)
            threading.Thread(target=self._clientthread, args=(c))

    def _clientthread(c: Client):
        pass


def clientthread(conn: socket.socket):
    while True:
        try:
            message = conn.recv(2048)
            if message:
                message = message.decode()
                if message.startswith("AUTH"):
                    try:
                        _, username = message.split(" ")
                        if auth(conn, username):
                            ret = b"OK"
                        else:
                            ret = b"ERROR connection not found"
                    except:
                        ret = b"ERROR invalid auth message"
                    conn.send(ret)
                elif message.startswith("HANDSHAKE"):
                    try:
                        _, username, pubkey = message.split(" ")
                        other = get_conn_by_username(username)
                        if other is None:
                            ret = b"ERROR username not found"
                            conn.send(ret)
                        else:
                            msg = f"HANDSHAKEREQUEST {get_username_by_conn(conn)} {pubkey}"
                            ret = msg.encode()
                            other.send(ret)
                    except:
                        pass
            else:
                remove(conn)
        except:
            continue


def broadcast(message: str, conn: socket.socket):
    for client in clients:
        if client != conn:
            try:
                client.send(message)
            except:
                client.close()
                remove(clients)


def remove(conn):
    if conn in clients:
        clients.remove(conn)


def main():
    server = create_server(HOST, PORT)
    server.listen(100)
    print(f"Server running in port {PORT}")
    while True:
        conn, addr = server.accept()
        clients.append((conn, None))
        start_new_thread(clientthread, (conn,))


if __name__ == "__main__":
    main()

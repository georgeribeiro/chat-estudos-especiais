import socket
from typing import List, Tuple, Any
from _thread import start_new_thread

"""
https://www.geeksforgeeks.org/simple-chat-room-using-python/
"""

HOST = "127.0.0.1"
PORT = 5555


clients: List[Tuple[socket.socket, Any]] = []


def create_server(host, port) -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    return server


def auth(conn: socket.socket, username: str) -> bool:
    for i in range(len(clients)):
        if clients[i][0] == conn:
            clients[i] = (conn, username)
            return True
    return False


def get_conn_by_username(username) -> socket.socket:
    for c in clients:
        if c[1] == username:
            return c[0]
    return None


def get_username_by_conn(conn) -> str:
    for c in clients:
        if c[0] == conn:
            return c[1]
    return None


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
    while True:
        conn, addr = server.accept()
        clients.append((conn, None))
        start_new_thread(clientthread, (conn,))


if __name__ == "__main__":
    main()

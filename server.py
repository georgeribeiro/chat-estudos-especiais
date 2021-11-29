import socket
import argparse
from typing import List, Tuple
from _thread import start_new_thread
from communication import Client

"""
https://www.geeksforgeeks.org/simple-chat-room-using-python/
"""


clients: List[Client] = []


def create_server(host, port) -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    return server


def clientthread(c: Client):
    c.conn.send(b"Bem vindo ao chat!")

    while True:
        try:
            message = c.conn.recv(2048)
            if message:
                print(message)
                broadcast(message, c.conn)
            else:
                remove(c.conn)
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


def get_parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Servidor do chat para mostrar algoritmos de criptografia"
    )
    parser.add_argument("-H", "--host", type=str, default="localhost")
    parser.add_argument("-p", "--port", type=int, required=True)
    return parser


def main():
    parser = get_parse()
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    server.listen(100)
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        start_new_thread(clientthread, (conn,))


if __name__ == "__main__":
    main()

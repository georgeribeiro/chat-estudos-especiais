import socket
import argparse
from typing import List, Tuple

"""
https://www.geeksforgeeks.org/simple-chat-room-using-python/
"""

clients: Tuple[str, List[socket.socket]] = []


def create_server(host, port) -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    return server


def clientthread(conn: socket.socket):
    conn.send("Bem vindo ao chat!")

    while True:
        try:
            message = conn.recv(2048)
            print(message)
        except:
            continue


def broadcast(message: str, conn: socket.socket):
    for client in clients:
        if client != conn:
            try:
                client.send(message)
            except:
                client.close()


def remove(conn):
    if conn in clients:
        list


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
    server.close()


if __name__ == "__main__":
    main()

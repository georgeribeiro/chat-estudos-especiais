import socket
import argparse
import sys
import select

HOST = "127.0.0.1"
PORT = 5555


def connect_to_server(host: str, port: int) -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((host, port))
    return server


def auth(server: socket.socket, username):
    message = f"AUTH {username}"
    message = message.encode()
    server.send(message)
    data = server.recv(2048)
    sys.stdout.write(data.decode())
    sys.stdout.flush()


def main():
    server = connect_to_server(HOST, PORT)
    sys.stdout.write("Username: ")
    sys.stdout.flush()
    username = sys.stdin.readline().rstrip("\n")
    auth(server, username)

    # while True:
    #     sockets_list = [sys.stdin, server]

    #     read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

    #     for sock in read_sockets:
    #         if sock == server:
    #             message = sock.recv(2048)
    #             print(message)
    #         else:
    #             message = sys.stdin.readline()
    #             server.send(message.encode())
    #             sys.stdout.write(message)
    #             sys.stdout.flush()
    server.close()


if __name__ == "__main__":
    main()

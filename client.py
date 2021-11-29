import socket
import argparse
import sys
import select


def get_parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Servidor do chat para mostrar algoritmos de criptografia"
    )
    parser.add_argument("-H", "--host", type=str, default="localhost")
    parser.add_argument("-p", "--port", type=int, required=True)
    return parser


def connect_to_server(host: str, port: int) -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((host, port))
    return server


def main():
    parser = get_parse()
    args = parser.parse_args()
    server = connect_to_server(args.host, args.port)
    while True:
        sockets_list = [sys.stdin, server]

        read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

        for sock in read_sockets:
            if sock == server:
                message = sock.recv(2048)
                print(message)
            else:
                message = sys.stdin.readline()
                server.send(message.encode())
                sys.stdout.write(message)
                sys.stdout.flush()
    server.close()


if __name__ == "__main__":
    main()

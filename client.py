import socket
from sys import path
from Crypto.PublicKey import RSA
from Crypto import Random
from pathlib import Path

HOST = "127.0.0.1"
PORT = 5555
HERE = Path(__file__).resolve().parent


def connect_to_server(host: str, port: int) -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((host, port))
    return server


def auth(server: socket.socket, username) -> bool:
    message = f"AUTH {username}"
    message = message.encode()
    server.send(message)
    data = server.recv(2048)
    return data.decode().rstrip("\n") == "OK"


def generate_rsa_keys(username: str, length: int = 2048):
    priv_key = RSA.generate(length, Random.new().read)
    pub_key = priv_key.publickey()
    return priv_key, pub_key


def save_keys(priv_key: RSA._RSAobj, pub_key: RSA._RSAobj, username: str):
    with open(HERE.joinpath(f"{username}.key"), "w") as priv_file:
        print(f"{priv_key.exportKey().decode()}", file=priv_file)
    with open(HERE.joinpath(f"{username}.pub"), "w") as pub_file:
        print(f"{pub_key.exportKey().decode()}", file=pub_file)


def key_is_generated(username):
    path = HERE.joinpath(f"{username}.key")
    return path.exists()


def handshake(user1, user2):
    pass


def main():
    server = connect_to_server(HOST, PORT)
    username = input("Username: ")
    if not auth(server, username):
        print("Authentication Failed")
    if not key_is_generated(username):
        print("Generating RSA private and public key")
        priv, pub = generate_rsa_keys(username, 2048)
        save_keys(priv, pub, username)
    server.close()


if __name__ == "__main__":
    main()

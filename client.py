import pathlib
import socket
import threading
from Crypto.PublicKey import RSA
from Crypto import Random
from pathlib import Path
import os
import platform

HERE = Path(__file__).resolve().parent


class Client:
    def __init__(self) -> None:
        self.username: str = None
        self.user: User = None
        self._server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host: str, port: int) -> None:
        self._server.connect((host, port))
        threading.Thread(target=self._listen_server)

    def send(self, action: str, message: str):
        data = " ".join([s for s in (action, message) if s])
        self._server.send(data.encode())

    def auth(self, username):
        self.username = username
        self.user = User(username)
        self.send("AUTH", username)

    def handshake(self, username):
        pass

    def _listen_server(self):
        while True:
            data = self._server.recv(2048)
            message = data.decode()
            if message:
                print(message)


class User:
    def __init__(self, username: str) -> None:
        self.username = username
        self._privkey = None
        self._pubkey = None

    def generate_keys(self, length: int = 2048) -> None:
        self._privkey = RSA.generate(length, Random.new().read)

    def save_keys(self) -> None:
        with open(HERE.joinpath(f"{self.username}.key"), "w") as priv_file:
            print(f"{self.privkey.exportKey().decode()}", file=priv_file)
        with open(HERE.joinpath(f"{self.username}.pub"), "w") as pub_file:
            print(f"{self.pubkey.exportKey().decode()}", file=pub_file)

    def exist_keys(self):
        path = HERE.joinpath(f"{self.username}.key")
        return path.exists()

    def load_keys(self) -> bool:
        if self.exist_keys():
            with self.privkey_file().open("r") as f:
                pkey = f.read()
                self._privkey = RSA.importKey(pkey)
            return True
        else:
            return False

    def remove_keys(self):
        self.privkey_file().unlink()
        self.pubkey_file().unlink()

    def print_keys(self):
        print(self.privkey)

    @property
    def privkey(self) -> RSA._RSAobj:
        return self._privkey

    @property
    def pubkey(self) -> RSA._RSAobj:
        return self._privkey.publickey()

    def privkey_file(self) -> pathlib.Path:
        return HERE.joinpath(f"{self.username}.key")

    def pubkey_file(self) -> pathlib.Path:
        return HERE.joinpath(f"{self.username}.pub")

def clear():
    so = platform.system()
    os.system('cls' if so == 'Windows' else 'clear')


def generate_keys(client: Client):
    client.user.generate_keys()
    client.user.save_keys()
    input("Chaves geradas com sucesso!")


def menu(client: Client):
    menu = """Escolha uma opção:
1) Autenticar usuário
2) Gerar chaves RSA
3) Carregar chave do usuário de arquivo
4) Imprimir chaves
5) Trocar chaves com outro usuário
6) Sair

Selecione uma opção: """
    while True:
        clear()
        if client.username:
            print(f"Bem vindo {client.username}!", end=" ")
        opt = input(menu)
        match opt:
            case "1":
                while True:
                    clear()
                    username = input("Usuário: ")
                    if username == "":
                        continue
                    client.auth(username)
                    break
            case "2":
                if client.username is None:
                    input("Usuário não autenticado, por favor efetue a autenticação do usuário com a opção 1!")
                    continue
                if client.user.exist_keys():
                    if input("As chaves pública e privada já foram geradas. Deseja excluir e gerá-las novamente? (S/n) ") in ["S", "s"]:
                        client.user.remove_keys()
                        generate_keys(client)
                else:
                    generate_keys(client)
            case "3":
                if client.username is None:
                    input("Usuário não autenticado, por favor efetue a autenticação do usuário com a opção 1!")
                    continue
                if not client.user.load_keys():
                    input('Chaves não geradas ainda. Por favor gere pela opção 2!')
                    continue
            case "4":
                if client.username is None:
                    input("Usuário não autenticado, por favor efetue a autenticação do usuário com a opção 1!")
                    continue
                if not client.user.exist_keys():
                    input('Chaves não geradas ainda. Por favor gere pela opção 2!')
                    continue
                client.user.print_keys()
            case "6":
                break


def main():
    client = Client()
    client.connect("", 5555)
    menu(client)


if __name__ == "__main__":
    main()

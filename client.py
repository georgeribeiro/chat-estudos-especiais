import pathlib
import socket
import sys
from Crypto.PublicKey import RSA
from Crypto import Random
from pathlib import Path
import os
import platform
import base64
import threading


HERE = Path(__file__).resolve().parent


class Client:
    def __init__(self) -> None:
        self.user: User = None
        self._server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connected = {}
        
    def connect(self, host: str, port: int) -> None:
        self._server.connect((host, port))
        t = threading.Thread(target=self._listen_server, args=())
        t.daemon = True
        t.start()

    def close(self):
        self._server.close()

    def send(self, action: str, data: str):
        data = " ".join([s for s in (action, data) if s])
        self._server.sendall(data.encode())

    def auth(self, username):
        self.user = User(username)
        self.send("AUTH", username)

    def handshake(self, username):
        key = self.user.pubkey.exportKey()
        key64 = base64.b64encode(key).decode()
        data = f"{username} {key64}"
        self.send("HANDSHAKE", data)

    def _listen_server(self):
        while True:
            data = self._server.recv(2048)
            message = data.decode()
            if message:
                match message.split():
                    case ["HANDSHAKE", username, pubkey]:
                        input("nao sei")
                    case ["ERROR", message]:
                        clear()
                        input(message)


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

    def exists_keys(self):
        path = HERE.joinpath(f"{self.username}.key")
        return path.exists()

    def load_keys(self) -> bool:
        if self.exists_keys():
            with self.privkey_file().open("r") as f:
                pkey = f.read()
                self._privkey = RSA.importKey(pkey)
            return True
        else:
            return False

    def remove_keys(self):
        self.privkey_file().unlink()
        self.pubkey_file().unlink()

    def print_keys(self) -> str:
        return self.privkey.exportKey().decode() + "\n\n" + self.pubkey.exportKey().decode() + "\n"

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
        if client.user is not None:
            print(f"Bem vindo {client.user.username}!", end=" ")
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
                if client.user is None:
                    input("Usuário não autenticado, por favor efetue a autenticação do usuário com a opção 1!")
                    continue
                if client.user.exists_keys():
                    if input("As chaves pública e privada já foram geradas. Deseja excluir e gerá-las novamente? (S/n) ") in ["S", "s"]:
                        client.user.remove_keys()
                        generate_keys(client)
                else:
                    generate_keys(client)
            case "3":
                if client.user is None:
                    input("Usuário não autenticado, por favor efetue a autenticação do usuário com a opção 1!")
                    continue
                if client.user.load_keys():
                    input('Chaves carregadas com sucesso!')
                    continue
                else:
                    input('Chaves não geradas ainda. Por favor gere pela opção 2!')
            case "4":
                if client.user is None:
                    input("Usuário não autenticado, por favor efetue a autenticação do usuário com a opção 1!")
                    continue
                if not client.user.exists_keys():
                    input('Chaves não geradas ainda. Por favor gere pela opção 2!')
                    continue
                if client.user.privkey is None:
                    input('Chaves não geradas ou não carregadas pelo usuário! Por favor use opção 2 pra gerar ou 3 pra carregar!')
                    continue
                clear()
                input(client.user.print_keys())
            case "5":
                if client.user is None:
                    input("Usuário não autenticado, por favor efetue a autenticação do usuário com a opção 1!")
                    continue
                if not client.user.exists_keys():
                    input('Chaves não geradas ainda. Por favor gere pela opção 2!')
                    continue
                if client.user.privkey is None:
                    input('Chaves não geradas ou não carregadas pelo usuário! Por favor use opção 2 pra gerar ou 3 pra carregar!')
                    continue
                while True:
                    username = input("Digite o nome do outro usuário: ")
                    if username == "":
                        continue
                    break
                client.handshake(username)
            case "6":
                client.close()
                break


def main():
    client = Client()
    client.connect("", 5555)
    menu(client)


if __name__ == "__main__":
    main()

import socket
import threading
from typing import List, Any

"""
https://www.geeksforgeeks.org/simple-chat-room-using-python/
"""

class Client:
    def __init__(self, conn: socket.socket, addr: Any, username: str = None) -> None:
        self.conn = conn
        self.addr = addr
        self.username = username

    def __eq__(self, __o: "Client") -> bool:
        return self.conn == __o.conn


class Server:
    def __init__(self, host: str, port: int) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))
        self._clients: List[Client] = []

    def listen(self, max_connections):
        self._sock.listen(max_connections)
        while True:
            conn, addr = self._sock.accept()
            c = Client(conn, addr)
            self._clients.append(c)
            threading.Thread(target=self._clientthread, args=(c,)).start()
            
    def response(self, c: Client, code: str, message: str = ""):
        data = " ".join([s for s in (code, message) if s])
        c.conn.sendall(data.encode())

    def _clientthread(self, c: Client):
        while True:
            try:
                data = c.conn.recv(2048)
                if data:
                    message = data.decode()
                    match message.split():
                        case ["AUTH", username]:
                            c.username = username
                            self.response(c, "OK", f"Usuário {username} autenticado com sucesso!")
                        case ["HSREQUEST", username, pubkey]:
                            if c.username == username:
                                self.response(c, "ERROR", "O usuário não pode trocar chaves consigo mesmo")
                                continue
                            for o in self._clients:
                                if o.username == username:
                                    data = f"{c.username} {pubkey}"
                                    self.response(o, "HSREQUEST", data)
                                    break
                            else:
                                self.response(c, "ERROR", "Usuário não encontrado")
                        case ["HSCONFIRM", username, pubkey]:
                            if c.username == username:
                                self.response(c, "ERROR", "O usuário não pode trocar chaves consigo mesmo")
                                continue
                            for o in self._clients:
                                if o.username == username:
                                    data = f"{c.username} {pubkey}"
                                    self.response(o, "HSCONFIRM", data)
                                    break
                            else:
                                self.response(c, "ERROR", "Usuário não encontrado")
                        case ["MSG", username, message]:
                            if c.username == username:
                                self.response(c, "ERROR", "O usuário não pode enviar mensagens para si mesmo")
                                continue
                            for o in self._clients:
                                if o.username == username:
                                    data = f"{c.username} {message}"
                                    self.response(o, "MSG", data)
                                    break
                            else:
                                self.response(c, "ERROR", "Usuário não encontrado")
                        case _:
                            self.response(c, "ERROR", "Ação inválida")
                else:
                    c.conn.close()
                    self._clients.remove(c)
                    break
            except Exception as e:
                print(e)
                c.conn.close()
                self._clients.remove(c)
                break


def main():
    server = Server("", 5555)
    print(f"Server running in port 5555")
    server.listen(100)


if __name__ == "__main__":
    main()

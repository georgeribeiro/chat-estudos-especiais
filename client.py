import pathlib
import socket
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA512
from pathlib import Path
import base64
import threading
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from typing import List


HERE = Path(__file__).resolve().parent


class Recipient:
    def __init__(self, username: str, pubkey: RSA._RSAobj) -> None:
        self.username = username
        self.pubkey = pubkey
        self.messages: List[str] = []


class Client:
    def __init__(self, callback = None) -> None:
        self.user: User = None
        self.callback = callback
        self._server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recipient: Recipient = None
        self.window: ChatWindow = None
        
    def connect(self, host: str, port: int) -> None:
        self._server.connect((host, port))
        t = threading.Thread(target=self._listen_server, args=())
        t.daemon = True
        t.start()

    def close(self):
        self._server.close()

    def send(self, action: str, *data: List[str]):
        data = "|".join([s for s in (action, *data) if s])
        self._server.sendall(data.encode())

    def auth(self, username):
        self.user = User(username)
        self.send("AUTH", username)

    def handshake(self, username):
        key = self.user.pubkey.exportKey()
        key64 = base64.b64encode(key).decode()
        self.send("HSREQUEST", username, key64)

    def send_assign_message(self, message: str):
        h = SHA512.new()
        h.update(message.encode())
        print(f"HASH de envio: {h.hexdigest()}")
        signer = PKCS1_PSS.new(self.user.privkey)
        signature = signer.sign(h)
        print(f"ASSINATURA DE ENVIO: {signature}")
        encoded_signature = base64.b64encode(signature).decode()
        self.send("MSGSIGNED", self.recipient.username, message, encoded_signature)

    def send_cipher_message(self, message: str):
        encrytor = PKCS1_OAEP.new(self.recipient.pubkey)
        msg = encrytor.encrypt(message.encode())
        print(f"MENSAGEM CIFRADA DE ENVIO: {msg}")
        data = base64.b64encode(msg)
        self.send("MSG", self.recipient.username, data.decode())

    def _listen_server(self):
        while True:
            data = self._server.recv(2048)
            message = data.decode()
            if message:
                match message.split("|"):
                    case ["HSREQUEST", username, pubkey]:
                        key = base64.b64decode(pubkey).decode()
                        self.recipient = Recipient(username, RSA.importKey(key))
                        mykey = self.user.pubkey.exportKey()
                        mykey64 = base64.b64encode(mykey).decode()
                        self.send("HSCONFIRM", username, mykey64)
                        GLib.idle_add(self.callback, "HSREQUEST", username)
                    case ["HSCONFIRM", username, pubkey]:
                        key = base64.b64decode(pubkey).decode()
                        self.recipient = Recipient(username, RSA.importKey(key))
                        GLib.idle_add(self.callback, "HSCONFIRM", username)
                    case ["MSGSIGNED", username, message, encoded_signature]:
                        h = SHA512.new()
                        h.update(message.encode())
                        print(f"HASH de recebimento: {h.hexdigest()}")
                        verifier = PKCS1_PSS.new(self.recipient.pubkey)
                        signature = base64.b64decode(encoded_signature)
                        print(f"ASSINATURA DE RECEBIMENTO: {signature}")
                        if verifier.verify(h, signature):
                            GLib.idle_add(self.callback, "MSG", username, message)
                        else:
                            GLib.idle_add(self.callback, "ERROR", "Mensagem n??o aut??ntica!")
                    case ["MSG", username, message]:
                        encryptor = PKCS1_OAEP.new(self.user.privkey)
                        data = base64.b64decode(message)
                        print(f"MENSAGEM CIFRADA DE RECEBIMENTO: {data}")
                        msg: bytes = encryptor.decrypt(data)
                        GLib.idle_add(self.callback, "MSG", username, msg.decode())
                    case ["OK", msg]:
                        GLib.idle_add(self.callback, "OK", msg)
                    case ["ERROR", msg]:
                        GLib.idle_add(self.callback, "ERROR", msg)



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



class InputDialog(Gtk.Dialog):
    def __init__(self, parent, title="") -> None:
        super().__init__(title, transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        self.set_default_size(150, 100)
        self.entry = Gtk.Entry()
        box = self.get_content_area()
        self.set_modal(True)
        box.add(self.entry)
        self.show_all()


class MessageDialog(Gtk.MessageDialog):
    def __init__(self, parent, message: str) -> None:
        super().__init__(
            transient_for=parent,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )

    
class QuestionDialog(Gtk.MessageDialog):
    def __init__(self, parent, message: str) -> None:
        super().__init__(
            transient_for=parent,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=message
        )


class ChatWindow:
    def __init__(self, client: Client) -> None:
        self.client = client
        self.builder = Gtk.Builder()
        self.builder.add_from_file("chat.glade")
        self.window = self.builder.get_object("application")
        self.txt_message = self.builder.get_object("txt_message")
        self.lbl_message = self.builder.get_object("lbl_message")
        self.ent_text = self.builder.get_object("ent_text")
        self.client.callback = self.on_client_event
        self.builder.connect_signals(self)

    def onDestroy(self, *args):
        Gtk.main_quit()

    def insert_message(self, message):
        buf = self.txt_message.get_buffer()
        end_iter = buf.get_end_iter()
        buf.insert(end_iter, message + "\n")

    def btn_sair_on_click(self, button):
        Gtk.main_quit()

    def btn_autenticar_on_click(self, button):
        dlg = InputDialog(self.window, "Nome do usu??rio")
        resp = dlg.run()
        match resp:
            case Gtk.ResponseType.OK:
                username = dlg.entry.get_text()
                self.client.auth(username)
        dlg.destroy()

    def btn_gerar_rsa_on_click(self, button):
        if self.client.user is None:
            dlg = MessageDialog(self.window, "Usu??rio n??o autenticado!")
            dlg.run()
            dlg.destroy()
            return
        if self.client.user.exists_keys():
            dlg = QuestionDialog(self.window, message="As chaves p??blica e privada j?? foram geradas. Deseja excluir e ger??-las novamente?")
            match dlg.run():
                case Gtk.ResponseType.YES:
                    self.client.user.remove_keys()
                    self.client.user.generate_keys()
                    self.client.user.save_keys()
                    self.insert_message("Chaves geradas com sucesso!")
            dlg.destroy()
            return
        else:
            self.client.user.generate_keys()
            self.client.user.save_keys()
            self.insert_message("Chaves Geradas com sucesso!")
    
    def btn_carregar_chave_on_click(self, button):
        if self.client.user is None:
            dlg = MessageDialog(self.window, "Usu??rio n??o autenticado!")
            dlg.run()
            dlg.destroy()
            return
        if self.client.user.load_keys():
            self.insert_message("Chaves carregadas com sucesso!")
        else:
            dlg = MessageDialog(self.window, "Problema ao carregar chaves. Usu??rio n??o possui chaves geradas!")
            dlg.run()
            dlg.destroy()

    def btn_mostrar_chave_on_click(self, button):
        if self.client.user is None:
            dlg = MessageDialog(self.window, "Usu??rio n??o autenticado!")
            dlg.run()
            dlg.destroy()
            return
        if self.client.user.privkey is None:
            dlg = MessageDialog(self.window, "Chaves n??o geradas ou n??o carregadas!")
            dlg.run()
            dlg.destroy()
            return
        keys = self.client.user.print_keys()
        self.insert_message(keys)

    def btn_trocar_chave_on_click(self, button):
        if self.client.user is None:
            dlg = MessageDialog(self.window, "Usu??rio n??o autenticado!")
            dlg.run()
            dlg.destroy()
            return
        if self.client.user.privkey is None:
            dlg = MessageDialog(self.window, "Chaves n??o geradas ou n??o carregadas!")
            dlg.run()
            dlg.destroy()
            return
        dlg = InputDialog(self.window, "Nome do usu??rio")
        resp = dlg.run()
        match resp:
            case Gtk.ResponseType.OK:
                username = dlg.entry.get_text()
                self.client.handshake(username)
        dlg.destroy()

    def on_client_event(self, *args):
        match args:
            case ["HSREQUEST", username]:
                self.lbl_message.set_text(f"{self.client.user.username} -> {username}")
                self.insert_message(f"Conectado ao usu??rio {username}")
            case ["HSCONFIRM", username]:
                self.lbl_message.set_text(f"{self.client.user.username} -> {username}")
                self.insert_message(f"Conectado ao usu??rio {username}")
            case ["MSG", username, message]:
                self.insert_message(f"{username}: {message}")
            case ["OK", message]:
                self.insert_message(message)
            case ["ERROR", message]:
                self.insert_message("ERROR! " + message)

    def btn_assinar_enviar_on_click(self, button):
        if self.client.user is None:
            dlg = MessageDialog(self.window, "Usu??rio n??o autenticado!")
            dlg.run()
            dlg.destroy()
            return
        if self.client.user.privkey is None:
            dlg = MessageDialog(self.window, "Chaves n??o geradas ou n??o carregadas!")
            dlg.run()
            dlg.destroy()
            return
        if self.client.recipient is None:
            dlg = MessageDialog(self.window, "Usu??rio n??o conectado a outro usu??rio!")
            dlg.run()
            dlg.destroy()
            return
        self.client.send_assign_message(self.ent_text.get_text())

    def btn_cifrar_enviar_on_click(self, button):
        if self.client.user is None:
            dlg = MessageDialog(self.window, "Usu??rio n??o autenticado!")
            dlg.run()
            dlg.destroy()
            return
        if self.client.user.privkey is None:
            dlg = MessageDialog(self.window, "Chaves n??o geradas ou n??o carregadas!")
            dlg.run()
            dlg.destroy()
            return
        if self.client.recipient is None:
            dlg = MessageDialog(self.window, "Usu??rio n??o conectado a outro usu??rio!")
            dlg.run()
            dlg.destroy()
            return
        self.client.send_cipher_message(self.ent_text.get_text())
        

    def show(self):
        self.window.show_all()
        


def main():
    client = Client()
    client.connect("", 5555)
    chat = ChatWindow(client)
    client.window = chat
    chat.show()

    Gtk.main()



if __name__ == "__main__":
    main()

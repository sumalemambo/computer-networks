import socket
from sqlite3 import connect

class Client:
    def __init__(self, sock=None, header=64, format="utf-8", disconnect_msg="DISCONNECT"):
        if sock is None:
            self.clientsocket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.clientsocket = sock
            
        self.header = header
        self.format = format
        self.disconnect_msg = disconnect_msg
    
    def connect(self, host, port):
        self.clientsocket.connect((host, port))

    def game(self):
            print(
            """
            -------- Bienvenido al Juego --------
            - Seleccione una opción
            1-Jugar
            2-Salir
            """
            )
            answer = input(">>")
            if answer == 1:
                pass

    def start(self):
        self.connect("localhost", 5050)
        self.game()




clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(("localhost", 5050))


while True:
    print(
    """
    -------- Bienvenido al Juego --------
    - Seleccione una opción
    1-Jugar
    2-Salir
    """
    )
    answer = input(">>")
    if answer == 2:
        break
    
    msg = input()
    message = msg.encode("utf-8")
    msg_lenght = len(message)
    send_lenght = str(msg_lenght).encode("utf-8")
    send_lenght += b' ' * (64 - len(send_lenght))
    clientsocket.send(send_lenght)
    clientsocket.send(message)

    msg_length = clientsocket.recv(64).decode("utf-8")
    if msg_length:
        msg_length = int(msg_length)
        msg = clientsocket.recv(msg_length).decode("utf-8")
        print(f"{msg}")


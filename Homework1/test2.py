import socket
import ast


BUFFER = 1024
INIT= "!INIT"
AVAILABLE = "!AVAILABLE"
NOT_AVAILABLE = "!NOT_AVAILABLE"
REQUEST_STATE = "!REQUEST_STATE"
REQUEST_MOVE = "!REQUEST_MOVE"
FORMAT = "UTF-8"

X = "X"
O= "O"



address = "localhost"
serverport = 5001

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect((address, serverport))

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
    if answer == "1":
        clientsocket.send(INIT.encode(FORMAT))
        response = clientsocket.recv(BUFFER).decode(FORMAT)
        if response == AVAILABLE:
            print("respuesta de disponibilidad: OK")
            while True:
                # Repeat while no winner
                # Ask server to send the current table
                clientsocket.send(REQUEST_STATE.encode(FORMAT))
                # Receive table
                response = clientsocket.recv(BUFFER).decode(FORMAT)
                if response == X or response == O:
                    break
                # Transform it back to list
                table = ast.literal_eval(response)
                print(table)
                print("Ingrese su jugada (x, y): ")
                play = input(">>")
                clientsocket.send(play.encode(FORMAT))
            if response == X:
                print("Has ganado!")
            else:
                print("Ha ganado el bot!")
        else:
            print("respuesta de disponibilidad: NO DISPONIBLE")
            
    else:
        break

clientsocket.close()
import socket
import ast


BUFFER = 1024
INIT= "!INIT"
AVAILABLE = "!AVAILABLE"
NOT_AVAILABLE = "!NOT_AVAILABLE"
REQUEST_TABLE = "!REQUEST_TABLE"
REQUEST_STATE = "!REQUEST_STATE"
REQUEST_MOVE = "!REQUEST_MOVE"
DISCONNECT = "!DISCONNECT"
FORMAT = "UTF-8"

X = "X"
O = "O"
EMPTY = None
E = "E"

def printTabla(tabla):
    print("+---+---+---+---+")
    print("|   | 0 | 1 | 2 |")
    print("|---+---+---+---|")
    print("| 0 |",(tabla[0][0]," ")[tabla[0][0] == None],"|",(tabla[0][1]," ")[tabla[0][1] == None],"|",(tabla[0][2]," ")[tabla[0][2] == None],"|")
    print("|---+---+---+---|")
    print("| 1 |",(tabla[1][0]," ")[tabla[1][0] == None],"|",(tabla[1][1]," ")[tabla[1][1] == None],"|",(tabla[1][2]," ")[tabla[1][2] == None],"|")
    print("|---+---+---+---|")
    print("| 2 |",(tabla[2][0]," ")[tabla[2][0] == None],"|",(tabla[2][1]," ")[tabla[2][1] == None],"|",(tabla[2][2]," ")[tabla[2][2] == None],"|")
    print("+---+---+---+---+")



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
                if (response == X) or (response == O) or (response == E):
                    break
                # Transform it back to list
                table = ast.literal_eval(response)
                printTabla(table)
                print("Ingrese su jugada (x, y): ")
                play = input(">>")
                clientsocket.send(play.encode(FORMAT))
            if response == X:
                print("Has ganado!")
            elif response == O:
                print("Ha ganado el bot!")
            else:
                print("Empate!")
            clientsocket.send(REQUEST_TABLE.encode(FORMAT))
            response = clientsocket.recv(BUFFER).decode(FORMAT)
            table = ast.literal_eval(response)
            printTabla(table)
        else:
            print("respuesta de disponibilidad: NO DISPONIBLE")
            
    else:
        break
clientsocket.send(DISCONNECT.encode(FORMAT))
clientsocket.close()
